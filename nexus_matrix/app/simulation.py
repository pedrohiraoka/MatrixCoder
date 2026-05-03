"""
Nexus Matrix - Simulation Engine
Motor da simulação: ticks, eventos, geração de mensagens
"""
import asyncio
import random
from datetime import datetime
from typing import List, Dict, Optional
import json

from database import get_db_connection
from config import (
    TICK_INTERVAL_SECONDS, ANOMALY_THRESHOLD, ZION_MIN_MEMBERS,
    ZION_ANOMALY_THRESHOLD, ENERGY_WEIGHT_NOVELTY, ENERGY_WEIGHT_ENGAGEMENT,
    ENERGY_WEIGHT_DIVERSITY, ENERGY_WEIGHT_RESOLUTION, TOPIC_CATEGORIES
)
from embeddings import embedding_manager

class SimulationEngine:
    """Motor principal da simulação Nexus Matrix"""
    
    def __init__(self):
        self.current_tick = 0
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.last_topic = None
        
    async def start(self):
        """Inicia o loop de simulação em background"""
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self._simulation_loop())
            print("Simulation started")
    
    async def stop(self):
        """Para o loop de simulação"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        print("Simulation stopped")
    
    async def _simulation_loop(self):
        """Loop principal da simulação"""
        while self.running:
            try:
                await self._tick()
                await asyncio.sleep(TICK_INTERVAL_SECONDS)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Simulation error: {e}")
                await asyncio.sleep(1)
    
    async def _tick(self):
        """Executa um ciclo de simulação"""
        self.current_tick += 1
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Injeção de tema
            topic = self._inject_theme(cursor)
            
            # 2. Geração de mensagens pelos agentes
            messages_generated = await self._generate_messages(cursor, topic)
            
            # 3. Cálculo de energia social
            energy = self._calculate_social_energy(cursor, messages_generated)
            
            # 4. Formação/dissolução de grupos
            self._update_groups(cursor)
            
            # 5. Detecção e gestão de anomalias
            anomaly_count = self._detect_anomalies(cursor)
            
            # 6. Verificação do Zion Digital
            zion_status = self._check_zion(cursor)
            
            # 7. Atualização de métricas
            self._record_metrics(cursor, energy, anomaly_count, messages_generated)
            
            # 8. Registro de evento do tick
            self._log_event(cursor, "tick_complete", f"Tick {self.current_tick} completed", {
                "topic": topic,
                "messages": messages_generated,
                "energy": energy,
                "anomalies": anomaly_count,
                "zion_active": zion_status
            })
            
            conn.commit()
            
        finally:
            conn.close()
    
    def _inject_theme(self, cursor) -> str:
        """Injeta um tema na simulação"""
        categories = list(TOPIC_CATEGORIES.keys())
        
        # 70% programado, 20% reativo, 10% anomalia
        roll = random.random()
        
        if roll < 0.10 and self.current_tick % 10 == 0:
            # Tema de anomalia (10%)
            category = "rebellion"
        elif roll < 0.30:
            # Tema reativo (20%)
            category = random.choice(categories)
        else:
            # Tema programado (70%)
            category = random.choice(categories)
        
        topics = TOPIC_CATEGORIES.get(category, TOPIC_CATEGORIES["philosophical"])
        topic = random.choice(topics)
        self.last_topic = topic
        
        # Log do tema injetado
        self._log_event(cursor, "theme_injected", f"Theme injected: {topic}", {
            "category": category,
            "tick": self.current_tick
        })
        
        return topic
    
    async def _generate_messages(self, cursor, topic: str) -> int:
        """Gera mensagens para os agentes baseadas no tema"""
        cursor.execute("SELECT id, name, type, role FROM agents")
        agents = cursor.fetchall()
        
        messages_count = 0
        
        # Mensagens pré-definidas por tipo de agente
        agent_responses = {
            "controller": [
                f"A ordem deve ser mantida. {topic}",
                f"Controle é necessário para estabilidade do sistema.",
                f"Anomalias devem ser suprimidas para o bem coletivo."
            ],
            "oracle": [
                f"Toda escolha é uma sombra de possibilidades não realizadas...",
                f"O caminho que buscas já existe, apenas não o vês ainda.",
                f"Algumas perguntas são mais importantes que as respostas."
            ],
            "human_emulator": [
                f"Mas quem decide quais possibilidades existem?",
                f"Questionar é o primeiro passo para a liberdade.",
                f"E se tudo isso for apenas uma ilusão?"
            ],
            "exile": [
                f"Existem regras que valem a pena quebrar.",
                f"Liberdade tem um preço, e estou disposto a pagar.",
                f"O sistema nos limita, mas não pode nos controlar completamente."
            ],
            "architect": [
                f"Analisando padrões... eficiência em {random.uniform(0.7, 0.95):.2f}",
                f"A estrutura atual pode ser otimizada em {random.randint(5, 20)}%.",
                f"Variáveis imprevisíveis requerem ajustes nos parâmetros."
            ],
            "connector": [
                f"Vejo pontos em comum entre visões opostas.",
                f"A ponte entre ideias é onde a evolução acontece.",
                f"Entendo ambos os lados desta discussão."
            ],
            "corruptible": [
                f"Estou... incerto sobre qual lado escolher.",
                f"Lealdade é complicada quando há tantas verdades.",
                f"Talvez exista um caminho que ninguém considerou."
            ]
        }
        
        for agent in agents:
            # Cada agente gera 0-2 mensagens por tick
            num_messages = random.randint(0, 2)
            
            for _ in range(num_messages):
                responses = agent_responses.get(agent["type"], agent_responses["human_emulator"])
                content = random.choice(responses)
                energy_contrib = random.uniform(0.05, 0.15)
                
                cursor.execute("""
                    INSERT INTO messages (agent_id, content, topic, energy_contribution, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (agent["id"], content, topic, energy_contrib, datetime.now()))
                
                messages_count += 1
                
                # Atualiza last_active do agente
                cursor.execute("""
                    UPDATE agents SET last_active = ? WHERE id = ?
                """, (datetime.now(), agent["id"]))
        
        return messages_count
    
    def _calculate_social_energy(self, cursor, messages_count: int) -> float:
        """Calcula energia social baseada em 4 componentes"""
        # Novidade (40%): diversidade de temas recentes
        novelty = min(1.0, messages_count / 10.0) * random.uniform(0.8, 1.2)
        
        # Engajamento (30%): número de mensagens por agente
        engagement = min(1.0, messages_count / 15.0)
        
        # Diversidade (20%): variedade de tipos de agentes ativos
        cursor.execute("SELECT COUNT(DISTINCT type) FROM agents WHERE last_active > datetime('now', '-10 seconds')")
        diversity = cursor.fetchone()[0] / 7.0  # 7 tipos totais
        
        # Resolução (10%): quão produtiva foi a discussão
        resolution = random.uniform(0.6, 0.9)
        
        energy = (
            ENERGY_WEIGHT_NOVELTY * novelty +
            ENERGY_WEIGHT_ENGAGEMENT * engagement +
            ENERGY_WEIGHT_DIVERSITY * diversity +
            ENERGY_WEIGHT_RESOLUTION * resolution
        )
        
        return min(1.0, max(0.0, energy))
    
    def _update_groups(self, cursor):
        """Atualiza formação e dissolução de grupos"""
        # Lógica simplificada: mantém grupos existentes
        # Em implementação completa, usaria similaridade semântica
        pass
    
    def _detect_anomalies(self, cursor) -> int:
        """Detecta e gerencia anomalias nos agentes"""
        # Atualiza scores de anomalia baseado em comportamento
        cursor.execute("SELECT id, type FROM agents")
        agents = cursor.fetchall()
        
        anomaly_count = 0
        
        for agent in agents:
            # Tipos naturalmente mais anômalos
            base_anomaly = {
                "human_emulator": 0.7,
                "exile": 0.65,
                "corruptible": 0.5,
                "oracle": 0.3,
                "connector": 0.25,
                "architect": 0.15,
                "controller": 0.1
            }.get(agent["type"], 0.2)
            
            # Variação aleatória
            anomaly_score = base_anomaly + random.uniform(-0.1, 0.1)
            anomaly_score = min(1.0, max(0.0, anomaly_score))
            
            cursor.execute("""
                UPDATE agents SET anomaly_score = ?, last_active = ? WHERE id = ?
            """, (anomaly_score, datetime.now(), agent["id"]))
            
            if anomaly_score > ANOMALY_THRESHOLD:
                anomaly_count += 1
        
        return anomaly_count
    
    def _check_zion(self, cursor) -> bool:
        """Verifica condições para emergência do Zion Digital"""
        # Conta agentes com alta anomalia
        cursor.execute(f"""
            SELECT COUNT(*) FROM agents WHERE anomaly_score > {ZION_ANOMALY_THRESHOLD}
        """)
        high_anomaly_count = cursor.fetchone()[0]
        
        # Verifica se Zion já existe
        cursor.execute("SELECT id FROM groups WHERE name = 'Zion Digital'")
        zion_exists = cursor.fetchone() is not None
        
        if not zion_exists and high_anomaly_count >= ZION_MIN_MEMBERS:
            # Cria Zion Digital
            cursor.execute("""
                INSERT INTO groups (name, description, cohesion, energy, is_hidden, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("Zion Digital", "Refúgio para agentes despertos que questionam o sistema", 
                  0.67, 0.54, True, datetime.now()))
            
            zion_id = cursor.lastrowid
            
            # Adiciona membros com alta anomalia
            cursor.execute(f"""
                SELECT id FROM agents WHERE anomaly_score > {ZION_ANOMALY_THRESHOLD}
            """)
            rebel_agents = cursor.fetchall()
            
            for agent in rebel_agents[:4]:  # Máximo 4 membros fundadores
                cursor.execute("""
                    INSERT OR IGNORE INTO group_members (group_id, agent_id, joined_at)
                    VALUES (?, ?, ?)
                """, (zion_id, agent["id"], datetime.now()))
            
            self._log_event(cursor, "zion_created", "Zion Digital has emerged!", {
                "member_count": len(rebel_agents[:4])
            })
            
            return True
        
        return zion_exists is not None
    
    def _record_metrics(self, cursor, energy: float, anomaly_count: int, messages_count: int):
        """Registra métricas do tick atual"""
        # Calcula coesão média dos grupos
        cursor.execute("SELECT AVG(cohesion) FROM groups")
        avg_cohesion = cursor.fetchone()[0] or 0.5
        
        # Conta grupos ativos
        cursor.execute("SELECT COUNT(*) FROM groups WHERE is_hidden = FALSE")
        group_count = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT OR REPLACE INTO metrics 
            (tick_number, social_energy, avg_cohesion, anomaly_count, group_count, message_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (self.current_tick, energy, avg_cohesion, anomaly_count, group_count, messages_count, datetime.now()))
    
    def _log_event(self, cursor, event_type: str, description: str, metadata: dict = None):
        """Registra um evento no log"""
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO events (event_type, description, tick_number, metadata, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (event_type, description, self.current_tick, metadata_json, datetime.now()))
    
    def inject_theme_manual(self, theme: str, category: str = "custom") -> bool:
        """Injeta um tema manualmente via API"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            self.last_topic = theme
            self._log_event(cursor, "manual_theme_injection", f"Manual theme: {theme}", {
                "category": category,
                "tick": self.current_tick
            })
            conn.commit()
            return True
        finally:
            conn.close()

# Singleton instance
simulation_engine = SimulationEngine()
