'use client'

import { useState } from 'react'
import { processData, DataProcessRequest } from '@/lib/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function DataPanel() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  
  // Transformations
  const [transformations, setTransformations] = useState<string[]>(['normalize'])

  // Generate sample data
  const generateSampleData = () => {
    return Array.from({ length: 100 }, (_, i) => ({
      id: i,
      timestamp: new Date(Date.now() - i * 60000).toISOString(),
      value: Math.random() * 100,
      category: ['A', 'B', 'C'][Math.floor(Math.random() * 3)],
      score: Math.random() * 10,
    }))
  }

  const handleProcess = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const data = generateSampleData()
      const request: DataProcessRequest = {
        data,
        transformations,
      }
      
      const response = await processData(request)
      setResult(response)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const toggleTransformation = (t: string) => {
    setTransformations((prev) =>
      prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]
    )
  }

  const metricsData = result?.metrics
    ? [
        { name: 'Rows', value: result.metrics.rows },
        { name: 'Columns', value: result.metrics.columns },
        { name: 'Nulls', value: result.metrics.null_count },
      ]
    : []

  return (
    <div className="bg-matrix-gray/50 border border-matrix-green/30 rounded-lg p-6 glow-border">
      <h2 className="text-2xl font-bold mb-4 glow-text">🧬 O Construto - Manipulação de Dados</h2>
      <p className="text-sm text-matrix-green/70 mb-6">
        Transforme fluxos massivos de dados da Matrix
      </p>

      {/* Transformations */}
      <div className="mb-6">
        <label className="block text-xs mb-2">Transformações:</label>
        <div className="flex flex-wrap gap-2">
          {['normalize', 'aggregate', 'rolling_mean', 'log_transform'].map((t) => (
            <button
              key={t}
              onClick={() => toggleTransformation(t)}
              className={`px-3 py-1 text-xs border rounded transition-all ${
                transformations.includes(t)
                  ? 'bg-matrix-green text-matrix-black border-matrix-green'
                  : 'bg-matrix-black text-matrix-green border-matrix-green/30 hover:border-matrix-green'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={handleProcess}
        disabled={loading}
        className="w-full bg-matrix-green/20 hover:bg-matrix-green/30 border border-matrix-green rounded px-4 py-2 text-sm font-bold transition-all disabled:opacity-50"
      >
        {loading ? 'PROCESSANDO...' : 'PROCESSAR DADOS SINTÉTICOS'}
      </button>

      {/* Results */}
      {result && (
        <div className="mt-6 space-y-4">
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold">{result.rows_processed}</div>
              <div className="text-xs text-matrix-green/70">Linhas</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{result.columns.length}</div>
              <div className="text-xs text-matrix-green/70">Colunas</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{result.metrics.memory_usage_bytes}</div>
              <div className="text-xs text-matrix-green/70">Bytes</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{result.metrics.null_count}</div>
              <div className="text-xs text-matrix-green/70">Nulos</div>
            </div>
          </div>

          {/* Metrics Chart */}
          {metricsData.length > 0 && (
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metricsData}>
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
                  <Bar dataKey="value" fill="#008F11" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Preview */}
          {result.preview && result.preview.length > 0 && (
            <div>
              <h3 className="text-sm font-bold mb-2">PREVIEW DOS DADOS</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-matrix-green/30">
                      {Object.keys(result.preview[0]).map((key) => (
                        <th key={key} className="text-left p-2 text-matrix-green/70">
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.preview.map((row: any, i: number) => (
                      <tr key={i} className="border-b border-matrix-green/10 hover:bg-matrix-green/5">
                        {Object.values(row).map((val: any, j: number) => (
                          <td key={j} className="p-2">
                            {typeof val === 'number' ? val.toFixed(2) : String(val).slice(0, 20)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
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
    </div>
  )
}
