import { useCallback, useRef, useState } from 'react'
import { startAudioCapture } from '../services/audio'

interface UseAudioStreamReturn {
  isCapturing: boolean
  error: string | null
  startCapture: (onChunk: (buffer: ArrayBuffer) => void) => Promise<void>
  stopCapture: () => void
}

export function useAudioStream(): UseAudioStreamReturn {
  const [isCapturing, setIsCapturing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const stopRef = useRef<(() => void) | null>(null)

  const startCapture = useCallback(async (onChunk: (buffer: ArrayBuffer) => void) => {
    if (stopRef.current) return // Already capturing

    try {
      setError(null)
      const stop = await startAudioCapture({
        onChunk,
        onError: (err) => setError(err.message),
      })
      stopRef.current = stop
      setIsCapturing(true)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Microphone access denied'
      setError(message)
    }
  }, [])

  const stopCapture = useCallback(() => {
    if (stopRef.current) {
      stopRef.current()
      stopRef.current = null
      setIsCapturing(false)
    }
  }, [])

  return { isCapturing, error, startCapture, stopCapture }
}
