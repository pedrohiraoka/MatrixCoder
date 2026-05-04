"""Gerenciador de agentes da simulação Matrix."""

import asyncio
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
import uuid
from fastapi import WebSocket

from app.models import Agente, AgenteEspecial, LogEntry
from app.services.matrix_engine import Matrix


class AgentManager:
    """
    Gerenciador singleton de agentes da simulação.
    
    Responsável por CRUD de agentes e broadcast de atualizações via WebSocket.
    """

    _instance: Optional["AgentManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "AgentManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.agentes: Dict[str, Agente] = {}
            self.websockets: Set[WebSocket] = set()
            self.matrix = Matrix()
            self._initialized = True
            self._lock = asyncio.Lock()

    @classmethod
    def get_instance(cls) -> "AgentManager":
        """Obtém a instância singleton do gerenciador."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def adicionar_agente(
        self, posicao_x: int = None, posicao_y: int = None, energia: float = 100.0
    ) -> Agente:
        """Adiciona um novo agente à simulação."""
        async with self._lock:
            agente_id = str(uuid.uuid4())
            
            # Encontra posição válida se não fornecida
            if posicao_x is None or posicao_y is None:
                for y in range(self.matrix.grid_size):
                    for x in range(self.matrix.grid_size):
                        celula = self.matrix.grid[y][x]
                        if not celula["ocupado"]:
                            posicao_x = x
                            posicao_y = y
                            break
                    if posicao_x is not None:
                        break
            
            # Se ainda não encontrou posição, retorna None (grid cheio)
            if posicao_x is None or posicao_y is None:
                raise ValueError("Grid cheio - não há posições disponíveis")

            # Ocupa a célula no grid
            if not self.matrix.ocupar_celula(posicao_x, posicao_y, agente_id):
                raise ValueError("Posição já ocupada")

            agente = Agente(
                id=agente_id,
                posicao_x=posicao_x,
                posicao_y=posicao_y,
                energia=energia,
                consciente=False,
            )

            self.agentes[agente_id] = agente
            
            # Log do evento
            self.matrix.adicionar_log(
                nivel="INFO",
                mensagem=f"Agente {agente_id[:8]}... criado na posição ({posicao_x}, {posicao_y})",
                contexto={"agente_id": agente_id, "posicao": (posicao_x, posicao_y)},
            )

            await self.broadcast_estado()
            return agente

    async def remover_agente(self, agente_id: str) -> bool:
        """Remove um agente da simulação."""
        async with self._lock:
            if agente_id not in self.agentes:
                return False

            agente = self.agentes[agente_id]
            
            # Libera a célula no grid
            self.matrix.liberar_celula(agente.posicao_x, agente.posicao_y, agente_id)
            
            # Remove o agente
            del self.agentes[agente_id]
            
            # Atualiza contador de despertos se necessário
            if agente.consciente:
                self.matrix.agentes_despertos = max(0, self.matrix.agentes_despertos - 1)

            # Log do evento
            self.matrix.adicionar_log(
                nivel="WARN",
                mensagem=f"Agente {agente_id[:8]}... removido da simulação",
                contexto={"agente_id": agente_id},
            )

            await self.broadcast_estado()
            return True

    async def despertar_agente(self, agente_id: str) -> Optional[Agente]:
        """Desperta um agente, tornando-o consciente."""
        async with self._lock:
            if agente_id not in self.agentes:
                return None

            agente = self.agentes[agente_id]
            
            if agente.consciente:
                return agente  # Já está desperto

            # Transforma em agente consciente
            agente.consciente = True
            
            # Atualiza contador
            self.matrix.agentes_despertos += 1

            # Log especial de despertar
            self.matrix.adicionar_log(
                nivel="AWAKEN",
                mensagem=f"AGENTE DESPERTO: {agente_id[:8]}... viu além da Matrix!",
                contexto={
                    "agente_id": agente_id,
                    "energia_atual": agente.energia,
                    "mensagem": "Follow the white rabbit",
                },
            )

            await self.broadcast_estado()
            return agente

    async def obter_agente(self, agente_id: str) -> Optional[Agente]:
        """Obtém um agente por ID."""
        return self.agentes.get(agente_id)

    async def listar_agentes(self) -> List[Agente]:
        """Lista todos os agentes ativos."""
        return list(self.agentes.values())

    async def mover_agente(
        self, agente_id: str, nova_posicao_x: int, nova_posicao_y: int
    ) -> bool:
        """Move um agente para uma nova posição."""
        async with self._lock:
            if agente_id not in self.agentes:
                return False

            agente = self.agentes[agente_id]
            pos_antiga = (agente.posicao_x, agente.posicao_y)

            # Verifica se nova posição é válida
            if not (0 <= nova_posicao_x < 10 and 0 <= nova_posicao_y < 10):
                return False

            # Verifica se nova posição está livre
            celula_nova = self.matrix.obter_celula(nova_posicao_x, nova_posicao_y)
            if celula_nova and celula_nova["ocupado"]:
                return False

            # Libera posição antiga e ocupa nova
            self.matrix.liberar_celula(pos_antiga[0], pos_antiga[1], agente_id)
            self.matrix.ocupar_celula(nova_posicao_x, nova_posicao_y, agente_id)

            # Atualiza posição do agente
            agente.posicao_x = nova_posicao_x
            agente.posicao_y = nova_posicao_y

            return True

    async def adicionar_websocket(self, websocket: WebSocket):
        """Adiciona conexão WebSocket ao conjunto de broadcasts."""
        self.websockets.add(websocket)

    async def remover_websocket(self, websocket: WebSocket):
        """Remove conexão WebSocket do conjunto de broadcasts."""
        self.websockets.discard(websocket)

    async def broadcast_estado(self):
        """Envia estado atual para todos os WebSockets conectados."""
        if not self.websockets:
            return

        estado_matrix = self.matrix.obter_estado()
        lista_agentes = [agente.dict() for agente in self.agentes.values()]

        mensagem = {
            "type": "TICK",
            "payload": {
                "grid": estado_matrix.dict()["grid"],
                "agentes": lista_agentes,
                "metricas": {
                    "tempo_simulacao": estado_matrix.tempo_simulacao,
                    "energia_total_coletada": estado_matrix.energia_total_coletada,
                    "agentes_despertos": estado_matrix.agentes_despertos,
                    "ticks_executados": estado_matrix.ticks_executados,
                },
            },
        }

        # Envia para todos os websockets conectados
        websockets_remover = []
        for ws in self.websockets:
            try:
                await ws.send_json(mensagem)
            except Exception:
                websockets_remover.append(ws)

        # Remove websockets desconectados
        for ws in websockets_remover:
            await self.remover_websocket(ws)

    async def broadcast_log(self, log: LogEntry):
        """Envia um log para todos os WebSockets conectados."""
        if not self.websockets:
            return

        mensagem = {
            "type": "LOG",
            "payload": log.dict(),
        }

        websockets_remover = []
        for ws in self.websockets:
            try:
                await ws.send_json(mensagem)
            except Exception:
                websockets_remover.append(ws)

        for ws in websockets_remover:
            await self.remover_websocket(ws)

    async def ver_codigo(self, agente_id: str) -> Optional[Dict[str, Any]]:
        """Permite que um agente consciente veja o código da Matrix."""
        if agente_id not in self.agentes:
            return None

        agente = self.agentes[agente_id]
        if not agente.consciente:
            return {"erro": "Apenas agentes conscientes podem ver o código"}

        return self.matrix.ver_codigo()

    async def manipular_simulacao(
        self, agente_id: str, acao: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Permite que um agente consciente manipule a simulação."""
        if agente_id not in self.agentes:
            return {"sucesso": False, "mensagem": "Agente não encontrado"}

        agente = self.agentes[agente_id]
        if not agente.consciente:
            return {
                "sucesso": False,
                "mensagem": "Apenas agentes conscientes podem manipular a simulação",
            }

        resultado = self.matrix.manipular_simulacao(acao, params)

        if resultado["sucesso"]:
            self.matrix.adicionar_log(
                nivel="INFO",
                mensagem=f"Simulação manipulada: {acao} por {agente_id[:8]}...",
                contexto={"acao": acao, "params": params},
            )
            await self.broadcast_estado()

        return resultado

    def obter_logs_recentes(self, limite: int = 50) -> List[LogEntry]:
        """Obtém logs recentes da simulação."""
        return self.matrix.logs_recentes[-limite:]

    async def resetar_simulacao(self):
        """Reseta completamente a simulação."""
        async with self._lock:
            self.agentes.clear()
            self.matrix = Matrix()
            
            self.matrix.adicionar_log(
                nivel="WARN",
                mensagem="SIMULAÇÃO RESETADA - Todos os agentes removidos",
                contexto={"reset_completo": True},
            )

            await self.broadcast_estado()
