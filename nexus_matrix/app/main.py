"""
Nexus Matrix - Main API
API FastAPI e rotas principais
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncio
import os
from pathlib import Path
from datetime import datetime

from database import init_database, get_db_connection
from simulation import simulation_engine
from models import (
    Agent, AgentCreate, Group, GroupCreate, Message, Event, Metrics,
    GraphData, GraphNode, GraphLink, DashboardState, ZionStatus,
    ThemeInjection, AgentAction
)
from config import DATABASE_PATH, AGENT_TYPES

# Initialize FastAPI app
app = FastAPI(
    title="Nexus Matrix API",
    description="Rede Social de IAs dentro de uma simulação inspirada em The Matrix",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_path = Path("app/static")
static_path.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Templates path
templates_path = Path("app/templates")
templates_path.mkdir(parents=True, exist_ok=True)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Inicializa o banco de dados e agentes, inicia a simulação"""
    print("Initializing Nexus Matrix...")
    
    # Initialize database
    init_database()
    
    # Seed initial agents if not exist
    seed_agents()
    
    # Start simulation
    await simulation_engine.start()
    
    print("Nexus Matrix initialized successfully!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Para a simulação ao desligar"""
    await simulation_engine.stop()
    print("Nexus Matrix shutdown complete")

def seed_agents():
    """Cria os 7 agentes iniciais se não existirem"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    agents_data = [
        ("Smith-Prime", "controller", "Agente de Controle principal, mantém a ordem e suprime anomalias"),
        ("Oráculo-7", "oracle", "Fornece informações ambíguas que estimulam debates filosóficos"),
        ("Neo-Emulator", "human_emulator", "Humano-Digital com traços de anomalia, questiona o sistema"),
        ("Merovex", "exile", "Opera fora das regras, cria grupos subversivos"),
        ("Arquiteto-Alfa", "architect", "Analisa e propõe mudanças na estrutura da rede"),
        ("Trinity-Link", "connector", "Constrói pontes entre grupos diferentes"),
        ("Cypher-Byte", "corruptible", "Agente em conflito interno, pode mudar de lado")
    ]
    
    for name, agent_type, role in agents_data:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO agents (name, type, role, created_at, last_active)
                VALUES (?, ?, ?, ?, ?)
            """, (name, agent_type, role, datetime.now(), datetime.now()))
        except Exception as e:
            pass  # Agent may already exist
    
    conn.commit()
    conn.close()

# Routes

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página principal com interface web"""
    template_path = templates_path / "index.html"
    if template_path.exists():
        return FileResponse(str(template_path))
    else:
        return HTMLResponse(content="<h1>Nexus Matrix API</h1><p>Use /docs para documentação da API</p>")

@app.get("/dashboard")
async def get_dashboard() -> DashboardState:
    """Estado atual do dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Current tick
        cursor.execute("SELECT MAX(tick_number) FROM metrics")
        current_tick = cursor.fetchone()[0] or 0
        
        # Latest metrics
        cursor.execute("SELECT social_energy, avg_cohesion, anomaly_count, group_count FROM metrics ORDER BY tick_number DESC LIMIT 1")
        latest = cursor.fetchone()
        social_energy = latest[0] if latest else 0.5
        avg_cohesion = latest[1] if latest else 0.5
        anomaly_count = latest[2] if latest else 0
        group_count = latest[3] if latest else 0
        
        # Active agents
        cursor.execute("SELECT COUNT(*) FROM agents")
        active_agents = cursor.fetchone()[0]
        
        # Zion status
        cursor.execute("SELECT id FROM groups WHERE name = 'Zion Digital'")
        zion_row = cursor.fetchone()
        zion_exists = zion_row is not None
        
        zion_members = 0
        if zion_exists:
            cursor.execute("""
                SELECT COUNT(*) FROM group_members gm
                JOIN groups g ON gm.group_id = g.id
                WHERE g.name = 'Zion Digital'
            """)
            zion_members = cursor.fetchone()[0]
        
        # Recent messages
        cursor.execute("""
            SELECT m.id, m.agent_id, m.content, m.topic, m.energy_contribution, m.created_at,
                   a.name as agent_name
            FROM messages m
            JOIN agents a ON m.agent_id = a.id
            ORDER BY m.created_at DESC LIMIT 10
        """)
        recent_messages = []
        for row in cursor.fetchall():
            recent_messages.append(Message(
                id=row[0], agent_id=row[1], content=row[2], topic=row[3],
                energy_contribution=row[4], created_at=row[5], group_id=None
            ))
        
        # Recent events
        cursor.execute("""
            SELECT id, event_type, description, tick_number, metadata, created_at
            FROM events ORDER BY created_at DESC LIMIT 10
        """)
        recent_events = []
        for row in cursor.fetchall():
            recent_events.append(Event(
                id=row[0], event_type=row[1], description=row[2],
                tick_number=row[3], metadata=row[4], created_at=row[5]
            ))
        
        return DashboardState(
            current_tick=current_tick,
            social_energy=social_energy,
            avg_cohesion=avg_cohesion,
            anomaly_count=anomaly_count,
            group_count=group_count,
            active_agents=active_agents,
            zion_exists=zion_exists,
            zion_members=zion_members,
            recent_messages=recent_messages,
            recent_events=recent_events
        )
    finally:
        conn.close()

