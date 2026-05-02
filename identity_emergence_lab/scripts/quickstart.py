#!/usr/bin/env python3
"""
Quickstart Script - Identity Emergence Lab

Script de inicialização rápida que:
1. Inicia o backend em background
2. Aguarda a API ficar disponível
3. Inicia o frontend Streamlit
"""

import subprocess
import sys
import time
import socket
import os

def check_port_available(port: int) -> bool:
    """Verifica se uma porta está disponível."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def wait_for_api(timeout: int = 30):
    """Aguarda a API ficar disponível."""
    print("⏳ Aguardando API ficar disponível...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = subprocess.run(
                ['curl', '-s', 'http://localhost:8000/health'],
                capture_output=True,
                timeout=2
            )
            if response.returncode == 0 and b'healthy' in response.stdout:
                print("✅ API disponível!")
                return True
        except:
            pass
        time.sleep(1)
    
    print("⚠️ Timeout ao aguardar API")
    return False

def main():
    print("🎭 Identity Emergence Lab - Quickstart")
    print("=" * 50)
    
    # Verificar portas
    if not check_port_available(8000):
        print("❌ Porta 8000 já está em uso")
        sys.exit(1)
    
    if not check_port_available(8501):
        print("❌ Porta 8501 já está em uso")
        sys.exit(1)
    
    print("✅ Portas disponíveis")
    
    # Mudar para diretório do projeto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    os.chdir(project_dir)
    
    # Iniciar backend
    print("\n🚀 Iniciando backend...")
    backend_process = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'backend.api:app', 
         '--host', '0.0.0.0', '--port', '8000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Aguardar API
    if not wait_for_api():
        print("❌ Falha ao iniciar backend")
        backend_process.terminate()
        sys.exit(1)
    
    # Iniciar frontend
    print("\n🎨 Iniciando frontend...")
    print("\n" + "=" * 50)
    print("✅ Sistema pronto!")
    print("📊 Frontend: http://localhost:8501")
    print("🔌 API: http://localhost:8000")
    print("=" * 50)
    print("\nPressione Ctrl+C para parar\n")
    
    try:
        # Iniciar Streamlit
        subprocess.run(
            ['streamlit', 'run', 'frontend/app.py', 
             '--server.port', '8501',
             '--server.address', '0.0.0.0']
        )
    except KeyboardInterrupt:
        print("\n\n⏹️ Parando sistema...")
    finally:
        backend_process.terminate()
        backend_process.wait()
        print("👋 Sistema encerrado")

if __name__ == "__main__":
    main()
