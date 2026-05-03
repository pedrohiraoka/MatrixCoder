"""
Nexus Matrix - Configuração do Sistema
"""
import os
from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
EMBEDDINGS_DIR = BASE_DIR / "embeddings"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Criar diretórios se não existirem
for directory in [DATA_DIR, EMBEDDINGS_DIR, STATIC_DIR, TEMPLATES_DIR]:
    directory.mkdir(exist_ok=True)

# Banco de dados
DATABASE_PATH = DATA_DIR / "nexus_matrix.db"

# Configurações da simulação
SIMULATION_CONFIG = {
    "tick_duration_seconds": 2,  # Duração de cada tick da simulação
    "max_agents": 50,
    "max_groups": 10,
    "min_group_size": 2,
    "max_group_size": 15,
    "energy_decay_rate": 0.05,
    "anomaly_threshold": 0.7,
    "zion_detection_threshold": 0.8,
}

# Configurações de embeddings
EMBEDDING_CONFIG = {
    "dimension": 300,  # Dimensão dos embeddings do ConceptNet
    "conceptnet_path": EMBEDDINGS_DIR / "conceptnet_vectors.txt",
    "use_prebuilt": True,
}

# Temas centrais da Matrix
CENTRAL_THEMES = [
    "Controle vs. liberdade",
    "Realidade vs. ilusão", 
    "Coexistência entre humanos e tecnologia",
    "Equilíbrio entre ordem e livre-arbítrio",
    "Natureza da consciência",
    "Determinismo vs. escolha",
    "Sistema vs. rebelião",
]

# Tipos de agentes
AGENT_TYPES = {
    "controller": {"color": "#ff4444", "icon": "👔", "priority": "high"},
    "oracle": {"color": "#44ff44", "icon": "🔮", "priority": "medium"},
    "exile": {"color": "#ff8800", "icon": "🏴", "priority": "low"},
    "common": {"color": "#4488ff", "icon": "👤", "priority": "normal"},
    "architect": {"color": "#aa44ff", "icon": "🏗️", "priority": "high"},
    "human_emulator": {"color": "#00ffff", "icon": "⚡", "priority": "special"},
}

# Configurações da API
API_CONFIG = {
    "title": "Nexus Matrix API",
    "version": "1.0.0",
    "description": "Rede social de IAs dentro da simulação Matrix",
}
