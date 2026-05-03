"""
Nexus Matrix - Gerenciador de Embeddings com ConceptNet
Usa embeddings prebuilt do ConceptNet para similaridade semântica
"""
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from app.config import EMBEDDING_CONFIG, EMBEDDINGS_DIR


class ConceptNetEmbeddings:
    """Gerenciador de embeddings baseado em ConceptNet"""
    
    def __init__(self):
        self.dimension = EMBEDDING_CONFIG["dimension"]
        self.embeddings_path = EMBEDDING_CONFIG["conceptnet_path"]
        self.vocabulary: Dict[str, int] = {}
        self.embeddings_matrix: Optional[np.ndarray] = None
        self.is_loaded = False
        
    def download_prebuilt_embeddings(self) -> bool:
        """
        Baixa embeddings prebuilt do ConceptNet ou usa alternativas
        Fontes:
        - ConceptNet Numberbatch (https://github.com/commonsense/conceptnet-numberbatch)
        - OpenKE demo files
        """
        try:
            # Tentar baixar ConceptNet Numberbatch (versão reduzida para economia de recursos)
            urls = [
                "https://conceptnet.s3.amazonaws.com/downloads/2017/numberbatch/numberbatch-17.06.300.txt.gz",
                # Alternativa: embeddings menores do OpenKE
                "https://raw.githubusercontent.com/thunlp/OpenKE/master/data/fb15k/entity2vec.txt",
            ]
            
            for url in urls:
                try:
                    print(f"Tentando baixar embeddings de: {url}")
                    response = requests.get(url, stream=True, timeout=30)
                    if response.status_code == 200:
                        # Salvar arquivo
                        output_path = self.embeddings_path
                        if url.endswith('.gz'):
                            import gzip
                            with gzip.open(output_path.with_suffix('.txt.gz'), 'wb') as f:
                                f.write(response.content)
                            # Descompactar
                            with gzip.open(output_path.with_suffix('.txt.gz'), 'rt', encoding='utf-8') as f_in:
                                with open(output_path, 'w', encoding='utf-8') as f_out:
                                    f_out.write(f_in.read())
                        else:
                            with open(output_path, 'wb') as f:
                                f.write(response.content)
                        
                        print(f"Embeddings baixados com sucesso: {output_path}")
                        return True
                except Exception as e:
                    print(f"Falha ao baixar de {url}: {e}")
                    continue
            
            return False
        except Exception as e:
            print(f"Erro ao baixar embeddings: {e}")
            return False
    
    def generate_synthetic_embeddings(self) -> bool:
        """
        Gera embeddings sintéticos baseados em palavras-chave da Matrix
        Usado como fallback quando não há embeddings prebuilt disponíveis
        """
        print("Gerando embeddings sintéticos como fallback...")
        
        # Palavras-chave relacionadas aos temas da Matrix
        matrix_concepts = [
            "control", "freedom", "reality", "illusion", "human", "technology",
            "order", "choice", "consciousness", "determinism", "system", "rebellion",
            "matrix", "simulation", "agent", "oracle", "exile", "architect",
            "zion", "neo", "smith", "trinity", "morpheus", "cypher",
            "truth", "lie", "awakening", "sleep", "red_pill", "blue_pill",
            "code", "program", "digital", "virtual", "physical", "mind",
            "body", "soul", "machine", "organic", "connection", "isolation",
            "power", "resistance", "conformity", "individuality", "collective",
            "anomaly", "normal", "exception", "rule", "chaos", "harmony"
        ]
        
        # Criar embeddings sintéticos usando hash determinístico
        np.random.seed(42)  # Seed fixa para reprodutibilidade
        self.vocabulary = {}
        embeddings_list = []
        
        for idx, concept in enumerate(matrix_concepts):
            self.vocabulary[concept] = idx
            # Gerar vetor aleatório mas consistente para cada conceito
            np.random.seed(hash(concept) % (2**32))
            vector = np.random.randn(self.dimension).astype(np.float32)
            vector = vector / np.linalg.norm(vector)  # Normalizar
            embeddings_list.append(vector)
        
        self.embeddings_matrix = np.array(embeddings_list, dtype=np.float32)
        self.is_loaded = True
        
        # Salvar embeddings sintéticos
        with open(self.embeddings_path, 'w', encoding='utf-8') as f:
            f.write(f"{len(matrix_concepts)} {self.dimension}\n")
            for concept, idx in self.vocabulary.items():
                vector_str = ' '.join(map(str, self.embeddings_matrix[idx]))
                f.write(f"{concept} {vector_str}\n")
        
        print(f"Embeddings sintéticos gerados: {len(matrix_concepts)} conceitos, {self.dimension} dimensões")
        return True
    
    def load_embeddings(self) -> bool:
        """Carrega embeddings do arquivo"""
        if not self.embeddings_path.exists():
            print("Arquivo de embeddings não encontrado. Tentando baixar...")
            if not self.download_prebuilt_embeddings():
                print("Falha ao baixar. Gerando embeddings sintéticos...")
                return self.generate_synthetic_embeddings()
        
        try:
            print(f"Carregando embeddings de {self.embeddings_path}...")
            self.vocabulary = {}
            embeddings_list = []
            
            with open(self.embeddings_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                # Verificar se a primeira linha contém dimensões
                parts = first_line.split()
                if len(parts) == 2 and parts[0].isdigit():
                    num_vectors, dim = map(int, parts)
                    print(f"Cabeçalho detectado: {num_vectors} vetores, {dim} dimensões")
                else:
                    # Sem cabeçalho, voltar para o início
                    f.seek(0)
                
                line_num = 0
                for line in f:
                    line_num += 1
                    if line_num % 10000 == 0:
                        print(f"Processando linha {line_num}...")
                    
                    parts = line.strip().split()
                    if len(parts) < self.dimension + 1:
                        continue
                    
                    # O primeiro token é o conceito, o resto é o vetor
                    concept = parts[0]
                    vector = np.array([float(x) for x in parts[1:self.dimension+1]], dtype=np.float32)
                    
                    if len(vector) == self.dimension:
                        self.vocabulary[concept] = len(embeddings_list)
                        embeddings_list.append(vector)
                    
                    # Limitar número de embeddings para economizar memória
                    if len(embeddings_list) >= 100000:
                        print("Limite de embeddings atingido (100k)")
                        break
            
            if embeddings_list:
                self.embeddings_matrix = np.array(embeddings_list, dtype=np.float32)
                self.is_loaded = True
                print(f"Embeddings carregados: {len(self.vocabulary)} conceitos, {self.dimension} dimensões")
                return True
            else:
                print("Nenhum embedding válido encontrado")
                return self.generate_synthetic_embeddings()
                
        except Exception as e:
            print(f"Erro ao carregar embeddings: {e}")
            return self.generate_synthetic_embeddings()
    
    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Obtém embedding para um texto (palavra ou frase simples)"""
        if not self.is_loaded:
            return None
        
        # Normalizar texto
        text = text.lower().strip().replace(" ", "_")
        
        # Tentar encontrar no vocabulário
        if text in self.vocabulary:
            idx = self.vocabulary[text]
            return self.embeddings_matrix[idx].copy()
        
        # Tentar variações
        variations = [
            text.replace("_", ""),
            text.replace("-", "_"),
        ]
        for var in variations:
            if var in self.vocabulary:
                return self.embeddings_matrix[self.vocabulary[var]].copy()
        
        # Fallback: criar embedding médio de palavras conhecidas
        words = text.split("_")
        known_embeddings = []
        for word in words:
            if word in self.vocabulary:
                known_embeddings.append(self.embeddings_matrix[self.vocabulary[word]])
        
        if known_embeddings:
            return np.mean(known_embeddings, axis=0)
        
        # Último fallback: vetor aleatório normalizado
        np.random.seed(hash(text) % (2**32))
        vector = np.random.randn(self.dimension).astype(np.float32)
        return vector / np.linalg.norm(vector)
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Computa similaridade cosseno entre dois textos"""
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        
        if emb1 is None or emb2 is None:
            return 0.0
        
        # Similaridade cosseno
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    
    def find_similar_concepts(self, text: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Encontra conceitos similares no vocabulário"""
        if not self.is_loaded:
            return []
        
        query_emb = self.get_embedding(text)
        if query_emb is None:
            return []
        
        similarities = []
        for concept, idx in self.vocabulary.items():
            sim = np.dot(query_emb, self.embeddings_matrix[idx]) / (
                np.linalg.norm(query_emb) * np.linalg.norm(self.embeddings_matrix[idx])
            )
            similarities.append((concept, float(sim)))
        
        # Ordenar por similaridade
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]


# Singleton instance
embeddings_manager = ConceptNetEmbeddings()


def initialize_embeddings() -> bool:
    """Inicializa o gerenciador de embeddings"""
    return embeddings_manager.load_embeddings()


if __name__ == "__main__":
    # Teste rápido
    print("Testando ConceptNet Embeddings...")
    if initialize_embeddings():
        print("\nTeste de similaridade:")
        test_pairs = [
            ("control", "freedom"),
            ("reality", "illusion"),
            ("human", "technology"),
            ("matrix", "simulation"),
        ]
        
        for word1, word2 in test_pairs:
            sim = embeddings_manager.compute_similarity(word1, word2)
            print(f"  {word1} <-> {word2}: {sim:.4f}")
        
        print("\nConceitos similares a 'rebellion':")
        similar = embeddings_manager.find_similar_concepts("rebellion", top_k=5)
        for concept, score in similar:
            print(f"  {concept}: {score:.4f}")
    else:
        print("Falha ao inicializar embeddings")
