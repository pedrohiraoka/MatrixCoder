"""
FastAPI main application for GvG Simulator
Setup, lifespan management, WebSocket handling, and REST endpoints
"""
import json
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import PlayerState, GuildState, PlayerCommand, EventType, GameEvent
from .state import world_state
from .database import init_db, log_event_to_db, log_transaction
from .game_engine import atualizar_mundo, evento_global_aleatorio


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    Initialize database and start async game loops on startup.
    """
    # Startup
    print("[Main] Starting GvG Simulator...")
    init_db()
    
    # Start async game loops as background tasks
    update_task = asyncio.create_task(atualizar_mundo())
    global_event_task = asyncio.create_task(evento_global_aleatorio())
    
    print("[Main] Game engine loops started")
    
    yield
    
    # Shutdown
    print("[Main] Shutting down...")
    update_task.cancel()
    global_event_task.cancel()
    
    try:
        await update_task
    except asyncio.CancelledError:
        pass
    
    try:
        await global_event_task
    except asyncio.CancelledError:
        pass


import asyncio

app = FastAPI(
    title="GvG Simulator",
    description="Guild Wars Simulator with Real-time WebSocket Updates",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "game": "GvG Simulator",
        "dia_noite": world_state.dia_noite,
        "ciclo": world_state.ciclo,
        "jogadores_online": len(world_state.jogadores),
        "guildas": len(world_state.guildas)
    }


@app.get("/painel_guerra")
async def painel_guerra():
    """
    Returns complete world state - the "view code" mechanic.
    Shows territory control, resources, guild stats.
    """
    return world_state.get_world_state().model_dump(mode='json')


@app.post("/player/create")
async def create_player(player_data: dict):
    """Create/register a new player"""
    player_id = player_data.get("player_id")
    name = player_data.get("name", "Anônimo")
    guild_id = player_data.get("guild_id")
    guild_rank = player_data.get("guild_rank", "Member")
    
    if not player_id:
        raise HTTPException(status_code=400, detail="player_id required")
    
    player = PlayerState(
        player_id=player_id,
        name=name,
        guild_id=guild_id,
        guild_rank=guild_rank
    )
    
    await world_state.add_player(player)
    
    # Log event
    event = GameEvent(
        event_type=EventType.SPAWN,
        message=f"{name} entrou no mundo!",
        data={"player_id": player_id}
    )
    await world_state.log_event(event)
    log_event_to_db(
        event_type="player_join",
        message=event.message,
        data={"player_id": player_id, "name": name}
    )
    
    # Broadcast to all
    await world_state.broadcast({
        "type": "player_joined",
        "event": event.model_dump(mode='json'),
        "player": player.model_dump(mode='json')
    })
    
    return {"status": "success", "player": player.model_dump(mode='json')}


@app.post("/guild/create")
async def create_guild(guild_data: dict):
    """Create a new guild"""
    guild_id = guild_data.get("guild_id")
    name = guild_data.get("name")
    leader_id = guild_data.get("leader_id")
    
    if not all([guild_id, name, leader_id]):
        raise HTTPException(status_code=400, detail="guild_id, name, and leader_id required")
    
    guild = GuildState(
        guild_id=guild_id,
        name=name,
        leader_id=leader_id,
        membros=[leader_id]
    )
    
    await world_state.add_guild(guild)
    
    # Update player guild info
    if leader_id in world_state.jogadores:
        world_state.jogadores[leader_id].guild_id = guild_id
        world_state.jogadores[leader_id].guild_rank = "Guild Master"
    
    event = GameEvent(
        event_type=EventType.WAR_DECLARED,
        message=f"Guilda {name} foi fundada por {leader_id}!",
        data={"guild_id": guild_id}
    )
    await world_state.log_event(event)
    log_event_to_db(
        event_type="guild_create",
        message=event.message,
        data={"guild_id": guild_id, "name": name}
    )
    
    await world_state.broadcast({
        "type": "guild_created",
        "event": event.model_dump(mode='json'),
        "guild": guild.model_dump(mode='json')
    })
    
    return {"status": "success", "guild": guild.model_dump(mode='json')}


@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str):
    """
    WebSocket endpoint for real-time communication.
    - Sends initial world state on connect
    - Listens for player commands
    - Broadcasts updates to all connected clients
    """
    await websocket.accept()
    
    # Register connection
    world_state.register_websocket(player_id, websocket)
    print(f"[WebSocket] Player {player_id} connected")
    
    # Send initial state
    initial_state = world_state.get_world_state().model_dump(mode='json')
    await websocket.send_json({
        "type": "initial_state",
        "state": initial_state,
        "player_id": player_id
    })
    
    # Get recent events
    async with world_state.lock:
        recent_events = [e.model_dump(mode='json') for e in world_state.eventos[-10:]]
    
    if recent_events:
        await websocket.send_json({
            "type": "recent_events",
            "events": recent_events
        })
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            await handle_player_command(player_id, message, websocket)
            
    except WebSocketDisconnect:
        print(f"[WebSocket] Player {player_id} disconnected")
        world_state.unregister_websocket(player_id)
        
        # Notify others
        event = GameEvent(
            event_type=EventType.BATTLE,
            message=f"Jogador {player_id} saiu do jogo",
            data={}
        )
        await world_state.broadcast({
            "type": "player_left",
            "event": event.model_dump(mode='json'),
            "player_id": player_id
        })
    except Exception as e:
        print(f"[WebSocket] Error with {player_id}: {e}")
        world_state.unregister_websocket(player_id)


async def handle_player_command(player_id: str, message: dict, websocket: WebSocket):
    """Handle incoming player commands"""
    command = message.get("command")
    payload = message.get("payload", {})
    
    if command == "move":
        direction = payload.get("direction")
        if direction in ["up", "down", "left", "right"]:
            success = await world_state.move_player(player_id, direction)
            
            if success:
                player = world_state.jogadores.get(player_id)
                if player:
                    await websocket.send_json({
                        "type": "move_result",
                        "success": True,
                        "position": player.position,
                        "player": player.model_dump(mode='json')
                    })
                    
                    # Broadcast position update
                    await world_state.broadcast({
                        "type": "player_moved",
                        "player_id": player_id,
                        "position": player.position
                    })
    
    elif command == "collect":
        recurso = await world_state.collect_resource(player_id)
        
        if recurso:
            player = world_state.jogadores.get(player_id)
            
            event = GameEvent(
                event_type=EventType.RESOURCE_COLLECTED,
                message=f"{player_id} coletou {recurso.value}!",
                data={"player_id": player_id, "recurso": recurso.value}
            )
            await world_state.log_event(event)
            log_transaction(
                player_id=player_id,
                amount=world_state._resource_value(recurso),
                transaction_type="earn",
                description=f"Coleta de {recurso.value}"
            )
            
            await websocket.send_json({
                "type": "collect_result",
                "success": True,
                "recurso": recurso.value,
                "ouro": player.ouro if player else 0,
                "player": player.model_dump(mode='json') if player else None
            })
            
            await world_state.broadcast({
                "type": "resource_collected",
                "event": event.model_dump(mode='json')
            })
    
    elif command == "strategy":
        # Only Guild Masters can use strategy commands
        if player_id not in world_state.jogadores:
            await websocket.send_json({
                "type": "error",
                "message": "Player not found"
            })
            return
        
        player = world_state.jogadores[player_id]
        
        if player.guild_rank != "Guild Master":
            await websocket.send_json({
                "type": "error",
                "message": "Apenas Guild Master pode usar comandos estratégicos!"
            })
            return
        
        strategy_type = payload.get("strategy_type")
        
        if strategy_type == "capture_territory":
            x = payload.get("target_x")
            y = payload.get("target_y")
            
            if x is not None and y is not None and player.guild_id:
                success = await world_state.capture_territory(
                    player_id, player.guild_id, x, y
                )
                
                if success:
                    event = GameEvent(
                        event_type=EventType.TERRITORY_CAPTURED,
                        message=f"{player.name} capturou território em ({x}, {y})!",
                        data={"player_id": player_id, "x": x, "y": y}
                    )
                    await world_state.log_event(event)
                    log_transaction(
                        player_id=player_id,
                        amount=-100,
                        transaction_type="spend",
                        description="Captura de território",
                        guild_id=player.guild_id
                    )
                    
                    await websocket.send_json({
                        "type": "strategy_result",
                        "success": True,
                        "action": "territory_captured"
                    })
                    
                    await world_state.broadcast({
                        "type": "territory_captured",
                        "event": event.model_dump(mode='json')
                    })
        
        elif strategy_type == "build_structure":
            x = payload.get("target_x")
            y = payload.get("target_y")
            structure_type = payload.get("structure_type", "torre")
            
            if x is not None and y is not None and player.guild_id:
                success = await world_state.build_structure(
                    player_id, player.guild_id, x, y, structure_type
                )
                
                if success:
                    event = GameEvent(
                        event_type=EventType.STRUCTURE_BUILT,
                        message=f"{player.name} construiu {structure_type} em ({x}, {y})!",
                        data={"player_id": player_id, "estrutura": structure_type}
                    )
                    await world_state.log_event(event)
                    log_transaction(
                        player_id=player_id,
                        amount=-200,
                        transaction_type="spend",
                        description=f"Construção de {structure_type}",
                        guild_id=player.guild_id
                    )
                    
                    await websocket.send_json({
                        "type": "strategy_result",
                        "success": True,
                        "action": "structure_built"
                    })
                    
                    await world_state.broadcast({
                        "type": "structure_built",
                        "event": event.model_dump(mode='json')
                    })
        
        elif strategy_type == "declare_war":
            target_guild = payload.get("target_guild")
            
            event = GameEvent(
                event_type=EventType.WAR_DECLARED,
                message=f"⚔️ {player.name} declarou guerra para {target_guild or 'todos'}!",
                data={"player_id": player_id, "alvo": target_guild}
            )
            await world_state.log_event(event)
            log_event_to_db(
                event_type="war_declared",
                message=event.message,
                data={"declarer": player_id, "target": target_guild}
            )
            
            await websocket.send_json({
                "type": "strategy_result",
                "success": True,
                "action": "war_declared"
            })
            
            await world_state.broadcast({
                "type": "war_declared",
                "event": event.model_dump(mode='json')
            })
