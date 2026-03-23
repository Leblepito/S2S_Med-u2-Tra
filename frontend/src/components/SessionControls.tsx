import { useEffect, useRef, useState } from 'react'

interface SessionControlsProps {
  isCapturing: boolean
  transcriptCount: number
  speakerCount: number
  onNewSession: () => void
  onToggleHistory: () => void
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

export function SessionControls({
  isCapturing,
  transcriptCount,
  speakerCount,
  onNewSession,
  onToggleHistory,
}: SessionControlsProps) {
  const [elapsed, setElapsed] = useState(0)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (isCapturing) {
      intervalRef.current = setInterval(() => {
        setElapsed((prev) => prev + 1)
      }, 1000)
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [isCapturing])

  return (
    <div className="flex items-center gap-3" data-testid="session-controls">
      {/* Timer */}
      <span
        className={`font-mono text-xs tabular-nums ${
          isCapturing ? 'text-red-500' : 'text-gray-400 dark:text-gray-500'
        }`}
        data-testid="session-timer"
      >
        {formatTime(elapsed)}
      </span>

      {/* Session summary */}
      {transcriptCount > 0 && (
        <span className="text-xs text-gray-400 dark:text-gray-500 hidden sm:inline">
          {transcriptCount} transcripts, {speakerCount} speakers
        </span>
      )}

      {/* New Session */}
      <button
        onClick={() => {
          onNewSession()
          setElapsed(0)
        }}
        className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
      >
        New
      </button>

      {/* History Toggle */}
      <button
        onClick={onToggleHistory}
        className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
        aria-label="Toggle history"
      >
        History
      </button>
    </div>
  )
}

export { formatTime }
