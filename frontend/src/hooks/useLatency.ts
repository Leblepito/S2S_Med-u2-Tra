import { useEffect, useState } from 'react'

const POLL_INTERVAL_MS = 2000

export function useLatency(url: string): number | null {
  const [latencyMs, setLatencyMs] = useState<number | null>(null)

  useEffect(() => {
    let active = true

    async function fetchLatency() {
      try {
        const res = await fetch(url)
        if (res.ok && active) {
          const data = await res.json()
          setLatencyMs(data.total_p50 ?? null)
        }
      } catch {
        // Network error — keep previous value or null
      }
    }

    fetchLatency()
    const interval = setInterval(fetchLatency, POLL_INTERVAL_MS)

    return () => {
      active = false
      clearInterval(interval)
    }
  }, [url])

  return latencyMs
}
