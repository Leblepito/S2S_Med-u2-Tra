import { useCallback, useEffect, useRef, useState } from 'react'

const STORAGE_KEY = 'babelflow_sessions'
const MAX_SESSIONS = 50

export interface HistoryEntry {
  timestamp: number
  type: 'transcript' | 'translation'
  speaker_id: number
  text: string
  lang?: string
  translations?: Record<string, string>
}

export interface Session {
  id: string
  startedAt: number
  entries: HistoryEntry[]
}

function loadSessions(): Session[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveSessions(sessions: Session[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions.slice(-MAX_SESSIONS)))
}

interface UseConversationHistoryReturn {
  sessionId: string
  entries: HistoryEntry[]
  sessions: Session[]
  addEntry: (entry: HistoryEntry) => void
  clearSession: () => void
  deleteSession: (id: string) => void
  clearAll: () => void
  exportAsText: () => string
  exportAsJSON: () => string
}

export function useConversationHistory(): UseConversationHistoryReturn {
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID())
  const [entries, setEntries] = useState<HistoryEntry[]>([])
  const [sessions, setSessions] = useState<Session[]>(() => loadSessions())
  const entriesRef = useRef(entries)
  entriesRef.current = entries

  // Auto-save current session to localStorage on change
  useEffect(() => {
    if (entries.length === 0) return
    const saved = loadSessions()
    const idx = saved.findIndex((s) => s.id === sessionId)
    const current: Session = { id: sessionId, startedAt: entries[0].timestamp, entries }
    if (idx >= 0) {
      saved[idx] = current
    } else {
      saved.push(current)
    }
    const trimmed = saved.slice(-MAX_SESSIONS)
    saveSessions(trimmed)
    setSessions(trimmed)
  }, [entries, sessionId])

  const addEntry = useCallback((entry: HistoryEntry) => {
    setEntries((prev) => [...prev, entry])
  }, [])

  const clearSession = useCallback(() => {
    // Save current if non-empty, then start new
    setEntries([])
    setSessionId(crypto.randomUUID())
  }, [])

  const deleteSession = useCallback((id: string) => {
    const saved = loadSessions().filter((s) => s.id !== id)
    saveSessions(saved)
    setSessions(saved)
  }, [])

  const clearAll = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY)
    setSessions([])
  }, [])

  const exportAsText = useCallback((): string => {
    return entriesRef.current.map((e) => {
      if (e.type === 'transcript') {
        return `Speaker ${e.speaker_id}: ${e.text}`
      }
      const lines = [`Speaker ${e.speaker_id}: ${e.text}`]
      if (e.translations) {
        for (const [lang, text] of Object.entries(e.translations)) {
          lines.push(`  \u2192 ${lang.toUpperCase()}: ${text}`)
        }
      }
      return lines.join('\n')
    }).join('\n')
  }, [])

  const exportAsJSON = useCallback((): string => {
    return JSON.stringify(entriesRef.current, null, 2)
  }, [])

  return {
    sessionId,
    entries,
    sessions,
    addEntry,
    clearSession,
    deleteSession,
    clearAll,
    exportAsText,
    exportAsJSON,
  }
}
