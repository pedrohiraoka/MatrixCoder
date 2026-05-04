'use client'

import { useState, useEffect } from 'react'

interface WorldGridProps {
  worldState: any
  playerId: string
  onMove: (direction: string) => void
  onCollect: () => void
}

/**
 * 20x20 Interactive World Grid
 * Renders terrain, resources, dangers, and player position
 */
export default function WorldGrid({ 
  worldState, 
  playerId, 
  onMove, 
  onCollect 
}: WorldGridProps) {
  const [selectedTile, setSelectedTile] = useState<{x: number, y: number} | null>(null)
  const [playerPosition, setPlayerPosition] = useState<[number, number]>([0, 0])

  // Update player position when world state changes
  useEffect(() => {
    if (worldState?.jogadores?.[playerId]?.position) {
      setPlayerPosition(worldState.jogadores[playerId].position)
    }
  }, [worldState?.jogadores, playerId])

  // Keyboard controls
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!worldState) return
      
      switch (e.key.toLowerCase()) {
        case 'arrowup':
        case 'w':
          e.preventDefault()
          onMove('up')
          break
        case 'arrowdown':
        case 's':
          e.preventDefault()
          onMove('down')
          break
        case 'arrowleft':
        case 'a':
          e.preventDefault()
          onMove('left')
          break
        case 'arrowright':
        case 'd':
          e.preventDefault()
          onMove('right')
          break
        case ' ':
          e.preventDefault()
          onCollect()
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onMove, onCollect, worldState])

  if (!worldState || !worldState.grid) {
    return (
      <div className="medieval-panel h-96 flex items-center justify-center">
        <p className="text-medieval-gold animate-pulse">Carregando mundo...</p>
      </div>
    )
  }

  const getTileClass = (tile: any) => {
    let baseClass = 'cell'
    
    if (tile.perigo) {
      baseClass += ' cell-danger'
    } else if (tile.recurso) {
      baseClass += ' cell-resource'
    } else {
      switch (tile.tile_type) {
        case 'plains': baseClass += ' cell-plains'; break
        case 'forest': baseClass += ' cell-forest'; break
        case 'mountain': baseClass += ' cell-mountain'; break
        case 'water': baseClass += ' cell-water'; break
        case 'castle': baseClass += ' cell-castle'; break
      }
    }
    
    return baseClass
  }

  const getTileContent = (tile: any) => {
    // Player indicator
    if (tile.x === playerPosition[0] && tile.y === playerPosition[1]) {
      return <span className="text-lg">🧙</span>
    }
    
    // Danger indicator
    if (tile.perigo) {
      return <span className="text-lg">⚠️</span>
    }
    
    // Resource indicator
    if (tile.recurso) {
      const icons: Record<string, string> = {
        gold: '💰',
        food: '🍖',
        wood: '🪵',
        iron: '⛏️'
      }
      return <span className="text-lg">{icons[tile.recurso] || '📦'}</span>
    }
    
    // Structure indicator
    if (tile.estrutura) {
      return <span className="text-lg">🏗️</span>
    }
    
    // Castle indicator
    if (tile.tile_type === 'castle') {
      return <span className="text-lg">🏰</span>
    }
    
    // Territory owner indicator
    if (tile.owner_guild) {
      return <span className="text-xs text-medieval-gold font-bold">🚩</span>
    }
    
    return null
  }

  const handleTileClick = (tile: any) => {
    setSelectedTile({ x: tile.x, y: tile.y })
    
    // Auto-collect if resource and player is on this tile
    if (tile.recurso && tile.x === playerPosition[0] && tile.y === playerPosition[1]) {
      onCollect()
    }
  }

  const getTileTooltip = (tile: any) => {
    const parts: string[] = []
    
    parts.push(`(${tile.x}, ${tile.y})`)
    parts.push(tile.tile_type.charAt(0).toUpperCase() + tile.tile_type.slice(1))
    
    if (tile.recurso) {
      parts.push(`Recurso: ${tile.recurso.toUpperCase()}`)
    }
    if (tile.perigo) {
      parts.push(`⚠️ PERIGO: ${tile.perigo.toUpperCase()}`)
    }
    if (tile.owner_guild) {
      parts.push(`🚩 Território: ${tile.owner_guild}`)
    }
    if (tile.estrutura) {
      parts.push(`🏗️ ${tile.estrutura}`)
    }
    if (tile.x === playerPosition[0] && tile.y === playerPosition[1]) {
      parts.push('📍 Sua posição')
    }
    
    return parts.join(' | ')
  }

  return (
    <div className="space-y-4">
      {/* Grid Container */}
      <div className="medieval-panel overflow-auto">
        <div 
          className="grid gap-px bg-gray-800 p-1"
          style={{ 
            gridTemplateColumns: `repeat(${worldState.grid.length}, minmax(0, 1fr))`,
            maxWidth: 'fit-content',
            margin: '0 auto'
          }}
        >
          {worldState.grid.map((row: any[], y: number) => (
            row.map((tile: any, x: number) => (
              <div
                key={`${x}-${y}`}
                className={getTileClass(tile)}
                onClick={() => handleTileClick(tile)}
                title={getTileTooltip(tile)}
              >
                {getTileContent(tile)}
              </div>
            ))
          ))}
        </div>
      </div>

      {/* Selected Tile Info */}
      {selectedTile && worldState.grid[selectedTile.y][selectedTile.x] && (
        <div className="medieval-panel">
          <h3 className="text-medieval-gold font-bold mb-2">
            📍 Tile ({selectedTile.x}, {selectedTile.y})
          </h3>
          <div className="text-sm text-gray-300 space-y-1">
            {(() => {
              const tile = worldState.grid[selectedTile.y][selectedTile.x]
              return (
                <>
                  <p><span className="text-medieval-gold">Terreno:</span> {tile.tile_type}</p>
                  {tile.recurso && (
                    <p><span className="text-medieval-gold">Recurso:</span> {tile.recurso} (+ouro ao coletar)</p>
                  )}
                  {tile.perigo && (
                    <p><span className="text-medieval-accent">Perigo:</span> {tile.perigo}</p>
                  )}
                  {tile.owner_guild && (
                    <p><span className="text-medieval-gold">Dono:</span> {tile.owner_guild}</p>
                  )}
                  {tile.estrutura && (
                    <p><span className="text-medieval-gold">Estrutura:</span> {tile.estrutura}</p>
                  )}
                </>
              )
            })()}
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="medieval-panel">
        <h3 className="text-medieval-gold font-bold mb-2">Legenda</h3>
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-1">
            <span className="w-4 h-4 bg-green-900/50 border border-gray-600"></span>
            <span>Planície</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-4 h-4 bg-emerald-900/60 border border-gray-600"></span>
            <span>Floresta</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-4 h-4 bg-stone-700/70 border border-gray-600"></span>
            <span>Montanha</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-4 h-4 bg-blue-800/60 border border-gray-600"></span>
            <span>Água</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-lg">💰</span>
            <span>Ouro</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-lg">⚠️</span>
            <span>Perigo</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-lg">🧙</span>
            <span>Você</span>
          </div>
        </div>
      </div>
    </div>
  )
}
