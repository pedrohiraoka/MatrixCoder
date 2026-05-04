"""Controlador de IA - Loop assíncrono principal da simulação."""

import asyncio
from typing import Optional
from datetime import datetime
import logging

from app.config import settings
from app.services.agent_manager import AgentManager
from app.models import LogEntry

logger = logging.getLogger(__name__)


class AIController:
    """
    Controlador de IA que gerencia o loop principal da simulação.
    
    Executa em background, atualizando agentes e coletando métricas.
    """

    def __init__(self):
        self.manager = AgentManager.get_instance()
        self.running: bool = False
        self.task: Optional[asyncio.Task] = None
        self.tick_interval = settings.simulation_tick_ms / 1000.0  # Converte para segundos

    async def iniciar(self):
        """Inicia o loop de simulação em background."""
        if self.running:
            logger.warning("Simulação já está rodando")
            return

        self.running = True
        self.task = asyncio.create_task(self._loop_simulacao())
        
        self.manager.matrix.adicionar_log(
            nivel="INFO",
            mensagem="Sistema de simulação iniciado - IA no controle",
            contexto={"tick_interval_ms": settings.simulation_tick_ms},
        )
        
        logger.info(f"Simulação iniciada com tick de {settings.simulation_tick_ms}ms")

    async def parar(self):
        """Para o loop de simulação."""
        self.running = False
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
        
        self.manager.matrix.adicionar_log(
            nivel="WARN",
            mensagem="Sistema de simulação parado",
            contexto={"running": False},
        )
        
        logger.info("Simulação parada")

    async def _loop_simulacao(self):
        """Loop principal da simulação."""
        while self.running:
            try:
                await self._executar_tick()
                await asyncio.sleep(self.tick_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no loop de simulação: {e}")
                await asyncio.sleep(1)  # Previne loop infinito de erros

    async def _executar_tick(self):
        """Executa um tick da simulação."""
        manager = self.manager
        matrix = manager.matrix

        # Incrementa contador de ticks
        matrix.incrementar_tick()

        # Aplica regras a cada agente
        for agente_id, agente in list(manager.agentes.items()):
            # Aplica regras da Matrix
            alteracoes = matrix.aplicar_regras(agente)

            # Processa movimento se houver
            if alteracoes["nova_posicao"]:
                nova_x, nova_y = alteracoes["nova_posicao"]
                await manager.mover_agente(agente_id, nova_x, nova_y)

            # Verifica despertar automático (energia crítica)
            if alteracoes["despertou"]:
                await manager.despertar_agente(agente_id)

        # Regenera energia ambiental periodicamente
        if matrix.ticks_executados % 10 == 0:
            matrix.regenerar_energia_ambiental()

        # Broadcast do estado atualizado
        await manager.broadcast_estado()

        # Log periódico (a cada 20 ticks)
        if matrix.ticks_executados % 20 == 0:
            matrix.adicionar_log(
                nivel="INFO",
                mensagem=f"Tick {matrix.ticks_executados}: Energia coletada={matrix.energia_total_coletada:.1f}, Agentes={len(manager.agentes)}, Despertos={matrix.agentes_despertos}",
                contexto={
                    "ticks": matrix.ticks_executados,
                    "energia": matrix.energia_total_coletada,
                    "agentes_count": len(manager.agentes),
                    "despertos": matrix.agentes_despertos,
                },
            )


# Singleton global
ai_controller = AIController()
