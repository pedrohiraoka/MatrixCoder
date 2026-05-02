/**
 * Nexus Matrix - Dashboard e Gráficos
 */

let energyChart = null;

// Inicializar gráfico de energia
function initializeEnergyChart() {
    const ctx = document.getElementById('energy-chart');
    if (!ctx) return;
    
    energyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Energia Social',
                data: [],
                borderColor: '#00ff41',
                backgroundColor: 'rgba(0, 255, 65, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 500
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(0, 255, 65, 0.1)'
                    },
                    ticks: {
                        color: '#008f11'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 255, 65, 0.1)'
                    },
                    ticks: {
                        color: '#008f11'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Atualizar gráfico de energia
async function updateEnergyChart() {
    try {
        const response = await fetch('/metrics/history?ticks=50');
        const data = await response.json();
        
        if (energyChart && data.metrics) {
            energyChart.data.labels = data.metrics.map(m => `Tick ${m.tick}`);
            energyChart.data.datasets[0].data = data.metrics.map(m => m.total_energy);
            energyChart.update('none'); // Update without full animation
        }
    } catch (error) {
        console.error('Erro ao atualizar gráfico:', error);
    }
}

// Carregar mensagens com HTMX fallback
async function loadMessages() {
    try {
        const response = await fetch('/messages/recent?limit=20');
        const data = await response.json();
        
        const container = document.getElementById('message-feed');
        if (!container) return;
        
        if (!data.messages || data.messages.length === 0) {
            container.innerHTML = '<div class="empty">Nenhuma mensagem ainda</div>';
            return;
        }
        
        container.innerHTML = data.messages.map(msg => `
            <div class="message ${msg.is_anomalous ? 'anomalous' : ''}">
                <div class="message-header">
                    <span class="agent-name">${escapeHtml(msg.agent_name)}</span>
                    <span class="agent-type ${msg.agent_type}">${msg.agent_type}</span>
                    <span class="group-name">${msg.group_name || 'Sem grupo'}</span>
                    <span class="message-time">${new Date(msg.created_at).toLocaleTimeString()}</span>
                </div>
                <div class="message-content">${escapeHtml(msg.content)}</div>
                <div class="message-meta">
                    <span>Energia: ${msg.energy_contribution.toFixed(2)}</span>
                    ${msg.is_anomalous ? '<span class="anomaly-tag">⚠️ ANOMALIA</span>' : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar mensagens:', error);
    }
}

// Carregar eventos
async function loadEvents() {
    try {
        const response = await fetch('/events/recent?limit=10');
        const data = await response.json();
        
        const container = document.getElementById('events-list');
        if (!container) return;
        
        if (!data.events || data.events.length === 0) {
            container.innerHTML = '<div class="empty">Nenhum evento registrado</div>';
            return;
        }
        
        container.innerHTML = data.events.map(evt => `
            <div class="event ${evt.injected_by_central_ai ? 'central-ai' : ''}">
                <div class="event-header">
                    <span class="event-type">${evt.type}</span>
                    <span class="event-tick">Tick ${evt.tick}</span>
                </div>
                <div class="event-title">${escapeHtml(evt.title)}</div>
                <div class="event-description">${escapeHtml(evt.description)}</div>
                <div class="event-meta">
                    <span>Impacto: ${(evt.impact_score * 100).toFixed(0)}%</span>
                    ${evt.injected_by_central_ai ? '<span class="ia-badge">🤖 IA Central</span>' : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar eventos:', error);
    }
}

// Carregar agentes
async function loadAgents() {
    try {
        const response = await fetch('/agents');
        const data = await response.json();
        
        const container = document.getElementById('agents-list');
        if (!container) return;
        
        if (!data.agents || data.agents.length === 0) {
            container.innerHTML = '<div class="empty">Nenhum agente registrado</div>';
            return;
        }
        
        container.innerHTML = data.agents.map(agent => `
            <div class="agent-card" style="border-left-color: ${agent.color}">
                <div class="agent-header">
                    <span class="agent-icon">${agent.icon}</span>
                    <span class="agent-name">${escapeHtml(agent.name)}</span>
                </div>
                <div class="agent-role">${escapeHtml(agent.role)}</div>
                <div class="agent-stats">
                    <span>Anomalia: ${(agent.anomaly_score * 100).toFixed(0)}%</span>
                    <span>Energia: ${(agent.energy_level * 100).toFixed(0)}%</span>
                </div>
                <div class="agent-beliefs">
                    ${agent.beliefs.slice(0, 3).map(b => `<span class="belief-tag">${escapeHtml(b)}</span>`).join('')}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar agentes:', error);
    }
}

// Carregar status do Zion
async function loadZionStatus() {
    try {
        const response = await fetch('/zion/status');
        const data = await response.json();
        
        const container = document.getElementById('zion-info');
        const statusIndicator = document.getElementById('zion-status');
        
        if (!container) return;
        
        if (!data.exists) {
            container.innerHTML = `
                <div class="zion-status dormant">
                    <div class="zion-icon">🔒</div>
                    <p>Zion Digital ainda não emergiu</p>
                    <p class="zion-hint">Aguardando massa crítica de anomalias...</p>
                </div>
            `;
            if (statusIndicator) {
                statusIndicator.textContent = 'Zion: Inativo';
                statusIndicator.className = 'zion-indicator inactive';
            }
        } else {
            container.innerHTML = `
                <div class="zion-status ${data.status}">
                    <div class="zion-icon">${data.status === 'active' ? '⚡' : '💤'}</div>
                    <h3>${escapeHtml(data.name)}</h3>
                    <p>Tema: ${escapeHtml(data.theme)}</p>
                    <p>Membros: ${data.member_count}</p>
                    <p>Coesão: ${(data.cohesion * 100).toFixed(0)}%</p>
                    ${data.members ? `
                        <div class="zion-members">
                            ${data.members.map(m => `<span class="member-tag">${escapeHtml(m.name)}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
            if (statusIndicator) {
                statusIndicator.textContent = `Zion: ${data.status === 'active' ? 'ATIVO' : 'Dormente'}`;
                statusIndicator.className = `zion-indicator ${data.status}`;
            }
        }
    } catch (error) {
        console.error('Erro ao carregar status do Zion:', error);
    }
}

// Utilitário para escapar HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Inicializar dashboard
async function initializeDashboard() {
    // Inicializar gráfico
    initializeEnergyChart();
    
    // Carregar dados iniciais
    await loadMessages();
    await loadEvents();
    await loadAgents();
    await loadZionStatus();
    await updateEnergyChart();
    
    // Atualizações periódicas
    setInterval(() => {
        loadMessages();
        loadZionStatus();
    }, 2000);
    
    setInterval(() => {
        loadEvents();
        updateEnergyChart();
    }, 5000);
    
    setInterval(() => {
        loadAgents();
    }, 10000);
}

// Exportar funções globais
window.initializeDashboard = initializeDashboard;
window.loadMessages = loadMessages;
window.loadEvents = loadEvents;
window.loadAgents = loadAgents;
window.loadZionStatus = loadZionStatus;
window.updateEnergyChart = updateEnergyChart;
window.escapeHtml = escapeHtml;
