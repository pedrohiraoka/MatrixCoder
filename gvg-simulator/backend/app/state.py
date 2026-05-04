"""
In-memory state management for GvG Simulator
Thread-safe state with asyncio.Lock support
"""
import asyncio
import random
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from .models import (
    TileType, ResourceType, GameTile, GuildState, 
    PlayerState, WorldStateSchema, GameEvent, EventType
)


class WorldState:
    """
    Singleton-like in-memory world state.
    Maintains 20x20 grid, players, guilds, and global state.
    Uses asyncio.Lock for thread-safety in async context.
    """
    
    GRID_SIZE = 20
    
    def __init__(self):
        self.lock = asyncio.Lock()
        self.dia_noite: str = "dia"
        self.ciclo: int = 1
        self.grid: List[List[GameTile]] = []
        self.jogadores: Dict[str, PlayerState] = {}
        self.guildas: Dict[str, GuildState] = {}
        self.eventos: List[GameEvent] = []
        self.connected_websockets: Dict[str, Any] = {}  # player_id -> websocket
        
        self._initialize_grid()
    
    def _initialize_grid(self):
        """Initialize 20x20 grid with random terrain"""
        self.grid = []
        for y in range(self.GRID_SIZE):
            row = []
            for x in range(self.GRID_SIZE):
                tile_type = self._random_tile_type()
                tile = GameTile(
                    x=x,
                    y=y,
                    tile_type=tile_type,
                    recurso=self._maybe_resource(tile_type),
                    perigo=self._maybe_danger(tile_type)
                )
                row.append(tile)
            self.grid.append(row)
        
        # Add castles at corners for guilds
        self.grid[0][0].tile_type = TileType.CASTLE
        self.grid[0][19].tile_type = TileType.CASTLE
        self.grid[19][0].tile_type = TileType.CASTLE
        self.grid[19][19].tile_type = TileType.CASTLE
    
    def _random_tile_type(self) -> TileType:
        """Random terrain generation with weights"""
        rand = random.random()
        if rand < 0.5:
            return TileType.PLAINS
        elif rand < 0.7:
            return TileType.FOREST
        elif rand < 0.85:
            return TileType.MOUNTAIN
        elif rand < 0.95:
            return TileType.WATER
        else:
            return TileType.PLAINS
    
    def _maybe_resource(self, tile_type: TileType) -> Optional[ResourceType]:
        """Chance to spawn resource on certain tiles"""
        if tile_type in [TileType.FOREST, TileType.MOUNTAIN, TileType.PLAINS]:
            if random.random() < 0.15:
                return random.choice(list(ResourceType))
        return None
    
    def _maybe_danger(self, tile_type: TileType) -> Optional[str]:
        """Chance to spawn danger on certain tiles"""
        if tile_type in [TileType.FOREST, TileType.MOUNTAIN]:
            if random.random() < 0.08:
                return random.choice(["monstro", "armadilha", "inimigo"])
        return None
    
    async def add_player(self, player: PlayerState):
        """Add player to world"""
        async with self.lock:
            self.jogadores[player.player_id] = player
            # Spawn player at random safe location
            safe_spawn = self._find_safe_spawn()
            player.position = safe_spawn
    
    async def remove_player(self, player_id: str):
        """Remove player from world"""
        async with self.lock:
            if player_id in self.jogadores:
                del self.jogadores[player_id]
    
    async def add_guild(self, guild: GuildState):
        """Add guild to world"""
        async with self.lock:
            self.guildas[guild.guild_id] = guild
    
    def _find_safe_spawn(self) -> Tuple[int, int]:
        """Find a safe spawn point (plains without danger)"""
        attempts = 0
        while attempts < 100:
            x = random.randint(0, self.GRID_SIZE - 1)
            y = random.randint(0, self.GRID_SIZE - 1)
            tile = self.grid[y][x]
            if tile.tile_type == TileType.PLAINS and not tile.perigo:
                return (x, y)
            attempts += 1
        return (0, 0)  # Fallback
    
    async def move_player(self, player_id: str, direction: str) -> bool:
        """Move player in direction"""
        async with self.lock:
            if player_id not in self.jogadores:
                return False
            
            player = self.jogadores[player_id]
            x, y = player.position
            
            if direction == "up":
                y = max(0, y - 1)
            elif direction == "down":
                y = min(self.GRID_SIZE - 1, y + 1)
            elif direction == "left":
                x = max(0, x - 1)
            elif direction == "right":
                x = min(self.GRID_SIZE - 1, x + 1)
            
            player.position = (x, y)
            return True
    
    async def collect_resource(self, player_id: str) -> Optional[ResourceType]:
        """Collect resource at player position"""
        async with self.lock:
            if player_id not in self.jogadores:
                return None
            
            player = self.jogadores[player_id]
            x, y = player.position
            tile = self.grid[y][x]
            
            if tile.recurso:
                recurso = tile.recurso
                tile.recurso = None
                player.ouro += self._resource_value(recurso)
                return recurso
            return None
    
    def _resource_value(self, resource: ResourceType) -> int:
        """Return gold value for resource type"""
        values = {
            ResourceType.GOLD: 50,
            ResourceType.FOOD: 20,
            ResourceType.WOOD: 15,
            ResourceType.IRON: 30
        }
        return values.get(resource, 10)
    
    async def capture_territory(self, player_id: str, guild_id: str, x: int, y: int) -> bool:
        """Capture territory for guild"""
        async with self.lock:
            if player_id not in self.jogadores or guild_id not in self.guildas:
                return False
            
            if x < 0 or x >= self.GRID_SIZE or y < 0 or y >= self.GRID_SIZE:
                return False
            
            tile = self.grid[y][x]
            guild = self.guildas[guild_id]
            player = self.jogadores[player_id]
            
            # Capture costs ouro
            if player.ouro >= 100:
                player.ouro -= 100
                tile.owner_guild = guild_id
                if (x, y) not in guild.territorios:
                    guild.territorios.append((x, y))
                guild.pontos_conquista += 10
                player.pontos_conquista += 5
                return True
            return False
    
    async def build_structure(self, player_id: str, guild_id: str, x: int, y: int, structure_type: str) -> bool:
        """Build structure on territory"""
        async with self.lock:
            if player_id not in self.jogadores or guild_id not in self.guildas:
                return False
            
            tile = self.grid[y][x]
            guild = self.guildas[guild_id]
            player = self.jogadores[player_id]
            
            # Must own territory and have enough ouro
            if tile.owner_guild == guild_id and player.ouro >= 200:
                player.ouro -= 200
                tile.estrutura = structure_type
                return True
            return False
    
    async def spawn_resource(self, x: int, y: int, resource_type: ResourceType):
        """Spawn resource at location"""
        async with self.lock:
            if 0 <= x < self.GRID_SIZE and 0 <= y < self.GRID_SIZE:
                tile = self.grid[y][x]
                if not tile.recurso and tile.tile_type != TileType.WATER:
                    tile.recurso = resource_type
                    return True
        return False
    
    async def spawn_danger(self, x: int, y: int, danger_type: str):
        """Spawn danger at location"""
        async with self.lock:
            if 0 <= x < self.GRID_SIZE and 0 <= y < self.GRID_SIZE:
                tile = self.grid[y][x]
                if not tile.perigo and tile.tile_type not in [TileType.WATER, TileType.CASTLE]:
                    tile.perigo = danger_type
                    return True
        return False
    
    async def toggle_day_night(self):
        """Toggle day/night cycle"""
        async with self.lock:
            self.dia_noite = "noite" if self.dia_noite == "dia" else "dia"
            if self.dia_noite == "dia":
                self.ciclo += 1
    
    def get_world_state(self) -> WorldStateSchema:
        """Get serializable world state"""
        grid_data = []
        for row in self.grid:
            row_data = []
            for tile in row:
                row_data.append({
                    "x": tile.x,
                    "y": tile.y,
                    "tile_type": tile.tile_type.value,
                    "recurso": tile.recurso.value if tile.recurso else None,
                    "perigo": tile.perigo,
                    "owner_guild": tile.owner_guild,
                    "estrutura": tile.estrutura
                })
            grid_data.append(row_data)
        
        guilds_data = {}
        for gid, guild in self.guildas.items():
            guilds_data[gid] = {
                "guild_id": guild.guild_id,
                "name": guild.name,
                "leader_id": guild.leader_id,
                "membros": guild.membros,
                "ouro": guild.ouro,
                "pontos_conquista": guild.pontos_conquista,
                "territorios": guild.territorios
            }
        
        players_data = {}
        for pid, player in self.jogadores.items():
            players_data[pid] = {
                "player_id": player.player_id,
                "name": player.name,
                "guild_id": player.guild_id,
                "guild_rank": player.guild_rank,
                "ouro": player.ouro,
                "pontos_conquista": player.pontos_conquista,
                "position": player.position
            }
        
        return WorldStateSchema(
            dia_noite=self.dia_noite,
            ciclo=self.ciclo,
            grid=grid_data,
            guildas=guilds_data,
            jogadores=players_data
        )
    
    async def log_event(self, event: GameEvent):
        """Log event and broadcast to all connected websockets"""
        async with self.lock:
            self.eventos.append(event)
            # Keep only last 100 events
            if len(self.eventos) > 100:
                self.eventos = self.eventos[-100:]
    
    def register_websocket(self, player_id: str, websocket):
        """Register websocket connection"""
        self.connected_websockets[player_id] = websocket
    
    def unregister_websocket(self, player_id: str):
        """Unregister websocket connection"""
        if player_id in self.connected_websockets:
            del self.connected_websockets[player_id]
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected websockets"""
        async with self.lock:
            disconnected = []
            for player_id, ws in self.connected_websockets.items():
                try:
                    await ws.send_json(message)
                except Exception:
                    disconnected.append(player_id)
            
            # Clean up disconnected
            for pid in disconnected:
                del self.connected_websockets[pid]


# Global singleton instance
world_state = WorldState()
