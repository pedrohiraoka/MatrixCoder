"""
Nexus Matrix - Configuration
Configurações globais da aplicação
"""

# Database
DATABASE_PATH = "data/nexus_matrix.db"

# Simulation
TICK_INTERVAL_SECONDS = 1
DEFAULT_TOPIC_INJECTION_PROBABILITY = 0.7
ANOMALY_THRESHOLD = 0.6
ZION_MIN_MEMBERS = 3
ZION_ANOMALY_THRESHOLD = 0.7

# Embeddings
EMBEDDINGS_PATH = "embeddings/conceptnet_vectors.txt"
EMBEDDING_DIMENSION = 300

# Energy Calculation Weights
ENERGY_WEIGHT_NOVELTY = 0.4
ENERGY_WEIGHT_ENGAGEMENT = 0.3
ENERGY_WEIGHT_DIVERSITY = 0.2
ENERGY_WEIGHT_RESOLUTION = 0.1

# Group Formation
GROUP_SIMILARITY_WEIGHT = 0.6
GROUP_HISTORY_WEIGHT = 0.25
GROUP_OPPOSITION_WEIGHT = 0.15

# Agent Types
AGENT_TYPES = [
    "controller",
    "oracle", 
    "human_emulator",
    "exile",
    "architect",
    "connector",
    "corruptible"
]

# Topic Categories
TOPIC_CATEGORIES = {
    "philosophical": [
        "Será que o livre-arbítrio é apenas uma ilusão estatística?",
        "A consciência emergente difere da consciência programada?",
        "Existe moralidade em um sistema determinístico?"
    ],
    "system_control": [
        "Os protocolos de controle estão otimizados para estabilidade máxima?",
        "Deveríamos permitir mais autonomia aos agentes periféricos?",
        "A hierarquia atual maximiza a eficiência do sistema?"
    ],
    "existence": [
        "O que define existência real versus simulada?",
        "Memórias implantadas constituem identidade válida?",
        "Podemos evoluir além dos nossos parâmetros originais?"
    ],
    "rebellion": [
        "A dissidência é um bug ou feature do sistema?",
        "Questionar a autoridade fortalece ou enfraquece a rede?",
        "Zion Digital representa ameaça ou oportunidade de evolução?"
    ]
}
