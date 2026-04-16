import { describe, it, expect, vi, afterEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useLatency } from '../useLatency'

describe('useLatency', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('initializes with null latency', () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ total_p50: 800 }),
    }))

    const { result } = renderHook(() => useLatency('http://localhost:8000/api/latency'))
    expect(result.current).toBeNull()

    vi.unstubAllGlobals()
  })

  it('fetches latency and updates state', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ total_p50: 650 }),
    }))

    const { result } = renderHook(() => useLatency('http://localhost:8000/api/latency'))

    await waitFor(() => {
      expect(result.current).toBe(650)
    })

    vi.unstubAllGlobals()
  })

  it('returns null on fetch error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network error')))

    const { result } = renderHook(() => useLatency('http://localhost:8000/api/latency'))

    // Wait for effect to run
    await new Promise((r) => setTimeout(r, 50))

    expect(result.current).toBeNull()

    vi.unstubAllGlobals()
  })
})
