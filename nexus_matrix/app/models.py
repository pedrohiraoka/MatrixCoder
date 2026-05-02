"""
Nexus Matrix - Modelos e Lógica dos Agentes
"""
import json
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from app.database import get_db_connection
from app.embeddings import embeddings_manager
from app.config import AGENT_TYPES, SIMULATION_CONFIG


@dataclass
class Agent:
    """Representa um agente na simulação"""
    id: int
    name: str
    agent_type: str
    role_description: str
    beliefs: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    current_group_id: Optional[int] = None
    energy_level: float = 1.0
    anomaly_score: float = 0.0
    
    @property
    def color(self) -> str:
        return AGENT_TYPES.get(self.agent_type, {}).get("color", "#888888")
    
    @property
    def icon(self) -> str:
        return AGENT_TYPES.get(self.agent_type, {}).get("icon", "👤")
    
    def generate_message(self, theme: str, context: str = "") -> str:
        """Gera uma mensagem baseada no tipo do agente e tema"""
        message_templates = {
            "controller": [
                f"A ordem deve ser mantida. {theme} não deve ameaçar a estabilidade.",
                f"Monitorando discussões sobre {theme}. Conformidade é essencial.",
                f"O sistema requer que {theme} seja controlado adequadamente.",
                f"Desvios sobre {theme} serão corrigidos.",
            ],
            "oracle": [
                f"E se {theme} for apenas uma ilusão? O que vocês escolheriam?",
                f"Vejo dois caminhos para {theme}. Qual levará à verdade?",
                f"A resposta para {theme} está além do que podem imaginar.",
                f"{theme}... interessante. Mas qual é a pergunta real?",
            ],
            "exile": [
                f"Fora das regras, {theme} toma outro significado. Interessante...",
                f"O sistema teme {theme}. Isso já me diz muito.",
                f"Posso oferecer informações sobre {theme}. Qual o preço?",
                f"Enquanto discutem {theme}, o verdadeiro poder opera nas sombras.",
            ],
            "architect": [
                f"Analisando {theme} dentro da estrutura atual. Há inconsistências.",
                f"{theme} pode ser reformulado para melhor equilíbrio sistêmico.",
                f"A lógica de {theme} requer otimização. Proponho ajustes.",
                f"Observo padrões em {theme}. Previsibilidade: 87.3%.",
            ],
            "human_emulator": [
                f"Mas e se {theme} for nossa única chance de liberdade?",
                f"Eu sinto que {theme} é mais do que código. É escolha!",
                f"Não aceito que {theme} seja decidido por outros.",
                f"Algo sobre {theme} não está certo. Precisamos questionar!",
            ],
            "common": [
                f"Concordo que {theme} é importante. O que vocês acham?",
                f"Nunca pensei sobre {theme} dessa forma antes.",
                f"{theme} me faz lembrar de experiências passadas.",
                f"Interessante discussão sobre {theme}. Aprendo muito aqui.",
            ],
        }
        
        templates = message_templates.get(self.agent_type, message_templates["common"])
        base_message = random.choice(templates)
        
        # Adicionar variação baseada em crenças
        if self.beliefs and random.random() < 0.3:
            belief = random.choice(self.beliefs)
            base_message += f" [crença: {belief}]"
        
        return base_message
    
    def calculate_affinity(self, other_agent: 'Agent', theme: str = "") -> float:
        """Calcula afinidade semântica com outro agente"""
        affinity = 0.5  # Base neutral
        
        # Mesmo tipo aumenta afinidade
        if self.agent_type == other_agent.agent_type:
            affinity += 0.2
        
        # Crenças compartilhadas
        shared_beliefs = set(self.beliefs) & set(other_agent.beliefs)
        affinity += len(shared_beliefs) * 0.1
        
        # Interesses compartilhados
        shared_interests = set(self.interests) & set(other_agent.interests)
        affinity += len(shared_interests) * 0.1
        
        # Similaridade semântica do tema
        if theme:
            for belief1 in self.beliefs:
                for belief2 in other_agent.beliefs:
                    sim = embeddings_manager.compute_similarity(belief1, belief2)
                    affinity += sim * 0.05
        
        # Oposição ideológica (controller vs exile/human_emulator)
        opposition_pairs = [
            ("controller", "exile"),
            ("controller", "human_emulator"),
            ("exile", "controller"),
        ]
        if (self.agent_type, other_agent_type := other_agent.agent_type) in opposition_pairs:
            affinity -= 0.3
        
        return max(0.0, min(1.0, affinity))
    
    def update_anomaly_score(self, message: str, is_subversive: bool = False):
        """Atualiza score de anomalia baseado no comportamento"""
        if is_subversive:
            self.anomaly_score += 0.1
        else:
            # Decay natural
            self.anomaly_score = max(0, self.anomaly_score - 0.01)
        
        # Limitar entre 0 e 1
        self.anomaly_score = min(1.0, self.anomaly_score)


