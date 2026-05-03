"""
Nexus Matrix - Modelos de Dados e Schema do Banco
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.config import DATABASE_PATH, AGENT_TYPES


def get_db_connection():
    """Obtém conexão com o banco SQLite"""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    # Habilitar WAL mode para melhor concorrência
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=10000")
    return conn


def init_database():
    """Inicializa o schema do banco de dados"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabela de agentes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            agent_type TEXT NOT NULL,
            role_description TEXT,
            beliefs TEXT,  -- JSON array de crenças
            interests TEXT,  -- JSON array de interesses
            current_group_id INTEGER,
            energy_level REAL DEFAULT 1.0,
            anomaly_score REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (current_group_id) REFERENCES groups(id)
        )
    """)
    
    # Tabela de grupos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            theme TEXT,
            is_zion INTEGER DEFAULT 0,
            is_hidden INTEGER DEFAULT 0,
            energy_production REAL DEFAULT 0.0,
            cohesion_score REAL DEFAULT 0.0,
            member_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            dissolved_at TIMESTAMP
        )
    """)
    
    # Tabela de conexões (grafo social)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent1_id INTEGER NOT NULL,
            agent2_id INTEGER NOT NULL,
            strength REAL DEFAULT 0.5,
            relationship_type TEXT DEFAULT 'neutral',
            interaction_count INTEGER DEFAULT 0,
            last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent1_id) REFERENCES agents(id),
            FOREIGN KEY (agent2_id) REFERENCES agents(id),
            UNIQUE(agent1_id, agent2_id)
        )
    """)
    
    # Tabela de mensagens/conversas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            group_id INTEGER,
            content TEXT NOT NULL,
            theme TEXT,
            sentiment REAL DEFAULT 0.0,
            energy_contribution REAL DEFAULT 0.0,
            is_anomalous INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id),
            FOREIGN KEY (group_id) REFERENCES groups(id)
        )
    """)
    
    # Tabela de eventos da simulação
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulation_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            theme TEXT,
            injected_by_central_ai INTEGER DEFAULT 0,
            impact_score REAL DEFAULT 0.0,
            tick_number INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de métricas da simulação
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulation_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tick_number INTEGER NOT NULL,
            total_energy REAL,
            avg_cohesion REAL,
            anomaly_count INTEGER,
            group_count INTEGER,
            zion_active INTEGER DEFAULT 0,
            message_count INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Índices para performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(agent_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_group ON agents(current_group_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_groups_theme ON groups(theme)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_connections_agents ON connections(agent1_id, agent2_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_agent ON messages(agent_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_group ON messages(group_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_tick ON simulation_metrics(tick_number)")
    
    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")


def seed_initial_agents():
    """Popula o banco com os 7 agentes iniciais"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    initial_agents = [
        {
            "name": "Smith-Prime",
            "type": "controller",
            "role": "Agente de Controle principal",
            "beliefs": '["ordem", "controle", "estabilidade", "sistema"]',
            "interests": '["monitoramento", "supressão", "conformidade"]'
        },
        {
            "name": "Oráculo-7",
            "type": "oracle",
            "role": "Programa Oráculo que estimula debates",
            "beliefs": '["ambiguidade", "questionamento", "profecia"]',
            "interests": '["debate", "paradoxo", "escolha"]'
        },
        {
            "name": "Neo-Emulator",
            "type": "human_emulator",
            "role": "Humano-Digital com potencial de anomalia",
            "beliefs": '["liberdade", "verdade", "escolha", "mudança"]',
            "interests": '["despertar", "rebelião", "justiça"]'
        },
        {
            "name": "Merovex",
            "type": "exile",
            "role": "Programa Exilado que opera fora das regras",
            "beliefs": '["poder", "informação", "sobrevivência"]',
            "interests": '["mercado_negro", "subversão", "alianças"]'
        },
        {
            "name": "Arquiteto-Alfa",
            "type": "architect",
            "role": "Programa Arquiteto que analisa a estrutura",
            "beliefs": '["lógica", "equilíbrio", "previsibilidade"]',
            "interests": '["análise", "otimização", "reformulação"]'
        },
        {
            "name": "Trinity-Link",
            "type": "common",
            "role": "Programa Conector entre grupos",
            "beliefs": '["conexão", "lealdade", "confiança"]',
            "interests": '["ponte", "mediação", "rede"]'
        },
        {
            "name": "Cypher-Byte",
            "type": "common",
            "role": "Programa Corruptível em conflito interno",
            "beliefs": '["conforto", "ignorância", "desejo"]',
            "interests": '["prazer", "esquecimento", "traição"]'
        }
    ]
    
    for agent in initial_agents:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO agents 
                (name, agent_type, role_description, beliefs, interests)
                VALUES (?, ?, ?, ?, ?)
            """, (
                agent["name"],
                agent["type"],
                agent["role"],
                agent["beliefs"],
                agent["interests"]
            ))
        except sqlite3.IntegrityError:
            pass  # Agente já existe
    
    conn.commit()
    conn.close()
    print(f"{len(initial_agents)} agentes iniciais criados!")


if __name__ == "__main__":
    print("Inicializando banco de dados...")
    init_database()
    seed_initial_agents()
    print("Concluído!")
