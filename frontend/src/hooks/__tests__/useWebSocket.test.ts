import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useWebSocket } from '../useWebSocket'
import type { ConfigMessage } from '../../types'

// Track mock calls
const mockConnect = vi.fn()
const mockDisconnect = vi.fn()
const mockSendAudio = vi.fn()
const mockOn = vi.fn()

vi.mock('../../services/websocket', () => {
  return {
    BabelWebSocket: class MockBabelWebSocket {
      connect = mockConnect
      disconnect = mockDisconnect
      sendAudio = mockSendAudio
      on = mockOn
      off = vi.fn()
    },
  }
})

describe('useWebSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('initializes with disconnected status', () => {
    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws/translate'))
    expect(result.current.status).toBe('disconnected')
  })

  it('registers event listeners on mount', () => {
    renderHook(() => useWebSocket('ws://localhost:8000/ws/translate'))
    expect(mockOn).toHaveBeenCalledWith('statusChange', expect.any(Function))
    expect(mockOn).toHaveBeenCalledWith('message', expect.any(Function))
    expect(mockOn).toHaveBeenCalledWith('ttsAudio', expect.any(Function))
  })

  it('connect calls BabelWebSocket.connect', () => {
    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws/translate'))
    const config: ConfigMessage = {
      type: 'config',
      source_lang: 'auto',
      target_langs: ['en'],
      enable_diarization: false,
    }
    act(() => {
      result.current.connect(config)
    })
    expect(mockConnect).toHaveBeenCalledWith(config)
  })

  it('disconnect calls BabelWebSocket.disconnect', () => {
    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws/translate'))
    act(() => {
      result.current.disconnect()
    })
    expect(mockDisconnect).toHaveBeenCalled()
  })

  it('sendAudio calls BabelWebSocket.sendAudio', () => {
    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws/translate'))
    const buffer = new ArrayBuffer(960)
    act(() => {
      result.current.sendAudio(buffer)
    })
    expect(mockSendAudio).toHaveBeenCalledWith(buffer)
  })

  it('lastMessage starts as null', () => {
    const { result } = renderHook(() => useWebSocket('ws://localhost:8000/ws/translate'))
    expect(result.current.lastMessage).toBeNull()
  })

  it('disconnects on unmount', () => {
    const { unmount } = renderHook(() => useWebSocket('ws://localhost:8000/ws/translate'))
    unmount()
    expect(mockDisconnect).toHaveBeenCalled()
  })
})
