'use client'

import { useState } from 'react'
import { encryptData, decryptData } from '@/lib/api'

export default function CryptoPanel() {
  const [loading, setLoading] = useState(false)
  const [encryptResult, setEncryptResult] = useState<string | null>(null)
  const [decryptResult, setDecryptResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  // Input state
  const [payload, setPayload] = useState('Mensagem secreta da Matrix')
  const [encryptedInput, setEncryptedInput] = useState('')

  const handleEncrypt = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await encryptData(payload)
      setEncryptResult(response.result)
      setEncryptedInput(response.result)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDecrypt = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await decryptData(encryptedInput || encryptResult || '')
      setDecryptResult(response.result)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  return (
    <div className="bg-matrix-gray/50 border border-matrix-green/30 rounded-lg p-6 glow-border">
      <h2 className="text-2xl font-bold mb-4 glow-text">🔐 O Cofre - Criptografia</h2>
      <p className="text-sm text-matrix-green/70 mb-6">
        Proteja dados com criptografia Fernet de ponta a ponta
      </p>

      {/* Encrypt Section */}
      <div className="mb-6">
        <label className="block text-xs mb-2">Payload para Criptografar:</label>
        <textarea
          value={payload}
          onChange={(e) => setPayload(e.target.value)}
          className="w-full bg-matrix-black border border-matrix-green/30 rounded px-3 py-2 text-sm focus:outline-none focus:border-matrix-green h-20 resize-none"
        />
        <button
          onClick={handleEncrypt}
          disabled={loading || !payload}
          className="mt-2 w-full bg-matrix-green/20 hover:bg-matrix-green/30 border border-matrix-green rounded px-4 py-2 text-sm font-bold transition-all disabled:opacity-50"
        >
          {loading ? 'CRIPTOGRAFANDO...' : '🔒 CRIPTOGRAFAR'}
        </button>
      </div>

      {/* Encrypted Result */}
      {encryptResult && (
        <div className="mb-6">
          <label className="block text-xs mb-2">Resultado Criptografado:</label>
          <div className="relative">
            <textarea
              readOnly
              value={encryptResult}
              className="w-full bg-matrix-black border border-matrix-green/30 rounded px-3 py-2 text-xs font-mono focus:outline-none h-24 resize-none break-all"
            />
            <button
              onClick={() => copyToClipboard(encryptResult)}
              className="absolute top-1 right-1 bg-matrix-green/20 hover:bg-matrix-green/30 border border-matrix-green/50 rounded px-2 py-1 text-xs"
            >
              Copiar
            </button>
          </div>
        </div>
      )}

      {/* Decrypt Section */}
      <div className="mb-4">
        <label className="block text-xs mb-2">Dados para Descriptografar:</label>
        <textarea
          value={encryptedInput}
          onChange={(e) => setEncryptedInput(e.target.value)}
          placeholder="Cole o texto criptografado aqui..."
          className="w-full bg-matrix-black border border-matrix-green/30 rounded px-3 py-2 text-sm font-mono focus:outline-none focus:border-matrix-green h-24 resize-none"
        />
        <button
          onClick={handleDecrypt}
          disabled={loading || !encryptedInput}
          className="mt-2 w-full bg-matrix-dark-green/30 hover:bg-matrix-dark-green/50 border border-matrix-dark-green rounded px-4 py-2 text-sm font-bold transition-all disabled:opacity-50"
        >
          {loading ? 'DESCRIPTOGRAFANDO...' : '🔓 DECRYPT'}
        </button>
      </div>

      {/* Decrypted Result */}
      {decryptResult && (
        <div>
          <label className="block text-xs mb-2">Resultado Descriptografado:</label>
          <div className="p-3 bg-matrix-green/10 border border-matrix-green/30 rounded text-sm">
            {decryptResult}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mt-4 p-3 bg-red-900/30 border border-red-500 rounded text-sm text-red-300">
          ERRO: {error}
        </div>
      )}

      {/* Info */}
      <div className="mt-6 text-xs text-matrix-green/50">
        <p>Algoritmo: Fernet (AES-CBC 128-bit + HMAC)</p>
        <p>Todos os logs são registrados no sistema.</p>
      </div>
    </div>
  )
}
