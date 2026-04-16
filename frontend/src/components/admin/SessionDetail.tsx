import { useEffect, useState } from 'react'
import { API_URL } from '../../config'

interface DetailEntry {
  timestamp: number
  type: string
  speaker_id: number
  text: string
  lang?: string
  translations?: Record<string, string>
}

interface SessionData {
  id: string
  started_at: string
  entries: DetailEntry[]
}

interface SessionDetailProps {
  sessionId: string
  onBack: () => void
}

export function SessionDetail({ sessionId, onBack }: SessionDetailProps) {
  const [session, setSession] = useState<SessionData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchDetail() {
      try {
        const res = await fetch(`${API_URL}/api/admin/sessions/${sessionId}`)
        if (res.ok) setSession(await res.json())
      } catch {
        // Network error
      }
      setLoading(false)
    }
    fetchDetail()
  }, [sessionId])

  const handleExportText = () => {
    if (!session) return
    const text = session.entries.map((e) => {
      const lines = [`Speaker ${e.speaker_id}: ${e.text}`]
      if (e.translations) {
        for (const [lang, t] of Object.entries(e.translations)) {
          lines.push(`  \u2192 ${lang.toUpperCase()}: ${t}`)
        }
      }
      return lines.join('\n')
    }).join('\n')
    navigator.clipboard?.writeText(text)
  }

  const handleExportJSON = () => {
    if (!session) return
    const blob = new Blob([JSON.stringify(session.entries, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `session-${sessionId}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return <div className="text-center text-gray-400 py-8">Loading...</div>
  }

  if (!session) {
    return <div className="text-center text-gray-400 py-8">Session not found</div>
  }

  return (
    <div data-testid="session-detail">
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={onBack}
          className="text-xs text-blue-500 hover:text-blue-600"
        >
          {'\u2190'} Back to list
        </button>
        <div className="flex gap-2">
          <button
            onClick={handleExportText}
            className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
          >
            Copy Text
          </button>
          <button
            onClick={handleExportJSON}
            className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
          >
            Download JSON
          </button>
        </div>
      </div>

      <div className="text-xs text-gray-400 dark:text-gray-500 mb-3">
        {new Date(session.started_at).toLocaleString()} &middot; {session.entries.length} entries
      </div>

      <div className="space-y-2">
        {session.entries.map((e, i) => (
          <div key={i} className="text-sm">
            <span className="font-medium text-gray-700 dark:text-gray-300">
              Speaker {e.speaker_id}:
            </span>{' '}
            <span className="text-gray-600 dark:text-gray-400">{e.text}</span>
            {e.translations && (
              <div className="ml-4 mt-0.5">
                {Object.entries(e.translations).map(([lang, text]) => (
                  <div key={lang} className="text-xs text-gray-500">
                    {'\u2192'} {lang.toUpperCase()}: {text}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
