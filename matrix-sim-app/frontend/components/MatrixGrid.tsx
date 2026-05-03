'use client';

import { Agent } from '@/lib/matrix_types';

interface MatrixGridProps {
  agents: Agent[];
  onSelectAgent: (agent: Agent) => void;
}

export default function MatrixGrid({ agents, onSelectAgent }: MatrixGridProps) {
  const gridSize = 20; // 20x20 grid
  const cellSize = 'w-3 h-3 md:w-4 md:h-4';

  // Create a map of agent positions for quick lookup
  const agentMap = new Map<string, Agent>();
  agents.forEach(agent => {
    const key = `${agent.position_x},${agent.position_y}`;
    agentMap.set(key, agent);
  });

  return (
    <div className="matrix-border p-4 rounded bg-matrix-dark">
      <h2 className="text-xl font-bold mb-4">The Matrix Grid ({gridSize}x{gridSize})</h2>
      
      <div className="overflow-x-auto">
        <div 
          className="grid gap-px bg-matrix-dim/20 inline-block p-1"
          style={{ 
            gridTemplateColumns: `repeat(${gridSize}, minmax(0, 1fr))` 
          }}
        >
          {Array.from({ length: gridSize * gridSize }).map((_, index) => {
            const x = index % gridSize;
            const y = Math.floor(index / gridSize);
            const key = `${x},${y}`;
            const agent = agentMap.get(key);

            return (
              <div
                key={index}
                onClick={() => agent && onSelectAgent(agent)}
                className={`
                  ${cellSize}
                  border border-matrix-dim/30
                  transition-all duration-200
                  ${agent 
                    ? agent.is_conscious
                      ? 'bg-yellow-400 hover:bg-yellow-300 cursor-pointer animate-pulse'
                      : 'bg-matrix-green hover:bg-green-400 cursor-pointer'
                    : 'bg-matrix-black hover:bg-matrix-dim/50'
                  }
                `}
                title={agent ? `${agent.name} (${agent.energy.toFixed(1)}%) - ${agent.is_conscious ? 'AWAKE' : 'ASLEEP'}` : ''}
              />
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 mt-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-matrix-black border border-matrix-dim/30"></div>
          <span>Empty</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-matrix-green"></div>
          <span>Agent (Unconscious)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-yellow-400 animate-pulse"></div>
          <span>Agent (Conscious/Awake)</span>
        </div>
      </div>

      {/* Stats */}
      <div className="mt-4 text-sm opacity-70">
        <p>Occupied: {agents.length} / {gridSize * gridSize} cells ({((agents.length / (gridSize * gridSize)) * 100).toFixed(1)}%)</p>
        <p>Conscious: {agents.filter(a => a.is_conscious).length}</p>
      </div>
    </div>
  );
}
