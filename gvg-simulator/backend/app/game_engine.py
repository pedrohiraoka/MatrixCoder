"""
Game engine with async loop for world updates
Handles day/night cycle, spawns, events, and WebSocket broadcasts
"""
import asyncio
import random
from datetime import datetime

from .models import ResourceType, GameEvent, EventType
from .state import world_state
from .database import log_event_to_db


async def atualizar_mundo():
    """
    Main async game loop.
    Runs every 3 seconds to update world state.
    Manages day/night cycle, resource spawns, danger spawns, and event broadcasting.
    """
    print("[Game Engine] World update loop started")
    
    while True:
        try:
            # Wait 3 seconds between updates
            await asyncio.sleep(3)
            
            # Toggle day/night every 10 cycles (~30 seconds)
            if world_state.ciclo % 10 == 0:
                await world_state.toggle_day_night()
                
                # Broadcast day/night change
                event = GameEvent(
                    event_type=EventType.DAY_NIGHT_CYCLE,
                    message=f"O mundo agora está em {world_state.dia_noite}! Ciclo {world_state.ciclo}",
                    data={"dia_noite": world_state.dia_noite, "ciclo": world_state.ciclo}
                )
                await world_state.log_event(event)
                await world_state.broadcast({
                    "type": "world_update",
                    "event": event.model_dump(mode='json'),
                    "state": world_state.get_world_state().model_dump(mode='json')
                })
                
                # Log to database
                log_event_to_db(
                    event_type=EventType.DAY_NIGHT_CYCLE.value,
                    message=event.message,
                    data=event.data
                )
            
            # Random resource spawn (20% chance per cycle)
            if random.random() < 0.2:
                x = random.randint(0, world_state.GRID_SIZE - 1)
                y = random.randint(0, world_state.GRID_SIZE - 1)
                resource = random.choice(list(ResourceType))
                
                if await world_state.spawn_resource(x, y, resource):
                    event = GameEvent(
                        event_type=EventType.SPAWN,
                        message=f"Novo recurso {resource.value} apareceu em ({x}, {y})!",
                        data={"x": x, "y": y, "recurso": resource.value}
                    )
                    await world_state.log_event(event)
                    await world_state.broadcast({
                        "type": "resource_spawn",
                        "event": event.model_dump(mode='json'),
                        "position": {"x": x, "y": y}
                    })
                    log_event_to_db(
                        event_type=EventType.SPAWN.value,
                        message=event.message,
                        data=event.data
                    )
            
            # Random danger spawn (10% chance per cycle, higher at night)
            danger_chance = 0.15 if world_state.dia_noite == "noite" else 0.08
            if random.random() < danger_chance:
                x = random.randint(0, world_state.GRID_SIZE - 1)
                y = random.randint(0, world_state.GRID_SIZE - 1)
                danger = random.choice(["monstro", "armadilha", "inimigo", "chefe"])
                
                if await world_state.spawn_danger(x, y, danger):
                    event = GameEvent(
                        event_type=EventType.SPAWN,
                        message=f"⚠️ {danger.upper()} apareceu em ({x}, {y})!",
                        data={"x": x, "y": y, "perigo": danger}
                    )
                    await world_state.log_event(event)
                    await world_state.broadcast({
                        "type": "danger_spawn",
                        "event": event.model_dump(mode='json'),
                        "position": {"x": x, "y": y}
                    })
                    log_event_to_db(
                        event_type=EventType.SPAWN.value,
                        message=event.message,
                        data=event.data
                    )
            
            # Periodic world state broadcast (every 5 cycles)
            if world_state.ciclo % 5 == 0:
                await world_state.broadcast({
                    "type": "world_state",
                    "state": world_state.get_world_state().model_dump(mode='json')
                })
            
        except Exception as e:
            print(f"[Game Engine] Error in update loop: {e}")
            await asyncio.sleep(1)  # Prevent tight error loop


async def evento_global_aleatorio():
    """
    Occasional global events (every ~60 seconds)
    Adds meta-game excitement and discovery
    """
    print("[Game Engine] Global event scheduler started")
    
    eventos_possiveis = [
        {
            "nome": "Chuva de Ouro",
            "mensagem": "✨ Uma chuva de ouro cai sobre o reino! Todos ganham +50 ouro.",
            "efeito": lambda: aplicar_bonus_global(50)
        },
        {
            "nome": "Invasão de Monstros",
            "mensagem": "⚔️ Monstros invadem territórios desprotegidos!",
            "efeito": lambda: spawn_invasao()
        },
        {
            "nome": "Descoberta Antiga",
            "mensagem": "📜 Ruínas antigas foram descobertas! Recursos extras spawnam.",
            "efeito": lambda: spawn_recursos_extras()
        },
        {
            "nome": "Bênção dos Deuses",
            "mensagem": "🙏 Os deuses abençoam todas as guildas! +10 pontos de conquista.",
            "efeito": lambda: bonus_conquista()
        }
    ]
    
    while True:
        await asyncio.sleep(60)  # Every 60 seconds
        
        try:
            evento = random.choice(eventos_possiveis)
            
            event = GameEvent(
                event_type=EventType.BATTLE,  # Using BATTLE as generic event type
                message=evento["mensagem"],
                data={"evento_global": evento["nome"]}
            )
            
            await world_state.log_event(event)
            await world_state.broadcast({
                "type": "global_event",
                "event": event.model_dump(mode='json')
            })
            
            log_event_to_db(
                event_type="global_event",
                message=evento["mensagem"],
                data={"evento": evento["nome"]}
            )
            
            # Apply effect
            await evento["efeito"]()
            
        except Exception as e:
            print(f"[Game Engine] Error in global event: {e}")


async def aplicar_bonus_global(valor: int):
    """Apply gold bonus to all players"""
    async with world_state.lock:
        for player in world_state.jogadores.values():
            player.ouro += valor


async def spawn_invasao():
    """Spawn multiple dangers across the map"""
    for _ in range(5):
        x = random.randint(0, world_state.GRID_SIZE - 1)
        y = random.randint(0, world_state.GRID_SIZE - 1)
        await world_state.spawn_danger(x, y, "invasor")


async def spawn_recursos_extras():
    """Spawn extra resources"""
    for _ in range(10):
        x = random.randint(0, world_state.GRID_SIZE - 1)
        y = random.randint(0, world_state.GRID_SIZE - 1)
        resource = random.choice([ResourceType.GOLD, ResourceType.IRON])
        await world_state.spawn_resource(x, y, resource)


async def bonus_conquista():
    """Give conquest points to all guilds"""
    async with world_state.lock:
        for guild in world_state.guildas.values():
            guild.pontos_conquista += 10
