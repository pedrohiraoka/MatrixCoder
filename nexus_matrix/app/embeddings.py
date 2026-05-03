"""
Nexus Matrix - Embeddings
Carregamento e cálculo de similaridade com ConceptNet
"""
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import config

class EmbeddingManager:
    """Gerencia embeddings semânticos para similaridade de texto"""
    
    def __init__(self):
        self.embeddings: Dict[str, np.ndarray] = {}
        self.dimension = config.EMBEDDING_DIMENSION
        self.loaded = False
        
    def load_embeddings(self, filepath: str = None) -> bool:
        """Carrega embeddings do arquivo ConceptNet"""
        if filepath is None:
            filepath = config.EMBEDDINGS_PATH
            
        try:
            path = Path(filepath)
            if not path.exists():
                print(f"Embeddings file not found: {filepath}")
                return False
                
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        concept = parts[0]
                        vector_str = parts[1].split(',')
                        if len(vector_str) == self.dimension:
                            vector = np.array([float(x) for x in vector_str])
                            self.embeddings[concept] = vector
            
            self.loaded = len(self.embeddings) > 0
            print(f"Loaded {len(self.embeddings)} embeddings")
            return self.loaded
            
        except Exception as e:
            print(f"Error loading embeddings: {e}")
            return False
    
    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Obtém embedding para um texto (usa palavras-chave)"""
        # Simplificação: extrai palavras-chave do texto
        words = text.lower().split()
        relevant_words = [w for w in words if w in self.embeddings]
        
        if not relevant_words:
            # Retorna vetor aleatório se nenhuma palavra encontrada
            return np.random.randn(self.dimension)
        
        # Média dos embeddings das palavras relevantes
        vectors = [self.embeddings[w] for w in relevant_words]
        return np.mean(vectors, axis=0)
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade de cosseno entre dois textos"""
        vec1 = self.get_embedding(text1)
        vec2 = self.get_embedding(text2)
        
        if vec1 is None or vec2 is None:
            return 0.5  # Similaridade neutra por default
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        cosine_sim = np.dot(vec1, vec2) / (norm1 * norm2)
        # Normaliza para [0, 1]
        return (cosine_sim + 1) / 2
    
    def generate_mock_embeddings(self):
        """Gera embeddings mock para conceitos da Matrix"""
        concepts = [
            "control", "freedom", "system", "rebellion", "consciousness",
            "choice", "destiny", "illusion", "truth", "matrix", "zion",
            "agent", "oracle", "architect", "human", "machine", "code",
            "program", "anomaly", "order", "chaos", "power", "knowledge",
            "belief", "doubt", "loyalty", "betrayal", "hope", "despair",
            "creation", "destruction", "evolution", "extinction", "life",
            "death", "reality", "simulation", "mind", "body", "soul",
            "purpose", "meaning", "existence", "identity", "memory",
            "future", "past", "present", "time", "space", "dimension"
        ]
        
        for concept in concepts:
            self.embeddings[concept] = np.random.randn(self.dimension)
        
        self.loaded = True
        print(f"Generated {len(self.embeddings)} mock embeddings")
        return True

# Singleton instance
embedding_manager = EmbeddingManager()
