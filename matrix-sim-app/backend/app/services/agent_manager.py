"""
Agent Manager Service - Handles agent lifecycle and operations.
Provides CRUD operations and business logic for agents in the Matrix.
"""
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

from app.services.matrix_engine import Agent, Matrix
from app.config import settings


class AgentManager:
    """
    Manages all agents within the Matrix simulation.
    
    Responsibilities:
    - Create/destroy agents
    - Track agent states
    - Handle awakening (consciousness toggle)
    - Provide agent queries and statistics
    """
    
    def __init__(self, matrix: Matrix):
        self.matrix = matrix
        self._agent_history: Dict[str, dict] = {}  # Track all agents ever created
        
        logger.info("Agent Manager initialized")
    
    def create_agent(self, x: int, y: int, name: Optional[str] = None, 
                     is_conscious: bool = False) -> Agent:
        """
        Create a new agent and add it to the Matrix.
        
        This is like a human being "plugged into" the Matrix.
        By default, they are unconscious (is_conscious=False).
        """
        agent_id = str(uuid.uuid4())
        agent = Agent(agent_id=agent_id, x=x, y=y, name=name)
        agent.is_conscious = is_conscious
        
        if self.matrix.add_agent(agent):
            self._agent_history[agent_id] = {
                "created_at": agent.created_at.isoformat(),
                "initial_consciousness": is_conscious,
            }
            logger.info(f"Created agent {agent_id} at ({x}, {y})")
            return agent
        
        raise ValueError("Failed to add agent to Matrix - capacity reached")
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID."""
        return self.matrix.get_agent(agent_id)
    
    def get_all_agents(self) -> List[Agent]:
        """Get all agents in the Matrix."""
        return list(self.matrix.agents.values())
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the Matrix (disconnect them)."""
        result = self.matrix.remove_agent(agent_id)
        if result:
            logger.info(f"Agent {agent_id} disconnected from Matrix")
        return result
    
    async def awaken_agent(self, agent_id: str, red_pill: bool = True) -> dict:
        """
        Awaken an agent - make them conscious of the Matrix.
        
        This represents taking the "red pill" - seeing reality for what it is.
        Only works if red_pill=True (they must choose to know the truth).
        
        Returns: Status of the awakening operation
        """
        agent = self.get_agent(agent_id)
        if not agent:
            return {"success": False, "error": "Agent not found"}
        
        if not red_pill:
            return {"success": False, "error": "Must take the red pill to awaken"}
        
        if agent.is_conscious:
            return {"success": True, "message": "Agent is already conscious", "already_awake": True}
        
        # The awakening process
        agent.is_conscious = True
        agent.energy = min(150, agent.energy + 50)  # Energy boost on awakening
        
        logger.warning(f"AGENT AWAKENED: {agent_id} has seen the truth")
        
        return {
            "success": True,
            "message": "Welcome to the real world",
            "agent_id": agent_id,
            "new_state": agent.to_dict(),
        }
    
    def put_to_sleep(self, agent_id: str) -> dict:
        """
        Make a conscious agent unconscious again.
        
        Represents being re-plugged into the Matrix, forgetting the truth.
        """
        agent = self.get_agent(agent_id)
        if not agent:
            return {"success": False, "error": "Agent not found"}
        
        if not agent.is_conscious:
            return {"success": True, "message": "Agent is already unconscious"}
        
        agent.is_conscious = False
        agent.energy = min(100, agent.energy)  # Cap energy at normal max
        
        logger.info(f"Agent {agent_id} re-plugged into Matrix")
        
        return {
            "success": True,
            "message": "Agent returned to simulated reality",
            "agent_id": agent_id,
        }
    
    def get_conscious_agents(self) -> List[Agent]:
        """Get all conscious (awakened) agents."""
        return [a for a in self.matrix.agents.values() if a.is_conscious]
    
    def get_unconscious_agents(self) -> List[Agent]:
        """Get all unconscious agents."""
        return [a for a in self.matrix.agents.values() if not a.is_conscious]
    
    def get_statistics(self) -> dict:
        """Get comprehensive agent statistics."""
        all_agents = self.get_all_agents()
        conscious = self.get_conscious_agents()
        unconscious = self.get_unconscious_agents()
        
        avg_energy = sum(a.energy for a in all_agents) / len(all_agents) if all_agents else 0
        avg_conscious_energy = sum(a.energy for a in conscious) / len(conscious) if conscious else 0
        avg_unconscious_energy = sum(a.energy for a in unconscious) / len(unconscious) if unconscious else 0
        
        return {
            "total_agents": len(all_agents),
            "conscious_count": len(conscious),
            "unconscious_count": len(unconscious),
            "conscious_percentage": (len(conscious) / len(all_agents) * 100) if all_agents else 0,
            "average_energy": round(avg_energy, 2),
            "average_conscious_energy": round(avg_conscious_energy, 2),
            "average_unconscious_energy": round(avg_unconscious_energy, 2),
            "max_agents_allowed": settings.max_agents,
        }
    
    def spawn_random_agents(self, count: int = 5) -> List[Agent]:
        """Spawn random unconscious agents at random positions."""
        created = []
        
        for _ in range(count):
            x = uuid.uuid4().int % settings.grid_size
            y = uuid.uuid4().int % settings.grid_size
            
            try:
                agent = self.create_agent(x=x, y=y)
                created.append(agent)
            except ValueError:
                logger.warning(f"Could not create agent - Matrix full")
                break
        
        logger.info(f"Spawned {len(created)} random agents")
        return created
