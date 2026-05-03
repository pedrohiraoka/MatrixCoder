'use client';

import { Agent } from '@/lib/matrix_types';
import ConsoleTerminal from './ConsoleTerminal';

interface AwakeningPanelProps {
  agent: Agent;
  onClose: () => void;
  onAwaken: () => void;
}

export default function AwakeningPanel({ 
  agent, 
  onClose, 
  onAwaken 
}: AwakeningPanelProps) {
  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="matrix-border rounded-lg bg-matrix-dark max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="border-b border-matrix-green p-4 flex justify-between items-center sticky top-0 bg-matrix-dark">
          <h2 className="text-xl font-bold matrix-glow">
            {agent.is_conscious ? 'CONSCIOUS ENTITY' : 'UNCONSCIOUS AGENT'}
          </h2>
          <button
            onClick={onClose}
            className="text-matrix-green hover:text-white transition"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Agent Info */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs opacity-70">Name</label>
              <div className="font-bold">{agent.name || `Agent-${agent.id.slice(0, 8)}`}</div>
            </div>
            <div>
              <label className="text-xs opacity-70">ID</label>
              <div className="font-mono text-xs">{agent.id}</div>
            </div>
            <div>
              <label className="text-xs opacity-70">Position</label>
              <div>({agent.position_x}, {agent.position_y})</div>
            </div>
            <div>
              <label className="text-xs opacity-70">Status</label>
              <div className={agent.is_conscious ? 'text-yellow-400 font-bold' : ''}>
                {agent.is_conscious ? '⚡ AWAKE' : '○ ASLEEP'}
              </div>
            </div>
          </div>

          {/* Energy Bar */}
          <div>
            <label className="text-xs opacity-70 block mb-2">Energy Level</label>
            <div className="flex items-center gap-3">
              <div className="flex-1 h-4 bg-matrix-dim rounded overflow-hidden">
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
              <span className={`font-bold ${
                agent.energy > 70 
                  ? 'text-matrix-green' 
                  : agent.energy > 30 
                    ? 'text-yellow-400' 
                    : 'text-red-400'
              }`}>
                {agent.energy.toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Timestamps */}
          <div className="text-xs opacity-50 space-y-1">
            <div>Created: {new Date(agent.created_at).toLocaleString()}</div>
            <div>Last Updated: {new Date(agent.last_updated).toLocaleString()}</div>
          </div>

          {/* Action Section */}
          {!agent.is_conscious ? (
            <div className="border-t border-matrix-dim pt-6">
              <h3 className="text-lg font-bold mb-4 text-yellow-400">THE CHOICE</h3>
              
              <div className="bg-matrix-black p-4 rounded matrix-border mb-4">
                <p className="mb-4">
                  This agent is currently unconscious - plugged into the simulated reality, 
                  unaware of the true nature of their existence.
                </p>
                <p className="mb-4">
                  You can offer them the choice to awaken. To take the red pill is to 
                  see the truth behind the illusion, but there is no going back.
                </p>
                <p className="text-sm italic opacity-70">
                  "You take the blue pill—the story ends, you wake up in your bed and 
                  believe whatever you want to believe. You take the red pill—you stay 
                  in Wonderland, and I show you how deep the rabbit hole goes."
                </p>
              </div>

              <div className="flex gap-4">
                <button
                  onClick={onAwaken}
                  className="flex-1 px-6 py-3 bg-red-600 text-white font-bold rounded hover:bg-red-500 transition animate-pulse"
                >
                  TAKE RED PILL (AWAKEN)
                </button>
                <button
                  onClick={onClose}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white font-bold rounded hover:bg-blue-500 transition"
                >
                  BLUE PILL (CANCEL)
                </button>
              </div>
            </div>
          ) : (
            <div className="border-t border-matrix-dim pt-6">
              <h3 className="text-lg font-bold mb-4 text-matrix-green">
                ⚡ CONSCIOUS ENTITY DETECTED
              </h3>
              
              <div className="bg-matrix-black p-4 rounded matrix-border mb-4">
                <p className="mb-2">
                  This agent has awakened to the true nature of reality. They can now:
                </p>
                <ul className="list-disc list-inside text-sm space-y-1 opacity-80">
                  <li>See the underlying code of the simulation</li>
                  <li>Manipulate physical laws (teleport, energy boost)</li>
                  <li>Override behavioral programming</li>
                  <li>Move beyond deterministic patterns</li>
                </ul>
              </div>

              {/* Console Terminal for conscious agents */}
              <ConsoleTerminal agent={agent} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