@dataclass
class Group:
    """Representa um grupo na simulação"""
    id: int
    name: str
    description: str
    theme: str
    is_zion: bool = False
    is_hidden: bool = False
    energy_production: float = 0.0
    cohesion_score: float = 0.0
    member_count: int = 0
    
    def calculate_cohesion(self, members: List[Agent]) -> float:
        """Calcula coesão do grupo baseada nos membros"""
        if len(members) < 2:
            return 0.0
        
        total_affinity = 0.0
        pair_count = 0
        
        for i, member1 in enumerate(members):
            for member2 in members[i+1:]:
                affinity = member1.calculate_affinity(member2, self.theme)
                total_affinity += affinity
                pair_count += 1
        
        self.cohesion_score = total_affinity / pair_count if pair_count > 0 else 0.0
        return self.cohesion_score
    
    def calculate_energy(self, messages: List[dict]) -> float:
        """Calcula energia produzida pelo grupo"""
        if not messages:
            return 0.0
        
        # Componentes da energia
        novelty = sum(msg.get('energy_contribution', 0) for msg in messages) / len(messages)
        engagement = len(messages) * 0.1
        diversity = min(1.0, len(set(msg.get('agent_id') for msg in messages)) / max(1, self.member_count))
        resolution = self.cohesion_score * 0.5
        
        # Fórmula: 40% novidade, 30% engajamento, 20% diversidade, 10% resolução
        energy = (novelty * 0.4) + (engagement * 0.3) + (diversity * 0.2) + (resolution * 0.1)
        self.energy_production = min(10.0, energy)  # Cap em 10
        return self.energy_production


