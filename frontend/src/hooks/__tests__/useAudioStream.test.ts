import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useAudioStream } from '../useAudioStream'

const mockStopFn = vi.fn()

vi.mock('../../services/audio', () => ({
  startAudioCapture: vi.fn().mockImplementation(() => Promise.resolve(mockStopFn)),
}))

// Access the mocked module for per-test overrides
import { startAudioCapture } from '../../services/audio'
const mockedStart = vi.mocked(startAudioCapture)

describe('useAudioStream', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockedStart.mockImplementation(() => Promise.resolve(mockStopFn))
  })

  it('initializes with isCapturing false', () => {
    const { result } = renderHook(() => useAudioStream())
    expect(result.current.isCapturing).toBe(false)
  })

  it('initializes with null error', () => {
    const { result } = renderHook(() => useAudioStream())
    expect(result.current.error).toBeNull()
  })

  it('startCapture sets isCapturing to true', async () => {
    const { result } = renderHook(() => useAudioStream())

    await act(async () => {
      await result.current.startCapture(vi.fn())
    })

    expect(result.current.isCapturing).toBe(true)
  })

  it('stopCapture sets isCapturing to false', async () => {
    const { result } = renderHook(() => useAudioStream())

    await act(async () => {
      await result.current.startCapture(vi.fn())
    })

    act(() => {
      result.current.stopCapture()
    })

    expect(result.current.isCapturing).toBe(false)
    expect(mockStopFn).toHaveBeenCalled()
  })

  it('sets error on startCapture failure', async () => {
    mockedStart.mockRejectedValueOnce(new Error('Microphone denied'))

    const { result } = renderHook(() => useAudioStream())

    await act(async () => {
      await result.current.startCapture(vi.fn())
    })

    expect(result.current.error).toBe('Microphone denied')
    expect(result.current.isCapturing).toBe(false)
  })
})
