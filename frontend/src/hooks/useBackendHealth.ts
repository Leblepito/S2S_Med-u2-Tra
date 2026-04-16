import { useCallback, useEffect, useRef, useState } from 'react'

interface UseBackendHealthReturn {
  isHealthy: boolean
  lastChecked: Date | null
}

export function useBackendHealth(
  apiUrl: string,
  intervalMs = 5000,
): UseBackendHealthReturn {
  const [isHealthy, setIsHealthy] = useState(true)
  const [lastChecked, setLastChecked] = useState<Date | null>(null)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const check = useCallback(async () => {
    try {
      const res = await fetch(`${apiUrl}/health`, { signal: AbortSignal.timeout(3000) })
      setIsHealthy(res.ok)
    } catch {
      setIsHealthy(false)
    }
    setLastChecked(new Date())
  }, [apiUrl])

  useEffect(() => {
    check()
    timerRef.current = setInterval(check, intervalMs)
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [check, intervalMs])

  return { isHealthy, lastChecked }
}
