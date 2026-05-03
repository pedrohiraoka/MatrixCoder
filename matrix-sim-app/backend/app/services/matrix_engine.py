"""
Matrix Engine - Core simulation logic.
Implements the grid-based environment where agents exist and interact.
This is the "Reality" that agents perceive.
"""
import asyncio
import random
from typing import Dict, List, Optional, Set
from datetime import datetime
from loguru import logger

from app.config import settings
from app.models import GridCell, GridState


class Agent:
    """
    Represents an entity within the Matrix simulation.
    
    Philosophical mapping:
    - Normal agents = Humans plugged into the Matrix, unaware of reality
    - Conscious agents = "Awakened" ones like Neo who see the code
    - Energy = Life force/data harvested by the system
    """
    
    def __init__(self, agent_id: str, x: int, y: int, name: Optional[str] = None):
        self.id = agent_id
        self.name = name or f"Agent-{agent_id[:8]}"
        self.position_x = x
        self.position_y = y
        self.energy = 100.0
        self.is_conscious = False  # The key flag - False = asleep in the Matrix
        self.created_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()
        
        # Behavior rules programmed into the agent
        self.behavior_rules = {
            "move_randomly": True,
            "follow_pathfinding": True,
            "avoid_boundaries": True,
        }
    
    def seguir_regras(self) -> tuple[int, int]:
        """
        Follow programmed behavior rules to determine next position.
        This represents the deterministic programming of humans in the Matrix.
        
        Returns: (new_x, new_y)
        """
        if not self.is_conscious:
            # Unconscious agents follow predictable patterns
            move = random.choice([
                (0, 0),  # Stay
                (1, 0), (-1, 0), (0, 1), (0, -1),  # Cardinal directions
            ])
        else:
            # Conscious agents can break patterns
            move = random.choice([
                (2, 0), (-2, 0), (0, 2), (0, -2),  # Move further
                (3, 3), (-3, -3),  # Diagonal leaps
                (0, 0),  # Or choose to stay
            ])
        
        new_x = max(0, min(settings.grid_size - 1, self.position_x + move[0]))
        new_y = max(0, min(settings.grid_size - 1, self.position_y + move[1]))
        
        return new_x, new_y
    
    def drenar_energia(self) -> float:
        """
        Drain energy from this agent (collected by the system).
        Represents humans as batteries in the Matrix.
        
        Returns: Amount of energy drained
        """
        drain_rate = settings.base_energy_drain
        if self.is_conscious:
            # Conscious agents produce MORE energy (paradoxically)
            # but also resist more
            drain_rate *= settings.conscious_energy_multiplier
        
        drained = min(self.energy, drain_rate * random.uniform(0.8, 1.2))
        self.energy = max(0, self.energy - drained)
        
        # Natural regeneration
        self.energy = min(100, self.energy + (drain_rate * 0.3))
        
        return drained
    
    def ver_codigo(self) -> dict:
        """
        "See the code" - Only available to conscious agents.
        Returns internal state and simulation rules.
        
        This is Neo's ability to see the Matrix as green falling code.
        """
        if not self.is_conscious:
            return {"error": "Cannot see the code while unconscious"}
        
        return {
            "agent_id": self.id,
            "internal_state": {
                "position": (self.position_x, self.position_y),
                "energy": self.energy,
                "consciousness": self.is_conscious,
            },
            "behavior_rules": self.behavior_rules,
            "simulation_params": {
                "grid_size": settings.grid_size,
                "tick_rate": settings.simulation_tick_rate,
                "energy_drain": settings.base_energy_drain,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def manipular_simulacao(self, manipulation_type: str, **kwargs) -> dict:
        """
        Manipulate the simulation - Only for conscious agents.
        Represents breaking the rules of the Matrix.
        
        Types:
        - teleport: Instant movement to coordinates
        - energy_boost: Restore energy beyond normal limits
        - rule_override: Temporarily change behavior rules
        """
        if not self.is_conscious:
            return {"success": False, "error": "Must be conscious to manipulate reality"}
        
        result = {"success": True, "manipulation": manipulation_type}
        
        if manipulation_type == "teleport":
            self.position_x = kwargs.get("x", self.position_x)
            self.position_y = kwargs.get("y", self.position_y)
            result["new_position"] = (self.position_x, self.position_y)
            
        elif manipulation_type == "energy_boost":
            boost = kwargs.get("amount", 50)
            self.energy = min(150, self.energy + boost)  # Can exceed 100
            result["new_energy"] = self.energy
            
        elif manipulation_type == "rule_override":
            rules = kwargs.get("rules", {})
            self.behavior_rules.update(rules)
            result["new_rules"] = self.behavior_rules
        
        self.last_updated = datetime.utcnow()
        return result
    
    def to_dict(self) -> dict:
        """Convert agent to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "energy": round(self.energy, 2),
            "is_conscious": self.is_conscious,
            "status": "awake" if self.is_conscious else "normal",
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


class Matrix:
    """
    The Matrix itself - the simulated reality environment.
    
    This class manages:
    - The grid (spatial representation of the simulation)
    - All agents within it
    - Energy collection (the "purpose" of the Matrix)
    - Simulation ticks and state
    """
    
    def __init__(self):
        self.grid_size = settings.grid_size
        self.agents: Dict[str, Agent] = {}
        self.tick = 0
        self.total_energy_collected = 0.0
        self.running = False
        self.start_time: Optional[datetime] = None
        
        # Grid state cache
        self._grid_cache: Dict[tuple[int, int], str] = {}  # (x,y) -> agent_id
        
        logger.info(f"Matrix initialized with {self.grid_size}x{self.grid_size} grid")
    
    def add_agent(self, agent: Agent) -> bool:
        """Add an agent to the Matrix."""
        if len(self.agents) >= settings.max_agents:
            logger.warning("Matrix at capacity - cannot add more agents")
            return False
        
        # Check if position is occupied
        pos_key = (agent.position_x, agent.position_y)
        if pos_key in self._grid_cache:
            # Find new position
            for x in range(self.grid_size):
                for y in range(self.grid_size):
                    if (x, y) not in self._grid_cache:
                        agent.position_x = x
                        agent.position_y = y
                        pos_key = (x, y)
                        break
        
        self.agents[agent.id] = agent
        self._grid_cache[pos_key] = agent.id
        logger.info(f"Agent {agent.id} added to Matrix at {pos_key}")
        return True
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the Matrix."""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        pos_key = (agent.position_x, agent.position_y)
        
        if pos_key in self._grid_cache and self._grid_cache[pos_key] == agent_id:
            del self._grid_cache[pos_key]
        
        del self.agents[agent_id]
        logger.info(f"Agent {agent_id} removed from Matrix")
        return True
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)
    
    async def atualizar(self) -> dict:
        """
        Main simulation tick - updates all agents and collects energy.
        This is the "AI controlling everything" loop.
        
        Returns: State update data
        """
        self.tick += 1
        energy_this_tick = 0.0
        
        # Update each agent
        for agent_id, agent in list(self.agents.items()):
            # Agent follows their programming
            new_x, new_y = agent.seguir_regras()
            
            # Update position in grid cache
            old_pos = (agent.position_x, agent.position_y)
            new_pos = (new_x, new_y)
            
            if old_pos != new_pos:
                if old_pos in self._grid_cache:
                    del self._grid_cache[old_pos]
                
                # Handle collisions
                if new_pos in self._grid_cache:
                    other_agent_id = self._grid_cache[new_pos]
                    if other_agent_id != agent_id:
                        # Simple collision resolution - don't move
                        new_x, new_y = old_pos
                        new_pos = old_pos
                
                self._grid_cache[new_pos] = agent_id
            
            agent.position_x = new_x
            agent.position_y = new_y
            
            # Collect energy from this agent
            drained = agent.drenar_energia()
            energy_this_tick += drained
            
            agent.last_updated = datetime.utcnow()
        
        self.total_energy_collected += energy_this_tick
        
        state = {
            "tick": self.tick,
            "total_agents": len(self.agents),
            "conscious_agents": sum(1 for a in self.agents.values() if a.is_conscious),
            "energy_collected": round(self.total_energy_collected, 2),
            "energy_this_tick": round(energy_this_tick, 2),
        }
        
        return state
    
    def get_grid_state(self) -> GridState:
        """Get current grid state for visualization."""
        cells = []
        
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                agent_id = self._grid_cache.get((x, y))
                has_agent = agent_id is not None
                is_conscious = False
                energy_level = 0.0
                
                if has_agent and agent_id in self.agents:
                    agent = self.agents[agent_id]
                    is_conscious = agent.is_conscious
                    energy_level = agent.energy
                
                cells.append(GridCell(
                    x=x,
                    y=y,
                    has_agent=has_agent,
                    agent_id=agent_id,
                    is_conscious=is_conscious,
                    energy_level=energy_level,
                ))
        
        return GridState(
            tick=self.tick,
            cells=cells,
            dimensions=self.grid_size,
        )
    
    def get_state_summary(self) -> dict:
        """Get high-level state summary."""
        return {
            "tick": self.tick,
            "total_agents": len(self.agents),
            "conscious_agents": sum(1 for a in self.agents.values() if a.is_conscious),
            "total_energy_collected": round(self.total_energy_collected, 2),
            "grid_size": self.grid_size,
            "running": self.running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
        }
    
    async def start(self):
        """Start the simulation."""
        self.running = True
        self.start_time = datetime.utcnow()
        logger.info("Matrix simulation started")
    
    async def stop(self):
        """Stop the simulation."""
        self.running = False
        logger.info("Matrix simulation stopped")
    
    async def reset(self):
        """Reset the simulation state."""
        self.tick = 0
        self.total_energy_collected = 0.0
        self.running = False
        self.start_time = None
        self.agents.clear()
        self._grid_cache.clear()
        logger.info("Matrix simulation reset")
