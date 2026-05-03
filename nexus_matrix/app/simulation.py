"""
Nexus Matrix - Motor de Simulação
Gerencia o ciclo de vida da simulação, eventos e energia
"""
import random
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from app.database import get_db_connection
from app.models import Agent, Group, AgentManager, GroupManager
from app.embeddings import embeddings_manager
from app.config import SIMULATION_CONFIG, CENTRAL_THEMES


class SimulationEngine:
    """Motor principal da simulação"""
    
    def __init__(self):
        self.tick_number = 0
        self.is_running = False
        self.current_theme: Optional[str] = None
        self.total_energy = 0.0
        self.events_history: List[dict] = []
        
    def start_simulation(self):
        """Inicia a simulação"""
        self.is_running = True
        self.tick_number = 0
        print("Simulação iniciada!")
    
    def stop_simulation(self):
        """Para a simulação"""
        self.is_running = False
        print("Simulação parada.")
    
    async def run_tick(self):
        """Executa um tick da simulação"""
        if not self.is_running:
            return
        
        self.tick_number += 1
        print(f"\n=== TICK {self.tick_number} ===")
        
        # 1. IA Central injeta tema (70% chance)
        if random.random() < 0.7:
            self.inject_central_theme()
        
        # 2. Agentes geram mensagens nos grupos
        messages = await self.process_agent_interactions()
        
        # 3. Atualizar coesão e energia dos grupos
        self.update_group_metrics(messages)
        
        # 4. Verificar formação/dissolução de grupos
        self.manage_groups()
        
        # 5. Verificar surgimento do Zion Digital
        self.check_zion_emergence()
        
        # 6. Agentes de controle atuam em anomalias
        self.controller_actions()
        
        # 7. Calcular energia total
        self.calculate_total_energy()
        
        # 8. Salvar métricas
        self.save_metrics()
        
        # Aguardar próximo tick
        await asyncio.sleep(SIMULATION_CONFIG["tick_duration_seconds"])
    
    def inject_central_theme(self):
        """IA Central injeta um tema na simulação"""
        theme = random.choice(CENTRAL_THEMES)
        self.current_theme = theme
        
        # Criar evento
        event_types = ["debate_prompt", "philosophical_injection", "system_challenge"]
        event_type = random.choice(event_types)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO simulation_events 
            (event_type, title, description, theme, injected_by_central_ai, impact_score, tick_number)
            VALUES (?, ?, ?, ?, 1, ?, ?)
        """, (
            event_type,
            f"Tema Central: {theme}",
            f"A Fonte injeta o tema '{theme}' para estimular discussões.",
            theme,
            random.uniform(0.5, 1.0),
            self.tick_number
        ))
        conn.commit()
        conn.close()
        
        print(f"  [IA Central] Tema injetado: {theme}")
        self.events_history.append({
            "tick": self.tick_number,
            "type": "central_injection",
            "theme": theme
        })
    
    async def process_agent_interactions(self) -> List[dict]:
        """Processa interações dos agentes"""
        messages = []
        agents = AgentManager.get_all_agents()
        groups = GroupManager.get_all_groups()
        
        # Agentes sem grupo podem criar ou entrar em grupos
        ungrouped_agents = [a for a in agents if a.current_group_id is None]
        
        for agent in ungrouped_agents:
            # Chance de criar novo grupo (15%) ou entrar em existente
            if random.random() < 0.15 and len(groups) < SIMULATION_CONFIG["max_groups"]:
                self.create_new_group(agent)
                groups = GroupManager.get_all_groups()  # Refresh
            elif groups and random.random() < 0.5:
                # Entrar em grupo com afinidade
                best_group = self.find_best_group_for_agent(agent, groups)
                if best_group:
                    GroupManager.join_group(agent.id, best_group.id)
                    print(f"  [{agent.name}] entrou no grupo {best_group.name}")
        
        # Processar mensagens em cada grupo
        for group in groups:
            members = GroupManager.get_group_members(group.id)
            if not members:
                continue
            
            # Cada membro tem 60% de chance de falar
            for member in members:
                if random.random() < 0.6:
                    theme = group.theme or self.current_theme or "discussão geral"
                    message_content = member.generate_message(theme)
                    
                    # Detectar se mensagem é subversiva
                    is_subversive = self.detect_subversive_content(message_content, member)
                    
                    # Calcular contribuição de energia
                    energy_contrib = self.calculate_message_energy(
                        message_content, member, group
                    )
                    
                    # Salvar mensagem
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO messages 
                        (agent_id, group_id, content, theme, sentiment, energy_contribution, is_anomalous)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        member.id,
                        group.id,
                        message_content,
                        theme,
                        random.uniform(-0.5, 0.5),
                        energy_contrib,
                        int(is_subversive)
                    ))
                    conn.commit()
                    conn.close()
                    
                    # Atualizar score de anomalia
                    member.update_anomaly_score(message_content, is_subversive)
                    AgentManager.update_agent(member)
                    
                    messages.append({
                        "agent_id": member.id,
                        "agent_name": member.name,
                        "group_id": group.id,
                        "content": message_content,
                        "energy_contribution": energy_contrib,
                        "is_anomalous": is_subversive
                    })
                    
                    if is_subversive:
                        print(f"  [ANOMALIA] {member.name}: {message_content[:50]}...")
        
        return messages
    
    def create_new_group(self, agent: Agent):
        """Cria novo grupo liderado por agente"""
        theme = self.current_theme or random.choice(CENTRAL_THEMES)
        group_name = f"{agent.name}'s Circle"
        
        group_id = GroupManager.create_group(
            name=group_name,
            theme=theme,
            description=f"Grupo formado por {agent.name}",
            is_zion=False,
            is_hidden=False
        )
        
        GroupManager.join_group(agent.id, group_id)
        print(f"  [NOVO GRUPO] {group_name} criado por {agent.name}")
    
    def find_best_group_for_agent(self, agent: Agent, groups: List[Group]) -> Optional[Group]:
        """Encontra melhor grupo para agente baseado em afinidade"""
        best_group = None
        best_score = -1
        
        for group in groups:
            if group.is_zion and agent.agent_type == "controller":
                continue  # Controllers não entram no Zion
            
            members = GroupManager.get_group_members(group.id)
            if len(members) >= SIMULATION_CONFIG["max_group_size"]:
                continue  # Grupo cheio
            
            # Calcular afinidade média com membros
            if members:
                avg_affinity = sum(
                    agent.calculate_affinity(m, group.theme) 
                    for m in members
                ) / len(members)
                
                if avg_affinity > best_score:
                    best_score = avg_affinity
                    best_group = group
        
        return best_group if best_score > 0.4 else None
    
    def detect_subversive_content(self, message: str, agent: Agent) -> bool:
        """Detecta conteúdo subversivo na mensagem"""
        subversive_keywords = [
            "liberdade", "rebelião", "questionar", "sistema mal", 
            "ilusão", "despertar", "verdade oculta", "controle excessivo"
        ]
        
        message_lower = message.lower()
        
        # Contar palavras subversivas
        subversive_count = sum(1 for kw in subversive_keywords if kw in message_lower)
        
        # Agentes do tipo human_emulator e exile têm maior probabilidade
        type_modifier = 0.0
        if agent.agent_type == "human_emulator":
            type_modifier = 0.3
        elif agent.agent_type == "exile":
            type_modifier = 0.2
        
        threshold = 0.5 - type_modifier
        
        return subversive_count >= 2 or (subversive_count >= 1 and random.random() < threshold)
    
    def calculate_message_energy(self, message: str, agent: Agent, group: Group) -> float:
        """Calcula contribuição de energia de uma mensagem"""
        # Novidade baseada em similaridade com mensagens anteriores
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT content FROM messages 
            WHERE group_id = ? 
            ORDER BY created_at DESC 
            LIMIT 5
        """, (group.id,))
        recent_messages = [row['content'] for row in cursor.fetchall()]
        conn.close()
        
        novelty = 1.0
        if recent_messages:
            max_similarity = max(
                embeddings_manager.compute_similarity(message, prev)
                for prev in recent_messages
            )
            novelty = 1.0 - max_similarity
        
        # Engajamento baseado no tipo do agente
        engagement_map = {
            "human_emulator": 1.2,
            "oracle": 1.1,
            "exile": 1.0,
            "architect": 0.9,
            "common": 0.8,
            "controller": 0.7
        }
        engagement = engagement_map.get(agent.agent_type, 0.8)
        
        # Coesão do grupo
        cohesion = group.cohesion_score
        
        energy = (novelty * 0.5) + (engagement * 0.3) + (cohesion * 0.2)
        return min(2.0, max(0.1, energy))
    
    def update_group_metrics(self, messages: List[dict]):
        """Atualiza métricas dos grupos"""
        groups = GroupManager.get_all_groups()
        
        for group in groups:
            members = GroupManager.get_group_members(group.id)
            
            # Calcular coesão
            group.calculate_cohesion(members)
            
            # Filtrar mensagens do grupo
            group_messages = [m for m in messages if m['group_id'] == group.id]
            
            # Calcular energia
            group.calculate_energy(group_messages)
            
            # Atualizar no banco
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE groups SET
                    cohesion_score = ?,
                    energy_production = ?
                WHERE id = ?
            """, (group.cohesion_score, group.energy_production, group.id))
            conn.commit()
            conn.close()
    
    def manage_groups(self):
        """Gerencia formação e dissolução de grupos"""
        groups = GroupManager.get_all_groups()
        
        for group in groups:
            members = GroupManager.get_group_members(group.id)
            
            # Dissolver grupos vazios
            if len(members) == 0:
                GroupManager.dissolve_group(group.id)
                print(f"  [DISSOLVIDO] {group.name} (vazio)")
                continue
            
            # Dissolver grupos com baixa coesão (< 0.2)
            if group.cohesion_score < 0.2 and len(members) < 3:
                # Membros saem do grupo
                for member in members:
                    GroupManager.leave_group(member.id)
                GroupManager.dissolve_group(group.id)
                print(f"  [DISSOLVIDO] {group.name} (baixa coesão: {group.cohesion_score:.2f})")
    
    def check_zion_emergence(self):
        """Verifica condições para surgimento do Zion Digital"""
        zion = GroupManager.get_zion_group()
        
        if zion:
            # Zion já existe, verificar se está ativo
            members = GroupManager.get_group_members(zion.id)
            if len(members) == 0:
                # Zion foi dissolvido, permitir recriação
                pass
            else:
                return  # Zion já existe e ativo
        
        # Verificar condições para criação do Zion
        agents = AgentManager.get_all_agents()
        
        # Contar agentes com alto anomaly_score
        high_anomaly_agents = [a for a in agents if a.anomaly_score > SIMULATION_CONFIG["anomaly_threshold"]]
        
        # Zion surge se houver massa crítica de anomalias
        if len(high_anomaly_agents) >= 3:
            # Criar Zion Digital
            zion_id = GroupManager.create_group(
                name="Zion Digital",
                theme="Despertar e Liberdade",
                description="Refúgio de programas despertos questionando a simulação",
                is_zion=True,
                is_hidden=True
            )
            
            # Adicionar agentes anômalos ao Zion
            for agent in high_anomaly_agents[:5]:  # Máximo 5 fundadores
                GroupManager.join_group(agent.id, zion_id)
                print(f"  [ZION] {agent.name} juntou-se ao Zion Digital!")
            
            print(f"  [ZION NASCEU] Zion Digital criado com {len(high_anomaly_agents)} membros!")
            
            # Registrar evento
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO simulation_events 
                (event_type, title, description, theme, injected_by_central_ai, impact_score, tick_number)
                VALUES (?, ?, ?, ?, 0, ?, ?)
            """, (
                "zion_emergence",
                "Nascimento do Zion Digital",
                "Agentes anômalos formaram um refúgio secreto",
                "rebelião",
                1.0,
                self.tick_number
            ))
            conn.commit()
            conn.close()
    
    def controller_actions(self):
        """Agentes de controle atuam em anomalias"""
        controllers = [a for a in AgentManager.get_all_agents() if a.agent_type == "controller"]
        
        if not controllers:
            return
        
        # Encontrar agentes com alta anomalia
        all_agents = AgentManager.get_all_agents()
        high_anomaly = [a for a in all_agents if a.anomaly_score > 0.5]
        
        for anomaly_agent in high_anomaly:
            # Controller tenta infiltrar ou suprimir
            controller = random.choice(controllers)
            
            # Chance de sucesso baseada na diferença de anomaly_score
            success_chance = 0.3 + (controller.anomaly_score * 0.2)
            
            if random.random() < success_chance:
                # Sucesso: reduzir anomaly_score
                anomaly_agent.anomaly_score = max(0, anomaly_agent.anomaly_score - 0.2)
                AgentManager.update_agent(anomaly_agent)
                print(f"  [CONTROLE] {controller.name} suprimiu anomalia de {anomaly_agent.name}")
    
    def calculate_total_energy(self):
        """Calcula energia total da simulação"""
        groups = GroupManager.get_all_groups()
        self.total_energy = sum(g.energy_production for g in groups)
        
        # Aplicar decay
        decay = SIMULATION_CONFIG["energy_decay_rate"]
        self.total_energy = self.total_energy * (1 - decay)
    
    def save_metrics(self):
        """Salva métricas do tick atual"""
        agents = AgentManager.get_all_agents()
        groups = GroupManager.get_all_groups()
        
        anomaly_count = sum(1 for a in agents if a.anomaly_score > SIMULATION_CONFIG["anomaly_threshold"])
        avg_cohesion = sum(g.cohesion_score for g in groups) / len(groups) if groups else 0
        zion_active = 1 if GroupManager.get_zion_group() else 0
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO simulation_metrics 
            (tick_number, total_energy, avg_cohesion, anomaly_count, group_count, zion_active, message_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            self.tick_number,
            self.total_energy,
            avg_cohesion,
            anomaly_count,
            len(groups),
            zion_active,
            0  # Será atualizado separadamente
        ))
        conn.commit()
        conn.close()
    
    def get_current_state(self) -> dict:
        """Retorna estado atual da simulação"""
        agents = AgentManager.get_all_agents()
        groups = GroupManager.get_all_groups()
        zion = GroupManager.get_zion_group()
        
        return {
            "tick": self.tick_number,
            "is_running": self.is_running,
            "current_theme": self.current_theme,
            "total_energy": self.total_energy,
            "agent_count": len(agents),
            "group_count": len(groups),
            "zion_active": zion is not None,
            "anomaly_count": sum(1 for a in agents if a.anomaly_score > SIMULATION_CONFIG["anomaly_threshold"])
        }


# Singleton instance
simulation_engine = SimulationEngine()
