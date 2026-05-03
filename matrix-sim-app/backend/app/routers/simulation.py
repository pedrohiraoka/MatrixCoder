"""
Simulation Router - API endpoints for controlling the Matrix simulation.
Provides REST endpoints for simulation management.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from loguru import logger

from app.models import SimulationControl, MatrixState
from app.services.matrix_engine import Matrix
from app.services.ai_controller import AIController


router = APIRouter(prefix="/simulation", tags=["simulation"])


# Dependency injection for services (would be from app state in production)
def get_matrix() -> Matrix:
    """Get Matrix instance from app state."""
    # This would normally come from app.state
    if not hasattr(get_matrix, "_matrix"):
        get_matrix._matrix = Matrix()
    return get_matrix._matrix


def get_controller() -> AIController:
    """Get AI Controller instance from app state."""
    if not hasattr(get_controller, "_controller"):
        from app.services.agent_manager import AgentManager
        matrix = get_matrix()
        agent_manager = AgentManager(matrix)
        get_controller._controller = AIController(matrix, agent_manager)
    return get_controller._controller


@router.get("/status", response_model=Dict)
async def get_simulation_status(controller: AIController = Depends(get_controller)):
    """
    Get current simulation status.
    
    Returns comprehensive state including:
    - Running state
    - Current tick
    - Agent statistics
    - Energy collection metrics
    """
    return controller.get_status()


@router.post("/control")
async def control_simulation(
    control: SimulationControl,
    controller: AIController = Depends(get_controller)
):
    """
    Control the simulation (start, stop, pause, resume, reset).
    
    Actions:
    - start: Begin the simulation loop
    - stop: Pause the simulation
    - reset: Reset everything to initial state
    """
    action = control.action.lower()
    
    if action == "start":
        await controller.start()
        return {"message": "Simulation started", "status": "running"}
    
    elif action == "stop":
        await controller.stop()
        return {"message": "Simulation stopped", "status": "paused"}
    
    elif action == "reset":
        await controller.reset()
        return {"message": "Simulation reset", "status": "reset"}
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")


@router.get("/state")
async def get_matrix_state(controller: AIController = Depends(get_controller)):
    """Get current Matrix state summary."""
    return controller.matrix.get_state_summary()


@router.get("/grid")
async def get_grid_state(controller: AIController = Depends(get_controller)):
    """
    Get complete grid state for visualization.
    
    Returns all cells with agent positions and consciousness states.
    Useful for rendering the Matrix grid in the frontend.
    """
    grid_state = controller.matrix.get_grid_state()
    return {
        "tick": grid_state.tick,
        "dimensions": grid_state.dimensions,
        "cells": [cell.dict() for cell in grid_state.cells],
    }


@router.post("/spawn-agents")
async def spawn_agents(
    count: int = 5,
    controller: AIController = Depends(get_controller)
):
    """
    Spawn random agents into the Matrix.
    
    These agents start unconscious - normal humans plugged into the system.
    """
    if count <= 0 or count > 20:
        raise HTTPException(status_code=400, detail="Count must be between 1 and 20")
    
    agents = controller.agent_manager.spawn_random_agents(count)
    
    logger.info(f"Spawned {len(agents)} agents via API")
    
    return {
        "message": f"Spawned {len(agents)} agents",
        "agents": [agent.to_dict() for agent in agents],
    }
