"""
API Module - FastAPI Server

Expõe endpoints REST e WebSocket para:
- Controle da simulação (start, stop, reset)
- Estado em tempo real dos agentes
- Métricas de divergência
- Logs e exportação
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio

from .engine import get_engine, SimulationEngine
from .semantics import initialize_semantics

# Criar aplicação FastAPI
app = FastAPI(
    title="Identity Emergence Lab API",
    description="API para controle e monitoramento da simulação Tachikoma",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelos Pydantic
class SpeedRequest(BaseModel):
    multiplier: float = 1.0

class ResetRequest(BaseModel):
    preserve_ghosts: bool = True
    full_reset: bool = False

class ExportRequest(BaseModel):
    filepath: Optional[str] = None


# Endpoints de Controle
@app.post("/start")
async def start_simulation():
    """Inicia a simulação."""
    engine = get_engine()
    await engine.start()
    return {"status": "started", "message": "Simulação iniciada"}

@app.post("/stop")
async def stop_simulation():
    """Para a simulação."""
    engine = get_engine()
    await engine.stop()
    return {"status": "stopped", "message": "Simulação pausada"}

@app.post("/speed")
async def set_speed(request: SpeedRequest):
    """Define velocidade da simulação."""
    engine = get_engine()
    engine.set_speed(request.multiplier)
    return {
        "status": "success",
        "speed_multiplier": request.multiplier
    }

@app.post("/cycle")
async def run_single_cycle():
    """Executa um único ciclo (modo passo-a-passo)."""
    engine = get_engine()
    await engine.run_single_cycle()
    return {"status": "cycle_executed", "cycle": engine.current_cycle}

@app.post("/reset")
async def reset_simulation(request: ResetRequest = None):
    """Reseta a simulação."""
    engine = get_engine()
    
    if request and request.full_reset:
        engine.reset_all()
        return {"status": "full_reset", "message": "Reset completo"}
    else:
        preserve = request.preserve_ghosts if request else True
        engine.reset_network(preserve_ghosts=preserve)
        return {
            "status": "network_reset",
            "preserve_ghosts": preserve,
            "message": "Rede resetada"
        }


# Endpoints de Estado
@app.get("/state")
async def get_state():
    """Retorna estado completo da simulação."""
    engine = get_engine()
    return engine.get_state()

@app.get("/agent/{agent_id}")
async def get_agent_state(agent_id: int):
    """Retorna estado de um agente específico."""
    engine = get_engine()
    
    if not 0 <= agent_id < 10:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    return engine.get_agent_state(agent_id)

@app.get("/agents")
async def get_all_agents():
    """Retorna estado de todos os agentes."""
    engine = get_engine()
    return {
        "num_agents": len(engine.agents),
        "agents": [agent.get_state() for agent in engine.agents]
    }

@app.get("/divergence")
async def get_divergence_metrics():
    """Retorna métricas de divergência entre agentes."""
    engine = get_engine()
    return engine.get_divergence_metrics()

@app.get("/events")
async def get_events(limit: int = 50):
    """Retorna eventos recentes."""
    engine = get_engine()
    events = engine.event_history[-limit:]
    return {
        "count": len(events),
        "events": [e.to_dict() for e in events]
    }

@app.get("/reflections")
async def get_reflections(limit: int = 10):
    """Retorna reflexões recentes."""
    engine = get_engine()
    reflections = engine.reflection_logs[-limit:]
    return {
        "count": len(reflections),
        "reflections": reflections
    }


# Endpoints de Memória
@app.get("/memory/collective/stats")
async def get_collective_stats():
    """Retorna estatísticas da memória coletiva."""
    engine = get_engine()
    return engine.collective_memory.get_stats()

@app.get("/memory/collective/facts")
async def get_collective_facts(limit: int = 100, offset: int = 0):
    """Retorna fatos da memória coletiva."""
    engine = get_engine()
    facts = engine.collective_memory.get_facts(limit, offset)
    return {
        "count": len(facts),
        "facts": facts
    }

@app.get("/memory/ghost/{agent_id}")
async def get_ghost_memory(agent_id: int):
    """Retorna memória Ghost de um agente."""
    engine = get_engine()
    
    if not 0 <= agent_id < 10:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    agent = engine.agents[agent_id]
    return agent.ghost.export()


# Endpoints de Exportação
@app.post("/export")
async def export_logs(request: ExportRequest = None):
    """Exporta logs da simulação."""
    engine = get_engine()
    
    filepath = request.filepath if request else None
    exported_path = engine.export_logs(filepath)
    
    return {
        "status": "success",
        "filepath": exported_path,
        "message": f"Logs exportados para {exported_path}"
    }


# Endpoint de Saúde
@app.get("/health")
async def health_check():
    """Verifica saúde da API."""
    return {
        "status": "healthy",
        "service": "Identity Emergence Lab API"
    }


# Inicialização
@app.on_event("startup")
async def startup_event():
    """Inicializa componentes no startup."""
    print("🚀 Iniciando Identity Emergence Lab API...")
    
    # Inicializar sistema semântico
    initialize_semantics()
    
    # Pré-carregar engine
    get_engine()
    
    print("✅ API pronta!")


@app.on_event("shutdown")
async def shutdown_event():
    """Limpeza no shutdown."""
    engine = get_engine()
    await engine.stop()
    print("👋 API encerrada")
