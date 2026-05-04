'use client';

import React from 'react';
import { Agente } from '@/lib/matrix_types';

interface AwakeningPanelProps {
  agente: Agente | null;
  isOpen: boolean;
  onConfirm: (id: string) => void;
  onCancel: () => void;
}

export default function AwakeningPanel({
  agente,
  isOpen,
  onConfirm,
  onCancel,
}: AwakeningPanelProps) {
  if (!isOpen || !agente) return null;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 animate-fade-in-up">
      <div className="bg-matrix-bg-secondary border-2 border-matrix-cyan rounded-lg p-6 max-w-md w-full mx-4 shadow-neon-cyan animate-glitch">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-mono text-cyan mb-2 animate-pulse">
            DESPERTAR AGENTE
          </h2>
          <div className="w-full h-px bg-gradient-to-r from-transparent via-matrix-cyan to-transparent mb-4" />
          
          <p className="text-sm text-matrix-dim mb-4">
            Deseja despertar este agente?
          </p>
          
          <div className="bg-matrix-bg border border-matrix-cyan rounded p-4 mb-4">
            <div className="font-mono text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-matrix-dim">ID:</span>
                <span className="text-matrix-green">{agente.id.slice(0, 12)}...</span>
              </div>
              <div className="flex justify-between">
                <span className="text-matrix-dim">Energia:</span>
                <span className={agente.energia < 20 ? 'text-red-500' : 'text-matrix-green'}>
                  {agente.energia.toFixed(1)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-matrix-dim">Posição:</span>
                <span>({agente.posicao_x}, {agente.posicao_y})</span>
              </div>
            </div>
          </div>

          <p className="text-xs text-matrix-cyan italic mb-2">
            "Ele verá a verdade por trás da simulação."
          </p>
          
          <p className="text-xs text-matrix-dim">
            Follow the white rabbit...
          </p>
        </div>

        <div className="flex gap-3">
          <button
            className="btn-matrix flex-1 border-matrix-dim text-matrix-dim hover:border-matrix-dim hover:text-matrix-dim"
            onClick={onCancel}
          >
            Cancelar
          </button>
          
          <button
            className="btn-matrix flex-1 bg-matrix-cyan text-matrix-bg border-matrix-cyan hover:bg-matrix-green hover:border-matrix-green animate-pulse"
            onClick={() => onConfirm(agente.id)}
          >
            <span className="animate-glitch inline-block">DESPERTAR</span>
          </button>
        </div>

        <div className="mt-4 text-center">
          <p className="text-xs text-matrix-dim">
            ⚠️ Esta ação é irreversível
          </p>
        </div>
      </div>
    </div>
  );
}
