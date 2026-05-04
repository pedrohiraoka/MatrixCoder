'use client'

import { useEffect, useCallback, useRef, useState } from 'react'

interface UseWebSocketOptions {
  onConnect?: () => void
  onDisconnect?: () => void
  onMessage?: (message: any) => void
}

/**
 * Custom WebSocket hook for GvG Simulator
 * Manages connection, reconnection, and message handling
 */
export default function useWebSocket(
  playerId: string,
  options: UseWebSocketOptions = {}
) {
  const [connected, setConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<any>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const retryCountRef = useRef(0)
  const MAX_RETRIES = 5

  const connect = useCallback(() => {
    if (!playerId || wsRef.current?.readyState === WebSocket.OPEN) return

    try {
      const ws = new WebSocket(`ws://localhost:8000/ws/${playerId}`)
      
      ws.onopen = () => {
        console.log('[WebSocket] Connected')
        setConnected(true)
        retryCountRef.current = 0
        options.onConnect?.()
      }

      ws.onclose = () => {
        console.log('[WebSocket] Disconnected')
        setConnected(false)
        options.onDisconnect?.()
        
        // Auto-reconnect with exponential backoff
        if (retryCountRef.current < MAX_RETRIES && playerId) {
          const delay = Math.min(1000 * Math.pow(2, retryCountRef.current), 10000)
          console.log(`[WebSocket] Reconnecting in ${delay}ms...`)
          
          reconnectTimeoutRef.current = setTimeout(() => {
            retryCountRef.current++
            connect()
          }, delay)
        }
      }

      ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error)
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          setLastMessage(message)
          options.onMessage?.(message)
        } catch (e) {
          console.error('[WebSocket] Parse error:', e)
        }
      }

      wsRef.current = ws
    } catch (error) {
      console.error('[WebSocket] Connection error:', error)
    }
  }, [playerId, options])

  const sendMessage = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    } else {
      console.warn('[WebSocket] Cannot send - not connected')
    }
  }, [])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    
    setConnected(false)
  }, [])

  // Connect when playerId changes
  useEffect(() => {
    if (playerId) {
      connect()
    }
    
    return () => {
      disconnect()
    }
  }, [playerId, connect, disconnect])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      disconnect()
    }
  }, [disconnect])

  return {
    connected,
    lastMessage,
    sendMessage,
    disconnect,
    reconnect: connect
  }
}
