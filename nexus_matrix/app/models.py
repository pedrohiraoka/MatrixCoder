"""
Nexus Matrix - Models
Modelos de dados e gerenciadores para agentes, grupos, mensagens
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

# Pydantic Models para API

class AgentBase(BaseModel):
    name: str
    type: str
    role: str
    
class AgentCreate(AgentBase):
    pass

class Agent(AgentBase):
    id: int
    anomaly_score: float = 0.0
    energy_level: float = 1.0
    created_at: datetime
    last_active: datetime
    
    class Config:
        from_attributes = True

class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    
class GroupCreate(GroupBase):
    pass

class Group(GroupBase):
    id: int
    cohesion: float = 0.5
    energy: float = 0.5
    is_hidden: bool = False
    created_at: datetime
    member_count: int = 0
    
    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str
    topic: Optional[str] = None
    
class MessageCreate(MessageBase):
    agent_id: int
    group_id: Optional[int] = None

class Message(MessageBase):
    id: int
    agent_id: int
    group_id: Optional[int]
    energy_contribution: float = 0.0
    created_at: datetime
    
    class Config:
        from_attributes = True

class EventBase(BaseModel):
    event_type: str
    description: str
    
class EventCreate(EventBase):
    tick_number: int = 0
    metadata: Optional[Dict[str, Any]] = None

class Event(EventBase):
    id: int
    tick_number: int
    metadata: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class MetricsBase(BaseModel):
    tick_number: int
    
class MetricsCreate(MetricsBase):
    social_energy: float = 0.0
    avg_cohesion: float = 0.0
    anomaly_count: int = 0
    group_count: int = 0
    message_count: int = 0

class Metrics(MetricsBase):
    id: int
    social_energy: float
    avg_cohesion: float
    anomaly_count: int
    group_count: int
    message_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class GraphNode(BaseModel):
    id: int
    name: str
    type: str
    anomaly_score: float
    energy_level: float
    group: Optional[str] = None

class GraphLink(BaseModel):
    source: int
    target: int
    strength: float
    connection_type: str

class GraphData(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]

class DashboardState(BaseModel):
    current_tick: int
    social_energy: float
    avg_cohesion: float
    anomaly_count: int
    group_count: int
    active_agents: int
    zion_exists: bool
    zion_members: int
    recent_messages: List[Message]
    recent_events: List[Event]

class ZionStatus(BaseModel):
    exists: bool
    status: str = "inactive"
    name: Optional[str] = None
    member_count: int = 0
    members: List[Dict[str, Any]] = []
    cohesion: float = 0.0
    energy: float = 0.0

class ThemeInjection(BaseModel):
    theme: str
    category: str = "custom"
    priority: str = "normal"

class AgentAction(BaseModel):
    agent_id: int
    action_type: str
    target_id: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None
