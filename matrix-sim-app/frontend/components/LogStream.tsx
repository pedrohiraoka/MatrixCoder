'use client'

import { useState, useEffect } from 'react'
import { logStreamClient, LogMessage } from '@/lib/ws'

export default function LogStream() {
  const [logs, setLogs] = useState<LogMessage[]>([])
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const connect = async () => {
      try {
        await logStreamClient.connect()
        setConnected(true)
      } catch (error) {
        console.error('Failed to connect to log stream:', error)
        setConnected(false)
      }
    }

    connect()

    const unsubscribe = logStreamClient.subscribe((message) => {
      setLogs((prev) => [...prev.slice(-99), message])
    })

    // Heartbeat
    const interval = setInterval(() => {
      if (logStreamClient.isConnected()) {
        logStreamClient.send({ type: 'heartbeat' })
      }
    }, 10000)

    return () => {
      unsubscribe()
      clearInterval(interval)
    }
  }, [])

  const clearLogs = () => setLogs([])

  return (
    <div className="bg-matrix-gray/50 border border-matrix-green/30 rounded-lg p-6 glow-border">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold glow-text">📡 Stream de Logs</h2>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${connected ? 'bg-matrix-green animate-pulse' : 'bg-red-500'}`} />
          <span className="text-xs">{connected ? 'CONECTADO' : 'DESCONECTADO'}</span>
          <button
            onClick={clearLogs}
            className="ml-2 text-xs text-matrix-green/70 hover:text-matrix-green underline"
          >
            Limpar
          </button>
        </div>
      </div>

      <div className="h-64 overflow-y-auto bg-matrix-black border border-matrix-green/20 rounded p-3 text-xs font-mono">
        {logs.length === 0 ? (
          <div className="text-matrix-green/30 text-center py-8">
            Aguardando logs da Matrix...
          </div>
        ) : (
          logs.map((log, i) => (
            <div
              key={i}
              className={`mb-1 pb-1 border-b border-matrix-green/10 last:border-0 ${
                log.type === 'error' ? 'text-red-400' : 'text-matrix-green/70'
              }`}
            >
              <span className="text-matrix-dark-green">[{new Date(log.timestamp).toLocaleTimeString()}]</span>{' '}
              <span className="text-matrix-green font-bold">{log.type.toUpperCase()}</span>:{' '}
              {log.message || JSON.stringify(log.data)}
            </div>
          ))
        )}
      </div>

      {/* Quick Stats */}
      <div className="mt-4 grid grid-cols-3 gap-2 text-xs">
        <div className="bg-matrix-black/50 rounded p-2 text-center">
          <div className="font-bold">{logs.length}</div>
          <div className="text-matrix-green/50">Total Logs</div>
        </div>
        <div className="bg-matrix-black/50 rounded p-2 text-center">
          <div className="font-bold">{logs.filter((l) => l.type === 'simulation_result').length}</div>
          <div className="text-matrix-green/50">Simulações</div>
        </div>
        <div className="bg-matrix-black/50 rounded p-2 text-center">
          <div className="font-bold">{connected ? '✓' : '✗'}</div>
          <div className="text-matrix-green/50">WS Status</div>
        </div>
      </div>
    </div>
  )
}
