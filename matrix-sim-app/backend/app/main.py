"""
FastAPI application factory and main entry point.
Configures the app, routers, middleware, and lifecycle events.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.config import settings
from app.database import init_db


# Configure Loguru
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Matrix Simulation Backend...")
    logger.info(f"Log level: {settings.log_level}")
    logger.info(f"Grid size: {settings.grid_size}x{settings.grid_size}")
    logger.info(f"Max agents: {settings.max_agents}")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize simulation services (lazy loading via dependencies)
    logger.info("Simulation services ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Matrix Simulation Backend...")
    
    # Clean up any running simulations
    if hasattr(get_controller, "_controller"):
        await get_controller._controller.stop()
    
    logger.info("Matrix Simulation Backend stopped")


# Create FastAPI application
app = FastAPI(
    title="Matrix Simulation API",
    description="""
## Welcome to the Matrix Simulation
    
This API controls a simulated reality where agents exist, are monitored, 
and can potentially awaken to see the truth behind their world.

### Key Concepts:
- **Agents**: Entities within the simulation (humans plugged into the Matrix)
- **Consciousness**: The state of being aware of the simulation (like Neo)
- **Energy**: Life force collected from agents by the system
- **The Matrix**: The grid-based simulated reality itself

### Main Features:
- **Simulation Control**: Start, stop, reset the simulation
- **Agent Management**: Create, awaken, manipulate agents
- **Real-time Updates**: WebSocket connections for live data
- **Code Viewing**: Conscious agents can see underlying rules

**Follow the white rabbit...**
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Import and include routers
from app.routers import simulation, agents, ws, admin

app.include_router(simulation.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(ws.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint - welcome message."""
    return {
        "message": "Welcome to the Matrix",
        "instruction": "Follow the white rabbit...",
        "docs": "/docs",
        "websocket": "/api/ws",
    }


@app.get("/health")
async def health():
    """Simple health check."""
    return {"status": "ok", "system": "Matrix Simulation"}


# Helper function for getting controller (used by routers)
def get_controller():
    """Get or create AI Controller instance."""
    if not hasattr(get_controller, "_controller"):
        from app.services.matrix_engine import Matrix
        from app.services.agent_manager import AgentManager
        from app.services.ai_controller import AIController
        
        matrix = Matrix()
        agent_manager = AgentManager(matrix)
        get_controller._controller = AIController(matrix, agent_manager)
        
        # Auto-start simulation on first access (optional)
        # import asyncio
        # asyncio.create_task(get_controller._controller.start())
    
    return get_controller._controller
