import { useCallback, useEffect, useRef, useState } from 'react'
import { AudioPlaybackQueue } from '../services/audio-playback'

interface UseTtsPlaybackReturn {
  isMuted: boolean
  enqueue: (data: ArrayBuffer) => void
  toggleMute: () => void
  clear: () => void
}

export function useTtsPlayback(): UseTtsPlaybackReturn {
  const queueRef = useRef<AudioPlaybackQueue>(new AudioPlaybackQueue())
  const [isMuted, setIsMuted] = useState(false)

  useEffect(() => {
    return () => {
      queueRef.current.dispose()
    }
  }, [])

  const enqueue = useCallback((data: ArrayBuffer) => {
    if (!isMuted) {
      queueRef.current.enqueue(data)
    }
  }, [isMuted])

  const toggleMute = useCallback(() => {
    setIsMuted((prev) => !prev)
  }, [])

  const clear = useCallback(() => {
    queueRef.current.clear()
  }, [])

  return { isMuted, enqueue, toggleMute, clear }
}
