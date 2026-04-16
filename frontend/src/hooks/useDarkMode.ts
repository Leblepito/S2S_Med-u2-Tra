import { useCallback, useEffect, useState } from 'react'

export function useDarkMode(): [boolean, () => void] {
  const [dark, setDark] = useState(() => {
    if (typeof window === 'undefined') return false
    const stored = localStorage.getItem('babelflow-dark')
    if (stored !== null) return stored === 'true'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('babelflow-dark', String(dark))
  }, [dark])

  const toggle = useCallback(() => setDark((prev) => !prev), [])

  return [dark, toggle]
}
