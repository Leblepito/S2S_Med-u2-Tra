import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useTtsPlayback } from '../useTtsPlayback'

// Mock AudioPlaybackQueue
const mockEnqueue = vi.fn()
const mockClear = vi.fn()
const mockDispose = vi.fn()

vi.mock('../../services/audio-playback', () => ({
  AudioPlaybackQueue: class {
    enqueue = mockEnqueue
    clear = mockClear
    dispose = mockDispose
    get queueLength() { return 0 }
    get isPlaying() { return false }
  },
}))

describe('useTtsPlayback', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('initializes unmuted', () => {
    const { result } = renderHook(() => useTtsPlayback())
    expect(result.current.isMuted).toBe(false)
  })

  it('enqueue calls queue when unmuted', () => {
    const { result } = renderHook(() => useTtsPlayback())
    const data = new ArrayBuffer(960)
    act(() => {
      result.current.enqueue(data)
    })
    expect(mockEnqueue).toHaveBeenCalledWith(data)
  })

  it('enqueue does NOT call queue when muted', () => {
    const { result } = renderHook(() => useTtsPlayback())
    act(() => {
      result.current.toggleMute()
    })
    expect(result.current.isMuted).toBe(true)

    const data = new ArrayBuffer(960)
    act(() => {
      result.current.enqueue(data)
    })
    expect(mockEnqueue).not.toHaveBeenCalled()
  })

  it('toggleMute flips state', () => {
    const { result } = renderHook(() => useTtsPlayback())
    expect(result.current.isMuted).toBe(false)

    act(() => { result.current.toggleMute() })
    expect(result.current.isMuted).toBe(true)

    act(() => { result.current.toggleMute() })
    expect(result.current.isMuted).toBe(false)
  })

  it('clear calls queue.clear', () => {
    const { result } = renderHook(() => useTtsPlayback())
    act(() => {
      result.current.clear()
    })
    expect(mockClear).toHaveBeenCalled()
  })

  it('disposes on unmount', () => {
    const { unmount } = renderHook(() => useTtsPlayback())
    unmount()
    expect(mockDispose).toHaveBeenCalled()
  })
})
