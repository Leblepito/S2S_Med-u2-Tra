import { describe, it, expect, vi, afterEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useBackendHealth } from '../useBackendHealth'

describe('useBackendHealth', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('starts healthy by default', () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('ok', { status: 200 }))
    const { result } = renderHook(() => useBackendHealth('http://localhost:8000', 60000))
    expect(result.current.isHealthy).toBe(true)
  })

  it('sets isHealthy true when health endpoint returns ok', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('ok', { status: 200 }))
    const { result } = renderHook(() => useBackendHealth('http://localhost:8000', 60000))

    await waitFor(() => {
      expect(result.current.lastChecked).not.toBeNull()
    })
    expect(result.current.isHealthy).toBe(true)
  })

  it('sets isHealthy false when health endpoint returns error', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('error', { status: 500 }))
    const { result } = renderHook(() => useBackendHealth('http://localhost:8000', 60000))

    await waitFor(() => {
      expect(result.current.lastChecked).not.toBeNull()
    })
    expect(result.current.isHealthy).toBe(false)
  })

  it('sets isHealthy false when fetch throws (network error)', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('Network error'))
    const { result } = renderHook(() => useBackendHealth('http://localhost:8000', 60000))

    await waitFor(() => {
      expect(result.current.lastChecked).not.toBeNull()
    })
    expect(result.current.isHealthy).toBe(false)
  })

  it('calls correct health URL', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('ok', { status: 200 }))
    renderHook(() => useBackendHealth('http://example.com', 60000))

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalled()
    })
    expect(fetchSpy).toHaveBeenCalledWith(
      'http://example.com/health',
      expect.objectContaining({ signal: expect.any(AbortSignal) }),
    )
  })
})
