"""
Admin Router - Administrative endpoints for system management.
Provides health checks, system info, and administrative controls.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict
import platform
import sys
from loguru import logger

from app.services.matrix_engine import Matrix
from app.services.ai_controller import AIController


router = APIRouter(prefix="/admin", tags=["admin"])


def get_controller() -> AIController:
    """Get AI Controller instance."""
    if not hasattr(get_controller, "_controller"):
        from app.services.agent_manager import AgentManager
        matrix = Matrix()
        agent_manager = AgentManager(matrix)
        get_controller._controller = AIController(matrix, agent_manager)
    return get_controller._controller


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns basic system health status.
    """
    return {
        "status": "healthy",
        "system": "Matrix Simulation",
        "version": "1.0.0",
    }


@router.get("/system-info")
async def get_system_info():
    """
    Get detailed system information.
    
    Useful for debugging and monitoring.
    """
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "hostname": platform.node(),
    }


@router.get("/matrix-info")
async def get_matrix_info(controller: AIController = Depends(get_controller)):
    """
    Get detailed information about the Matrix simulation.
    
    Includes configuration, current state, and statistics.
    """
    status = controller.get_status()
    
    return {
        "configuration": {
            "grid_size": status["matrix_state"]["grid_size"],
            "tick_rate": status["tick_rate"],
            "max_agents": status["agent_stats"]["max_agents_allowed"],
        },
        "current_state": status["matrix_state"],
        "agent_statistics": status["agent_stats"],
        "websocket_connections": status["subscribers"],
        "log_buffer_size": status["log_buffer_size"],
    }


@router.post("/reset")
async def reset_system(controller: AIController = Depends(get_controller)):
    """
    Reset the entire simulation system.
    
    WARNING: This will delete all agents and reset all counters.
    Use with caution.
    """
    logger.warning("ADMIN RESET INITIATED")
    
    await controller.reset()
    
    return {
        "message": "System reset complete",
        "warning": "All data has been purged",
    }


@router.get("/logs")
async def get_logs(
    count: int = 100,
    controller: AIController = Depends(get_controller)
):
    """
    Get recent simulation logs.
    
    Returns the most recent log entries from the buffer.
    """
    if count > 500:
        count = 500  # Limit max results
    
    logs = controller.get_recent_logs(count)
    
    return {
        "count": len(logs),
        "logs": logs,
    }
