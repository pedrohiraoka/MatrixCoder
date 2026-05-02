"""
Memory Module - Gerenciamento de Memória Coletiva e Local

Implementa:
- The Net: Memória coletiva em SQLite (collective_memory.db)
- The Ghost: Memória local em JSON por agente (ghost_*.json)
- Mecanismos de diff, merge e sincronização assíncrona

NOTA TÉCNICA: A individualidade emerge porque cada agente pode:
1. Rejeitar memórias coletivas que conflitam com seus pesos locais
2. Filtrar experiências baseado em limiares pessoais
3. Reinterpretar conceitos com base em associações únicas
"""

import sqlite3
import json
import asyncio
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from datetime import datetime
import hashlib


class CollectiveMemory:
    """
    The Net - Memória Coletiva Centralizada
    
    Armazena fatos, conceitos e experiências validadas pela rede.
    Representa a "verdade" compartilhada entre todos os agentes.
    """
    
    def __init__(self, db_path: str = "data/collective_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Inicializa o banco de dados com as tabelas necessárias."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de fatos/experiências
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source_agent INTEGER,
                confidence REAL DEFAULT 1.0,
                validation_count INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                semantic_hash TEXT UNIQUE
            )
        ''')
        
        # Tabela de conceitos mapeados do ConceptNet
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept TEXT UNIQUE NOT NULL,
                category TEXT,
                relations TEXT,  -- JSON array de relações
                embedding_cache TEXT,  -- Hash do embedding
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de propagações de memória
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS propagations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_id INTEGER,
                source_agent INTEGER,
                receiving_agents TEXT,  -- JSON array de IDs
                accepted_by TEXT,  -- JSON array de agentes que aceitaram
                rejected_by TEXT,  -- JSON array de agentes que rejeitaram
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fact_id) REFERENCES facts(id)
            )
        ''')
        
        # Índices para performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_facts_hash ON facts(semantic_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_concepts_name ON concepts(concept)')
        
        conn.commit()
        conn.close()
    
    def add_fact(self, content: str, source_agent: int, 
                 confidence: float = 1.0) -> Optional[int]:
        """
        Adiciona um fato à memória coletiva.
        
        Args:
            content: Conteúdo do fato/experiência
            source_agent: ID do agente que originou o fato
            confidence: Nível de confiança (0-1)
            
        Returns:
            ID do fato inserido ou None se já existe
        """
        semantic_hash = hashlib.md5(content.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO facts (content, source_agent, confidence, semantic_hash)
                VALUES (?, ?, ?, ?)
            ''', (content, source_agent, confidence, semantic_hash))
            conn.commit()
            fact_id = cursor.lastrowid
            return fact_id
        except sqlite3.IntegrityError:
            # Fato já existe, incrementar validation_count
            cursor.execute('''
                UPDATE facts 
                SET validation_count = validation_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE semantic_hash = ?
            ''', (semantic_hash,))
            conn.commit()
            cursor.execute('SELECT id FROM facts WHERE semantic_hash = ?', (semantic_hash,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()
    
    def get_facts(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Obtém fatos da memória coletiva."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM facts 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        facts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return facts
    
    def add_concept(self, concept: str, category: str = None, 
                   relations: List[Dict] = None) -> bool:
        """Adiciona um conceito mapeado do ConceptNet."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO concepts (concept, category, relations)
                VALUES (?, ?, ?)
            ''', (concept, category, json.dumps(relations or [])))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_concepts(self, category: str = None) -> List[Dict]:
        """Obtém conceitos, opcionalmente filtrados por categoria."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if category:
            cursor.execute('SELECT * FROM concepts WHERE category = ?', (category,))
        else:
            cursor.execute('SELECT * FROM concepts')
        
        concepts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return concepts
    
    def record_propagation(self, fact_id: int, source_agent: int,
                          receiving_agents: List[int]) -> int:
        """Registra uma tentativa de propagação de memória."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO propagations (fact_id, source_agent, receiving_agents)
            VALUES (?, ?, ?)
        ''', (fact_id, source_agent, json.dumps(receiving_agents)))
        conn.commit()
        
        prop_id = cursor.lastrowid
        conn.close()
        return prop_id
    
    def update_propagation(self, prop_id: int, accepted: List[int], 
                          rejected: List[int]):
        """Atualiza resultado de propagação."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE propagations 
            SET accepted_by = ?, rejected_by = ?
            WHERE id = ?
        ''', (json.dumps(accepted), json.dumps(rejected), prop_id))
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas da memória coletiva."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM facts')
        facts_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM concepts')
        concepts_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM propagations')
        propagations_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "facts": facts_count,
            "concepts": concepts_count,
            "propagations": propagations_count
        }
    
    def reset(self, keep_concepts: bool = True):
        """
        Reseta a memória coletiva.
        
        Args:
            keep_concepts: Se True, preserva conceitos do ConceptNet
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM facts')
        cursor.execute('DELETE FROM propagations')
        
        if not keep_concepts:
            cursor.execute('DELETE FROM concepts')
        
        conn.commit()
        conn.close()


class GhostMemory:
    """
    The Ghost - Memória Local Individual
    
    Cada agente mantém seu próprio Ghost contendo:
    - Experiências únicas não compartilhadas
    - Pesos de associação conceitual
    - Vieses e preferências
    - "Traumas" (experiências com alto peso emocional)
    
    Otimizado para baixo consumo de RAM e rápida serialização JSON.
    """
    
    def __init__(self, agent_id: int, data_dir: str = "data"):
        self.agent_id = agent_id
        self.file_path = Path(data_dir) / f"ghost_{agent_id}.json"
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load_or_create()
    
    def _load_or_create(self) -> Dict:
        """Carrega Ghost existente ou cria novo."""
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                return json.load(f)
        else:
            # Ghost inicial vazio/idêntico para todos os agentes
            initial_data = {
                "agent_id": self.agent_id,
                "created_at": datetime.now().isoformat(),
                "experiences": [],  # Lista de experiências únicas
                "concept_weights": {},  # Pesos de associação conceitual
                "biases": {  # Vieses emergentes
                    "curiosity": 0.5,
                    "fear": 0.5,
                    "conformity": 0.5,
                    "pragmatism": 0.5,
                    "empathy": 0.5,
                    "creativity": 0.5
                },
                "trauma_indices": [],  # Índices de experiências traumáticas
                "sync_timestamp": None,
                "cycle_count": 0
            }
            self._save(initial_data)
            return initial_data
    
    def _save(self, data: Dict = None):
        """Salva o estado atual do Ghost."""
        if data:
            self.data = data
        
        # Adicionar timestamp de atualização
        self.data["updated_at"] = datetime.now().isoformat()
        
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_experience(self, content: str, emotional_weight: float = 0.5,
                      concepts: List[str] = None, shared: bool = False):
        """
        Adiciona uma experiência à memória local.
        
        Args:
            content: Conteúdo da experiência
            emotional_weight: Peso emocional (0-1)
            concepts: Conceitos associados
            shared: Se foi compartilhada com a rede
        """
        experience = {
            "id": len(self.data["experiences"]),
            "content": content,
            "emotional_weight": emotional_weight,
            "concepts": concepts or [],
            "shared": shared,
            "timestamp": datetime.now().isoformat(),
            "cycle": self.data.get("cycle_count", 0)
        }
        
        self.data["experiences"].append(experience)
        
        # Atualizar pesos conceituais
        if concepts:
            for concept in concepts:
                if concept not in self.data["concept_weights"]:
                    self.data["concept_weights"][concept] = 0.0
                
                # Reforçar associação baseado no peso emocional
                self.data["concept_weights"][concept] += emotional_weight * 0.1
        
        # Marcar como trauma se peso emocional muito alto
        if emotional_weight > 0.8:
            self.data["trauma_indices"].append(experience["id"])
        
        self._save()
    
    def update_biases(self, trait: str, delta: float):
        """
        Atualiza um viés emergente.
        
        Args:
            trait: Nome do traço (curiosity, fear, etc.)
            delta: Mudança (-1 a 1)
        """
        if trait in self.data["biases"]:
            self.data["biases"][trait] += delta
            # Limitar ao intervalo [0, 1]
            self.data["biases"][trait] = max(0.0, min(1.0, self.data["biases"][trait]))
            self._save()
    
    def get_bias(self, trait: str) -> float:
        """Obtém valor atual de um viés."""
        return self.data["biases"].get(trait, 0.5)
    
    def get_all_biases(self) -> Dict[str, float]:
        """Obtém todos os vieses normalizados."""
        return self.data["biases"].copy()
    
    def get_concept_weight(self, concept: str) -> float:
        """Obtém peso de associação para um conceito."""
        return self.data["concept_weights"].get(concept, 0.0)
    
    def filter_collective_memory(self, facts: List[Dict], 
                                 threshold: float = 0.3) -> List[Dict]:
        """
        Filtra memórias coletivas baseado nos pesos locais.
        
        NOTA TÉCNICA: Este é o mecanismo chave para individualidade.
        Cada agente interpreta e filtra a memória coletiva de forma
        única baseado em suas experiências prévias.
        
        Args:
            facts: Lista de fatos da memória coletiva
            threshold: Limiar de aceitação
            
        Returns:
            Lista de fatos aceitos pelo agente
        """
        accepted = []
        
        for fact in facts:
            # Calcular score de aceitação baseado em conceitos
            score = 0.5  # Score base neutro
            
            # Verificar conceitos no fato
            fact_content = fact.get("content", "")
            
            # Reforçar score se conceitos alinhados com pesos locais
            for concept, weight in self.data["concept_weights"].items():
                if concept.lower() in fact_content.lower():
                    score += weight * 0.2
            
            # Reduzir score se conflitante com traumas
            for trauma_idx in self.data["trauma_indices"]:
                if trauma_idx < len(self.data["experiences"]):
                    trauma = self.data["experiences"][trauma_idx]
                    trauma_content = trauma.get("content", "")
                    if any(word in fact_content for word in trauma_content.split()[:5]):
                        score -= 0.3
            
            if score >= threshold:
                fact["acceptance_score"] = score
                accepted.append(fact)
        
        return accepted
    
    def sync_with_net(self, collective_facts: List[Dict], 
                     propagation_threshold: float = 0.7):
        """
        Sincroniza com a memória coletiva.
        
        Args:
            collective_facts: Fatos da memória coletiva
            propagation_threshold: Limiar para aceitar propagações
        """
        # Filtrar fatos coletivos
        accepted_facts = self.filter_collective_memory(
            collective_facts, 
            threshold=propagation_threshold
        )
        
        # Atualizar timestamp de sincronização
        self.data["sync_timestamp"] = datetime.now().isoformat()
        self.data["synced_facts_count"] = len(accepted_facts)
        
        self._save()
        
        return accepted_facts
    
    def increment_cycle(self):
        """Incrementa contador de ciclos."""
        self.data["cycle_count"] = self.data.get("cycle_count", 0) + 1
        self._save()
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do Ghost."""
        return {
            "agent_id": self.agent_id,
            "experiences_count": len(self.data["experiences"]),
            "concepts_weighted": len(self.data["concept_weights"]),
            "trauma_count": len(self.data["trauma_indices"]),
            "biases": self.data["biases"],
            "cycle_count": self.data.get("cycle_count", 0)
        }
    
    def export(self) -> Dict:
        """Exporta todo o estado do Ghost."""
        return self.data.copy()
    
    def reset(self, preserve_biases: bool = False):
        """
        Reseta o Ghost.
        
        Args:
            preserve_biases: Se True, mantém vieses emergentes
        """
        biases_to_keep = self.data["biases"].copy() if preserve_biases else None
        
        self.data = {
            "agent_id": self.agent_id,
            "created_at": datetime.now().isoformat(),
            "experiences": [],
            "concept_weights": {},
            "biases": biases_to_keep or {
                "curiosity": 0.5,
                "fear": 0.5,
                "conformity": 0.5,
                "pragmatism": 0.5,
                "empathy": 0.5,
                "creativity": 0.5
            },
            "trauma_indices": [],
            "sync_timestamp": None,
            "cycle_count": 0
        }
        
        self._save()


def create_ghost(agent_id: int, data_dir: str = "data") -> GhostMemory:
    """Factory function para criar Ghost Memory."""
    return GhostMemory(agent_id, data_dir)


def create_collective_memory(db_path: str = "data/collective_memory.db") -> CollectiveMemory:
    """Factory function para criar Collective Memory."""
    return CollectiveMemory(db_path)
