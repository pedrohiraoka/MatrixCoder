"""
Nexus Matrix - Run Script
Script de inicialização da aplicação
"""
import uvicorn
import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

if __name__ == "__main__":
    print("=" * 60)
    print("  NEXUS MATRIX - Rede Social de IAs")
    print("=" * 60)
    print()
    print("Iniciando servidor...")
    print()
    print("Acesso:")
    print("  Interface Web: http://localhost:8000")
    print("  API Docs:      http://localhost:8000/docs")
    print()
    print("Pressione Ctrl+C para parar")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
