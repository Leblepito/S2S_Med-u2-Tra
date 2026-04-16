import { useCallback } from 'react'
import { useWebSocket } from '../hooks/useWebSocket'
import { useAudioStream } from '../hooks/useAudioStream'
import { WS_URL } from '../config'
import type { ConfigMessage, ConnectionStatus } from '../types'

const STATUS_LABELS: Record<ConnectionStatus, string> = {
  disconnected: 'Disconnected',
  connecting: 'Connecting...',
  connected: 'Connected',
  error: 'Error',
}

const STATUS_COLORS: Record<ConnectionStatus, string> = {
  disconnected: 'bg-gray-400',
  connecting: 'bg-yellow-400 animate-pulse',
  connected: 'bg-green-500',
  error: 'bg-red-500',
}

interface AudioCaptureProps {
  config: ConfigMessage
}

export function AudioCapture({ config }: AudioCaptureProps) {
  const { status, connect, disconnect, sendAudio } = useWebSocket(WS_URL)
  const { isCapturing, error, startCapture, stopCapture } = useAudioStream()

  const handleStart = useCallback(async () => {
    connect(config)
    await startCapture(sendAudio)
  }, [config, connect, startCapture, sendAudio])

  const handleStop = useCallback(() => {
    stopCapture()
    disconnect()
  }, [stopCapture, disconnect])

  return (
    <div className="flex flex-col items-center gap-4 p-6">
      {/* Connection Status */}
      <div className="flex items-center gap-2">
        <div className={`w-3 h-3 rounded-full ${STATUS_COLORS[status]}`} />
        <span className="text-sm text-gray-600 dark:text-gray-400">{STATUS_LABELS[status]}</span>
      </div>

      {/* Mic Button — large round, mobile-friendly */}
      <button
        onClick={isCapturing ? handleStop : handleStart}
        className={`w-16 h-16 rounded-full font-medium text-white transition-all flex items-center justify-center text-sm shadow-lg active:scale-95 ${
          isCapturing
            ? 'bg-red-500 hover:bg-red-600 animate-pulse ring-4 ring-red-200 dark:ring-red-900'
            : 'bg-blue-500 hover:bg-blue-600 ring-4 ring-blue-200 dark:ring-blue-900'
        }`}
      >
        {isCapturing ? 'Stop' : 'Start'}
      </button>

      {/* Capturing Indicator */}
      {isCapturing && (
        <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
          <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          Listening...
        </div>
      )}

      {/* Error Display */}
      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}
    </div>
  )
}
