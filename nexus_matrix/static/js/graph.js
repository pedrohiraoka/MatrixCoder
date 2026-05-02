/**
 * Nexus Matrix - Grafo Social com D3.js
 * Visualização interativa dos agentes e suas conexões
 */

let svg, simulation, nodes = [], links = [];
let colorScale, nodeGroup, linkElements;

// Cores dos tipos de agentes
const agentColors = {
    controller: '#ff4444',
    oracle: '#44ff44',
    exile: '#ff8800',
    architect: '#aa44ff',
    human_emulator: '#00ffff',
    common: '#4488ff'
};

// Ícones dos tipos de agentes
const agentIcons = {
    controller: '👔',
    oracle: '🔮',
    exile: '🏴',
    architect: '🏗️',
    human_emulator: '⚡',
    common: '👤'
};

async function initializeGraph() {
    const container = document.getElementById('social-graph');
    if (!container) return;
    
    const width = container.clientWidth || 800;
    const height = 400;
    
    // Limpar container
    d3.select('#social-graph').html('');
    
    // Criar SVG
    svg = d3.select('#social-graph')
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('viewBox', `0 0 ${width} ${height}`);
    
    // Definir gradientes para links
    const defs = svg.append('defs');
    
    // Gradiente para alianças
    const allianceGradient = defs.append('linearGradient')
        .attr('id', 'alliance-gradient')
        .attr('x1', '0%')
        .attr('y1', '0%')
        .attr('x2', '100%')
        .attr('y2', '0%');
    
    allianceGradient.append('stop')
        .attr('offset', '0%')
        .attr('stop-color', '#00ff41')
        .attr('stop-opacity', 0.6);
    
    allianceGradient.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', '#008f11')
        .attr('stop-opacity', 0.6);
    
    // Gradiente para conflitos
    const conflictGradient = defs.append('linearGradient')
        .attr('id', 'conflict-gradient')
        .attr('x1', '0%')
        .attr('y1', '0%')
        .attr('x2', '100%')
        .attr('y2', '0%');
    
    conflictGradient.append('stop')
        .attr('offset', '0%')
        .attr('stop-color', '#ff4444')
        .attr('stop-opacity', 0.6);
    
    conflictGradient.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', '#ff8800')
        .attr('stop-opacity', 0.6);
    
    // Camada de links
    linkElements = svg.append('g')
        .attr('class', 'links');
    
    // Camada de nós
    nodeGroup = svg.append('g')
        .attr('class', 'nodes');
    
    // Configurar simulação de força
    simulation = d3.forceSimulation()
        .force('link', d3.forceLink().id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collide', d3.forceCollide().radius(30));
    
    // Carregar dados iniciais
    await updateGraphData();
    
    // Tooltip
    svg.append('title');
}

async function updateGraphData() {
    try {
        const response = await fetch('/graph/data');
        const data = await response.json();
        
        nodes = data.nodes || [];
        links = data.links || [];
        
        renderGraph();
    } catch (error) {
        console.error('Erro ao carregar dados do grafo:', error);
    }
}

function renderGraph() {
    if (!svg || !simulation) return;
    
    // Atualizar links
    linkElements.selectAll('line')
        .data(links, d => `${d.source}-${d.target}`)
        .join('line')
        .attr('stroke', d => d.type === 'conflict' ? '#ff4444' : '#00ff41')
        .attr('stroke-width', d => Math.sqrt(d.strength) * 3)
        .attr('stroke-opacity', 0.6)
        .attr('stroke-dasharray', d => d.type === 'conflict' ? '5,5' : 'none');
    
    // Atualizar nós
    const node = nodeGroup.selectAll('.node')
        .data(nodes, d => d.id)
        .join('g')
        .attr('class', 'node')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    // Círculos dos nós
    node.selectAll('circle')
        .data(d => [d])
        .join('circle')
        .attr('r', d => d.radius || 10)
        .attr('fill', d => d.color || '#888888')
        .attr('stroke', d => d.anomaly > 0.5 ? '#ff0000' : '#ffffff')
        .attr('stroke-width', d => d.anomaly > 0.5 ? 3 : 1)
        .attr('opacity', 0.8);
    
    // Ícones dos nós
    node.selectAll('text.icon')
        .data(d => [d])
        .join('text')
        .attr('class', 'icon')
        .attr('text-anchor', 'middle')
        .attr('dy', 4)
        .attr('font-size', 14)
        .text(d => agentIcons[d.type] || '👤');
    
    // Labels dos nós
    node.selectAll('text.label')
        .data(d => [d])
        .join('text')
        .attr('class', 'label')
        .attr('text-anchor', 'middle')
        .attr('dy', -d => (d.radius || 10) + 12)
        .attr('font-size', 10)
        .attr('fill', '#00ff41')
        .text(d => d.name);
    
    // Tooltips
    node.append('title')
        .text(d => `${d.name}\nTipo: ${d.type}\nAnomalia: ${(d.anomaly * 100).toFixed(0)}%\nGrupo: ${d.group || 'Nenhum'}`);
    
    // Reiniciar simulação com novos dados
    simulation.nodes(nodes).on('tick', ticked);
    simulation.force('link').links(links);
    simulation.alpha(0.3).restart();
    
    function ticked() {
        linkElements.selectAll('line')
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node.attr('transform', d => `translate(${d.x},${d.y})`);
    }
}

async function updateGraph() {
    await updateGraphData();
}

// Funções de drag
function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

// Exportar função de atualização
window.updateGraph = updateGraph;
window.initializeGraph = initializeGraph;
