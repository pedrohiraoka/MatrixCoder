"""
Engine Module - Loop Principal da Simulação

Gerencia:
- Ciclo de simulação assíncrono
- Geração e processamento de eventos
- Sincronização periódica entre agentes e rede
- Controle de velocidade e estado da simulação

NOTAS TÉCNICAS:
- O loop usa asyncio para não bloquear a UI
- Batching é usado para processamento eficiente
- Estado é exposto via API em tempo real
"""

import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime
import json

from .agent import Tachikoma, Reflection
from .memory import CollectiveMemory, create_collective_memory
from .events import EventGenerator, Event


# Configurações da simulação (ajustáveis)
CYCLE_DURATION = 1.0  # segundos por ciclo
SYNC_INTERVAL = 5  # sincronização a cada N ciclos
NOISE_INTENSITY = 0.05  # intensidade do ruído para divergência
PROPAGATION_THRESHOLD = 0.7  # limiar para propagação de memórias
NUM_AGENTS = 10  # número de agentes Tachikoma


class SimulationEngine:
    """
    Motor principal da simulação.
    
    Coordena todos os componentes do sistema Tachikoma,
    gerenciando o loop de simulação e estado global.
    """
    
    def __init__(self, data_dir: str = "data", seed: int = None):
        """
        Inicializa o motor de simulação.
        
        Args:
            data_dir: Diretório para dados (ghosts, banco)
            seed: Seed global para reprodutibilidade
        """
        self.data_dir = data_dir
        self.seed = seed
        
        # Componentes
        self.collective_memory = create_collective_memory(
            f"{data_dir}/collective_memory.db"
        )
        self.event_generator = EventGenerator(seed=seed)
        
        # Criar agentes
        self.agents: List[Tachikoma] = []
        for i in range(NUM_AGENTS):
            agent = Tachikoma(
                agent_id=i,
                collective_memory=self.collective_memory,
                data_dir=data_dir,
                noise_intensity=NOISE_INTENSITY
            )
            self.agents.append(agent)
        
        # Estado da simulação
        self.running = False
        self.current_cycle = 0
        self.speed_multiplier = 1.0
        self.event_history: List[Event] = []
        self.reflection_logs: List[Dict] = []
        
        # Callbacks para UI
        self.on_cycle_complete: Optional[Callable] = None
        self.on_event_generated: Optional[Callable] = None
        
        # Task do loop
        self._simulation_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Inicia o loop de simulação."""
        if self.running:
            return
        
        self.running = True
        self._simulation_task = asyncio.create_task(self._run_loop())
        print(f"🚀 Simulação iniciada com {NUM_AGENTS} agentes")
    
    async def stop(self):
        """Para o loop de simulação."""
        self.running = False
        if self._simulation_task:
            self._simulation_task.cancel()
            try:
                await self._simulation_task
            except asyncio.CancelledError:
                pass
        print("⏸️ Simulação pausada")
    
    async def _run_loop(self):
        """Loop principal da simulação."""
        while self.running:
            try:
                await self._execute_cycle()
                
                # Aguardar próximo ciclo (considerando speed multiplier)
                delay = CYCLE_DURATION / self.speed_multiplier
                await asyncio.sleep(delay)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Erro no ciclo {self.current_cycle}: {e}")
                # Continuar mesmo após erro
                await asyncio.sleep(1)
    
    async def _execute_cycle(self):
        """Executa um único ciclo de simulação."""
        self.current_cycle += 1
        
        # 1. Gerar evento
        event = self.event_generator.generate_event(
            cycle=self.current_cycle,
            agent_ids=list(range(NUM_AGENTS))
        )
        self.event_history.append(event)
        
        if self.on_event_generated:
            self.on_event_generated(event)
        
        # 2. Cada agente processa o evento
        cycle_reflections = []
        for agent in self.agents:
            reflection = agent.reflect(event)
            cycle_reflections.append(reflection)
            
            # 3. Tentar propagar reflexão
            fact_id = agent.propagate(reflection)
            
            # Atualizar ciclo do agente
            agent.increment_cycle()
        
        # 4. Log de reflexões
        self.reflection_logs.append({
            "cycle": self.current_cycle,
            "event": event.to_dict(),
            "reflections": [r.to_dict() for r in cycle_reflections],
            "timestamp": datetime.now().isoformat()
        })
        
        # 5. Sincronização periódica
        if self.current_cycle % SYNC_INTERVAL == 0:
            await self._sync_all_agents()
        
        # 6. Callback para UI
        if self.on_cycle_complete:
            self.on_cycle_complete(self.current_cycle)
    
    async def _sync_all_agents(self):
        """Sincroniza todos os agentes com a rede."""
        sync_tasks = [
            agent.sync_with_net(propagation_threshold=PROPAGATION_THRESHOLD)
            for agent in self.agents
        ]
        
        results = await asyncio.gather(*sync_tasks, return_exceptions=True)
        
        accepted_counts = [
            r if isinstance(r, int) else 0 
            for r in results
        ]
        
        total_accepted = sum(accepted_counts)
        if total_accepted > 0:
            print(f"🔄 Sincronização: {total_accepted} fatos aceitos")
    
    async def run_single_cycle(self):
        """Executa um único ciclo manualmente (para modo passo-a-passo)."""
        if self.running:
            return
        
        await self._execute_cycle()
    
    def set_speed(self, multiplier: float):
        """
        Define multiplicador de velocidade.
        
        Args:
            multiplier: 1.0 = normal, 5.0 = 5x, 10.0 = 10x
        """
        self.speed_multiplier = max(0.1, min(100.0, multiplier))
    
    def get_state(self) -> Dict:
        """Retorna estado completo da simulação."""
        return {
            "running": self.running,
            "current_cycle": self.current_cycle,
            "speed_multiplier": self.speed_multiplier,
            "num_agents": NUM_AGENTS,
            "agents": [agent.get_state() for agent in self.agents],
            "collective_stats": self.collective_memory.get_stats(),
            "recent_events": [
                e.to_dict() for e in self.event_history[-10:]
            ],
            "last_reflections": self.reflection_logs[-1] if self.reflection_logs else None
        }
    
    def get_agent_state(self, agent_id: int) -> Dict:
        """Retorna estado de um agente específico."""
        if 0 <= agent_id < len(self.agents):
            return self.agents[agent_id].get_state()
        return {}
    
    def get_divergence_metrics(self) -> Dict:
        """
        Calcula métricas de divergência entre agentes.
        
        Returns:
            Métricas incluindo variância dos vieses
        """
        import numpy as np
        
        biases_matrix = []
        for agent in self.agents:
            biases = agent.ghost.get_all_biases()
            biases_matrix.append(list(biases.values()))
        
        biases_array = np.array(biases_matrix)
        
        # Calcular variância por traço
        variance_by_trait = {}
        trait_names = list(self.agents[0].ghost.get_all_biases().keys())
        
        for i, trait in enumerate(trait_names):
            variance_by_trait[trait] = float(np.var(biases_array[:, i]))
        
        # Variância total média
        total_variance = float(np.mean(list(variance_by_trait.values())))
        
        return {
            "variance_by_trait": variance_by_trait,
            "total_divergence": total_variance,
            "cycle": self.current_cycle
        }
    
    def reset_network(self, preserve_ghosts: bool = True):
        """
        Reseta a memória coletiva.
        
        Args:
            preserve_ghosts: Se True, mantém Ghosts dos agentes
        """
        self.collective_memory.reset(keep_concepts=not preserve_ghosts)
        self.event_history.clear()
        self.reflection_logs.clear()
        self.current_cycle = 0
        
        # Resetar contadores dos agentes
        for agent in self.agents:
            agent.propagated_facts.clear()
            agent.reflection_history.clear()
            agent.current_cycle = 0
        
        print("🔄 Rede resetada")
    
    def reset_all(self):
        """Reseta completamente a simulação."""
        self.stop()
        self.reset_network(preserve_ghosts=False)
        
        # Recriar agentes com Ghosts zerados
        self.agents.clear()
        for i in range(NUM_AGENTS):
            agent = Tachikoma(
                agent_id=i,
                collective_memory=self.collective_memory,
                data_dir=self.data_dir,
                noise_intensity=NOISE_INTENSITY
            )
            agent.ghost.reset(preserve_biases=False)
            self.agents.append(agent)
        
        # Resetar gerador de eventos
        self.event_generator.reset(seed=self.seed)
        
        print("🔄 Simulação completamente resetada")
    
    def export_logs(self, filepath: str = None) -> str:
        """
        Exporta logs da simulação.
        
        Args:
            filepath: Caminho do arquivo (opcional)
            
        Returns:
            Caminho do arquivo exportado
        """
        if filepath is None:
            filepath = f"{self.data_dir}/simulation_log_{self.current_cycle}.json"
        
        export_data = {
            "metadata": {
                "export_time": datetime.now().isoformat(),
                "total_cycles": self.current_cycle,
                "num_agents": NUM_AGENTS,
                "seed": self.seed
            },
            "events": [e.to_dict() for e in self.event_history],
            "reflections": self.reflection_logs,
            "final_state": self.get_state(),
            "divergence_metrics": self.get_divergence_metrics()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filepath


# Singleton global
_simulation_engine: Optional[SimulationEngine] = None

def get_engine() -> SimulationEngine:
    """Obtém instância singleton do motor."""
    global _simulation_engine
    if _simulation_engine is None:
        _simulation_engine = SimulationEngine()
    return _simulation_engine
