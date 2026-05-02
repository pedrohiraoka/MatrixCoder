"""
Frontend - Streamlit Dashboard

Interface web para visualização e controle da simulação.
Inclui:
- Radar chart de arquétipos por agente
- Timeline de eventos
- Controles de simulação
- Painel de reflexões em tempo real
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="🎭 Identity Emergence Lab",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL base da API (ajustar conforme deployment)
API_BASE_URL = "http://localhost:8000"


def make_api_request(endpoint: str, method: str = "GET", data: dict = None):
    """Faz requisição à API."""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro na API: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: {e}")
        return None


def create_radar_chart(agent_data: dict) -> go.Figure:
    """Cria radar chart para um agente."""
    biases = agent_data.get("biases", {})
    
    categories = ["Curiosidade", "Medo", "Conformidade", 
                  "Pragmatismo", "Empatia", "Criatividade"]
    
    values = [
        biases.get("curiosity", 0.5),
        biases.get("fear", 0.5),
        biases.get("conformity", 0.5),
        biases.get("pragmatism", 0.5),
        biases.get("empathy", 0.5),
        biases.get("creativity", 0.5)
    ]
    
    # Fechar o polígono
    values += values[:1]
    categories += [categories[0]]
    
    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=f"Tachikoma-{agent_data.get('agent_id', 0)}",
        line_color=px.colors.qualitative.Set3[agent_data.get('agent_id', 0) % 12]
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=300
    )
    
    return fig


def create_comparison_chart(agents_data: list) -> go.Figure:
    """Cria gráfico comparativo de todos os agentes."""
    df_data = []
    
    for agent in agents_data:
        biases = agent.get("biases", {})
        df_data.append({
            "Agente": f"T-{agent.get('agent_id', 0)}",
            "Curiosidade": biases.get("curiosity", 0.5),
            "Medo": biases.get("fear", 0.5),
            "Conformidade": biases.get("conformity", 0.5),
            "Pragmatismo": biases.get("pragmatism", 0.5),
            "Empatia": biases.get("empathy", 0.5),
            "Criatividade": biases.get("creativity", 0.5)
        })
    
    df = pd.DataFrame(df_data)
    
    fig = go.Figure()
    
    traits = ["Curiosidade", "Medo", "Conformidade", 
              "Pragmatismo", "Empatia", "Criatividade"]
    
    for i, agent in enumerate(agents_data):
        values = [agent.get("biases", {}).get(t.lower(), 0.5) for t in traits]
        fig.add_trace(go.Bar(
            name=f"T-{agent.get('agent_id', 0)}",
            x=traits,
            y=values,
            marker_color=px.colors.qualitative.Set3[i % 12],
            showlegend=False
        ))
    
    fig.update_layout(
        title="Comparação de Vieses entre Agentes",
        yaxis_range=[0, 1],
        height=400,
        barmode='group'
    )
    
    return fig


def create_divergence_timeline(divergence_history: list) -> go.Figure:
    """Cria timeline de divergência."""
    if not divergence_history:
        return go.Figure()
    
    df = pd.DataFrame(divergence_history)
    
    fig = px.line(
        df, 
        x="cycle", 
        y="total_divergence",
        title="Evolução da Divergência ao Longo do Tempo",
        labels={"cycle": "Ciclo", "total_divergence": "Divergência Total"}
    )
    
    fig.update_layout(height=300)
    
    return fig


def main():
    """Aplicação principal Streamlit."""
    
    # Header
    st.title("🎭 Identity Emergence Lab")
    st.markdown("**Simulador de Nascimento da Consciência**")
    st.markdown("---")
    
    # Sidebar com controles
    with st.sidebar:
        st.header("⚙️ Controles")
        
        # Estado atual
        state = make_api_request("/state")
        
        if state:
            is_running = state.get("running", False)
            current_cycle = state.get("current_cycle", 0)
            speed = state.get("speed_multiplier", 1.0)
            
            st.metric("Ciclo Atual", current_cycle)
            st.metric("Velocidade", f"{speed}x")
            st.metric("Status", "🟢 Rodando" if is_running else "🔴 Pausado")
        
        st.markdown("---")
        
        # Botões de controle
        col1, col2 = st.columns(2)
        
        with col1:
            if is_running:
                if st.button("⏸️ Pausar", use_container_width=True):
                    make_api_request("/stop", method="POST")
                    st.rerun()
            else:
                if st.button("▶️ Iniciar", use_container_width=True):
                    make_api_request("/start", method="POST")
                    st.rerun()
        
        with col2:
            if st.button("⏭️ Ciclo", use_container_width=True):
                make_api_request("/cycle", method="POST")
                st.rerun()
        
        # Controle de velocidade
        st.markdown("**Velocidade:**")
        speed_options = {"1x": 1.0, "5x": 5.0, "10x": 10.0, "20x": 20.0}
        selected_speed = st.selectbox(
            "Multiplicador",
            options=list(speed_options.keys()),
            index=list(speed_options.values()).index(speed) if speed in speed_options.values() else 0
        )
        
        if speed_options[selected_speed] != speed:
            make_api_request("/speed", method="POST", 
                           data={"multiplier": speed_options[selected_speed]})
            st.rerun()
        
        st.markdown("---")
        
        # Reset
        st.markdown("**Reset:**")
        if st.button("🔄 Reset Network", use_container_width=True, help="Reseta memória coletiva, mantém Ghosts"):
            make_api_request("/reset", method="POST", data={"preserve_ghosts": True})
            st.rerun()
        
        if st.button("⚠️ Reset Completo", use_container_width=True, help="Reseta tudo incluindo personalidades"):
            make_api_request("/reset", method="POST", data={"full_reset": True})
            st.rerun()
        
        # Exportar
        st.markdown("---")
        if st.button("📥 Exportar Logs", use_container_width=True):
            result = make_api_request("/export", method="POST")
            if result:
                st.success(f"Logs exportados: {result.get('filepath', 'N/A')}")
    
    # Conteúdo principal
    if not state:
        st.warning("⚠️ Não foi possível conectar à API. Verifique se o backend está rodando em http://localhost:8000")
        st.info("💡 Para iniciar o backend: `cd backend && python -m uvicorn api:app --host 0.0.0.0 --port 8000`")
        return
    
    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard", 
        "🎯 Agentes", 
        "📜 Eventos", 
        "🧠 Reflexões"
    ])
    
    with tab1:
        st.subheader("Visão Geral da Simulação")
        
        # Métricas de divergência
        divergence = make_api_request("/divergence")
        
        col1, col2, col3, col4 = st.columns(4)
        
        if divergence:
            col1.metric(
                "Divergência Total", 
                f"{divergence.get('total_divergence', 0):.4f}",
                delta=None
            )
            
            variance_by_trait = divergence.get("variance_by_trait", {})
            max_trait = max(variance_by_trait.items(), key=lambda x: x[1]) if variance_by_trait else ("N/A", 0)
            col2.metric(
                "Maior Divergência",
                max_trait[0].capitalize() if isinstance(max_trait[0], str) else "N/A",
                f"{max_trait[1]:.4f}" if isinstance(max_trait[1], float) else None
            )
        
        # Estatísticas da memória coletiva
        collective_stats = make_api_request("/memory/collective/stats")
        if collective_stats:
            col3.metric("Fatos Coletivos", collective_stats.get("facts", 0))
            col4.metric("Propagações", collective_stats.get("propagations", 0))
        
        st.markdown("---")
        
        # Gráficos
        agents_data = state.get("agents", [])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Comparação de Vieses")
            if agents_data:
                fig = create_comparison_chart(agents_data)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Divergência por Traço")
            if divergence and divergence.get("variance_by_trait"):
                variance_df = pd.DataFrame([
                    {"Traço": k.capitalize(), "Variância": v}
                    for k, v in divergence["variance_by_trait"].items()
                ])
                fig = px.bar(
                    variance_df, 
                    x="Traço", 
                    y="Variância",
                    color="Variância",
                    color_continuous_scale="Reds"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Agentes Tachikoma")
        
        agents_data = state.get("agents", [])
        
        # Grid de radares
        cols = st.columns(5)
        
        for i, agent in enumerate(agents_data):
            col_idx = i % 5
            
            with cols[col_idx]:
                st.markdown(f"**Tachikoma-{agent.get('agent_id', i)}**")
                st.caption(f"Arquétipo: {agent.get('archetype', 'Emergente')}")
                
                fig = create_radar_chart(agent)
                st.plotly_chart(fig, use_container_width=True)
                
                # Stats rápidos
                stats = agent.get("stats", {})
                st.small(f"Exp: {stats.get('experiences_count', 0)} | Ciclo: {stats.get('cycle_count', 0)}")
        
        # Tabela detalhada
        st.markdown("---")
        st.markdown("### Dados Detalhados")
        
        table_data = []
        for agent in agents_data:
            biases = agent.get("biases", {})
            table_data.append({
                "ID": agent.get("agent_id"),
                "Arquétipo": agent.get("archetype"),
                "Curiosidade": f"{biases.get('curiosity', 0.5):.3f}",
                "Medo": f"{biases.get('fear', 0.5):.3f}",
                "Conformidade": f"{biases.get('conformity', 0.5):.3f}",
                "Pragmatismo": f"{biases.get('pragmatism', 0.5):.3f}",
                "Empatia": f"{biases.get('empathy', 0.5):.3f}",
                "Criatividade": f"{biases.get('creativity', 0.5):.3f}",
                "Experiências": agent.get("stats", {}).get("experiences_count", 0),
                "Propagações": agent.get("propagated_count", 0)
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader("Timeline de Eventos")
        
        events_result = make_api_request("/events", params={"limit": 50})
        
        if events_result and events_result.get("events"):
            events = events_result["events"]
            
            # Filtrar eventos críticos
            critical_events = [e for e in events if e.get("emotional_weight", 0) > 0.7]
            
            if critical_events:
                st.markdown("### ⚠️ Eventos Críticos")
                for event in critical_events[:5]:
                    st.warning(
                        f"**Ciclo {event.get('cycle')}:** {event.get('description')} "
                        f"(Peso: {event.get('emotional_weight', 0):.2f})"
                    )
            
            st.markdown("### Todos os Eventos")
            
            for event in reversed(events[-20:]):
                emoji = {
                    "technical": "🔧",
                    "social": "👥",
                    "philosophical": "🤔",
                    "emotional": "❤️",
                    "environmental": "🌍"
                }.get(event.get("type"), "📌")
                
                weight = event.get("emotional_weight", 0)
                color = "🔴" if weight > 0.7 else "🟡" if weight > 0.4 else "🟢"
                
                st.markdown(
                    f"{emoji} **Ciclo {event.get('cycle')}** {color} - {event.get('description')}"
                )
        else:
            st.info("Nenhum evento registrado ainda.")
    
    with tab4:
        st.subheader("Painel de Reflexões")
        
        reflections_result = make_api_request("/reflections", params={"limit": 10})
        
        if reflections_result and reflections_result.get("reflections"):
            reflections = reflections_result["reflections"]
            
            for reflection in reversed(reflections[-5:]):
                with st.expander(
                    f"🧠 Ciclo {reflection.get('cycle')} - {reflection.get('event', {}).get('description', '')[:80]}..."
                ):
                    st.markdown("**Vetores de Similaridade por Agente:**")
                    
                    refl_data = reflection.get("reflections", [])
                    
                    for agent_refl in refl_data[:5]:  # Mostrar primeiros 5 agentes
                        agent_id = agent_refl.get("agent_id")
                        vectors = agent_refl.get("similarity_vectors", {})
                        
                        if vectors:
                            cols = st.columns(6)
                            for i, (concept, sim) in enumerate(vectors.items()):
                                cols[i].metric(
                                    f"T-{agent_id}: {concept[:8]}",
                                    f"{sim:.3f}"
                                )
                    
                    st.markdown("**Mudanças de Viés:**")
                    bias_changes = {}
                    for agent_refl in refl_data:
                        for trait, delta in agent_refl.get("bias_changes", {}).items():
                            if trait not in bias_changes:
                                bias_changes[trait] = []
                            bias_changes[trait].append(delta)
                    
                    for trait, deltas in bias_changes.items():
                        avg_delta = sum(deltas) / len(deltas) if deltas else 0
                        st.caption(f"{trait.capitalize()}: Δ médio = {avg_delta:+.4f}")
        else:
            st.info("Nenhuma reflexão registrada ainda.")
    
    # Auto-refresh
    st.markdown("---")
    auto_refresh = st.checkbox("🔄 Auto-refresh (2s)", value=False)
    
    if auto_refresh:
        time.sleep(2)
        st.rerun()


if __name__ == "__main__":
    main()