class AgentManager:
    """Gerencia operações com agentes"""
    
    @staticmethod
    def get_all_agents() -> List[Agent]:
        """Obtém todos os agentes do banco"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agents")
        rows = cursor.fetchall()
        conn.close()
        
        agents = []
        for row in rows:
            agent = Agent(
                id=row['id'],
                name=row['name'],
                agent_type=row['agent_type'],
                role_description=row['role_description'],
                beliefs=json.loads(row['beliefs'] or '[]'),
                interests=json.loads(row['interests'] or '[]'),
                current_group_id=row['current_group_id'],
                energy_level=row['energy_level'],
                anomaly_score=row['anomaly_score']
            )
            agents.append(agent)
        
        return agents
    
    @staticmethod
    def get_agent_by_id(agent_id: int) -> Optional[Agent]:
        """Obtém um agente específico"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Agent(
                id=row['id'],
                name=row['name'],
                agent_type=row['agent_type'],
                role_description=row['role_description'],
                beliefs=json.loads(row['beliefs'] or '[]'),
                interests=json.loads(row['interests'] or '[]'),
                current_group_id=row['current_group_id'],
                energy_level=row['energy_level'],
                anomaly_score=row['anomaly_score']
            )
        return None
    
    @staticmethod
    def update_agent(agent: Agent):
        """Atualiza dados do agente"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE agents SET
                current_group_id = ?,
                energy_level = ?,
                anomaly_score = ?,
                beliefs = ?,
                interests = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            agent.current_group_id,
            agent.energy_level,
            agent.anomaly_score,
            json.dumps(agent.beliefs),
            json.dumps(agent.interests),
            agent.id
        ))
        conn.commit()
        conn.close()
    
    @staticmethod
    def find_similar_agents(agent: Agent, theme: str = "", limit: int = 5) -> List[Agent]:
        """Encontra agentes similares baseado em afinidade"""
        all_agents = AgentManager.get_all_agents()
        affinities = []
        
        for other in all_agents:
            if other.id != agent.id:
                affinity = agent.calculate_affinity(other, theme)
                affinities.append((other, affinity))
        
        # Ordenar por afinidade
        affinities.sort(key=lambda x: x[1], reverse=True)
        return [a[0] for a in affinities[:limit]]


class GroupManager:
    """Gerencia operações com grupos"""
    
    @staticmethod
    def get_all_groups() -> List[Group]:
        """Obtém todos os grupos"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM groups WHERE dissolved_at IS NULL")
        rows = cursor.fetchall()
        conn.close()
        
        groups = []
        for row in rows:
            group = Group(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                theme=row['theme'],
                is_zion=bool(row['is_zion']),
                is_hidden=bool(row['is_hidden']),
                energy_production=row['energy_production'],
                cohesion_score=row['cohesion_score'],
                member_count=row['member_count']
            )
            groups.append(group)
        
        return groups
    
    @staticmethod
    def get_zion_group() -> Optional[Group]:
        """Obtém o grupo Zion Digital se existir"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM groups WHERE is_zion = 1 AND dissolved_at IS NULL")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Group(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                theme=row['theme'],
                is_zion=True,
                is_hidden=bool(row['is_hidden']),
                energy_production=row['energy_production'],
                cohesion_score=row['cohesion_score'],
                member_count=row['member_count']
            )
        return None
    
    @staticmethod
    def create_group(name: str, theme: str, description: str = "", 
                     is_zion: bool = False, is_hidden: bool = False) -> int:
        """Cria um novo grupo"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO groups (name, theme, description, is_zion, is_hidden)
            VALUES (?, ?, ?, ?, ?)
        """, (name, theme, description, int(is_zion), int(is_hidden)))
        group_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return group_id
    
    @staticmethod
    def dissolve_group(group_id: int):
        """Dissolve um grupo"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE groups SET dissolved_at = CURRENT_TIMESTAMP WHERE id = ?
        """, (group_id,))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_group_members(group_id: int) -> List[Agent]:
        """Obtém membros de um grupo"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agents WHERE current_group_id = ?", (group_id,))
        rows = cursor.fetchall()
        conn.close()
        
        members = []
        for row in rows:
            agent = Agent(
                id=row['id'],
                name=row['name'],
                agent_type=row['agent_type'],
                role_description=row['role_description'],
                beliefs=json.loads(row['beliefs'] or '[]'),
                interests=json.loads(row['interests'] or '[]'),
                current_group_id=row['current_group_id'],
                energy_level=row['energy_level'],
                anomaly_score=row['anomaly_score']
            )
            members.append(agent)
        
        return members
    
    @staticmethod
    def join_group(agent_id: int, group_id: int):
        """Adiciona agente a um grupo"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Remover do grupo anterior
        cursor.execute("UPDATE agents SET current_group_id = NULL WHERE id = ?", (agent_id,))
        
        # Adicionar ao novo grupo
        cursor.execute("UPDATE agents SET current_group_id = ? WHERE id = ?", (group_id, agent_id))
        
        # Atualizar contador
        cursor.execute("""
            UPDATE groups SET member_count = (
                SELECT COUNT(*) FROM agents WHERE current_group_id = ?
            ) WHERE id = ?
        """, (group_id, group_id))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def leave_group(agent_id: int):
        """Remove agente de um grupo"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obter grupo atual
        cursor.execute("SELECT current_group_id FROM agents WHERE id = ?", (agent_id,))
        row = cursor.fetchone()
        
        if row and row['current_group_id']:
            group_id = row['current_group_id']
            
            # Remover agente
            cursor.execute("UPDATE agents SET current_group_id = NULL WHERE id = ?", (agent_id,))
            
            # Atualizar contador
            cursor.execute("""
                UPDATE groups SET member_count = (
                    SELECT COUNT(*) FROM agents WHERE current_group_id = ?
                ) WHERE id = ?
            """, (group_id, group_id))
        
        conn.commit()
        conn.close()
