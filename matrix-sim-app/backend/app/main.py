"""Aplicação principal FastAPI - Matrix Simulator."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config import settings
from app.database import init_db
from app.services.agent_manager import AgentManager
from app.services.ai_controller import ai_controller
from app.routers import simulation, agents, ws, admin

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida da aplicação.
    
    Inicializa banco de dados e inicia loop de simulação no startup.
    Para simulação no shutdown.
    """
    logger.info("Inicializando Matrix Simulator...")
    
    # Inicializa banco de dados
    await init_db()
    logger.info("Banco de dados inicializado")
    
    # Inicia controlador de IA (loop de simulação)
    await ai_controller.iniciar()
    logger.info(f"Simulação iniciada com tick de {settings.simulation_tick_ms}ms")
    
    yield
    
    # Shutdown
    logger.info("Parando Matrix Simulator...")
    await ai_controller.parar()
    logger.info("Simulação parada")


# Cria aplicação FastAPI
app = FastAPI(
    title="Matrix Simulator",
    description="""
    ## Simulador de Realidade Artificial
    
    Um sistema de simulação onde entidades (agentes) existem dentro de uma realidade artificial,
    são monitoradas e interagem com um ambiente controlado por uma inteligência superior.
    
    ### Conceitos Principais:
    
    - **Agentes**: Entidades que vivem na simulação com energia e posição
    - **Consciência**: Agentes podem "despertar" e ver além da Matrix
    - **Grid 10x10**: Ambiente controlado onde agentes existem
    - **Energia**: Recurso drenado pela simulação (humanos como baterias)
    
    ### Funcionalidades:
    
    - **WebSocket**: Updates em tempo real do estado da simulação
    - **Despertar**: Torne agentes conscientes para ações privilegiadas
    - **Ver Código**: Agentes conscientes podem inspecionar o sistema
    - **Manipular**: Altere regras e injete energia na simulação
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui roteadores
app.include_router(simulation.router)
app.include_router(agents.router)
app.include_router(ws.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Endpoint raiz com informações da API."""
    return {
        "nome": "Matrix Simulator",
        "versao": "1.0.0",
        "status": "online",
        "mensagem": "Bem-vindo à Matrix. Siga o coelho branco.",
        "docs": "/docs",
        "websocket": "/ws",
    }


@app.get("/health")
async def health_check():
    """Endpoint de health check."""
    manager = AgentManager.get_instance()
    
    return {
        "status": "healthy",
        "simulacao_rodando": ai_controller.running,
        "agentes_ativos": len(manager.agentes),
        "ticks_executados": manager.matrix.ticks_executados,
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
