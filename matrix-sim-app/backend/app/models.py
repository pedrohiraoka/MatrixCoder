"""
Pydantic models (schemas) for API request/response validation.
Defines the data structures for agents, simulation state, and logs.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Possible states for an agent in the simulation."""
    NORMAL = "normal"
    AWAKE = "awake"
    DISCONNECTED = "disconnected"


# ============== Agent Schemas ==============

class AgentBase(BaseModel):
    """Base schema for agent data."""
    position_x: int = Field(ge=0, description="X coordinate in the grid")
    position_y: int = Field(ge=0, description="Y coordinate in the grid")
    
    class Config:
        from_attributes = True


class AgentCreate(AgentBase):
    """Schema for creating a new agent."""
    is_conscious: bool = Field(default=False, description="Whether agent is 'awake' like Neo")
    name: Optional[str] = Field(default=None, max_length=50)


class AgentUpdate(BaseModel):
    """Schema for updating agent properties."""
    position_x: Optional[int] = Field(default=None, ge=0)
    position_y: Optional[int] = Field(default=None, ge=0)
    is_conscious: Optional[bool] = None
    energy: Optional[float] = None


class AgentResponse(AgentBase):
    """Full agent response schema."""
    id: str
    name: Optional[str]
    energy: float = Field(default=100.0, ge=0, le=100)
    is_conscious: bool
    status: AgentStatus
    created_at: datetime
    last_updated: datetime
    
    class Config:
        from_attributes = True


# ============== Simulation Schemas ==============

class MatrixState(BaseModel):
    """Current state of the entire Matrix simulation."""
    tick: int = Field(description="Current simulation tick number")
    total_agents: int
    conscious_agents: int
    total_energy_collected: float
    grid_size: int
    running: bool
    start_time: Optional[datetime] = None


class GridCell(BaseModel):
    """Represents a single cell in the simulation grid."""
    x: int
    y: int
    has_agent: bool
    agent_id: Optional[str] = None
    is_conscious: bool = False
    energy_level: float = 0.0


class GridState(BaseModel):
    """Complete grid state for frontend rendering."""
    tick: int
    cells: List[GridCell]
    dimensions: int


# ============== Log Schemas ==============

class LogLevel(str, Enum):
    """Log severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry(BaseModel):
    """A single log entry from the simulation."""
    timestamp: datetime
    level: LogLevel
    message: str
    source: str = "system"
    data: Optional[Dict[str, Any]] = None


class LogStream(BaseModel):
    """Stream of log entries."""
    logs: List[LogEntry]
    total_count: int


# ============== Control Schemas ==============

class SimulationControl(BaseModel):
    """Commands to control the simulation."""
    action: str = Field(..., description="start, stop, pause, resume, reset")


class AwakeningRequest(BaseModel):
    """Request to awaken an agent (make them conscious)."""
    agent_id: str
    red_pill: bool = Field(default=True, description="Must be True to awaken")


class CodeViewRequest(BaseModel):
    """Request to view the underlying code/rules of the simulation."""
    agent_id: str


class ManipulationRequest(BaseModel):
    """Request from a conscious agent to manipulate the simulation."""
    agent_id: str
    manipulation_type: str = Field(..., description="teleport, energy_boost, rule_override")
    target_x: Optional[int] = None
    target_y: Optional[int] = None
    value: Optional[float] = None


# ============== WebSocket Message Schemas ==============

class WSMessageType(str, Enum):
    """Types of WebSocket messages."""
    STATE_UPDATE = "state_update"
    LOG_ENTRY = "log_entry"
    AGENT_UPDATE = "agent_update"
    GRID_UPDATE = "grid_update"
    ERROR = "error"


class WSMessage(BaseModel):
    """Standard WebSocket message structure."""
    type: WSMessageType
    timestamp: datetime
    data: Dict[str, Any]
