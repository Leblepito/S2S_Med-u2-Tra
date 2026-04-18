import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { BabelWebSocket } from '../websocket'
import type { ConfigMessage, ServerJsonMessage } from '../../types'

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  readyState = MockWebSocket.CONNECTING
  url: string
  onopen: ((ev: Event) => void) | null = null
  onclose: ((ev: CloseEvent) => void) | null = null
  onmessage: ((ev: MessageEvent) => void) | null = null
  onerror: ((ev: Event) => void) | null = null

  sent: (string | ArrayBuffer)[] = []

  constructor(url: string) {
    this.url = url
  }

  send(data: string | ArrayBuffer) {
    this.sent.push(data)
  }

  close(code?: number, reason?: string) {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) {
      this.onclose(new CloseEvent('close', { code, reason }))
    }
  }

  // Test helpers
  simulateOpen() {
    this.readyState = MockWebSocket.OPEN
    if (this.onopen) this.onopen(new Event('open'))
  }

  simulateMessage(data: string | ArrayBuffer) {
    if (this.onmessage) {
      this.onmessage(new MessageEvent('message', { data }))
    }
  }

  simulateError() {
    if (this.onerror) this.onerror(new Event('error'))
  }
}

describe('BabelWebSocket', () => {
  let mockWs: MockWebSocket
  let bws: BabelWebSocket

  beforeEach(() => {
    const OriginalMock = MockWebSocket
    const Captured = class extends OriginalMock {
      constructor(url: string) {
        super(url)
        mockWs = this
      }
    }
    vi.stubGlobal('WebSocket', Captured)
    bws = new BabelWebSocket('ws://localhost:8000/ws/translate')
  })

  afterEach(() => {
    bws.disconnect()
    vi.unstubAllGlobals()
  })

  describe('connect', () => {
    it('creates WebSocket with correct URL and token', () => {
      const config: ConfigMessage = {
        type: 'config',
        source_lang: 'auto',
        target_langs: ['en', 'th'],
        enable_diarization: false,
      }
      bws.connect(config, 'test-token')
      expect(mockWs.url).toBe('ws://localhost:8000/ws/translate?token=test-token')
    })

    it('sends config message on open', () => {
      const config: ConfigMessage = {
        type: 'config',
        source_lang: 'tr',
        target_langs: ['en'],
        enable_diarization: false,
      }
      bws.connect(config)
      mockWs.simulateOpen()

      expect(mockWs.sent).toHaveLength(1)
      const sentConfig = JSON.parse(mockWs.sent[0] as string)
      expect(sentConfig.type).toBe('config')
      expect(sentConfig.source_lang).toBe('tr')
    })

    it('emits status change on connect', () => {
      const statusChanges: string[] = []
      bws.on('statusChange', (status) => statusChanges.push(status))

      const config: ConfigMessage = {
        type: 'config',
        source_lang: 'auto',
        target_langs: ['en'],
        enable_diarization: false,
      }
      bws.connect(config)
      expect(statusChanges).toContain('connecting')

      mockWs.simulateOpen()
      expect(statusChanges).toContain('connected')
    })
  })

  describe('disconnect', () => {
    it('closes WebSocket and emits disconnected', () => {
      const statusChanges: string[] = []
      bws.on('statusChange', (status) => statusChanges.push(status))

      const config: ConfigMessage = {
        type: 'config',
        source_lang: 'auto',
        target_langs: ['en'],
        enable_diarization: false,
      }
      bws.connect(config)
      mockWs.simulateOpen()
      bws.disconnect()

      expect(statusChanges).toContain('disconnected')
    })
  })

  describe('sendAudio', () => {
    it('sends binary data when connected', () => {
      const config: ConfigMessage = {
        type: 'config',
        source_lang: 'auto',
        target_langs: ['en'],
        enable_diarization: false,
      }
      bws.connect(config)
      mockWs.simulateOpen()

      const audioData = new ArrayBuffer(960)
      bws.sendAudio(audioData)

      // Config + audio = 2 messages
      expect(mockWs.sent).toHaveLength(2)
      expect(mockWs.sent[1]).toBeInstanceOf(ArrayBuffer)
    })

    it('does not send when disconnected', () => {
      // Create a fresh instance without connecting
      const freshBws = new BabelWebSocket('ws://localhost:8000/ws/translate')
      const audioData = new ArrayBuffer(960)
      freshBws.sendAudio(audioData)
      // Status should be disconnected, no data sent
      expect(freshBws.status).toBe('disconnected')
    })
  })

  describe('message handling', () => {
    it('parses JSON messages and emits them', () => {
      const messages: ServerJsonMessage[] = []
      bws.on('message', (msg) => messages.push(msg))

      const config: ConfigMessage = {
        type: 'config',
        source_lang: 'auto',
        target_langs: ['en'],
        enable_diarization: false,
      }
      bws.connect(config)
      mockWs.simulateOpen()

      const transcript: ServerJsonMessage = {
        type: 'partial_transcript',
        text: 'Merhaba',
        lang: 'tr',
        speaker_id: 0,
        confidence: 0.95,
      }
      mockWs.simulateMessage(JSON.stringify(transcript))

      expect(messages).toHaveLength(1)
      expect(messages[0].type).toBe('partial_transcript')
    })

    it('emits binary data as ttsAudio', () => {
      const audioChunks: ArrayBuffer[] = []
      bws.on('ttsAudio', (data) => audioChunks.push(data))

      const config: ConfigMessage = {
        type: 'config',
        source_lang: 'auto',
        target_langs: ['en'],
        enable_diarization: false,
      }
      bws.connect(config)
      mockWs.simulateOpen()

      const audioData = new ArrayBuffer(1024)
      mockWs.simulateMessage(audioData)

      expect(audioChunks).toHaveLength(1)
    })
  })

  describe('error handling', () => {
    it('emits error status on WebSocket error', () => {
      const statusChanges: string[] = []
      bws.on('statusChange', (status) => statusChanges.push(status))

      const config: ConfigMessage = {
        type: 'config',
        source_lang: 'auto',
        target_langs: ['en'],
        enable_diarization: false,
      }
      bws.connect(config)
      mockWs.simulateError()

      expect(statusChanges).toContain('error')
    })
  })

  describe('event system', () => {
    it('supports multiple listeners', () => {
      const calls1: string[] = []
      const calls2: string[] = []

      bws.on('statusChange', (s) => calls1.push(s))
      bws.on('statusChange', (s) => calls2.push(s))

      const config: ConfigMessage = {
        type: 'config',
        source_lang: 'auto',
        target_langs: ['en'],
        enable_diarization: false,
      }
      bws.connect(config)

      expect(calls1).toEqual(calls2)
    })

    it('off removes listener', () => {
      const calls: string[] = []
      const listener = (s: string) => calls.push(s)

      bws.on('statusChange', listener)
      bws.off('statusChange', listener)

      const config: ConfigMessage = {
        type: 'config',
        source_lang: 'auto',
        target_langs: ['en'],
        enable_diarization: false,
      }
      bws.connect(config)

      expect(calls).toHaveLength(0)
    })
  })
})
