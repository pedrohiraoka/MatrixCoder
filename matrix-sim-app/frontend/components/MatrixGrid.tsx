'use client';

import React, { useEffect, useState } from 'react';
import { Agente, CeldaGrid } from '@/lib/matrix_types';

interface MatrixGridProps {
  grid: CeldaGrid[][];
  agentes: Agente[];
  onCellClick?: (x: number, y: number) => void;
  onAgentClick?: (agente: Agente) => void;
}

export default function MatrixGrid({
  grid,
  agentes,
  onCellClick,
  onAgentClick,
}: MatrixGridProps) {
  const gridSize = grid.length || 10;

  // Cria mapa de agentes para acesso rápido
  const agenteMap = new Map<string, Agente>();
  agentes.forEach((ag) => agenteMap.set(ag.id, ag));

  const handleCellClick = (x: number, y: number) => {
    const celula = grid[y]?.[x];
    if (celula?.ocupado && celula.agente_id) {
      const agente = agenteMap.get(celula.agente_id);
      if (agente && onAgentClick) {
        onAgentClick(agente);
      }
    } else if (onCellClick) {
      onCellClick(x, y);
    }
  };

  return (
    <div className="inline-block border-2 border-matrix-green p-2 rounded bg-matrix-bg shadow-neon-green">
      <div
        className="grid gap-1"
        style={{
          gridTemplateColumns: `repeat(${gridSize}, minmax(0, 1fr))`,
        }}
      >
        {grid.length === 0 ? (
          // Renderiza grid vazio inicial
          Array.from({ length: 10 }).map((_, y) =>
            Array.from({ length: 10 }).map((_, x) => (
              <div
                key={`${x}-${y}`}
                className="matrix-cell matrix-cell-empty cursor-pointer hover:border-matrix-green"
                onClick={() => handleCellClick(x, y)}
              />
            ))
          )
        ) : (
          grid.map((linha, y) =>
            linha.map((celula, x) => {
              const agente = celula.ocupado && celula.agente_id
                ? agenteMap.get(celula.agente_id)
                : null;

              let cellClass = 'matrix-cell matrix-cell-empty cursor-pointer';

              if (agente) {
                if (agente.consciente) {
                  cellClass = 'matrix-cell matrix-cell-awake cursor-pointer';
                } else {
                  cellClass = 'matrix-cell matrix-cell-agent cursor-pointer';
                }
              }

              return (
                <div
                  key={`${x}-${y}`}
                  className={cellClass}
                  onClick={() => handleCellClick(x, y)}
                  title={
                    agente
                      ? `ID: ${agente.id.slice(0, 8)}...\nEnergia: ${agente.energia.toFixed(1)}\nConsciente: ${agente.consciente ? 'SIM' : 'NÃO'}`
                      : `Posição: (${x}, ${y})`
                  }
                />
              );
            })
          )
        )}
      </div>

      {/* Legenda */}
      <div className="mt-4 flex gap-4 text-xs font-mono">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-matrix-bg-secondary border border-matrix-green"></div>
          <span>Vazio</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-matrix-green opacity-50"></div>
          <span>Agente</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-matrix-cyan animate-pulse"></div>
          <span className="text-cyan">Desperto</span>
        </div>
      </div>
    </div>
  );
}
