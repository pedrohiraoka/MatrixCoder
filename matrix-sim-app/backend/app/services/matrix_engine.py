"""Motor da simulação Matrix - Gerencia o grid e regras do ambiente."""

import random
import asyncio
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from app.models import Agente, AgenteEspecial, CeldaGrid, MatrixState, LogEntry
from app.config import settings


class Matrix:
    """
    Classe que representa a Matrix - o ambiente de simulação controlado.
    
    Atributos:
        grid: Grade 10x10 de células com estado
        regras: Dicionário com coeficientes e limiares da simulação
        tempo_simulacao: Contador de ticks executados
        energia_total_coletada: Métrica de energia drenada dos agentes
    """

    def __init__(self):
        self.grid_size = settings.grid_size
        self.grid: List[List[Dict[str, Any]]] = [
            [
                {
                    "ocupado": False,
                    "agente_id": None,
                    "energia_ambiental": random.uniform(40.0, 60.0),
                }
                for _ in range(self.grid_size)
            ]
            for _ in range(self.grid_size)
        ]
        
        self.regras: Dict[str, Any] = {
            "drenagem_energia_base": 2.5,  # Energia drenada por tick
            "drenagem_consciente": 0.5,  # Agentes conscientes perdem menos
            "prob_movimento": 0.7,  # Probabilidade de agente se mover
            "limiar_despertar": 10.0,  # Energia mínima para despertar
            "regeneracao_ambiental": 0.5,  # Energia que volta ao grid
            "max_agentes": 50,
        }
        
        self.tempo_simulacao: int = 0
        self.energia_total_coletada: float = 0.0
        self.agentes_despertos: int = 0
        self.ticks_executados: int = 0
        self.logs_recentes: List[LogEntry] = []

    def obter_celula(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """Obtém o estado de uma célula do grid."""
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return self.grid[y][x]
        return None

    def ocupar_celula(self, x: int, y: int, agente_id: str) -> bool:
        """Marca uma célula como ocupada por um agente."""
        celula = self.obter_celula(x, y)
        if celula and not celula["ocupado"]:
            celula["ocupado"] = True
            celula["agente_id"] = agente_id
            return True
        return False

    def liberar_celula(self, x: int, y: int, agente_id: str) -> bool:
        """Libera uma célula ocupada por um agente."""
        celula = self.obter_celula(x, y)
        if celula and celula["agente_id"] == agente_id:
            celula["ocupado"] = False
            celula["agente_id"] = None
            return True
        return False

    def aplicar_regras(self, agente: Agente) -> Dict[str, Any]:
        """
        Aplica as regras da simulação a um agente.
        
        Retorna dicionário com alterações de estado aplicadas.
        """
        alteracoes = {
            "energia_drenada": 0.0,
            "nova_posicao": None,
            "despertou": False,
        }

        # Determina taxa de drenagem baseada na consciência
        if agente.consciente:
            drenagem = self.regras["drenagem_consciente"]
        else:
            drenagem = self.regras["drenagem_energia_base"]

        # Aplica drenagem de energia
        energia_anterior = agente.energia
        agente.energia = max(0.0, agente.energia - drenagem)
        alteracoes["energia_drenada"] = energia_anterior - agente.energia
        self.energia_total_coletada += alteracoes["energia_drenada"]

        # Verifica se agente deve despertar (energia muito baixa)
        if (
            not agente.consciente
            and agente.energia <= self.regras["limiar_despertar"]
        ):
            alteracoes["despertou"] = True

        # Movimento aleatório para agentes não-conscientes
        if not agente.consciente and random.random() < self.regras["prob_movimento"]:
            nova_pos = self._calcular_nova_posicao(agente.posicao_x, agente.posicao_y)
            if nova_pos:
                alteracoes["nova_posicao"] = nova_pos

        return alteracoes

    def _calcular_nova_posicao(
        self, x_atual: int, y_atual: int
    ) -> Optional[Tuple[int, int]]:
        """Calcula nova posição válida para movimento."""
        direcoes = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(direcoes)

        for dx, dy in direcoes:
            novo_x = x_atual + dx
            novo_y = y_atual + dy
            
            if 0 <= novo_x < self.grid_size and 0 <= novo_y < self.grid_size:
                celula = self.grid[novo_y][novo_x]
                if not celula["ocupado"]:
                    return (novo_x, novo_y)

        return None

    def regenerar_energia_ambiental(self):
        """Regenera lentamente a energia ambiental do grid."""
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                celula = self.grid[y][x]
                if not celula["ocupado"]:
                    celula["energia_ambiental"] = min(
                        100.0, celula["energia_ambiental"] + self.regras["regeneracao_ambiental"]
                    )

    def obter_estado(self) -> MatrixState:
        """Retorna o estado atual da Matrix como objeto Pydantic."""
        grid_py = [
            [
                CeldaGrid(
                    ocupado=celula["ocupado"],
                    agente_id=celula["agente_id"],
                    energia_ambiental=celula["energia_ambiental"],
                )
                for celula in linha
            ]
            for linha in self.grid
        ]

        return MatrixState(
            grid=grid_py,
            tempo_simulacao=self.tempo_simulacao,
            energia_total_coletada=self.energia_total_coletada,
            agentes_despertos=self.agentes_despertos,
            ticks_executados=self.ticks_executados,
        )

    def ver_codigo(self) -> Dict[str, Any]:
        """
        Revela o código interno da Matrix.
        Disponível apenas para agentes conscientes.
        """
        return {
            "regras": self.regras.copy(),
            "estado_grid": [[celula.copy() for celula in linha] for linha in self.grid],
            "metricas": {
                "tempo_simulacao": self.tempo_simulacao,
                "energia_total_coletada": self.energia_total_coletada,
                "agentes_despertos": self.agentes_despertos,
                "ticks_executados": self.ticks_executados,
            },
            "logs_recentes": [log.dict() for log in self.logs_recentes[-20:]],
            "versao_simulacao": "1.0.0",
            "mensagem_oculta": "Bem-vindo ao deserto do real.",
        }

    def manipular_simulacao(self, acao: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Permite manipular parâmetros da simulação.
        Disponível apenas para agentes conscientes.
        """
        resultado = {"sucesso": False, "mensagem": "", "dados": None}

        if acao == "injetar_energia":
            valor = params.get("valor", 0)
            if valor > 0:
                for y in range(self.grid_size):
                    for x in range(self.grid_size):
                        self.grid[y][x]["energia_ambiental"] = min(
                            100.0, self.grid[y][x]["energia_ambiental"] + valor / 100
                        )
                resultado["sucesso"] = True
                resultado["mensagem"] = f"Energia injetada: {valor} unidades"
                
        elif acao == "alterar_regra":
            chave = params.get("chave")
            valor = params.get("valor")
            if chave in self.regras and valor is not None:
                self.regras[chave] = valor
                resultado["sucesso"] = True
                resultado["mensagem"] = f"Regra '{chave}' alterada para {valor}"
                
        elif acao == "resetar_metricas":
            self.energia_total_coletada = 0.0
            self.ticks_executados = 0
            resultado["sucesso"] = True
            resultado["mensagem"] = "Métricas resetadas"
            
        else:
            resultado["mensagem"] = f"Ação desconhecida: {acao}"

        return resultado

    def adicionar_log(self, nivel: str, mensagem: str, contexto: Optional[Dict] = None):
        """Adiciona um log à lista recente."""
        log = LogEntry(
            nivel=nivel,
            mensagem=mensagem,
            contexto=contexto,
        )
        self.logs_recentes.append(log)
        
        # Mantém apenas os últimos 100 logs em memória
        if len(self.logs_recentes) > 100:
            self.logs_recentes = self.logs_recentes[-100:]

    def incrementar_tick(self):
        """Incrementa o contador de ticks da simulação."""
        self.tempo_simulacao += 1
        self.ticks_executados += 1
