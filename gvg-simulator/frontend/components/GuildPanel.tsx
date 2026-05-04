'use client'

import { useState } from 'react'

interface GuildPanelProps {
  playerId: string
  guildId: string
  ouro: number
  onStrategy: (strategyType: string, payload: any) => void
}

/**
 * Guild Master Strategic Panel
 * Only visible to players with guild_rank === "Guild Master"
 * Unlocks strategic powers: declare war, capture territory, build structures
 */
export default function GuildPanel({ 
  playerId, 
  guildId, 
  ouro,
  onStrategy 
}: GuildPanelProps) {
  const [selectedAction, setSelectedAction] = useState<string | null>(null)
  const [targetCoords, setTargetCoords] = useState<{x: string, y: string}>({ x: '', y: '' })
  const [structureType, setStructureType] = useState('torre')
  const [targetGuild, setTargetGuild] = useState('')

  const handleCaptureTerritory = () => {
    if (!targetCoords.x || !targetCoords.y) {
      alert('Selecione as coordenadas do território!')
      return
    }

    if (ouro < 100) {
      alert('Ouro insuficiente! Precisa de 100 ouro.')
      return
    }

    onStrategy('capture_territory', {
      target_x: parseInt(targetCoords.x),
      target_y: parseInt(targetCoords.y)
    })

    setTargetCoords({ x: '', y: '' })
    setSelectedAction(null)
  }

  const handleBuildStructure = () => {
    if (!targetCoords.x || !targetCoords.y) {
      alert('Selecione as coordenadas da estrutura!')
      return
    }

    if (ouro < 200) {
      alert('Ouro insuficiente! Precisa de 200 ouro.')
      return
    }

    onStrategy('build_structure', {
      target_x: parseInt(targetCoords.x),
      target_y: parseInt(targetCoords.y),
      structure_type: structureType
    })

    setTargetCoords({ x: '', y: '' })
    setSelectedAction(null)
  }

  const handleDeclareWar = () => {
    onStrategy('declare_war', {
      target_guild: targetGuild || 'todos'
    })

    setTargetGuild('')
    setSelectedAction(null)
  }

  return (
    <div className="medieval-panel">
      <h2 className="text-xl font-bold text-medieval-gold mb-4 flex items-center gap-2">
        👑 Painel do Guild Master
      </h2>
      
      <p className="text-sm text-gray-400 mb-4">
        Guilda: <span className="text-medieval-accent">{guildId}</span>
      </p>

      {/* Action Selection */}
      <div className="space-y-3">
        <div className="grid grid-cols-1 gap-2">
          <button
            onClick={() => setSelectedAction(selectedAction === 'capture' ? null : 'capture')}
            className={`medieval-button w-full text-left ${selectedAction === 'capture' ? 'bg-medieval-accent text-white' : ''}`}
            disabled={ouro < 100}
          >
            ⚔️ Capturar Território (100 ouro)
          </button>

          <button
            onClick={() => setSelectedAction(selectedAction === 'build' ? null : 'build')}
            className={`medieval-button w-full text-left ${selectedAction === 'build' ? 'bg-medieval-accent text-white' : ''}`}
            disabled={ouro < 200}
          >
            🏗️ Construir Estrutura (200 ouro)
          </button>

          <button
            onClick={() => setSelectedAction(selectedAction === 'war' ? null : 'war')}
            className={`medieval-button w-full text-left ${selectedAction === 'war' ? 'bg-medieval-accent text-white' : ''}`}
          >
            🔥 Declarar Guerra
          </button>
        </div>

        {/* Capture Territory Form */}
        {selectedAction === 'capture' && (
          <div className="bg-medieval-bg p-3 rounded border border-medieval-gold">
            <h3 className="text-medieval-gold font-bold mb-2">Capturar Território</h3>
            <div className="space-y-2">
              <div className="flex gap-2">
                <input
                  type="number"
                  placeholder="X (0-19)"
                  value={targetCoords.x}
                  onChange={(e) => setTargetCoords(prev => ({ ...prev, x: e.target.value }))}
                  className="w-full p-2 bg-medieval-dark border border-medieval-gold rounded text-white"
                  min="0"
                  max="19"
                />
                <input
                  type="number"
                  placeholder="Y (0-19)"
                  value={targetCoords.y}
                  onChange={(e) => setTargetCoords(prev => ({ ...prev, y: e.target.value }))}
                  className="w-full p-2 bg-medieval-dark border border-medieval-gold rounded text-white"
                  min="0"
                  max="19"
                />
              </div>
              <button
                onClick={handleCaptureTerritory}
                className="w-full medieval-button bg-medieval-accent"
              >
                Confirmar Captura
              </button>
            </div>
          </div>
        )}

        {/* Build Structure Form */}
        {selectedAction === 'build' && (
          <div className="bg-medieval-bg p-3 rounded border border-medieval-gold">
            <h3 className="text-medieval-gold font-bold mb-2">Construir Estrutura</h3>
            <div className="space-y-2">
              <select
                value={structureType}
                onChange={(e) => setStructureType(e.target.value)}
                className="w-full p-2 bg-medieval-dark border border-medieval-gold rounded text-white"
              >
                <option value="torre">🗼 Torre de Vigia</option>
                <option value="muralha">🧱 Muralha</option>
                <option value="mina">⛏️ Mina</option>
                <option value="acampamento">⛺ Acampamento</option>
              </select>
              
              <div className="flex gap-2">
                <input
                  type="number"
                  placeholder="X (0-19)"
                  value={targetCoords.x}
                  onChange={(e) => setTargetCoords(prev => ({ ...prev, x: e.target.value }))}
                  className="w-full p-2 bg-medieval-dark border border-medieval-gold rounded text-white"
                  min="0"
                  max="19"
                />
                <input
                  type="number"
                  placeholder="Y (0-19)"
                  value={targetCoords.y}
                  onChange={(e) => setTargetCoords(prev => ({ ...prev, y: e.target.value }))}
                  className="w-full p-2 bg-medieval-dark border border-medieval-gold rounded text-white"
                  min="0"
                  max="19"
                />
              </div>
              <button
                onClick={handleBuildStructure}
                className="w-full medieval-button bg-medieval-accent"
              >
                Confirmar Construção
              </button>
            </div>
          </div>
        )}

        {/* Declare War Form */}
        {selectedAction === 'war' && (
          <div className="bg-medieval-bg p-3 rounded border border-medieval-gold">
            <h3 className="text-medieval-gold font-bold mb-2">Declarar Guerra</h3>
            <div className="space-y-2">
              <input
                type="text"
                placeholder="Guilda alvo (ou deixe em branco para todos)"
                value={targetGuild}
                onChange={(e) => setTargetGuild(e.target.value)}
                className="w-full p-2 bg-medieval-dark border border-medieval-gold rounded text-white"
              />
              <button
                onClick={handleDeclareWar}
                className="w-full medieval-button bg-medieval-accent"
              >
                🔥 Declarar Guerra!
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Guild Stats */}
      <div className="mt-4 pt-4 border-t border-medieval-gold/30">
        <h3 className="text-medieval-gold font-bold mb-2">📊 Status da Guilda</h3>
        <div className="text-sm space-y-1">
          <p className="text-gray-300">
            <span className="text-medieval-gold">Seu Ouro:</span> {ouro}
          </p>
          <p className="text-gray-300">
            <span className="text-medieval-gold">Dica:</span> Colete recursos para ganhar ouro
          </p>
          <p className="text-gray-300">
            <span className="text-medieval-gold">Estratégia:</span> Conquiste territórios adjacentes
          </p>
        </div>
      </div>
    </div>
  )
}
