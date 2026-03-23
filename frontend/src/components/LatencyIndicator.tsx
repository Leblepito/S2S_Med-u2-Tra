interface LatencyIndicatorProps {
  latencyMs: number | null
}

function getColor(ms: number): string {
  if (ms < 1000) return 'bg-green-500'
  if (ms < 2000) return 'bg-yellow-400'
  return 'bg-red-500'
}

export function LatencyIndicator({ latencyMs }: LatencyIndicatorProps) {
  return (
    <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
      <span>Latency</span>
      {latencyMs !== null ? (
        <>
          <div
            data-testid="latency-dot"
            className={`w-2 h-2 rounded-full ${getColor(latencyMs)}`}
          />
          <span className="font-mono text-xs">{latencyMs}ms</span>
        </>
      ) : (
        <span className="text-gray-300 dark:text-gray-600">{'\u2014'}</span>
      )}
    </div>
  )
}
