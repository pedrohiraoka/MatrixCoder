# WebSocket Router - Real-time Log Streaming
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import asyncio
import json

router = APIRouter(prefix="/ws", tags=["WebSocket"])


# Store active connections
active_connections: list[WebSocket] = []


async def broadcast_log(message: dict):
    """Broadcast a log message to all connected clients"""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception:
            pass  # Connection might be closed


@router.websocket("/logs")
async def websocket_logs(websocket: WebSocket):
    """
    WebSocket endpoint for real-time log streaming.
    Connect to receive live simulation logs.
    """
    await websocket.accept()
    active_connections.append(websocket)

    try:
        # Send initial connection message
        await websocket.send_json(
            {
                "type": "connection",
                "message": "Connected to Matrix log stream",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Keep connection alive
        while True:
            # Wait for messages (heartbeat or config)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Echo back or process
                await websocket.send_json(
                    {
                        "type": "ack",
                        "received": data,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json(
                    {
                        "type": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print("Client disconnected from log stream")
    except Exception as e:
        if websocket in active_connections:
            active_connections.remove(websocket)
        print(f"WebSocket error: {e}")


@router.websocket("/stream")
async def websocket_stream(websocket: WebSocket):
    """
    General purpose WebSocket for streaming various data types.
    """
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            # Process and echo based on type
            msg_type = data.get("type", "unknown")

            response = {
                "type": f"{msg_type}_response",
                "status": "processed",
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
            }

            await websocket.send_json(response)

    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
    except Exception as e:
        if websocket in active_connections:
            active_connections.remove(websocket)
