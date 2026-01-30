'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { WebSocketMessage } from '@/lib/types'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
const MAX_RECONNECT_ATTEMPTS = 10

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
  autoReconnect?: boolean
  reconnectInterval?: number
}

export function useWebSocket(url: string = `${WS_URL}/ws/sensors/`, options: UseWebSocketOptions = {}) {
  const {
    onMessage,
    onOpen,
    onClose,
    onError,
    autoReconnect = true,
    reconnectInterval = 3000,
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const shouldReconnectRef = useRef(true)
  const reconnectAttemptsRef = useRef(0)

  const connect = useCallback(() => {
    // Prevent multiple connections - check for OPEN or CONNECTING states
    if (wsRef.current?.readyState === WebSocket.OPEN || 
        wsRef.current?.readyState === WebSocket.CONNECTING) {
      return
    }

    try {
      const ws = new WebSocket(url)

      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        reconnectAttemptsRef.current = 0 // Reset on successful connection
        onOpen?.()
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage(message)
          onMessage?.(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        wsRef.current = null
        onClose?.()

        // Auto-reconnect if enabled and under max attempts
        if (autoReconnect && shouldReconnectRef.current && 
            reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttemptsRef.current += 1
          const backoffInterval = reconnectInterval * Math.min(reconnectAttemptsRef.current, 5)
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Attempting to reconnect (${reconnectAttemptsRef.current}/${MAX_RECONNECT_ATTEMPTS})...`)
            connect()
          }, backoffInterval)
        } else if (reconnectAttemptsRef.current >= MAX_RECONNECT_ATTEMPTS) {
          console.warn('Max reconnection attempts reached. Please check if the backend is running.')
        }
      }

      ws.onerror = (error) => {
        // Use console.warn instead of console.error to reduce noise when backend is unavailable
        // Still pass the error event to the callback for debugging if needed
        console.warn('WebSocket connection error - backend may be unavailable:', error.type)
        onError?.(error)
      }

      wsRef.current = ws
    } catch (error) {
      // Use console.warn for connection failures - backend may not be running
      console.warn('Failed to create WebSocket connection - backend may be unavailable:', error)
    }
  }, [url, onMessage, onOpen, onClose, onError, autoReconnect, reconnectInterval])

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false
    reconnectAttemptsRef.current = 0
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setIsConnected(false)
  }, [])

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected')
    }
  }, [])

  // Reset reconnect attempts when manually reconnecting
  const reconnect = useCallback(() => {
    reconnectAttemptsRef.current = 0
    connect()
  }, [connect])

  useEffect(() => {
    shouldReconnectRef.current = true
    reconnectAttemptsRef.current = 0
    connect()

    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  return {
    isConnected,
    lastMessage,
    sendMessage,
    disconnect,
    reconnect,
  }
}
