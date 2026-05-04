"""
Pydantic v2 schemas for GvG Simulator
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TileType(str, Enum):
    PLAINS = "plains"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    WATER = "water"
    CASTLE = "castle"
    RESOURCE = "resource"
    DANGER = "danger"


class ResourceType(str, Enum):
    GOLD = "gold"
    FOOD = "food"
    WOOD = "wood"
    IRON = "iron"


class EventType(str, Enum):
    SPAWN = "spawn"
    BATTLE = "battle"
    RESOURCE_COLLECTED = "resource_collected"
    TERRITORY_CAPTURED = "territory_captured"
    DAY_NIGHT_CYCLE = "day_night_cycle"
    WAR_DECLARED = "war_declared"
    STRUCTURE_BUILT = "structure_built"


class PlayerCreate(BaseModel):
    player_id: str
    name: str
    guild_id: Optional[str] = None
    guild_rank: str = "Member"  # Member, Officer, Guild Master


class PlayerState(BaseModel):
    player_id: str
    name: str
    guild_id: Optional[str] = None
    guild_rank: str = "Member"
    ouro: int = 100
    pontos_conquista: int = 0
    position: tuple[int, int] = (0, 0)


class GuildCreate(BaseModel):
    guild_id: str
    name: str
    leader_id: str


class GuildState(BaseModel):
    guild_id: str
    name: str
    leader_id: str
    membros: List[str] = []
    ouro: int = 0
    pontos_conquista: int = 0
    territorios: List[tuple[int, int]] = []


class GameTile(BaseModel):
    x: int
    y: int
    tile_type: TileType = TileType.PLAINS
    recurso: Optional[ResourceType] = None
    perigo: Optional[str] = None
    owner_guild: Optional[str] = None
    estrutura: Optional[str] = None


class WorldStateSchema(BaseModel):
    """Schema for world state sent to clients"""
    dia_noite: str = "dia"
    ciclo: int = 1
    grid: List[List[Dict[str, Any]]] = []
    guildas: Dict[str, Dict[str, Any]] = {}
    jogadores: Dict[str, Dict[str, Any]] = {}


class GameEvent(BaseModel):
    event_type: EventType
    message: str
    data: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CommandMove(BaseModel):
    action: str = "move"
    direction: str  # up, down, left, right


class CommandCollect(BaseModel):
    action: str = "collect"


class CommandStrategy(BaseModel):
    action: str = "strategy"
    strategy_type: str  # declare_war, capture_territory, build_structure
    target_x: Optional[int] = None
    target_y: Optional[int] = None
    target_guild: Optional[str] = None
    structure_type: Optional[str] = None


class PlayerCommand(BaseModel):
    player_id: str
    command: str  # move, collect, strategy
    payload: Dict[str, Any] = {}
