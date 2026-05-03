"""
Nexus Matrix - Database
Conexão SQLite e inicialização do banco de dados
"""
import sqlite3
import os
from pathlib import Path

DATABASE_PATH = "data/nexus_matrix.db"

def get_db_connection():
    """Obtém conexão com o banco de dados"""
    db_path = Path(DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    
    # Enable WAL mode for better concurrency
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=10000")
    
    return conn

def init_database():
    """Inicializa o banco de dados com todas as tabelas"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Load sqlite-vss extension if available
        try:
            conn.enable_load_extension(True)
            # Try to load sqlite-vss (may not be available in all environments)
            # This is optional - the app will work without vector search
        except:
            pass
        
        # Tabela de Agentes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL,
                role TEXT NOT NULL,
                anomaly_score REAL DEFAULT 0.0,
                energy_level REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de Grupos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                cohesion REAL DEFAULT 0.5,
                energy REAL DEFAULT 0.5,
                is_hidden BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de Membros dos Grupos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_members (
                group_id INTEGER NOT NULL,
                agent_id INTEGER NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (group_id, agent_id),
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
                FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de Mensagens
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                group_id INTEGER,
                content TEXT NOT NULL,
                topic TEXT,
                energy_contribution REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE SET NULL
            )
        """)
        
        # Tabela de Eventos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                tick_number INTEGER DEFAULT 0,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de Métricas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tick_number INTEGER UNIQUE NOT NULL,
                social_energy REAL DEFAULT 0.0,
                avg_cohesion REAL DEFAULT 0.0,
                anomaly_count INTEGER DEFAULT 0,
                group_count INTEGER DEFAULT 0,
                message_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de Conexões do Grafo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS graph_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_agent_id INTEGER NOT NULL,
                target_agent_id INTEGER NOT NULL,
                strength REAL DEFAULT 0.5,
                connection_type TEXT DEFAULT 'semantic',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_agent_id) REFERENCES agents(id) ON DELETE CASCADE,
                FOREIGN KEY (target_agent_id) REFERENCES agents(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("Database initialized successfully!")
