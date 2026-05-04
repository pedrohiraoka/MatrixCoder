'use client';

import React from 'react';
import { Agente } from '@/lib/matrix_types';

interface AgentCardProps {
  agente: Agente;
  onAwaken?: (id: string) => void;
  onRemove?: (id: string) => void;
  onSelect?: (agente: Agente) => void;
}

export default function AgentCard({
  agente,
  onAwaken,
  onRemove,
  onSelect,
}: AgentCardProps) {
  const energiaPercent = Math.min(100, (agente.energia / 100) * 100);
  const energiaBaixa = agente.energia < 20;
  const energiaCritica = agente.energia < 10;

  return (
    <div
      className={`agent-card ${agente.consciente ? 'border-matrix-cyan' : ''} cursor-pointer`}
      onClick={() => onSelect?.(agente)}
    >
      <div className="flex justify-between items-start mb-2">
        <span className="font-mono text-xs text-matrix-dim">
          {agente.id.slice(0, 8)}...
        </span>
        {agente.consciente && (
          <span className="text-xs bg-matrix-cyan text-matrix-bg px-2 py-0.5 rounded font-bold animate-pulse">
            DESPERTO
          </span>
        )}
      </div>

      <div className="mb-2">
        <div className="flex justify-between text-xs mb-1">
          <span>Energia</span>
          <span className={energiaBaixa ? 'text-red-500' : ''}>
            {agente.energia.toFixed(1)}
          </span>
        </div>
        <div className="w-full h-2 bg-matrix-bg-secondary rounded overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${
              energiaCritica
                ? 'bg-red-500'
                : energiaBaixa
                ? 'bg-yellow-500'
                : agente.consciente
                ? 'bg-matrix-cyan'
                : 'bg-matrix-green'
            }`}
            style={{ width: `${energiaPercent}%` }}
          />
        </div>
      </div>

      <div className="text-xs text-matrix-dim mb-3">
        <div>Posição: ({agente.posicao_x}, {agente.posicao_y})</div>
        {agente.regras_comportamento && (
          <div className="mt-1">
            Mov: {(agente.regras_comportamento.prob_movimento * 100).toFixed(0)}%
          </div>
        )}
      </div>

      {!agente.consciente && (
        <div className="flex gap-2">
          <button
            className="btn-matrix flex-1 text-xs"
            onClick={(e) => {
              e.stopPropagation();
              onAwaken?.(agente.id);
            }}
            disabled={energiaCritica}
          >
            DESPERTAR
          </button>
          <button
            className="btn-matrix-danger text-xs px-2"
            onClick={(e) => {
              e.stopPropagation();
              onRemove?.(agente.id);
            }}
          >
            ×
          </button>
        </div>
      )}

      {agente.consciente && (
        <div className="text-xs text-matrix-cyan mt-2">
          <div className="animate-pulse">● Conectado à Matrix</div>
        </div>
      )}
    </div>
  );
}
