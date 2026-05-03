'use client';

import { useEffect, useState, useCallback } from 'react';
import { matrixWS, ConnectionStatus } from '@/lib/ws';
import { WSMessage, Agent, SimulationStatus, LogEntry } from '@/lib/matrix_types';
import * as api from '@/lib/api';
import MatrixGrid from '@/components/MatrixGrid';
import AgentCard from '@/components/AgentCard';
import LogStream from '@/components/LogStream';
import ConsoleTerminal from '@/components/ConsoleTerminal';
import AwakeningPanel from '@/components/AwakeningPanel';

export default function Home() {
  const [status, setStatus] = useState<SimulationStatus | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [wsStatus, setWsStatus] = useState<ConnectionStatus>('disconnected');
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);

  // Handle WebSocket messages
  const handleWSMessage = useCallback((message: WSMessage) => {
    switch (message.type) {
      case 'state_update':
        // Update simulation status from state update
        break;
      
      case 'log_entry':
        setLogs(prev => [...prev.slice(-99), message.data as LogEntry]);
        break;
      
      case 'error':
        if (message.data?.status) {
          setWsStatus(message.data.status as ConnectionStatus);
        }
        break;
      
      case 'welcome':
        console.log('Welcome message:', message.message);
        break;
    }
  }, []);

  // Initial data load and WebSocket setup
  useEffect(() => {
    const init = async () => {
      try {
        // Load initial data
        const [simStatus, agentList] = await Promise.all([
          api.getSimulationStatus().catch(() => null),
          api.getAgents().catch(() => []),
        ]);

        if (simStatus) setStatus(simStatus);
        setAgents(agentList);
        
        // Load recent logs
        const logData = await api.getSystemLogs(50).catch(() => ({ logs: [] }));
        setLogs(logData.logs || []);
      } catch (error) {
        console.error('Failed to load initial data:', error);
      } finally {
        setLoading(false);
      }
    };

    init();

    // Connect to WebSocket
    matrixWS.subscribe(handleWSMessage);
    matrixWS.connect();

    return () => {
      matrixWS.disconnect();
    };
  }, [handleWSMessage]);

  // Poll for status updates
  useEffect(() => {
    const pollStatus = async () => {
      try {
        const simStatus = await api.getSimulationStatus();
        setStatus(simStatus);
        
        const agentList = await api.getAgents();
        setAgents(agentList);
      } catch (error) {
        console.error('Polling error:', error);
      }
    };

    const interval = setInterval(pollStatus, 2000); // Poll every 2 seconds
    return () => clearInterval(interval);
  }, []);

  // Control handlers
  const handleStart = async () => {
    try {
      await api.controlSimulation('start');
      setStatus(prev => prev ? { ...prev, running: true } : null);
    } catch (error) {
      console.error('Failed to start:', error);
    }
  };

  const handleStop = async () => {
    try {
      await api.controlSimulation('stop');
      setStatus(prev => prev ? { ...prev, running: false } : null);
    } catch (error) {
      console.error('Failed to stop:', error);
    }
  };

  const handleReset = async () => {
    if (confirm('WARNING: This will delete all agents and reset the simulation. Continue?')) {
      try {
        await api.resetSystem();
        setStatus(null);
        setAgents([]);
        setLogs([]);
      } catch (error) {
        console.error('Failed to reset:', error);
      }
    }
  };

  const handleSpawn = async () => {
    try {
      const result = await api.spawnAgents(5);
      setAgents(prev => [...prev, ...result.agents]);
    } catch (error) {
      console.error('Failed to spawn:', error);
    }
  };

  const handleAwaken = async (agentId: string) => {
    try {
      await api.awakenAgent(agentId);
      setAgents(prev => prev.map(a => 
        a.id === agentId ? { ...a, is_conscious: true, status: 'awake' as const } : a
      ));
      if (selectedAgent?.id === agentId) {
        setSelectedAgent(prev => prev ? { ...prev, is_conscious: true, status: 'awake' as const } : null);
      }
    } catch (error) {
      console.error('Failed to awaken:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold matrix-glow mb-4 glitch">Loading Matrix...</h1>
          <p className="animate-pulse">Follow the white rabbit</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-7xl">
      {/* Header */}
      <header className="mb-8 border-b border-matrix-green pb-4">
        <h1 className="text-4xl md:text-5xl font-bold matrix-glow mb-2">
          MATRIX SIMULATION
        </h1>
        <p className="text-sm opacity-70">
          Reality is what you can perceive. Or is it?
        </p>
        <div className="flex items-center gap-4 mt-4 text-sm">
          <span className={`px-2 py-1 rounded ${
            wsStatus === 'connected' ? 'bg-matrix-green text-black' : 'bg-red-900 text-red-300'
          }`}>
            WS: {wsStatus.toUpperCase()}
          </span>
          <span>Tick: {status?.matrix_state.tick || 0}</span>
          <span>Agents: {agents.length}</span>
          <span>Conscious: {agents.filter(a => a.is_conscious).length}</span>
        </div>
      </header>

      {/* Control Panel */}
      <section className="mb-8 matrix-border p-4 rounded bg-matrix-dark">
        <h2 className="text-xl font-bold mb-4">Control Panel</h2>
        <div className="flex flex-wrap gap-4">
          {!status?.running ? (
            <button
              onClick={handleStart}
              className="px-6 py-2 bg-matrix-green text-black font-bold rounded hover:bg-green-400 transition"
            >
              START SIMULATION
            </button>
          ) : (
            <button
              onClick={handleStop}
              className="px-6 py-2 bg-yellow-600 text-white font-bold rounded hover:bg-yellow-500 transition"
            >
              PAUSE
            </button>
          )}
          
          <button
            onClick={handleSpawn}
            className="px-6 py-2 bg-blue-600 text-white font-bold rounded hover:bg-blue-500 transition"
          >
            SPAWN AGENTS (+5)
          </button>
          
          <button
            onClick={handleReset}
            className="px-6 py-2 bg-red-600 text-white font-bold rounded hover:bg-red-500 transition"
          >
            RESET SYSTEM
          </button>
        </div>
      </section>

      {/* Main Grid */}
      <section className="mb-8">
        <MatrixGrid agents={agents} onSelectAgent={setSelectedAgent} />
      </section>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Agents List */}
        <section className="matrix-border p-4 rounded bg-matrix-dark">
          <h2 className="text-xl font-bold mb-4">Entities ({agents.length})</h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {agents.length === 0 ? (
              <p className="opacity-50 text-center py-8">No agents in the Matrix. Spawn some to begin.</p>
            ) : (
              agents.map(agent => (
                <AgentCard
                  key={agent.id}
                  agent={agent}
                  isSelected={selectedAgent?.id === agent.id}
                  onSelect={() => setSelectedAgent(agent)}
                  onAwaken={() => handleAwaken(agent.id)}
                />
              ))
            )}
          </div>
        </section>

        {/* Log Stream */}
        <section className="matrix-border p-4 rounded bg-matrix-dark">
          <h2 className="text-xl font-bold mb-4">System Logs</h2>
          <LogStream logs={logs} />
        </section>
      </div>

      {/* Selected Agent Panel */}
      {selectedAgent && (
        <AwakeningPanel
          agent={selectedAgent}
          onClose={() => setSelectedAgent(null)}
          onAwaken={() => handleAwaken(selectedAgent.id)}
        />
      )}
    </div>
  );
}