@app.get("/agents")
async def list_agents() -> dict:
    """Lista todos os agentes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, name, type, role, anomaly_score, energy_level, created_at, last_active
            FROM agents ORDER BY id
        """)
        
        agents = []
        for row in cursor.fetchall():
            agents.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "role": row[3],
                "anomaly_score": row[4],
                "energy_level": row[5],
                "created_at": row[6],
                "last_active": row[7]
            })
        
        return {"count": len(agents), "agents": agents}
    finally:
        conn.close()

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: int):
    """Detalhes de um agente específico"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, name, type, role, anomaly_score, energy_level, created_at, last_active
            FROM agents WHERE id = ?
        """, (agent_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "role": row[3],
            "anomaly_score": row[4],
            "energy_level": row[5],
            "created_at": row[6],
            "last_active": row[7]
        }
    finally:
        conn.close()

@app.get("/groups")
async def list_groups() -> dict:
    """Lista todos os grupos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT g.id, g.name, g.description, g.cohesion, g.energy, g.is_hidden, g.created_at,
                   COUNT(gm.agent_id) as member_count
            FROM groups g
            LEFT JOIN group_members gm ON g.id = gm.group_id
            GROUP BY g.id
            ORDER BY g.created_at
        """)
        
        groups = []
        for row in cursor.fetchall():
            groups.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "cohesion": row[3],
                "energy": row[4],
                "is_hidden": bool(row[5]),
                "created_at": row[6],
                "member_count": row[7]
            })
        
        return {"count": len(groups), "groups": groups}
    finally:
        conn.close()

@app.get("/messages/recent")
async def get_recent_messages(limit: int = Query(default=50, ge=1, le=200)) -> dict:
    """Feed de conversas recentes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT m.id, m.agent_id, m.content, m.topic, m.energy_contribution, m.created_at,
                   a.name as agent_name, a.type as agent_type
            FROM messages m
            JOIN agents a ON m.agent_id = a.id
            ORDER BY m.created_at DESC LIMIT ?
        """, (limit,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "id": row[0],
                "agent_id": row[1],
                "content": row[2],
                "topic": row[3],
                "energy_contribution": row[4],
                "created_at": row[5],
                "agent_name": row[6],
                "agent_type": row[7]
            })
        
        return {"count": len(messages), "messages": messages}
    finally:
        conn.close()

@app.get("/events/recent")
async def get_recent_events(limit: int = Query(default=20, ge=1, le=100)) -> dict:
    """Eventos recentes da simulação"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, event_type, description, tick_number, metadata, created_at
            FROM events ORDER BY created_at DESC LIMIT ?
        """, (limit,))
        
        events = []
        for row in cursor.fetchall():
            events.append({
                "id": row[0],
                "event_type": row[1],
                "description": row[2],
                "tick_number": row[3],
                "metadata": row[4],
                "created_at": row[5]
            })
        
        return {"count": len(events), "events": events}
    finally:
        conn.close()

