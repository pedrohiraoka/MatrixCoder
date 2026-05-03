'use client'

import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { simulateML, MLSimulationRequest } from '@/lib/api'
import { logStreamClient, LogMessage } from '@/lib/ws'

export default function MLPanel() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [logs, setLogs] = useState<LogMessage[]>([])
  
  // Form state
  const [nSamples, setNSamples] = useState(1000)
  const [nFeatures, setNFeatures] = useState(5)
  const [contamination, setContamination] = useState(0.1)

  useEffect(() => {
    // Connect to WebSocket for real-time logs
    logStreamClient.connect().catch(console.error)
    
    const unsubscribe = logStreamClient.subscribe((message) => {
      setLogs((prev) => [...prev.slice(-49), message])
    })

    return () => {
      unsubscribe()
    }
  }, [])

  const handleSimulate = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const request: MLSimulationRequest = {
        n_samples: nSamples,
        n_features: nFeatures,
        contamination: contamination,
      }
      
      const response = await simulateML(request)
      setResult(response)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const chartData = result?.summary_stats?.mean 
    ? Object.entries(result.summary_stats.mean).map(([key, value]: [string, any]) => ({
        name: key,
        mean: value,
        std: result.summary_stats.std[key],
      }))
    : []

  return (
    <div className="bg-matrix-gray/50 border border-matrix-green/30 rounded-lg p-6 glow-border">
      <h2 className="text-2xl font-bold mb-4 glow-text">👁️ O Agente - Simulação ML</h2>
      <p className="text-sm text-matrix-green/70 mb-6">
        Detecte &quot;glitches&quot; na Matrix usando Isolation Forest
      </p>

      {/* Controls */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-xs mb-1">Amostras</label>
          <input
            type="number"
            value={nSamples}
            onChange={(e) => setNSamples(Number(e.target.value))}
            className="w-full bg-matrix-black border border-matrix-green/30 rounded px-2 py-1 text-sm focus:outline-none focus:border-matrix-green"
            min={100}
            max={10000}
          />
        </div>
        <div>
          <label className="block text-xs mb-1">Features</label>
          <input
            type="number"
            value={nFeatures}
            onChange={(e) => setNFeatures(Number(e.target.value))}
            className="w-full bg-matrix-black border border-matrix-green/30 rounded px-2 py-1 text-sm focus:outline-none focus:border-matrix-green"
            min={2}
            max={20}
          />
        </div>
        <div>
          <label className="block text-xs mb-1">Contaminação</label>
          <input
            type="number"
            value={contamination}
            onChange={(e) => setContamination(Number(e.target.value))}
            className="w-full bg-matrix-black border border-matrix-green/30 rounded px-2 py-1 text-sm focus:outline-none focus:border-matrix-green"
            min={0.01}
            max={0.5}
            step={0.01}
          />
        </div>
      </div>

      <button
        onClick={handleSimulate}
        disabled={loading}
        className="w-full bg-matrix-green/20 hover:bg-matrix-green/30 border border-matrix-green rounded px-4 py-2 text-sm font-bold transition-all disabled:opacity-50"
      >
        {loading ? 'SIMULANDO...' : 'EXECUTAR SIMULAÇÃO'}
      </button>

      {/* Results */}
      {result && (
        <div className="mt-6 space-y-4">
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold">{result.total_samples}</div>
              <div className="text-xs text-matrix-green/70">Total</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-400">{result.anomalies_detected}</div>
              <div className="text-xs text-matrix-green/70">Anomalias</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{result.anomaly_percentage.toFixed(1)}%</div>
              <div className="text-xs text-matrix-green/70">Porcentagem</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{result.processing_time_ms}ms</div>
              <div className="text-xs text-matrix-green/70">Tempo</div>
            </div>
          </div>

          {/* Chart */}
          {chartData.length > 0 && (
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#008F11" />
                  <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 10 }} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#0A0A0A', 
                      border: '1px solid #00FF41',
                      fontSize: '12px'
                    }} 
                  />
                  <Bar dataKey="mean" fill="#00FF41" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mt-4 p-3 bg-red-900/30 border border-red-500 rounded text-sm text-red-300">
          ERRO: {error}
        </div>
      )}

      {/* Logs */}
      {logs.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-bold mb-2">LOGS EM TEMPO REAL</h3>
          <div className="h-32 overflow-y-auto bg-matrix-black border border-matrix-green/20 rounded p-2 text-xs font-mono">
            {logs.map((log, i) => (
              <div key={i} className="text-matrix-green/70">
                [{new Date(log.timestamp).toLocaleTimeString()}] {log.type}: {log.message || JSON.stringify(log.data)}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
