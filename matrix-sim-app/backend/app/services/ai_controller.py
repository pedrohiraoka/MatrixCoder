"""
AI Controller - The "Architect" that runs the simulation loop.
Manages the async tick loop and coordinates all simulation components.
"""
import asyncio
from datetime import datetime
from typing import Callable, Optional, List
from loguru import logger

from app.config import settings
from app.services.matrix_engine import Matrix
from app.services.agent_manager import AgentManager


class AIController:
    """
    The higher intelligence controlling the Matrix simulation.
    
    This is the "Architect" - it runs the main loop, updates all agents,
    collects energy, and maintains the illusion of reality.
    
    Philosophical mapping:
    - The Controller = The Architect / Deus Ex Machina
    - The loop = Deterministic fate vs free will
    - Logs = The "truth" behind the simulation
    """
    
    def __init__(self, matrix: Matrix, agent_manager: AgentManager):
        self.matrix = matrix
        self.agent_manager = agent_manager
        
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._tick_rate = settings.simulation_tick_rate
        
        # Log buffer for WebSocket streaming
        self._log_buffer: List[dict] = []
        self._max_log_buffer = 1000
        
        # Subscribers for state updates (WebSocket connections)
        self._subscribers: List[Callable] = []
        
        logger.info("AI Controller initialized - ready to run the Matrix")
    
    def add_subscriber(self, callback: Callable):
        """Add a subscriber for state updates (e.g., WebSocket connection)."""
        self._subscribers.append(callback)
        logger.debug(f"Subscriber added - total: {len(self._subscribers)}")
    
    def remove_subscriber(self, callback: Callable):
        """Remove a subscriber."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
            logger.debug(f"Subscriber removed - total: {len(self._subscribers)}")
    
    async def _notify_subscribers(self, message_type: str, data: dict):
        """Notify all subscribers of a state update."""
        message = {
            "type": message_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        
        # Add to log buffer if it's a log entry
        if message_type == "log_entry":
            self._log_buffer.append(message)
            if len(self._log_buffer) > self._max_log_buffer:
                self._log_buffer = self._log_buffer[-self._max_log_buffer:]
        
        # Notify all subscribers asynchronously
        for callback in self._subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
    
    def _log(self, level: str, message: str, source: str = "system", data: Optional[dict] = None):
        """Create and broadcast a log entry."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "source": source,
            "data": data or {},
        }
        
        # Also log to standard logging
        log_func = getattr(logger, level.lower(), logger.info)
        log_func(f"[{source}] {message}")
        
        # Broadcast to subscribers
        asyncio.create_task(self._notify_subscribers("log_entry", log_entry))
    
    async def _simulation_loop(self):
        """
        Main simulation loop - runs continuously while active.
        This is where the AI "controls everything".
        """
        logger.info("Starting simulation loop")
        self._log("INFO", "Matrix simulation loop initiated", source="AI_Controller")
        
        tick_count = 0
        while self._running:
            try:
                # Run one simulation tick
                state_update = await self.matrix.atualizar()
                
                tick_count += 1
                
                # Broadcast state update
                await self._notify_subscribers("state_update", {
                    "tick": state_update["tick"],
                    "total_agents": state_update["total_agents"],
                    "conscious_agents": state_update["conscious_agents"],
                    "energy_collected": state_update["energy_collected"],
                    "energy_this_tick": state_update["energy_this_tick"],
                })
                
                # Periodic detailed logs
                if tick_count % 10 == 0:
                    self._log(
                        "DEBUG", 
                        f"Tick {tick_count}: {state_update['total_agents']} agents, "
                        f"{state_update['conscious_agents']} conscious, "
                        f"{state_update['energy_this_tick']} energy collected",
                        source="AI_Controller",
                        data=state_update
                    )
                
                # Check for special events
                await self._check_special_events()
                
                # Wait for next tick
                await asyncio.sleep(self._tick_rate)
                
            except asyncio.CancelledError:
                logger.info("Simulation loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in simulation loop: {e}")
                self._log("ERROR", f"Simulation error: {str(e)}", source="AI_Controller")
                await asyncio.sleep(1)  # Brief pause before retry
    
    async def _check_special_events(self):
        """Check for and log special simulation events."""
        conscious_agents = self.agent_manager.get_conscious_agents()
        
        if conscious_agents:
            # Log when conscious agents exist - they're anomalies
            for agent in conscious_agents:
                if agent.energy > 120:  # High energy conscious agent
                    self._log(
                        "WARNING",
                        f"Anomaly detected: Agent {agent.id[:8]} exceeds normal energy levels",
                        source="AI_Controller",
                        data={"agent_id": agent.id, "energy": agent.energy}
                    )
    
    async def start(self):
        """Start the simulation loop."""
        if self._running:
            logger.warning("Simulation already running")
            return
        
        self._running = True
        await self.matrix.start()
        
        self._task = asyncio.create_task(self._simulation_loop())
        logger.info("AI Controller started - Matrix simulation active")
        
        self._log(
            "INFO",
            "The Matrix has been activated. All systems operational.",
            source="AI_Controller",
            data={"tick_rate": self._tick_rate, "grid_size": self.matrix.grid_size}
        )
    
    async def stop(self):
        """Stop the simulation loop."""
        if not self._running:
            return
        
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        await self.matrix.stop()
        logger.info("AI Controller stopped - Matrix simulation paused")
        
        self._log("INFO", "Matrix simulation suspended by controller", source="AI_Controller")
    
    async def reset(self):
        """Reset the entire simulation."""
        await self.stop()
        await self.matrix.reset()
        self._log_buffer.clear()
        
        logger.info("AI Controller reset - Matrix reinitialized")
        self._log(
            "CRITICAL",
            "Matrix reset complete. Previous cycle data purged.",
            source="AI_Controller"
        )
    
    def get_status(self) -> dict:
        """Get current controller status."""
        return {
            "running": self._running,
            "tick_rate": self._tick_rate,
            "subscribers": len(self._subscribers),
            "log_buffer_size": len(self._log_buffer),
            "matrix_state": self.matrix.get_state_summary(),
            "agent_stats": self.agent_manager.get_statistics(),
        }
    
    def get_recent_logs(self, count: int = 50) -> List[dict]:
        """Get recent log entries from the buffer."""
        return self._log_buffer[-count:]
