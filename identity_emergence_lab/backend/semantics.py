"""
Semantics Module - Processamento Semântico e Embeddings

Responsável por:
- Carregamento de modelo de embeddings (sentence-transformers)
- Cálculo de similaridade cosseno com injeção de ruído controlado
- Validação conceitual via ConceptNet
- Cache LRU para otimização de performance

NOTA TÉCNICA: A divergência emergente é garantida pela injeção de ruído
no cálculo de similaridade. Cada agente aplica noise baseado em seu ID
e ciclo, criando variações mínimas mas acumulativas na interpretação.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from functools import lru_cache
import hashlib
import json
from pathlib import Path

# Configurações de emergência
NOISE_INTENSITY = 0.05  # Intensidade do ruído (0.0-1.0) - ajuste para calibrar divergência
CACHE_SIZE = 1000  # Tamanho do cache LRU
SIMILARITY_THRESHOLD = 0.6  # Limiar mínimo para considerar conceitos relacionados


class SemanticEngine:
    """
    Motor semântico para processamento de embeddings e similaridade.
    
    Carrega o modelo uma vez e reutiliza para todas as consultas,
    garantindo performance e consistência.
    """
    
    _instance: Optional['SemanticEngine'] = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._load_model()
        self._cache: Dict[str, np.ndarray] = {}
    
    def _load_model(self):
        """Carrega o modelo de embeddings uma única vez."""
        try:
            from sentence_transformers import SentenceTransformer
            print("🧠 Carregando modelo de embeddings...")
            self._model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Modelo carregado com sucesso!")
        except Exception as e:
            print(f"⚠️ Erro ao carregar modelo: {e}")
            print("Usando fallback com embeddings aleatórios para demonstração")
            self._model = None
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Obtém embedding para um texto, usando cache quando disponível.
        
        Args:
            text: Texto para codificar
            
        Returns:
            Vetor de embeddings normalizado
        """
        # Cache key baseada no hash do texto
        cache_key = hashlib.md5(text.encode()).hexdigest()
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        if self._model is not None:
            embedding = self._model.encode(text, convert_to_numpy=True)
        else:
            # Fallback: embedding aleatório determinístico baseado no texto
            np.random.seed(int(cache_key[:8], 16))
            embedding = np.random.randn(384)
        
        # Normalizar vetor
        embedding = embedding / np.linalg.norm(embedding)
        
        # Cache management
        if len(self._cache) >= CACHE_SIZE:
            # Remove 10% mais antigo
            keys_to_remove = list(self._cache.keys())[:CACHE_SIZE // 10]
            for key in keys_to_remove:
                del self._cache[key]
        
        self._cache[cache_key] = embedding
        return embedding
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calcula similaridade cosseno entre dois vetores.
        
        Args:
            vec1: Primeiro vetor
            vec2: Segundo vetor
            
        Returns:
            Similaridade cosseno (-1 a 1)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def similarity_with_noise(self, text1: str, text2: str, 
                              agent_id: int, cycle: int) -> float:
        """
        Calcula similaridade com injeção de ruído controlado para emergência.
        
        NOTAS TÉCNICAS:
        - O ruído é determinístico para o mesmo (agent_id, cycle)
        - Isso garante reprodutibilidade enquanto permite divergência
        - A intensidade é calibrada por NOISE_INTENSITY
        
        Args:
            text1: Primeiro texto
            text2: Segundo texto
            agent_id: ID do agente (para seed única)
            cycle: Ciclo atual (para variação temporal)
            
        Returns:
            Similaridade com ruído aplicado
        """
        # Obter embeddings
        vec1 = self.get_embedding(text1)
        vec2 = self.get_embedding(text2)
        
        # Similaridade base
        base_similarity = self.cosine_similarity(vec1, vec2)
        
        # Injeção de ruído controlado
        # Seed única por agente + ciclo garante divergência acumulativa
        seed = agent_id * 10000 + cycle
        np.random.seed(seed)
        noise = np.random.normal(0, NOISE_INTENSITY)
        
        # Aplicar ruído e limitar ao intervalo válido
        noisy_similarity = base_similarity + noise
        noisy_similarity = np.clip(noisy_similarity, -1.0, 1.0)
        
        return float(noisy_similarity)
    
    def find_similar_concepts(self, concept: str, 
                             concept_list: List[str],
                             agent_id: int, 
                             cycle: int,
                             top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Encontra conceitos similares em uma lista, ranqueados por similaridade.
        
        Args:
            concept: Conceito central
            concept_list: Lista de conceitos para comparar
            agent_id: ID do agente
            cycle: Ciclo atual
            top_k: Número de resultados para retornar
            
        Returns:
            Lista de tuplas (conceito, similaridade)
        """
        similarities = []
        
        for other_concept in concept_list:
            sim = self.similarity_with_noise(concept, other_concept, agent_id, cycle)
            if sim >= SIMILARITY_THRESHOLD:
                similarities.append((other_concept, sim))
        
        # Ordenar por similaridade decrescente
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def validate_conceptnet_relation(self, concept1: str, concept2: str, 
                                    relation: str) -> bool:
        """
        Valida se uma relação ConceptNet faz sentido semanticamente.
        
        NOTA: Implementação simplificada. Em produção, integraria com
        API do ConceptNet ou base local.
        
        Args:
            concept1: Primeiro conceito
            concept2: Segundo conceito
            relation: Tipo de relação (ex: "RelatedTo", "IsA", "Causes")
            
        Returns:
            True se a relação é semanticamente válida
        """
        # Validação básica por similaridade
        similarity = self.similarity_with_noise(concept1, concept2, 0, 0)
        
        # Relações diferentes têm limiares diferentes
        thresholds = {
            "RelatedTo": 0.3,
            "IsA": 0.5,
            "Causes": 0.4,
            "AtLocation": 0.3,
            "UsedFor": 0.4,
            "Desires": 0.5,
            "CapableOf": 0.5,
        }
        
        threshold = thresholds.get(relation, 0.4)
        return similarity >= threshold
    
    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """
        Codifica múltiplos textos em batch para performance.
        
        Args:
            texts: Lista de textos
            
        Returns:
            Matriz de embeddings [n_texts, embedding_dim]
        """
        if self._model is not None:
            embeddings = self._model.encode(texts, convert_to_numpy=True)
            # Normalizar cada vetor
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1  # Evitar divisão por zero
            embeddings = embeddings / norms
            return embeddings
        else:
            # Fallback
            result = []
            for text in texts:
                result.append(self.get_embedding(text))
            return np.array(result)
    
    def clear_cache(self):
        """Limpa o cache de embeddings."""
        self._cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """Retorna estatísticas do cache."""
        return {
            "size": len(self._cache),
            "max_size": CACHE_SIZE,
            "utilization": len(self._cache) / CACHE_SIZE
        }


# Singleton global
_semantic_engine: Optional[SemanticEngine] = None

def get_semantic_engine() -> SemanticEngine:
    """Obtém instância singleton do motor semântico."""
    global _semantic_engine
    if _semantic_engine is None:
        _semantic_engine = SemanticEngine()
    return _semantic_engine


def initialize_semantics():
    """Inicializa o sistema semântico (chamar no startup)."""
    global _semantic_engine
    _semantic_engine = SemanticEngine()
    return _semantic_engine
