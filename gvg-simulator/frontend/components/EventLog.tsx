'use client'

import { useEffect, useRef } from 'react'

interface EventLogProps {
  events: any[]
}

/**
 * Scrollable event feed showing game events received via WebSocket
 */
export default function EventLog({ events }: EventLogProps) {
  const logEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom on new events
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [events])

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'spawn': return '✨'
      case 'battle': return '⚔️'
      case 'resource_collected': return '💰'
      case 'territory_captured': return '🚩'
      case 'day_night_cycle': return '🌅'
      case 'war_declared': return '🔥'
      case 'structure_built': return '🏗️'
      default: return '📜'
    }
  }

  const getEventStyle = (eventType: string) => {
    switch (eventType) {
      case 'spawn': return 'text-blue-400'
      case 'battle': return 'text-red-400'
      case 'resource_collected': return 'text-green-400'
      case 'territory_captured': return 'text-purple-400'
      case 'day_night_cycle': return 'text-yellow-400'
      case 'war_declared': return 'text-orange-500 font-bold'
      case 'structure_built': return 'text-cyan-400'
      default: return 'text-gray-300'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp)
      return date.toLocaleTimeString('pt-BR', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
      })
    } catch {
      return ''
    }
  }

  return (
    <div className="medieval-panel">
      <h3 className="text-medieval-gold font-bold mb-3 flex items-center gap-2">
        📜 Registro de Eventos
        <span className="text-xs text-gray-500">({events.length})</span>
      </h3>
      
      <div className="bg-medieval-bg rounded border border-medieval-gold/30 h-64 overflow-y-auto p-2 space-y-2">
        {events.length === 0 ? (
          <p className="text-gray-500 text-sm text-center py-8">
            Nenhum evento ainda...
          </p>
        ) : (
          events.map((event, index) => (
            <div
              key={`${event.timestamp}-${index}`}
              className={`text-xs p-2 rounded bg-medieval-dark/50 border-l-2 ${getEventStyle(event.event_type)}`}
              style={{ borderLeftColor: 'currentColor' }}
            >
              <div className="flex items-start gap-2">
                <span className="text-sm">{getEventIcon(event.event_type)}</span>
                <div className="flex-1 min-w-0">
                  <p className="break-words">{event.message}</p>
                  {event.timestamp && (
                    <p className="text-gray-600 mt-1 text-[10px]">
                      {formatTimestamp(event.timestamp)}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={logEndRef} />
      </div>

      {/* Event Stats */}
      {events.length > 0 && (
        <div className="mt-3 pt-3 border-t border-medieval-gold/30 grid grid-cols-3 gap-2 text-center text-xs">
          <div>
            <span className="text-gray-500">Total:</span>
            <span className="text-medieval-gold ml-1">{events.length}</span>
          </div>
          <div>
            <span className="text-gray-500">Recursos:</span>
            <span className="text-green-400 ml-1">
              {events.filter(e => e.event_type === 'resource_collected').length}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Conquistas:</span>
            <span className="text-purple-400 ml-1">
              {events.filter(e => e.event_type === 'territory_captured').length}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
