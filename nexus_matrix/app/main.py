"""
Nexus Matrix - API FastAPI
Endpoints para a aplicação web e controle da simulação
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime

from app.config import API_CONFIG, STATIC_DIR, TEMPLATES_DIR
from app.database import init_database, seed_initial_agents
from app.embeddings import initialize_embeddings
from app.models import AgentManager, GroupManager
from app.simulation import simulation_engine

# Inicializar FastAPI
app = FastAPI(
    title=API_CONFIG["title"],
    version=API_CONFIG["version"],
    description=API_CONFIG["description"]
)

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Configurar templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Estado global da simulação
simulation_task: Optional[asyncio.Task] = None


class ThemeInjection(BaseModel):
    theme: str
    description: Optional[str] = ""


class AgentAction(BaseModel):
    agent_id: int
    action: str  # "join_group", "leave_group", "create_group"
    group_id: Optional[int] = None
    group_name: Optional[str] = None
    group_theme: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Inicializa o banco de dados e embeddings na inicialização"""
    print("Inicializando Nexus Matrix...")
    init_database()
    seed_initial_agents()
    initialize_embeddings()
    simulation_engine.start_simulation()
    print("Nexus Matrix inicializada com sucesso!")
    
    # Iniciar loop de simulação em background
    asyncio.create_task(run_simulation_loop())


async def run_simulation_loop():
    """Loop contínuo da simulação em background"""
    while True:
        try:
            await simulation_engine.run_tick()
        except Exception as e:
            print(f"Erro no tick da simulação: {e}")
            await asyncio.sleep(1)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página principal"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard")
async def get_dashboard():
    """Retorna estado atual do dashboard"""
    state = simulation_engine.get_current_state()
    
    # Adicionar detalhes
    agents = AgentManager.get_all_agents()
    groups = GroupManager.get_all_groups()
    
    state["agents"] = [
        {
            "id": a.id,
            "name": a.name,
            "type": a.agent_type,
            "icon": a.icon,
            "color": a.color,
            "group_id": a.current_group_id,
            "anomaly_score": a.anomaly_score,
            "energy_level": a.energy_level
        }
        for a in agents
    ]
    
    state["groups"] = [
        {
            "id": g.id,
            "name": g.name,
            "theme": g.theme,
            "is_zion": g.is_zion,
            "is_hidden": g.is_hidden,
            "member_count": g.member_count,
            "cohesion_score": g.cohesion_score,
            "energy_production": g.energy_production
        }
        for g in groups
    ]
    
    return state


@app.get("/agents")
async def get_agents():
    """Lista todos os agentes"""
    agents = AgentManager.get_all_agents()
    return {
        "count": len(agents),
        "agents": [
            {
                "id": a.id,
                "name": a.name,
                "type": a.agent_type,
                "role": a.role_description,
                "beliefs": a.beliefs,
                "interests": a.interests,
                "group_id": a.current_group_id,
                "anomaly_score": a.anomaly_score,
                "energy_level": a.energy_level,
                "icon": a.icon,
                "color": a.color
            }
            for a in agents
        ]
    }


@app.get("/agents/{agent_id}")
async def get_agent(agent_id: int):
    """Obtém detalhes de um agente específico"""
    agent = AgentManager.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    return {
        "id": agent.id,
        "name": agent.name,
        "type": agent.agent_type,
        "role": agent.role_description,
        "beliefs": agent.beliefs,
        "interests": agent.interests,
        "group_id": agent.current_group_id,
        "anomaly_score": agent.anomaly_score,
        "energy_level": agent.energy_level,
        "icon": agent.icon,
        "color": agent.color
    }


@app.get("/groups")
async def get_groups():
    """Lista todos os grupos ativos"""
    groups = GroupManager.get_all_groups()
    result = []
    
    for g in groups:
        members = GroupManager.get_group_members(g.id)
        result.append({
            "id": g.id,
            "name": g.name,
            "theme": g.theme,
            "description": g.description,
            "is_zion": g.is_zion,
            "is_hidden": g.is_hidden,
            "member_count": len(members),
            "members": [{"id": m.id, "name": m.name, "type": m.agent_type} for m in members],
            "cohesion_score": g.cohesion_score,
            "energy_production": g.energy_production
        })
    
    return {"count": len(result), "groups": result}


@app.get("/messages/recent")
async def get_recent_messages(limit: int = 50):
    """Obtém mensagens recentes"""
    conn = __import__('app.database', fromlist=['get_db_connection']).get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.*, a.name as agent_name, a.agent_type, g.name as group_name
        FROM messages m
        JOIN agents a ON m.agent_id = a.id
        LEFT JOIN groups g ON m.group_id = g.id
        ORDER BY m.created_at DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return {
        "count": len(rows),
        "messages": [
            {
                "id": row['id'],
                "agent_name": row['agent_name'],
                "agent_type": row['agent_type'],
                "group_name": row['group_name'],
                "content": row['content'],
                "theme": row['theme'],
                "energy_contribution": row['energy_contribution'],
                "is_anomalous": bool(row['is_anomalous']),
                "created_at": row['created_at']
            }
            for row in rows
        ]
    }


@app.get("/events/recent")
async def get_recent_events(limit: int = 20):
    """Obtém eventos recentes da simulação"""
    conn = __import__('app.database', fromlist=['get_db_connection']).get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM simulation_events
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return {
        "count": len(rows),
        "events": [
            {
                "id": row['id'],
                "type": row['event_type'],
                "title": row['title'],
                "description": row['description'],
                "theme": row['theme'],
                "injected_by_central_ai": bool(row['injected_by_central_ai']),
                "impact_score": row['impact_score'],
                "tick": row['tick_number'],
                "created_at": row['created_at']
            }
            for row in rows
        ]
    }