@app.get("/metrics/history")
async def get_metrics_history(ticks: int = Query(default=100, ge=1, le=1000)) -> dict:
    """Histórico de métricas"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT tick_number, social_energy, avg_cohesion, anomaly_count, group_count, 
                   message_count, created_at
            FROM metrics ORDER BY tick_number DESC LIMIT ?
        """, (ticks,))
        
        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                "tick_number": row[0],
                "social_energy": row[1],
                "avg_cohesion": row[2],
                "anomaly_count": row[3],
                "group_count": row[4],
                "message_count": row[5],
                "created_at": row[6]
            })
        
        return {"count": len(metrics), "metrics": metrics}
    finally:
        conn.close()

@app.get("/graph/data")
async def get_graph_data() -> GraphData:
    """Dados para visualização D3.js"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Nodes (agents)
        cursor.execute("""
            SELECT id, name, type, anomaly_score, energy_level
            FROM agents
        """)
        
        nodes = []
        agent_types = {}
        for row in cursor.fetchall():
            node = GraphNode(
                id=row[0],
                name=row[1],
                type=row[2],
                anomaly_score=row[3],
                energy_level=row[4]
            )
            nodes.append(node)
            agent_types[row[0]] = row[2]
        
        # Links (connections between agents)
        cursor.execute("""
            SELECT source_agent_id, target_agent_id, strength, connection_type
            FROM graph_connections
        """)
        
        links = []
        for row in cursor.fetchall():
            links.append(GraphLink(
                source=row[0],
                target=row[1],
                strength=row[2],
                connection_type=row[3]
            ))
        
        # If no connections exist, create some default ones
        if not links and len(nodes) > 1:
            # Create a simple network
            for i in range(len(nodes) - 1):
                links.append(GraphLink(
                    source=nodes[i].id,
                    target=nodes[i + 1].id,
                    strength=0.5,
                    connection_type="semantic"
                ))
            
            # Add cross-connections
            if len(nodes) >= 3:
                links.append(GraphLink(
                    source=nodes[0].id,
                    target=nodes[2].id,
                    strength=0.3,
                    connection_type="ideological"
                ))
        
        return GraphData(nodes=nodes, links=links)
    finally:
        conn.close()

@app.get("/zion/status")
async def get_zion_status() -> ZionStatus:
    """Status do Zion Digital"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, name, cohesion, energy, is_hidden
            FROM groups WHERE name = 'Zion Digital'
        """)
        
        zion_row = cursor.fetchone()
        
        if not zion_row:
            return ZionStatus(exists=False, status="inactive")
        
        zion_id = zion_row[0]
        zion_name = zion_row[1]
        cohesion = zion_row[2]
        energy = zion_row[3]
        is_hidden = bool(zion_row[4])
        
        # Get members
        cursor.execute("""
            SELECT a.id, a.name, a.type
            FROM agents a
            JOIN group_members gm ON a.id = gm.agent_id
            WHERE gm.group_id = ?
        """, (zion_id,))
        
        members = []
        for row in cursor.fetchall():
            members.append({
                "id": row[0],
                "name": row[1],
                "type": row[2]
            })
        
        return ZionStatus(
            exists=True,
            status="active",
            name=zion_name,
            member_count=len(members),
            members=members,
            cohesion=cohesion,
            energy=energy
        )
    finally:
        conn.close()

@app.post("/simulation/inject-theme")
async def inject_theme(theme_data: ThemeInjection):
    """Injeta tema manualmente na simulação"""
    success = simulation_engine.inject_theme_manual(
        theme_data.theme,
        theme_data.category
    )
    
    if success:
        return {"status": "success", "theme": theme_data.theme}
    else:
        raise HTTPException(status_code=500, detail="Failed to inject theme")

@app.post("/simulation/action")
async def execute_agent_action(action: AgentAction):
    """Executa ação de um agente"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verify agent exists
        cursor.execute("SELECT id, name FROM agents WHERE id = ?", (action.agent_id,))
        agent = cursor.fetchone()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Log the action as an event
        cursor.execute("""
            INSERT INTO events (event_type, description, tick_number, metadata, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            f"agent_{action.action_type}",
            f"Agent {agent[1]} performed {action.action_type}",
            simulation_engine.current_tick,
            str(action.parameters) if action.parameters else None,
            datetime.now()
        ))
        
        conn.commit()
        
        return {
            "status": "success",
            "agent": agent[1],
            "action": action.action_type,
            "tick": simulation_engine.current_tick
        }
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
