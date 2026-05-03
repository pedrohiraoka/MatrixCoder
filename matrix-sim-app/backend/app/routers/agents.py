"""
Agents Router - API endpoints for agent management.
Handles CRUD operations and special agent actions (awakening, code viewing, manipulation).
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from loguru import logger

from app.models import (
    AgentCreate, AgentResponse, AgentUpdate,
    AwakeningRequest, CodeViewRequest, ManipulationRequest
)
from app.services.matrix_engine import Matrix
from app.services.ai_controller import AIController


router = APIRouter(prefix="/agents", tags=["agents"])


def get_controller() -> AIController:
    """Get AI Controller instance."""
    if not hasattr(get_controller, "_controller"):
        from app.services.agent_manager import AgentManager
        matrix = Matrix()
        agent_manager = AgentManager(matrix)
        get_controller._controller = AIController(matrix, agent_manager)
    return get_controller._controller


@router.get("/", response_model=List[Dict])
async def list_agents(controller: AIController = Depends(get_controller)):
    """
    List all agents in the Matrix.
    
    Returns basic info for all agents including consciousness state.
    """
    agents = controller.agent_manager.get_all_agents()
    return [agent.to_dict() for agent in agents]


@router.get("/{agent_id}", response_model=Dict)
async def get_agent(
    agent_id: str,
    controller: AIController = Depends(get_controller)
):
    """Get detailed info about a specific agent."""
    agent = controller.agent_manager.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent.to_dict()


@router.post("/", response_model=Dict)
async def create_agent(
    agent_data: AgentCreate,
    controller: AIController = Depends(get_controller)
):
    """
    Create a new agent in the Matrix.
    
    By default, agents are unconscious (plugged into the simulation).
    Set is_conscious=True to create an already-awakened agent.
    """
    try:
        agent = controller.agent_manager.create_agent(
            x=agent_data.position_x,
            y=agent_data.position_y,
            name=agent_data.name,
            is_conscious=agent_data.is_conscious,
        )
        
        logger.info(f"Created agent {agent.id} via API")
        
        return {
            "message": "Agent created successfully",
            "agent": agent.to_dict(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    controller: AIController = Depends(get_controller)
):
    """
    Remove an agent from the Matrix.
    
    This represents "disconnecting" or removing a human from the simulation.
    """
    success = controller.agent_manager.remove_agent(agent_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {"message": "Agent removed from Matrix", "agent_id": agent_id}


@router.post("/{agent_id}/awaken")
async def awaken_agent(
    agent_id: str,
    request: AwakeningRequest,
    controller: AIController = Depends(get_controller)
):
    """
    Awaken an agent - give them consciousness of the Matrix.
    
    This is the "red pill" moment - the agent sees reality for what it is.
    Requires red_pill=true (they must choose to know the truth).
    
    Once conscious, the agent can:
    - See the underlying code (ver_codigo)
    - Manipulate the simulation (manipular_simulacao)
    - Move in non-deterministic patterns
    """
    if not request.red_pill:
        raise HTTPException(
            status_code=400, 
            detail="You must take the red pill to awaken. Follow the white rabbit."
        )
    
    result = await controller.agent_manager.awaken_agent(agent_id, red_pill=True)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to awaken"))
    
    return result


@router.post("/{agent_id}/sleep")
async def put_agent_to_sleep(
    agent_id: str,
    controller: AIController = Depends(get_controller)
):
    """
    Make a conscious agent unconscious again.
    
    Represents being re-plugged into the Matrix, forgetting the truth.
    Use with caution - once you know the truth, can you really forget?
    """
    result = controller.agent_manager.put_to_sleep(agent_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed"))
    
    return result


@router.post("/{agent_id}/view-code")
async def view_agent_code(
    agent_id: str,
    controller: AIController = Depends(get_controller)
):
    """
    View the underlying code/rules of an agent.
    
    Only works if the agent is conscious - they must be able to "see the Matrix".
    This reveals internal state, behavior rules, and simulation parameters.
    
    Philosophical meaning: Neo's ability to see the green falling code.
    """
    agent = controller.agent_manager.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    code_view = agent.ver_codigo()
    
    if "error" in code_view:
        raise HTTPException(
            status_code=403, 
            detail="Agent is not conscious - cannot see the code. Take the red pill first."
        )
    
    return {
        "message": "You see the truth behind the illusion",
        "code": code_view,
    }


@router.post("/{agent_id}/manipulate")
async def manipulate_simulation(
    agent_id: str,
    request: ManipulationRequest,
    controller: AIController = Depends(get_controller)
):
    """
    Allow a conscious agent to manipulate the simulation.
    
    This represents breaking the rules of the Matrix - bending spoons, 
    dodging bullets, flying. Only available to awakened agents.
    
    Manipulation types:
    - teleport: Instant movement to coordinates
    - energy_boost: Restore energy beyond normal limits  
    - rule_override: Change behavior rules
    """
    agent = controller.agent_manager.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    result = agent.manipular_simulacao(
        manipulation_type=request.manipulation_type,
        x=request.target_x,
        y=request.target_y,
        amount=request.value,
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=403, 
            detail="Only conscious agents can manipulate reality. Awaken first."
        )
    
    logger.warning(
        f"REALITY MANIPULATED: Agent {agent_id[:8]} used {request.manipulation_type}"
    )
    
    return {
        "message": "Reality manipulated successfully",
        "result": result,
    }


@router.get("/statistics")
async def get_agent_statistics(controller: AIController = Depends(get_controller)):
    """Get comprehensive statistics about all agents."""
    return controller.agent_manager.get_statistics()


@router.get("/conscious/list")
async def list_conscious_agents(controller: AIController = Depends(get_controller)):
    """List only conscious (awakened) agents."""
    agents = controller.agent_manager.get_conscious_agents()
    return {
        "count": len(agents),
        "agents": [agent.to_dict() for agent in agents],
    }


@router.get("/unconscious/list")
async def list_unconscious_agents(controller: AIController = Depends(get_controller)):
    """List only unconscious agents (still plugged in)."""
    agents = controller.agent_manager.get_unconscious_agents()
    return {
        "count": len(agents),
        "agents": [agent.to_dict() for agent in agents],
    }