@app.get("/metrics/history")
async def get_metrics_history(ticks: int = 100):
    """Obtém histórico de métricas"""
    conn = __import__('app.database', fromlist=['get_db_connection']).get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM simulation_metrics
        ORDER BY tick_number DESC
        LIMIT ?
    """, (ticks,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Inverter para ordem cronológica
    rows = list(reversed(rows))
    
    return {
        "count": len(rows),
        "metrics": [
            {
                "tick": row['tick_number'],
                "total_energy": row['total_energy'],
                "avg_cohesion": row['avg_cohesion'],
                "anomaly_count": row['anomaly_count'],
                "group_count": row['group_count'],
                "zion_active": bool(row['zion_active']),
                "timestamp": row['timestamp']
            }
            for row in rows
        ]
    }


@app.post("/simulation/inject-theme")
async def inject_theme(theme_data: ThemeInjection):
    """Injeta manualmente um tema na simulação"""
    conn = __import__('app.database', fromlist=['get_db_connection']).get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO simulation_events 
        (event_type, title, description, theme, injected_by_central_ai, impact_score, tick_number)
        VALUES (?, ?, ?, ?, 1, ?, ?)
    """, (
        "manual_injection",
        f"Tema Manual: {theme_data.theme}",
        theme_data.description or "Tema injetado manualmente por usuário",
        theme_data.theme,
        random.uniform(0.7, 1.0),
        simulation_engine.tick_number
    ))
    conn.commit()
    conn.close()
    
    simulation_engine.current_theme = theme_data.theme
    
    return {
        "success": True,
        "message": f"Tema '{theme_data.theme}' injetado com sucesso",
        "tick": simulation_engine.tick_number
    }


@app.post("/simulation/action")
async def perform_agent_action(action: AgentAction):
    """Executa ação de um agente"""
    agent = AgentManager.get_agent_by_id(action.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    if action.action == "join_group" and action.group_id:
        GroupManager.join_group(action.agent_id, action.group_id)
        return {"success": True, "message": f"{agent.name} entrou no grupo"}
    
    elif action.action == "leave_group":
        GroupManager.leave_group(action.agent_id)
        return {"success": True, "message": f"{agent.name} saiu do grupo"}
    
    elif action.action == "create_group" and action.group_name:
        group_id = GroupManager.create_group(
            name=action.group_name,
            theme=action.group_theme or "Geral",
            description=f"Criado por {agent.name}"
        )
        GroupManager.join_group(action.agent_id, group_id)
        return {"success": True, "message": f"Grupo '{action.group_name}' criado", "group_id": group_id}
    
    raise HTTPException(status_code=400, detail="Ação inválida")


@app.get("/graph/data")
async def get_graph_data():
    """Retorna dados para o grafo social (D3.js)"""
    agents = AgentManager.get_all_agents()
    groups = GroupManager.get_all_groups()
    
    # Nós (agentes)
    nodes = []
    for agent in agents:
        nodes.append({
            "id": agent.id,
            "name": agent.name,
            "type": agent.agent_type,
            "icon": agent.icon,
            "color": agent.color,
            "group": agent.current_group_id,
            "anomaly": agent.anomaly_score,
            "radius": 8 + (agent.anomaly_score * 10)  # Anomalias maiores têm raio maior
        })
    
    # Arestas (conexões baseadas em grupos compartilhados)
    links = []
    for i, agent1 in enumerate(agents):
        for agent2 in agents[i+1:]:
            # Se estão no mesmo grupo, criar conexão
            if agent1.current_group_id and agent1.current_group_id == agent2.current_group_id:
                affinity = agent1.calculate_affinity(agent2)
                links.append({
                    "source": agent1.id,
                    "target": agent2.id,
                    "strength": affinity,
                    "type": "alliance"
                })
            # Se têm tipos opostos, criar conexão de conflito
            elif (agent1.agent_type == "controller" and agent2.agent_type in ["exile", "human_emulator"]) or \
                 (agent2.agent_type == "controller" and agent1.agent_type in ["exile", "human_emulator"]):
                links.append({
                    "source": agent1.id,
                    "target": agent2.id,
                    "strength": 0.3,
                    "type": "conflict"
                })
    
    return {
        "nodes": nodes,
        "links": links,
        "groups": [
            {"id": g.id, "name": g.name, "is_zion": g.is_zion}
            for g in groups
        ]
    }


@app.get("/zion/status")
async def get_zion_status():
    """Retorna status do Zion Digital"""
    zion = GroupManager.get_zion_group()
    
    if not zion:
        return {
            "exists": False,
            "status": "inactive",
            "message": "Zion Digital ainda não emergiu"
        }
    
    members = GroupManager.get_group_members(zion.id)
    
    return {
        "exists": True,
        "status": "active" if len(members) > 0 else "dormant",
        "name": zion.name,
        "theme": zion.theme,
        "member_count": len(members),
        "members": [{"id": m.id, "name": m.name, "type": m.agent_type} for m in members],
        "is_hidden": zion.is_hidden,
        "cohesion": zion.cohesion_score,
        "energy": zion.energy_production
    }


# Import random para o endpoint de inject-theme
import random


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
