"""Roteadores de WebSocket para comunicação em tempo real."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import logging

from app.services.agent_manager import AgentManager
from app.models import LogEntry

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket para streaming de estado e logs da simulação.
    
    Envia automaticamente o estado atual ao conectar.
    Broadcasts são enviados a cada tick da simulação.
    """
    manager = AgentManager.get_instance()
    
    await websocket.accept()
    await manager.adicionar_websocket(websocket)
    
    logger.info(f"WebSocket conectado: {websocket.client}")
    
    # Envia estado inicial
    await manager.broadcast_estado()
    
    try:
        while True:
            # Recebe mensagens do cliente (comandos, etc.)
            data = await websocket.receive_json()
            
            # Processa comandos recebidos
            tipo = data.get("type")
            
            if tipo == "PING":
                await websocket.send_json({"type": "PONG"})
                
            elif tipo == "GET_LOGS":
                limite = data.get("limite", 50)
                logs = manager.obter_logs_recentes(limite)
                await websocket.send_json({
                    "type": "LOGS_BATCH",
                    "payload": [log.dict() for log in logs],
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket desconectado: {websocket.client}")
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
    finally:
        await manager.remover_websocket(websocket)
