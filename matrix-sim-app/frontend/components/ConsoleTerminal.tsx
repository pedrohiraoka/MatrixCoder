'use client';

import { useState } from 'react';
import { Agent } from '@/lib/matrix_types';
import * as api from '@/lib/api';

interface ConsoleTerminalProps {
  agent: Agent;
}

export default function ConsoleTerminal({ agent }: ConsoleTerminalProps) {
  const [code, setCode] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [manipulationType, setManipulationType] = useState<'teleport' | 'energy_boost' | 'rule_override'>('teleport');
  const [targetX, setTargetX] = useState<number>(0);
  const [targetY, setTargetY] = useState<number>(0);
  const [boostAmount, setBoostAmount] = useState<number>(50);

  const handleViewCode = async () => {
    if (!agent.is_conscious) {
      setError('Agent must be conscious to see the code. Take the red pill first.');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const result = await api.viewAgentCode(agent.id);
      setCode(result.code);
    } catch (err: any) {
      setError(err.message || 'Failed to view code');
    } finally {
      setLoading(false);
    }
  };

  const handleManipulate = async () => {
    if (!agent.is_conscious) {
      setError('Only conscious agents can manipulate reality.');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      await api.manipulateSimulation(
        agent.id,
        manipulationType,
        manipulationType === 'teleport' ? targetX : undefined,
        manipulationType === 'teleport' ? targetY : undefined,
        manipulationType === 'energy_boost' ? boostAmount : undefined
      );
      
      // Refresh code view after manipulation
      const result = await api.viewAgentCode(agent.id);
      setCode(result.code);
    } catch (err: any) {
      setError(err.message || 'Failed to manipulate simulation');
    } finally {
      setLoading(false);
    }
  };

  if (!agent.is_conscious) {
    return (
      <div className="p-4 text-center opacity-50">
        <p>This agent is unconscious.</p>
        <p className="text-sm mt-2">Awaken them to access the terminal and see the code.</p>
      </div>
    );
  }

  return (
    <div className="matrix-border rounded bg-black p-4 font-mono text-sm">
      <h3 className="text-lg font-bold mb-4 matrix-glow">CONSOLE TERMINAL</h3>
      
      {/* View Code Section */}
      <div className="mb-6">
        <button
          onClick={handleViewCode}
          disabled={loading}
          className="px-4 py-2 bg-matrix-green text-black font-bold rounded hover:bg-green-400 transition disabled:opacity-50"
        >
          {loading ? 'ACCESSING...' : 'VIEW CODE'}
        </button>
        
        {error && (
          <div className="mt-2 text-red-400 text-xs">{error}</div>
        )}
        
        {code && (
          <pre className="mt-4 p-3 bg-matrix-dim/20 rounded text-xs overflow-auto max-h-64 border border-matrix-dim/30">
            <code className="text-matrix-green">
              {JSON.stringify(code, null, 2)}
            </code>
          </pre>
        )}
      </div>

      {/* Manipulation Section */}
      <div className="border-t border-matrix-dim pt-4">
        <h4 className="font-bold mb-3 text-yellow-400">MANIPULATE REALITY</h4>
        
        <div className="space-y-3">
          {/* Manipulation Type */}
          <div>
            <label className="block text-xs mb-1">Type:</label>
            <select
              value={manipulationType}
              onChange={(e) => setManipulationType(e.target.value as any)}
              className="w-full bg-black border border-matrix-dim rounded px-2 py-1 text-matrix-green focus:border-matrix-green outline-none"
            >
              <option value="teleport">Teleport</option>
              <option value="energy_boost">Energy Boost</option>
              <option value="rule_override">Rule Override</option>
            </select>
          </div>

          {/* Teleport Coordinates */}
          {manipulationType === 'teleport' && (
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs mb-1">X:</label>
                <input
                  type="number"
                  value={targetX}
                  onChange={(e) => setTargetX(parseInt(e.target.value) || 0)}
                  min="0"
                  max="19"
                  className="w-full bg-black border border-matrix-dim rounded px-2 py-1 text-matrix-green focus:border-matrix-green outline-none"
                />
              </div>
              <div>
                <label className="block text-xs mb-1">Y:</label>
                <input
                  type="number"
                  value={targetY}
                  onChange={(e) => setTargetY(parseInt(e.target.value) || 0)}
                  min="0"
                  max="19"
                  className="w-full bg-black border border-matrix-dim rounded px-2 py-1 text-matrix-green focus:border-matrix-green outline-none"
                />
              </div>
            </div>
          )}

          {/* Energy Boost Amount */}
          {manipulationType === 'energy_boost' && (
            <div>
              <label className="block text-xs mb-1">Boost Amount:</label>
              <input
                type="number"
                value={boostAmount}
                onChange={(e) => setBoostAmount(parseInt(e.target.value) || 50)}
                min="10"
                max="100"
                className="w-full bg-black border border-matrix-dim rounded px-2 py-1 text-matrix-green focus:border-matrix-green outline-none"
              />
            </div>
          )}

          <button
            onClick={handleManipulate}
            disabled={loading}
            className="w-full px-4 py-2 bg-yellow-600 text-white font-bold rounded hover:bg-yellow-500 transition disabled:opacity-50"
          >
            {loading ? 'EXECUTING...' : 'EXECUTE MANIPULATION'}
          </button>
        </div>
      </div>
    </div>
  );
}
