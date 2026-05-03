'use client';

import { Agent } from '@/lib/matrix_types';

interface AgentCardProps {
  agent: Agent;
  isSelected: boolean;
  onSelect: () => void;
  onAwaken: () => void;
}

export default function AgentCard({ 
  agent, 
  isSelected, 
  onSelect, 
  onAwaken 
}: AgentCardProps) {
  const energyColor = agent.energy > 70 
    ? 'text-matrix-green' 
    : agent.energy > 30 
      ? 'text-yellow-400' 
      : 'text-red-400';

  return (
    <div
      onClick={onSelect}
      className={`
        p-3 rounded cursor-pointer transition-all
        border ${isSelected 
          ? 'border-matrix-green bg-matrix-green/10' 
          : 'border-matrix-dim/30 bg-matrix-black hover:bg-matrix-dim/20'
        }
        ${agent.is_conscious ? 'ring-1 ring-yellow-400' : ''}
      `}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-bold truncate">{agent.name || `Agent-${agent.id.slice(0, 8)}`}</span>
            {agent.is_conscious && (
              <span className="text-xs px-2 py-0.5 bg-yellow-400 text-black rounded font-bold animate-pulse">
                AWAKE
              </span>
            )}
          </div>
          
          <div className="text-xs opacity-70 mt-1">
            ID: {agent.id.slice(0, 8)}...
          </div>
          
          <div className="text-xs opacity-70">
            Position: ({agent.position_x}, {agent.position_y})
          </div>
        </div>
        
        <div className="text-right ml-4">
          <div className={`text-sm font-bold ${energyColor}`}>
            {agent.energy.toFixed(1)}%
          </div>
          <div className="w-20 h-2 bg-matrix-dim rounded mt-1 overflow-hidden">
            <div 
              className={`h-full transition-all ${
                agent.energy > 70 
                  ? 'bg-matrix-green' 
                  : agent.energy > 30 
                    ? 'bg-yellow-400' 
                    : 'bg-red-400'
              }`}
              style={{ width: `${Math.min(100, agent.energy)}%` }}
            />
          </div>
        </div>
      </div>
      
      {/* Actions */}
      {!agent.is_conscious && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onAwaken();
          }}
          className="mt-2 w-full px-3 py-1.5 text-xs bg-matrix-green text-black font-bold rounded hover:bg-green-400 transition"
        >
          TAKE RED PILL (AWAKEN)
        </button>
      )}
      
      {agent.is_conscious && (
        <div className="mt-2 text-xs text-yellow-400">
          ⚡ Can manipulate reality
        </div>
      )}
    </div>
  );
}
