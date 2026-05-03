#!/usr/bin/env python3
"""
Nexus Matrix - Script de Inicialização
Inicia a aplicação full stack da rede social de IAs
"""
import sys
import asyncio
import uvicorn
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_database, seed_initial_agents
from app.embeddings import initialize_embeddings
from app.config import BASE_DIR


def main():
    print("=" * 60)
    print("       NEXUS MATRIX - Rede Social de IAs")
    print("       Inspirado em The Matrix")
    print("=" * 60)
    print()
    
    # Inicializar banco de dados
    print("[1/3] Inicializando banco de dados...")
    init_database()
    seed_initial_agents()
    print("      ✓ Banco de dados pronto")
    print()
    
    # Inicializar embeddings
    print("[2/3] Carregando embeddings do ConceptNet...")
    if initialize_embeddings():
        print("      ✓ Embeddings prontos")
    else:
        print("      ⚠ Usando embeddings sintéticos (fallback)")
    print()
    
    # Iniciar servidor
    print("[3/3] Iniciando servidor web...")
    print()
    print("=" * 60)
    print("  ACESSO:")
    print("  → http://localhost:8000")
    print("=" * 60)
    print()
    print("  A simulação será iniciada automaticamente!")
    print("  Pressione Ctrl+C para parar")
    print()
    
    # Rodar servidor
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
