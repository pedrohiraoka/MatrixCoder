'use client';

import { useEffect, useRef } from 'react';
import { LogEntry } from '@/lib/matrix_types';

interface LogStreamProps {
  logs: LogEntry[];
}

export default function LogStream({ logs }: LogStreamProps) {
  const endRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new logs
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'DEBUG': return 'text-gray-400';
      case 'INFO': return 'text-matrix-green';
      case 'WARNING': return 'text-yellow-400';
      case 'ERROR': return 'text-orange-400';
      case 'CRITICAL': return 'text-red-500 font-bold';
      default: return 'text-matrix-green';
    }
  };

  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit',
        fractionalSecondDigits: 3
      });
    } catch {
      return timestamp;
    }
  };

  return (
    <div className="h-96 overflow-y-auto font-mono text-xs bg-black/50 p-2 rounded matrix-border">
      {logs.length === 0 ? (
        <div className="text-center opacity-50 py-8">
          Waiting for system logs...
          <br />
          <span className="text-xs">Start the simulation to see activity</span>
        </div>
      ) : (
        <div className="space-y-1">
          {logs.map((log, index) => (
            <div 
              key={`${log.timestamp}-${index}`}
              className="flex gap-2 hover:bg-matrix-dim/20 px-1 py-0.5 rounded"
            >
              <span className="text-gray-500 whitespace-nowrap">
                [{formatTime(log.timestamp)}]
              </span>
              <span className={`font-bold whitespace-nowrap ${getLevelColor(log.level)}`}>
                {log.level.padEnd(8)}
              </span>
              <span className="text-cyan-400 whitespace-nowrap">
                [{log.source}]
              </span>
              <span className="flex-1 break-all">
                {log.message}
              </span>
            </div>
          ))}
          <div ref={endRef} />
        </div>
      )}
    </div>
  );
}
