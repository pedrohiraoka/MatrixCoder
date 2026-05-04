'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { getWebSocketManager } from '@/lib/ws';
import { WebSocketState, Agente, CeldaGrid, LogEntry, Metricas } from '@/lib/matrix_types';
import { criarAgente, despertarAgente, removerAgente, resetarSimulacao, injetarAgenteEspecial } from '@/lib/api';
import MatrixGrid from '@/components/MatrixGrid';
import AgentCard from '@/components/AgentCard';
import LogStream from '@/components/LogStream';
import ConsoleTerminal from '@/components/ConsoleTerminal';
import AwakeningPanel from '@/components/AwakeningPanel';

export default function Dashboard() {
  const [wsState, setWsState] = useState<WebSocketState>({
    connected: false,
    error: null,
    grid: [],
    agentes: [],
    logs: [],
    metricas: null,
  });

  const [agenteSelecionado, setAgenteSelecionado] = useState<Agente | null>(null);
  const [awakeningOpen, setAwakeningOpen] = useState(false);
  const [filtroAwaken, setFiltroAwaken] = useState(false);
  const [carregando, setCarregando] = useState(true);

  // Subscribe ao WebSocket
  useEffect(() => {
    const wsManager = getWebSocketManager();
    
    const unsubscribe = wsManager.subscribe((state) => {
      setWsState(state);
      setCarregando(false);
    });

    return () => {
      unsubscribe();
    };
  }, []);

  // Handlers
  const handleCriarAgente = async () => {
    try {
      await criarAgente({ energia: 100 });
    } catch (error: any) {
      console.error('Erro ao criar agente:', error);
    }
  };

  const handleDespertar = async (id: string) => {
    try {
      await despertarAgente(id);
      setAwakeningOpen(false);
      setAgenteSelecionado(null);
    } catch (error: any) {
      console.error('Erro ao despertar agente:', error);
    }
  };

  const handleRemoverAgente = async (id: string) => {
    if (!confirm('Remover este agente da simulação?')) return;
    
    try {
      await removerAgente(id);
      if (agenteSelecionado?.id === id) {
        setAgenteSelecionado(null);
      }
    } catch (error: any) {
      console.error('Erro ao remover agente:', error);
    }
  };

  const handleAgentClick = useCallback((agente: Agente) => {
    setAgenteSelecionado(agente);
    if (!agente.consciente) {
      setAwakeningOpen(true);
    }
  }, []);

  const handleResetarSimulacao = async () => {
    if (!confirm('RESETAR COMPLETAMENTE A SIMULAÇÃO? Esta ação não pode ser desfeita.')) return;
    
    try {
      await resetarSimulacao();
      setAgenteSelecionado(null);
    } catch (error: any) {
      console.error('Erro ao resetar:', error);
    }
  };

  const handleInjetarNeo = async () => {
    try {
      await injetarAgenteEspecial();
    } catch (error: any) {
      console.error('Erro ao injetar agente especial:', error);
    }
  };

  const handleClearLogs = () => {
    setWsState((prev) => ({ ...prev, logs: [] }));
  };

  if (carregando) {
    return (
      <div className="min-h-screen bg-matrix-bg flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl text-neon animate-pulse mb-4">◈</div>
          <p className="font-mono text-matrix-green">Conectando à Matrix...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-matrix-bg p-4 md:p-8">
      {/* Header */}
      <header className="mb-6 border-b border-matrix-green pb-4">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-mono text-neon mb-1">MATRIX SIMULATOR</h1>
            <p className="text-xs text-matrix-dim font-mono">
              {wsState.connected ? '● Conectado' : '○ Desconectado'}
              {wsState.metricas && (
                <span className="ml-4">
                  | Ticks: {wsState.metricas.ticks_executados}
                  <span className="ml-2">| Energia: {wsState.metricas.energia_total_coletada.toFixed(1)}</span>
                </span>
              )}
            </p>
          </div>

          <div className="flex gap-2 flex-wrap">
            <button className="btn-matrix" onClick={handleCriarAgente}>
              + Criar Agente
            </button>
            <button className="btn-matrix" onClick={handleInjetarNeo}>
              Injetar Neo
            </button>
            <button
              className="btn-matrix-danger"
              onClick={handleResetarSimulacao}
            >
              Resetar
            </button>
          </div>
        </div>
      </header>

      {/* Conteúdo principal */}
      <main className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Grid da Matrix */}
        <div className="lg:col-span-2">
          <div className="bg-matrix-bg-secondary border border-matrix-green rounded p-4">
            <h2 className="text-sm font-mono text-neon mb-4">GRID DA MATRIX</h2>
            <div className="overflow-x-auto">
              <MatrixGrid
                grid={wsState.grid.length > 0 ? wsState.grid : []}
                agentes={wsState.agentes}
                onAgentClick={handleAgentClick}
              />
            </div>

            {/* Métricas */}
            {wsState.metricas && (
              <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
                <div className="bg-matrix-bg p-2 rounded border border-matrix-green">
                  <div className="text-matrix-dim">Tempo</div>
                  <div className="text-neon">{wsState.metricas.tempo_simulacao}s</div>
                </div>
                <div className="bg-matrix-bg p-2 rounded border border-matrix-green">
                  <div className="text-matrix-dim">Agentes</div>
                  <div className="text-neon">{wsState.agentes.length}</div>
                </div>
                <div className="bg-matrix-bg p-2 rounded border border-matrix-cyan">
                  <div className="text-matrix-dim">Despertos</div>
                  <div className="text-cyan">{wsState.metricas.agentes_despertos}</div>
                </div>
                <div className="bg-matrix-bg p-2 rounded border border-matrix-green">
                  <div className="text-matrix-dim">Energia Coletada</div>
                  <div className="text-neon">{wsState.metricas.energia_total_coletada.toFixed(1)}</div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Painel lateral */}
        <div className="space-y-6">
          {/* Lista de Agentes */}
          <div className="bg-matrix-bg-secondary border border-matrix-green rounded p-4 max-h-96 overflow-y-auto">
            <h2 className="text-sm font-mono text-neon mb-4">AGENTES ATIVOS</h2>
            {wsState.agentes.length === 0 ? (
              <p className="text-xs text-matrix-dim italic">Nenhum agente ativo</p>
            ) : (
              <div className="space-y-3">
                {wsState.agentes.map((agente) => (
                  <AgentCard
                    key={agente.id}
                    agente={agente}
                    onAwaken={handleDespertar}
                    onRemove={handleRemoverAgente}
                    onSelect={setAgenteSelecionado}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Logs */}
          <div className="h-64">
            <LogStream
              logs={wsState.logs}
              filtroAwaken={filtroAwaken}
              onClear={handleClearLogs}
            />
            <div className="mt-2 flex items-center gap-2">
              <label className="text-xs text-matrix-dim flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={filtroAwaken}
                  onChange={(e) => setFiltroAwaken(e.target.checked)}
                  className="accent-matrix-cyan"
                />
                Apenas despertares
              </label>
            </div>
          </div>
        </div>

        {/* Console Terminal */}
        <div className="lg:col-span-3 h-64">
          <ConsoleTerminal
            agenteSelecionado={agenteSelecionado}
            onComandoExecutado={(resultado) => console.log('Comando executado:', resultado)}
          />
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-8 pt-4 border-t border-matrix-green/30 text-center text-xs text-matrix-dim font-mono">
        <p>Bem-vindo à Matrix. Siga o coelho branco.</p>
        <p className="mt-1">
          {wsState.error && (
            <span className="text-red-500 mr-4">⚠ {wsState.error}</span>
          )}
          {wsState.agentes.filter((a) => a.consciente).length > 0 && (
            <span className="text-cyan">
              ★ {wsState.agentes.filter((a) => a.consciente).length} agente(s) consciente(s) detectado(s)
            </span>
          )}
        </p>
      </footer>

      {/* Modal de Despertar */}
      <AwakeningPanel
        agente={agenteSelecionado}
        isOpen={awakeningOpen}
        onConfirm={handleDespertar}
        onCancel={() => {
          setAwakeningOpen(false);
          setAgenteSelecionado(null);
        }}
      />
    </div>
  );
}
