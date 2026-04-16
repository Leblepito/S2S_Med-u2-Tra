import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { AudioPlaybackQueue } from '../audio-playback'

// Mock AudioContext for jsdom
const mockStart = vi.fn()
const mockConnect = vi.fn()
const mockClose = vi.fn().mockResolvedValue(undefined)

class MockAudioContext {
  sampleRate = 24000
  destination = {}

  createBuffer(channels: number, length: number, sampleRate: number) {
    return {
      length,
      sampleRate,
      numberOfChannels: channels,
      getChannelData: () => new Float32Array(length),
    }
  }

  createBufferSource() {
    const source = {
      buffer: null as unknown,
      connect: mockConnect,
      start: mockStart,
      onended: null as (() => void) | null,
    }
    // Auto-trigger onended after start for queue progression
    mockStart.mockImplementation(() => {
      setTimeout(() => source.onended?.(), 0)
    })
    return source
  }

  close = mockClose
}

describe('AudioPlaybackQueue', () => {
  let queue: AudioPlaybackQueue

  beforeEach(() => {
    vi.stubGlobal('AudioContext', MockAudioContext)
    queue = new AudioPlaybackQueue()
    vi.clearAllMocks()
  })

  afterEach(() => {
    queue.dispose()
    vi.unstubAllGlobals()
  })

  it('initializes with empty queue', () => {
    expect(queue.queueLength).toBe(0)
    expect(queue.isPlaying).toBe(false)
  })

  it('enqueue starts playback and reduces queue', () => {
    const chunk = new ArrayBuffer(960)
    queue.enqueue(chunk)
    // playNext is called immediately, queue item shifts out
    expect(queue.isPlaying).toBe(true)
    expect(mockStart).toHaveBeenCalled()
  })

  it('enqueue multiple chunks plays first immediately', () => {
    queue.enqueue(new ArrayBuffer(960))
    queue.enqueue(new ArrayBuffer(960))
    queue.enqueue(new ArrayBuffer(960))
    // First chunk playing, 2 remaining in queue
    expect(queue.queueLength).toBe(2)
    expect(mockStart).toHaveBeenCalledTimes(1)
  })

  it('clear empties the queue and stops', () => {
    queue.enqueue(new ArrayBuffer(960))
    queue.enqueue(new ArrayBuffer(960))
    queue.clear()
    expect(queue.queueLength).toBe(0)
    expect(queue.isPlaying).toBe(false)
  })

  it('dispose closes AudioContext', () => {
    queue.enqueue(new ArrayBuffer(960)) // creates context
    queue.dispose()
    expect(mockClose).toHaveBeenCalled()
  })
})
