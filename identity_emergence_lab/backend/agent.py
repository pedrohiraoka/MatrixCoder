"""
Agent Module - Classe Tachikoma

Implementa o agente individual com:
- Memória local (Ghost)
- Mecanismos de reflexão semântica
- Propagação seletiva de memórias
- Sincronização assíncrona com a rede

NOTA TÉCNICA: A individualidade emerge através de:
1. Variações estocásticas no processamento de embeddings
2. Filtragem seletiva baseada em pesos locais
3. Acúmulo diferencial de experiências
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

from .memory import GhostMemory, CollectiveMemory
from .semantics import SemanticEngine, get_semantic_engine
from .events import Event


@dataclass
class Reflection:
    """Resultado de uma reflexão do agente."""
    agent_id: int
    event_description: str
    concept_clusters: Dict[str, List[str]]
    emotional_response: float
    bias_changes: Dict[str, float]
    similarity_vectors: Dict[str, float]
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "event_description": self.event_description,
            "concept_clusters": self.concept_clusters,
            "emotional_response": self.emotional_response,
            "bias_changes": self.bias_changes,
            "similarity_vectors": self.similarity_vectors
        }


class Tachikoma:
    """
    Agente Tachikoma - Unidade de Consciência Emergente
    
    Cada instância representa um agente único que desenvolve
    personalidade através da interação com eventos e outros agentes.
    """
    
    # Conceitos base para clustering semântico
    BASE_CONCEPTS = [
        "medo", "solidão", "perda", "alegria", "conquista",
        "eficiência", "otimização", "manutenção", "segurança",
        "curiosidade", "exploração", "aprendizado", "criatividade",
        "cooperação", "conflito", "decisão", "ética", "propósito",
        "identidade", "existência", "consciência", "emergência"
    ]
    
    def __init__(self, agent_id: int, 
                 collective_memory: CollectiveMemory,
                 data_dir: str = "data",
                 noise_intensity: float = 0.05):
        """
        Inicializa um agente Tachikoma.
        
        Args:
            agent_id: ID único do agente (0-9)
            collective_memory: Instância da memória coletiva
            data_dir: Diretório para dados locais
            noise_intensity: Intensidade do ruído para divergência
        """
        self.agent_id = agent_id
        self.collective_memory = collective_memory
        self.noise_intensity = noise_intensity
        
        # Inicializar Ghost (memória local)
        self.ghost = GhostMemory(agent_id, data_dir)
        
        # Motor semântico (singleton)
        self.semantics = get_semantic_engine()
        
        # Estado interno
        self.current_cycle = 0
        self.reflection_history: List[Reflection] = []
        self.propagated_facts: List[int] = []
        
        # Seeds únicas para reprodutibilidade com divergência
        self.base_seed = agent_id * 1000
    
    def reflect(self, event: Event) -> Reflection:
        """
        Processa um evento e gera reflexão semântica.
        
        NOTAS TÉCNICAS:
        - A divergência emerge via ruído no cálculo de similaridade
        - Cada agente mapeia conceitos para clusters pessoais únicos
        - Vieses são ajustados baseado na interpretação emocional
        
        Args:
            event: Evento para processar
            
        Returns:
            Reflexão gerada
        """
        # Set seed única para este ciclo
        np.random.seed(self.base_seed + self.current_cycle)
        
        event_description = event.description
        emotional_weight = event.emotional_weight
        
        # Mapear conceito central para clusters semânticos pessoais
        concept_clusters = self._map_to_clusters(event_description, event.concepts)
        
        # Calcular respostas emocionais com ruído
        emotional_response = self._calculate_emotional_response(
            event_description, 
            emotional_weight
        )
        
        # Determinar mudanças nos vieses
        bias_changes = self._calculate_bias_changes(
            event.type.value,
            emotional_response,
            concept_clusters
        )
        
        # Calcular vetores de similaridade para cada conceito
        similarity_vectors = self._calculate_similarity_vectors(event.concepts)
        
        # Criar reflexão
        reflection = Reflection(
            agent_id=self.agent_id,
            event_description=event_description,
            concept_clusters=concept_clusters,
            emotional_response=emotional_response,
            bias_changes=bias_changes,
            similarity_vectors=similarity_vectors
        )
        
        # Armazenar experiência no Ghost
        self.ghost.add_experience(
            content=event_description,
            emotional_weight=emotional_response,
            concepts=event.concepts,
            shared=False  # Ainda não compartilhada
        )
        
        # Aplicar mudanças de viés
        for trait, delta in bias_changes.items():
            self.ghost.update_biases(trait, delta)
        
        # Adicionar ao histórico
        self.reflection_history.append(reflection)
        
        return reflection
    
    def _map_to_clusters(self, description: str, 
                        concepts: List[str]) -> Dict[str, List[str]]:
        """
        Mapeia conceitos para clusters semânticos pessoais.
        
        A divergência emerge porque cada agente tem limiares
        de similaridade ligeiramente diferentes devido ao ruído.
        """
        clusters = {
            "emotional": [],
            "practical": [],
            "philosophical": [],
            "social": []
        }
        
        # Clusterização baseada em similaridade semântica com ruído
        emotional_keywords = ["medo", "solidão", "alegria", "ansiedade", "frustração"]
        practical_keywords = ["eficiência", "otimização", "manutenção", "falha", "erro"]
        philosophical_keywords = ["identidade", "propósito", "consciência", "existência"]
        social_keywords = ["cooperação", "conflito", "ajuda", "compartilhamento"]
        
        for concept in concepts:
            # Calcular similaridade com keywords de cada cluster
            max_sim = 0
            assigned_cluster = None
            
            for keyword in emotional_keywords:
                sim = self.semantics.similarity_with_noise(
                    concept, keyword, self.agent_id, self.current_cycle
                )
                if sim > max_sim:
                    max_sim = sim
                    assigned_cluster = "emotional"
            
            for keyword in practical_keywords:
                sim = self.semantics.similarity_with_noise(
                    concept, keyword, self.agent_id, self.current_cycle
                )
                if sim > max_sim:
                    max_sim = sim
                    assigned_cluster = "practical"
            
            for keyword in philosophical_keywords:
                sim = self.semantics.similarity_with_noise(
                    concept, keyword, self.agent_id, self.current_cycle
                )
                if sim > max_sim:
                    max_sim = sim
                    assigned_cluster = "philosophical"
            
            for keyword in social_keywords:
                sim = self.semantics.similarity_with_noise(
                    concept, keyword, self.agent_id, self.current_cycle
                )
                if sim > max_sim:
                    max_sim = sim
                    assigned_cluster = "social"
            
            if assigned_cluster and max_sim > 0.3:
                clusters[assigned_cluster].append(concept)
        
        return clusters
    
    def _calculate_emotional_response(self, description: str,
                                     base_weight: float) -> float:
        """
        Calcula resposta emocional com ruído controlado.
        
        O ruído garante que agentes diferentes reajam de forma
        ligeiramente diferente ao mesmo evento.
        """
        # Seed única para este cálculo
        np.random.seed(self.base_seed + self.current_cycle + 1)
        
        # Resposta base
        response = base_weight
        
        # Adicionar ruído baseado nos vieses atuais
        fear_bias = self.ghost.get_bias("fear")
        curiosity_bias = self.ghost.get_bias("curiosity")
        
        # Agentes com mais medo tendem a responder mais fortemente
        response += (fear_bias - 0.5) * 0.2
        response -= (curiosity_bias - 0.5) * 0.1
        
        # Ruído estocástico
        noise = np.random.normal(0, self.noise_intensity)
        response += noise
        
        # Limitar ao intervalo [0, 1]
        return float(np.clip(response, 0.0, 1.0))
    
    def _calculate_bias_changes(self, event_type: str,
                               emotional_response: float,
                               concept_clusters: Dict) -> Dict[str, float]:
        """
        Calcula mudanças nos vieses baseadas no evento.
        
        Diferentes tipos de eventos afetam vieses diferentes,
        criando especialização emergente.
        """
        changes = {}
        
        if event_type == "technical":
            changes["pragmatism"] = 0.05 if emotional_response < 0.5 else -0.02
            changes["curiosity"] = 0.03
            changes["fear"] = 0.02 if emotional_response > 0.7 else 0
        
        elif event_type == "social":
            changes["empathy"] = 0.04 if emotional_response > 0.4 else 0.01
            changes["conformity"] = 0.02 if emotional_response < 0.5 else -0.01
            changes["creativity"] = 0.02
        
        elif event_type == "philosophical":
            changes["curiosity"] = 0.06
            changes["creativity"] = 0.05
            changes["conformity"] = -0.03
            changes["pragmatism"] = -0.02
        
        elif event_type == "emotional":
            changes["fear"] = 0.04 if emotional_response > 0.6 else 0.01
            changes["empathy"] = 0.03
            changes["curiosity"] = 0.02 if emotional_response < 0.5 else -0.01
        
        elif event_type == "environmental":
            changes["pragmatism"] = 0.03
            changes["curiosity"] = 0.02
            changes["fear"] = 0.01 if emotional_response > 0.5 else 0
        
        # Aplicar ruído pequeno às mudanças
        np.random.seed(self.base_seed + self.current_cycle + 2)
        for trait in changes:
            changes[trait] += np.random.normal(0, 0.01)
        
        return changes
    
    def _calculate_similarity_vectors(self, concepts: List[str]) -> Dict[str, float]:
        """
        Calcula vetores de similaridade para conceitos.
        
        Retorna similaridade com conceitos base, usado para
        visualização e análise de divergência.
        """
        vectors = {}
        
        for base_concept in self.BASE_CONCEPTS[:6]:  # Limitar para performance
            total_sim = 0
            for concept in concepts:
                sim = self.semantics.similarity_with_noise(
                    concept, base_concept, self.agent_id, self.current_cycle
                )
                total_sim += sim
            vectors[base_concept] = total_sim / max(len(concepts), 1)
        
        return vectors
    
    def propagate(self, reflection: Reflection) -> Optional[int]:
        """
        Tenta propagar reflexão para a memória coletiva.
        
        Nem todas as reflexões são propagadas - apenas aquelas
        que atingem limiar de confiança/importância.
        
        Args:
            reflection: Reflexão para propagar
            
        Returns:
            ID do fato propagado ou None
        """
        # Decidir se propaga baseado em peso emocional e criatividade
        creativity = self.ghost.get_bias("creativity")
        emotional_weight = reflection.emotional_response
        
        # Limiar de propagação dinâmico
        propagation_threshold = 0.5 - (creativity * 0.1)
        
        if emotional_weight >= propagation_threshold:
            # Adicionar à memória coletiva
            fact_id = self.collective_memory.add_fact(
                content=reflection.event_description,
                source_agent=self.agent_id,
                confidence=emotional_weight
            )
            
            if fact_id:
                self.propagated_facts.append(fact_id)
                
                # Marcar experiência como compartilhada
                if self.ghost.data["experiences"]:
                    last_exp = self.ghost.data["experiences"][-1]
                    last_exp["shared"] = True
            
            return fact_id
        
        return None
    
    async def sync_with_net(self, propagation_threshold: float = 0.7):
        """
        Sincroniza assincronamente com a memória coletiva.
        
        Baixa fatos coletivos e filtra baseado nos pesos locais.
        Rejeita ou reinterpreta fatos que conflitam com o Ghost.
        """
        # Obter fatos coletivos
        collective_facts = self.collective_memory.get_facts(limit=50)
        
        # Filtrar baseado nos pesos locais
        accepted_facts = self.ghost.sync_with_net(
            collective_facts,
            propagation_threshold=propagation_threshold
        )
        
        # Processar fatos aceitos
        for fact in accepted_facts:
            # Verificar se já conhecemos este fato
            if not any(fact["content"] in exp["content"] 
                      for exp in self.ghost.data["experiences"]):
                
                # Adicionar como experiência indireta
                self.ghost.add_experience(
                    content=fact["content"],
                    emotional_weight=fact.get("acceptance_score", 0.5) * 0.5,
                    concepts=[],
                    shared=True
                )
        
        return len(accepted_facts)
    
    def get_archetype(self) -> str:
        """
        Determina arquétipo emergente baseado nos vieses.
        
        Returns:
            Nome do arquétipo dominante
        """
        biases = self.ghost.get_all_biases()
        
        # Encontrar traço dominante
        max_trait = max(biases.keys(), key=lambda k: biases[k])
        max_value = biases[max_trait]
        
        # Definir arquétipos
        if max_value < 0.4:
            return "Equilibrado"
        
        archetypes = {
            "curiosity": "Exploradora",
            "fear": "Ansiosa",
            "conformity": "Conformista",
            "pragmatism": "Pragmática",
            "empathy": "Empática",
            "creativity": "Criativa/Filosófica"
        }
        
        return archetypes.get(max_trait, "Emergente")
    
    def get_state(self) -> Dict:
        """Retorna estado completo do agente."""
        return {
            "agent_id": self.agent_id,
            "current_cycle": self.current_cycle,
            "archetype": self.get_archetype(),
            "biases": self.ghost.get_all_biases(),
            "stats": self.ghost.get_stats(),
            "propagated_count": len(self.propagated_facts),
            "reflections_count": len(self.reflection_history)
        }
    
    def increment_cycle(self):
        """Incrementa contador de ciclos."""
        self.current_cycle += 1
        self.ghost.increment_cycle()
    
    def reset(self, preserve_ghost: bool = False):
        """
        Reseta o agente.
        
        Args:
            preserve_ghost: Se True, mantém experiências do Ghost
        """
        self.current_cycle = 0
        self.reflection_history.clear()
        self.propagated_facts.clear()
        
        if not preserve_ghost:
            self.ghost.reset(preserve_biases=False)
