import { LatencyIndicator } from './LatencyIndicator'

interface HeaderProps {
  latencyMs: number | null
  isMuted: boolean
  onToggleMute: () => void
  darkMode: boolean
  onToggleDark: () => void
}

export function Header({ latencyMs, isMuted, onToggleMute, darkMode, onToggleDark }: HeaderProps) {
  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 sm:px-6 py-3 sm:py-4 shadow-sm">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-0">
        <h1 className="text-lg sm:text-xl font-semibold text-gray-800 dark:text-gray-100">
          BabelFlow
          <span className="text-xs sm:text-sm font-normal text-gray-400 dark:text-gray-500 ml-2">
            Real-Time Translation
          </span>
        </h1>
        <div className="flex items-center gap-3">
          <LatencyIndicator latencyMs={latencyMs} />
          <button
            onClick={onToggleMute}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              isMuted
                ? 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                : 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
            }`}
          >
            {isMuted ? 'Unmute' : 'Mute'}
          </button>
          <button
            onClick={onToggleDark}
            aria-label="Toggle dark mode"
            className="p-1.5 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            {darkMode ? '\u2600' : '\u263E'}
          </button>
        </div>
      </div>
    </header>
  )
}
