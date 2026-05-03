'use client'

import { useState } from 'react'
import MatrixRain from '@/components/MatrixRain'
import MLPanel from '@/components/MLPanel'
import DataPanel from '@/components/DataPanel'
import CryptoPanel from '@/components/CryptoPanel'
import LogStream from '@/components/LogStream'

type Tab = 'ml' | 'data' | 'crypto'

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<Tab>('ml')

  return (
    <div className="min-h-screen relative">
      {/* Matrix Rain Background */}
      <MatrixRain opacity={0.25} />

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-4xl md:text-6xl font-bold mb-2 glow-text">
            MATRIX SIMULATION
          </h1>
          <p className="text-matrix-green/70 text-sm md:text-base">
            Python e a Simulação da Matrix — ML • Dados • Criptografia
          </p>
        </header>

        {/* Tabs */}
        <div className="flex justify-center gap-2 mb-8">
          <button
            onClick={() => setActiveTab('ml')}
            className={`px-4 py-2 text-sm border rounded transition-all ${
              activeTab === 'ml'
                ? 'bg-matrix-green text-matrix-black border-matrix-green font-bold'
                : 'bg-matrix-black text-matrix-green border-matrix-green/30 hover:border-matrix-green'
            }`}
          >
            👁️ O Agente (ML)
          </button>
          <button
            onClick={() => setActiveTab('data')}
            className={`px-4 py-2 text-sm border rounded transition-all ${
              activeTab === 'data'
                ? 'bg-matrix-green text-matrix-black border-matrix-green font-bold'
                : 'bg-matrix-black text-matrix-green border-matrix-green/30 hover:border-matrix-green'
            }`}
          >
            🧬 O Construto (Dados)
          </button>
          <button
            onClick={() => setActiveTab('crypto')}
            className={`px-4 py-2 text-sm border rounded transition-all ${
              activeTab === 'crypto'
                ? 'bg-matrix-green text-matrix-black border-matrix-green font-bold'
                : 'bg-matrix-black text-matrix-green border-matrix-green/30 hover:border-matrix-green'
            }`}
          >
            🔐 O Cofre (Crypto)
          </button>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Active Panel */}
          <div className="lg:col-span-2">
            {activeTab === 'ml' && <MLPanel />}
            {activeTab === 'data' && <DataPanel />}
            {activeTab === 'crypto' && <CryptoPanel />}
          </div>

          {/* Right Column - Log Stream */}
          <div className="lg:col-span-1">
            <LogStream />

            {/* Info Card */}
            <div className="mt-6 bg-matrix-gray/50 border border-matrix-green/30 rounded-lg p-6 glow-border">
              <h3 className="text-lg font-bold mb-3 glow-text">ℹ️ Sobre</h3>
              <ul className="text-xs text-matrix-green/70 space-y-2">
                <li>• <strong>ML:</strong> Isolation Forest detecta anomalias (&quot;glitches&quot;)</li>
                <li>• <strong>Dados:</strong> Pandas transforma fluxos massivos</li>
                <li>• <strong>Crypto:</strong> Fernet (AES-CBC + HMAC) protege dados</li>
                <li>• <strong>Real-time:</strong> WebSockets para streaming de logs</li>
              </ul>
              
              <div className="mt-4 pt-4 border-t border-matrix-green/20">
                <h4 className="text-xs font-bold mb-2">ENDPOINTS</h4>
                <code className="text-xs text-matrix-dark-green block">
                  POST /api/ml/simulate<br/>
                  POST /api/data/process<br/>
                  POST /api/crypto/encrypt<br/>
                  POST /api/crypto/decrypt<br/>
                  WS /ws/logs
                </code>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-xs text-matrix-green/30">
          <p>Wake up, Neo... The Matrix has you.</p>
          <p className="mt-1">Built with FastAPI + Next.js + Python</p>
        </footer>
      </div>
    </div>
  )
}
