'use client'

import { useState, useEffect } from 'react'
import WorldGrid from '@/components/WorldGrid'
import GuildPanel from '@/components/GuildPanel'
import EventLog from '@/components/EventLog'
import useWebSocket from '@/components/hooks/useWebSocket'

export default function Home() {
  const [playerId, setPlayerId] = useState<string>('')
  const [playerName, setPlayerName] = useState<string>('')
  const [guildId, setGuildId] = useState<string>('')
  const [isConnected, setIsConnected] = useState(false)
  const [worldState, setWorldState] = useState<any>(null)
  const [events, setEvents] = useState<any[]>([])
  const [playerData, setPlayerData] = useState<any>(null)

  const { 
    sendMessage, 
    lastMessage, 
    connected 
  } = useWebSocket(playerId, {
    onConnect: () => {
      setIsConnected(true)
      console.log('Conectado ao servidor GvG!')
    },
    onDisconnect: () => {
      setIsConnected(false)
      console.log('Desconectado do servidor')
    },
    onMessage: (message) => {
      handleMessage(message)
    }
  })

  const handleMessage = (message: any) => {
    switch (message.type) {
      case 'initial_state':
        setWorldState(message.state)
        break
      case 'world_update':
      case 'world_state':
        if (message.state) {
          setWorldState(message.state)
        }
        if (message.event) {
          setEvents(prev => [message.event, ...prev].slice(0, 50))
        }
        break
      case 'resource_spawn':
      case 'danger_spawn':
      case 'player_joined':
      case 'player_left':
      case 'guild_created':
      case 'territory_captured':
      case 'structure_built':
      case 'war_declared':
      case 'resource_collected':
      case 'global_event':
        if (message.event) {
          setEvents(prev => [message.event, ...prev].slice(0, 50))
        }
        if (message.state) {
          setWorldState(message.state)
        }
        break
      case 'move_result':
      case 'collect_result':
      case 'strategy_result':
        if (message.player) {
          setPlayerData(message.player)
        }
        break
      case 'recent_events':
        if (message.events) {
          setEvents(prev => [...message.events, ...prev].slice(0, 50))
        }
        break
    }
  }

  const handleLogin = async () => {
    if (!playerId.trim() || !playerName.trim()) return

    try {
      const response = await fetch('http://localhost:8000/player/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_id: playerId,
          name: playerName,
          guild_id: guildId || null,
          guild_rank: 'Member'
        })
      })

      const data = await response.json()
      
      if (data.status === 'success') {
        setPlayerData(data.player)
        // WebSocket will connect automatically via hook
      } else {
        alert('Erro ao criar jogador: ' + JSON.stringify(data))
      }
    } catch (error) {
      console.error('Erro:', error)
      alert('Erro de conexão com o servidor')
    }
  }

  const handleCreateGuild = async () => {
    if (!playerId || !playerName) return

    const guildName = prompt('Nome da guilda:')
    if (!guildName) return

    try {
      const response = await fetch('http://localhost:8000/guild/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          guild_id: `guild_${Date.now()}`,
          name: guildName,
          leader_id: playerId
        })
      })

      const data = await response.json()
      
      if (data.status === 'success') {
        alert(`Guilda "${guildName}" criada! Você é o Guild Master.`)
        setPlayerData(prev => ({
          ...prev,
          guild_id: data.guild.guild_id,
          guild_rank: 'Guild Master'
        }))
      }
    } catch (error) {
      console.error('Erro:', error)
      alert('Erro ao criar guilda')
    }
  }

  if (!playerData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="medieval-panel max-w-md w-full">
          <h1 className="text-3xl font-bold text-medieval-gold text-center mb-6">
            ⚔️ GvG Simulator
          </h1>
          <p className="text-gray-300 text-center mb-6">
            Guerras de Guildas em Tempo Real
          </p>
          
          <div className="space-y-4">
            <div>
              <label className="block text-medieval-gold mb-2">ID do Jogador</label>
              <input
                type="text"
                value={playerId}
                onChange={(e) => setPlayerId(e.target.value)}
                className="w-full p-2 bg-medieval-bg border border-medieval-gold rounded text-white"
                placeholder="ex: player1"
              />
            </div>
            
            <div>
              <label className="block text-medieval-gold mb-2">Nome</label>
              <input
                type="text"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                className="w-full p-2 bg-medieval-bg border border-medieval-gold rounded text-white"
                placeholder="ex: Aragorn"
              />
            </div>
            
            <div>
              <label className="block text-medieval-gold mb-2">Guilda (opcional)</label>
              <input
                type="text"
                value={guildId}
                onChange={(e) => setGuildId(e.target.value)}
                className="w-full p-2 bg-medieval-bg border border-medieval-gold rounded text-white"
                placeholder="ex: guild_123"
              />
            </div>
            
            <button
              onClick={handleLogin}
              disabled={!playerId.trim() || !playerName.trim()}
              className="w-full medieval-button mt-4 disabled:opacity-50"
            >
              Entrar no Mundo
            </button>
            
            <button
              onClick={handleCreateGuild}
              disabled={!playerId.trim() || !playerName.trim()}
              className="w-full medieval-button mt-2 disabled:opacity-50"
            >
              🏰 Criar Nova Guilda
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="medieval-panel flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-medieval-gold">⚔️ GvG Simulator</h1>
          <p className="text-sm text-gray-400">
            {playerData.name} | Ouro: {playerData.ouro} | Conquista: {playerData.pontos_conquista}
          </p>
          {playerData.guild_id && (
            <p className="text-sm text-medieval-accent">
              Guilda: {playerData.guild_id} | Rank: {playerData.guild_rank}
            </p>
          )}
        </div>
        
        <div className="flex items-center gap-4">
          <div className={`px-3 py-1 rounded ${connected ? 'bg-green-900 text-green-400' : 'bg-red-900 text-red-400'}`}>
            {connected ? '🟢 Conectado' : '🔴 Desconectado'}
          </div>
          {worldState && (
            <div className="text-right">
              <p className="text-medieval-gold">
                {worldState.dia_noite === 'dia' ? '☀️ Dia' : '🌙 Noite'} - Ciclo {worldState.ciclo}
              </p>
              <p className="text-xs text-gray-400">
                Jogadores: {Object.keys(worldState.jogadores || {}).length} | 
                Guildas: {Object.keys(worldState.guildas || {}).length}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* World Grid */}
        <div className="lg:col-span-3">
          <WorldGrid 
            worldState={worldState} 
            playerId={playerId}
            onMove={(direction) => sendMessage({ command: 'move', payload: { direction } })}
            onCollect={() => sendMessage({ command: 'collect', payload: {} })}
          />
        </div>

        {/* Side Panel */}
        <div className="space-y-6">
          {/* Guild Panel - Only for Guild Masters */}
          {playerData.guild_rank === 'Guild Master' && (
            <GuildPanel 
              playerId={playerId}
              guildId={playerData.guild_id}
              ouro={playerData.ouro}
              onStrategy={(strategyType, payload) => {
                sendMessage({ 
                  command: 'strategy', 
                  payload: { strategy_type: strategyType, ...payload } 
                })
              }}
            />
          )}

          {/* Event Log */}
          <EventLog events={events} />
        </div>
      </div>

      {/* Controls Info */}
      <div className="medieval-panel">
        <h3 className="text-medieval-gold font-bold mb-2">🎮 Controles</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-300">
          <div>
            <span className="text-medieval-gold">Movimento:</span> Setas ou WASD
          </div>
          <div>
            <span className="text-medieval-gold">Coletar:</span> Clique no recurso
          </div>
          <div>
            <span className="text-medieval-gold">Guild Master:</span> Painel estratégico
          </div>
          <div>
            <span className="text-medieval-gold">Objetivo:</span> Conquistar territórios!
          </div>
        </div>
      </div>
    </div>
  )
}
