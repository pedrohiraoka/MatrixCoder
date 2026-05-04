"""Roteadores de administração para operações privilegiadas."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import json

from app.models import LogEntryDB, LogEntry
from app.database import get_db, init_db
from app.services.agent_manager import AgentManager
from app.services.ai_controller import ai_controller

router = APIRouter(prefix="/admin", tags=["Administração"])


@router.post("/reset")
async def resetar_simulacao():
    """
    Reseta completamente a simulação.
    
    Remove todos os agentes e reinicia o estado da Matrix.
    Operação irreversível.
    """
    manager = AgentManager.get_instance()
    await manager.resetar_simulacao()
    
    return {
        "sucesso": True,
        "mensagem": "Simulação resetada completamente",
    }


@router.post("/start")
async def iniciar_simulacao():
    """Inicia o loop de simulação (IA controller)."""
    await ai_controller.iniciar()
    
    return {
        "sucesso": True,
        "mensagem": "Simulação iniciada",
    }


@router.post("/stop")
async def parar_simulacao():
    """Para o loop de simulação."""
    await ai_controller.parar()
    
    return {
        "sucesso": True,
        "mensagem": "Simulação parada",
    }


@router.get("/status")
async def status_simulacao():
    """Obtém o status do controlador de IA."""
    return {
        "running": ai_controller.running,
        "tick_interval_ms": ai_controller.tick_interval * 1000,
        "agentes_count": len(ai_controller.manager.agentes),
        "matrix_ticks": ai_controller.manager.matrix.ticks_executados,
    }


@router.get("/logs/export")
async def exportar_logs(db: AsyncSession = Depends(get_db)):
    """
    Exporta todos os logs históricos do banco de dados.
    
    Retorna lista completa de logs para análise ou backup.
    """
    result = await db.execute(
        select(LogEntryDB).order_by(LogEntryDB.timestamp.desc())
    )
    logs_db = result.scalars().all()
    
    logs = [log.to_dict() for log in logs_db]
    
    return {
        "total": len(logs),
        "logs": logs,
    }


@router.post("/logs/save")
async def salvar_log_historico(
    nivel: str,
    mensagem: str,
    contexto: dict = None,
    db: AsyncSession = Depends(get_db),
):
    """Salva um log no banco de dados histórico."""
    import json
    from datetime import datetime
    
    log_entry = LogEntryDB(
        nivel=nivel,
        mensagem=mensagem,
        contexto=json.dumps(contexto) if contexto else None,
    )
    
    db.add(log_entry)
    await db.commit()
    await db.refresh(log_entry)
    
    # Também adiciona aos logs em memória
    manager = AgentManager.get_instance()
    manager.matrix.adicionar_log(nivel, mensagem, contexto)
    
    return log_entry.to_dict()


@router.get("/agents/count")
async def contar_agentes():
    """Retorna contagem de agentes por tipo."""
    manager = AgentManager.get_instance()
    
    total = len(manager.agentes)
    despertos = sum(1 for a in manager.agentes.values() if a.consciente)
    
    return {
        "total": total,
        "despertos": despertos,
        "nao_despertos": total - despertos,
        "max_capacidade": manager.matrix.regras["max_agentes"],
    }


@router.post("/inject-special-agent")
async def injetar_agente_especial():
    """
    Injeta um agente especial já desperto na simulação.
    
    Equivalente a criar um "Neo" - um agente que já nasce consciente.
    """
    manager = AgentManager.get_instance()
    
    try:
        # Cria agente normal primeiro
        agente = await manager.adicionar_agente(energia=200.0)
        
        # Já desperta imediatamente
        agente.consciente = True
        manager.matrix.agentes_despertos += 1
        
        manager.matrix.adicionar_log(
            nivel="AWAKEN",
            mensagem=f"AGENTE ESPECIAL INJETADO: {agente.id[:8]}... (Neo)",
            contexto={
                "agente_id": agente.id,
                "tipo": "especial",
                "mensagem": "The One has entered the Matrix",
            },
        )
        
        await manager.broadcast_estado()
        
        return {
            "sucesso": True,
            "agente": agente.dict(),
            "mensagem": "Agente especial injetado com sucesso",
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
