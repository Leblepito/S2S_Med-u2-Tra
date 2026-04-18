import type { ConfigMessage, ConnectionStatus, ServerJsonMessage } from '../types'

export interface BabelWSEvents {
  statusChange: (status: ConnectionStatus) => void
  message: (msg: ServerJsonMessage) => void
  ttsAudio: (data: ArrayBuffer) => void
}

type EventName = keyof BabelWSEvents

export class BabelWebSocket {
  private ws: WebSocket | null = null
  private url: string
  private listeners = new Map<EventName, Set<(...args: never[]) => void>>()
  private pendingConfig: ConfigMessage | null = null

  constructor(url: string) {
    this.url = url
  }

  get status(): ConnectionStatus {
    if (!this.ws) return 'disconnected'
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting'
      case WebSocket.OPEN: return 'connected'
      default: return 'disconnected'
    }
  }

  connect(config: ConfigMessage, token?: string): void {
    this.disconnect()
    this.pendingConfig = config
    this.emit('statusChange', 'connecting')

    const urlWithToken = token ? `${this.url}?token=${token}` : this.url
    this.ws = new WebSocket(urlWithToken)
    this.ws.binaryType = 'arraybuffer'

    this.ws.onopen = () => {
      if (this.pendingConfig && this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify(this.pendingConfig))
      }
      this.emit('statusChange', 'connected')
    }

    this.ws.onmessage = (ev: MessageEvent) => {
      if (ev.data instanceof ArrayBuffer) {
        this.emit('ttsAudio', ev.data)
      } else if (typeof ev.data === 'string') {
        try {
          const msg = JSON.parse(ev.data) as ServerJsonMessage
          this.emit('message', msg)
        } catch {
          // Invalid JSON — ignore
        }
      }
    }

    this.ws.onerror = () => {
      this.emit('statusChange', 'error')
    }

    this.ws.onclose = () => {
      this.emit('statusChange', 'disconnected')
      this.ws = null
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.onclose = null
      this.ws.close()
      this.ws = null
      this.emit('statusChange', 'disconnected')
    }
  }

  sendAudio(data: ArrayBuffer): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(data)
    }
  }

  on<E extends EventName>(event: E, listener: BabelWSEvents[E]): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(listener as never)
  }

  off<E extends EventName>(event: E, listener: BabelWSEvents[E]): void {
    this.listeners.get(event)?.delete(listener as never)
  }

  private emit<E extends EventName>(event: E, ...args: Parameters<BabelWSEvents[E]>): void {
    for (const listener of this.listeners.get(event) ?? []) {
      (listener as (...a: unknown[]) => void)(...args)
    }
  }
}
