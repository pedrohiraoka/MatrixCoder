'use client';

import React, { useRef, useEffect } from 'react';
import { LogEntry } from '@/lib/matrix_types';

interface LogStreamProps {
  logs: LogEntry[];
  filtroAwaken?: boolean;
  onClear?: () => void;
}

export default function LogStream({
  logs,
  filtroAwaken = false,
  onClear,
}: LogStreamProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll para o último log
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  // Filtra logs se necessário
  const logsFiltrados = filtroAwaken
    ? logs.filter((log) => log.nivel === 'AWAKEN')
    : logs;

  const getLogClass = (nivel: string) => {
    switch (nivel) {
      case 'INFO':
        return 'log-info';
      case 'WARN':
        return 'log-warn';
      case 'ERROR':
        return 'log-error';
      case 'AWAKEN':
        return 'log-awaken';
      default:
        return 'log-info';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    } catch {
      return timestamp;
    }
  };

  return (
    <div className="bg-matrix-bg-secondary border border-matrix-green rounded p-3 h-full flex flex-col">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-sm font-mono text-neon">LOGS DO SISTEMA</h3>
        <div className="flex gap-2">
          <span className="text-xs text-matrix-dim">
            {logsFiltrados.length} entries
          </span>
          {onClear && (
            <button
              className="text-xs text-matrix-dim hover:text-matrix-green"
              onClick={onClear}
            >
              Limpar
            </button>
          )}
        </div>
      </div>

      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto font-mono text-xs space-y-1"
      >
        {logsFiltrados.length === 0 ? (
          <div className="text-matrix-dim italic py-4 text-center">
            Nenhum log...
          </div>
        ) : (
          logsFiltrados.map((log, index) => (
            <div
              key={log.id || index}
              className={`log-entry ${getLogClass(log.nivel)}`}
            >
              <span className="text-matrix-dim mr-2">
                [{formatTimestamp(log.timestamp)}]
              </span>
              <span className="font-bold mr-2">[{log.nivel}]</span>
              <span>{log.mensagem}</span>
              {log.contexto && (
                <details className="mt-1 ml-4 text-matrix-dim">
                  <summary className="cursor-pointer hover:text-matrix-green">
                    Detalhes
                  </summary>
                  <pre className="mt-1 text-xs overflow-x-auto">
                    {JSON.stringify(log.contexto, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
