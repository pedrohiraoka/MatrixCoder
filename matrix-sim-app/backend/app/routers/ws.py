"""
WebSocket Router - Real-time communication for Matrix simulation.
Streams logs, state updates, and grid changes to connected clients.
"""
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any
from loguru import logger

from app.services.matrix_engine import Matrix
from app.services.ai_controller import AIController


router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket client {client_id} connected")
        
        # Send welcome message
        await self.send_personal_message(
            websocket,
            {
                "type": "welcome",
                "message": "Connected to Matrix simulation",
                "instruction": "Follow the white rabbit...",
            }
        )
    
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket client {client_id} disconnected")
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """Send a message to a specific client."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        disconnected = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to {client_id}: {e}")
                disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)


# Global connection manager
manager = ConnectionManager()


async def ws_subscriber(message: dict):
    """Callback for AI Controller to notify WebSocket clients."""
    await manager.broadcast(message)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time Matrix updates.
    
    Connects clients to receive:
    - State updates (tick, energy, agent counts)
    - Log entries (simulation events)
    - Grid updates (agent positions)
    - Error messages
    
    Client should send ping messages to keep connection alive.
    """
    # Generate client ID
    client_id = f"client_{id(websocket)}"
    
    await manager.connect(websocket, client_id)
    
    # Get or create controller
    if not hasattr(websocket_endpoint, "_controller"):
        from app.services.agent_manager import AgentManager
        matrix = Matrix()
        agent_manager = AgentManager(matrix)
        controller = AIController(matrix, agent_manager)
        websocket_endpoint._controller = controller
        
        # Register this WebSocket as a subscriber
        controller.add_subscriber(ws_subscriber)
    
    controller = websocket_endpoint._controller
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                if msg_type == "ping":
                    await manager.send_personal_message(
                        websocket,
                        {"type": "pong", "timestamp": message.get("timestamp")}
                    )
                
                elif msg_type == "get_state":
                    # Send current state immediately
                    await manager.send_personal_message(
                        websocket,
                        {
                            "type": "state_update",
                            "data": controller.get_status(),
                        }
                    )
                
                elif msg_type == "get_logs":
                    # Send recent logs
                    count = message.get("count", 50)
                    logs = controller.get_recent_logs(count)
                    await manager.send_personal_message(
                        websocket,
                        {
                            "type": "log_history",
                            "data": {"logs": logs, "count": len(logs)},
                        }
                    )
                
                elif msg_type == "get_grid":
                    # Send current grid state
                    grid = controller.matrix.get_grid_state()
                    await manager.send_personal_message(
                        websocket,
                        {
                            "type": "grid_update",
                            "data": {
                                "tick": grid.tick,
                                "dimensions": grid.dimensions,
                                "cells": [cell.dict() for cell in grid.cells],
                            },
                        }
                    )
                
                else:
                    await manager.send_personal_message(
                        websocket,
                        {
                            "type": "error",
                            "message": f"Unknown message type: {msg_type}",
                        }
                    )
            
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    websocket,
                    {"type": "error", "message": "Invalid JSON"}
                )
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(client_id)


@router.websocket("/ws/logs")
async def websocket_logs_only(websocket: WebSocket):
    """
    WebSocket endpoint for logs only.
    
    Lightweight connection that only receives log entries,
    useful for terminal/console views.
    """
    client_id = f"log_client_{id(websocket)}"
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    
    except Exception as e:
        logger.error(f"Log WebSocket error: {e}")
        manager.disconnect(client_id)
