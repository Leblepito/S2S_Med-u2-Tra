import { useCallback, useEffect, useRef, useState } from 'react'
import { BabelWebSocket } from '../services/websocket'
import type { ConfigMessage, ConnectionStatus, ServerJsonMessage } from '../types'

interface UseWebSocketReturn {
  status: ConnectionStatus
  connect: (config: ConfigMessage) => void
  disconnect: () => void
  sendAudio: (data: ArrayBuffer) => void
  lastMessage: ServerJsonMessage | null
  lastTtsAudio: ArrayBuffer | null
}

export function useWebSocket(url: string): UseWebSocketReturn {
  const wsRef = useRef<BabelWebSocket | null>(null)
  const [status, setStatus] = useState<ConnectionStatus>('disconnected')
  const [lastMessage, setLastMessage] = useState<ServerJsonMessage | null>(null)
  const [lastTtsAudio, setLastTtsAudio] = useState<ArrayBuffer | null>(null)

  useEffect(() => {
    const ws = new BabelWebSocket(url)
    wsRef.current = ws

    ws.on('statusChange', setStatus)
    ws.on('message', setLastMessage)
    ws.on('ttsAudio', setLastTtsAudio)

    return () => {
      ws.disconnect()
      wsRef.current = null
    }
  }, [url])

  const connect = useCallback((config: ConfigMessage) => {
    wsRef.current?.connect(config)
  }, [])

  const disconnect = useCallback(() => {
    wsRef.current?.disconnect()
  }, [])

  const sendAudio = useCallback((data: ArrayBuffer) => {
    wsRef.current?.sendAudio(data)
  }, [])

  return { status, connect, disconnect, sendAudio, lastMessage, lastTtsAudio }
}
