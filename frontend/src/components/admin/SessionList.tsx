import { useCallback, useEffect, useState } from 'react'
import { API_URL } from '../../config'
import { SessionDetail } from './SessionDetail'

interface SessionSummary {
  id: string
  started_at: string
  duration_sec: number
  speaker_count: number
  transcript_count: number
  langs: string[]
}

const PAGE_SIZE = 20

export function SessionList() {
  const [sessions, setSessions] = useState<SessionSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(0)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const fetchSessions = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/api/admin/sessions?offset=${page * PAGE_SIZE}&limit=${PAGE_SIZE}`)
      if (res.ok) {
        setSessions(await res.json())
      }
    } catch {
      // Network error
    }
    setLoading(false)
  }, [page])

  useEffect(() => {
    fetchSessions()
  }, [fetchSessions])

  const handleDelete = useCallback(async (id: string) => {
    try {
      await fetch(`${API_URL}/api/admin/sessions/${id}`, { method: 'DELETE' })
      setSessions((prev) => prev.filter((s) => s.id !== id))
    } catch {
      // Network error
    }
  }, [])

  if (selectedId) {
    return <SessionDetail sessionId={selectedId} onBack={() => setSelectedId(null)} />
  }

  return (
    <div data-testid="session-list">
      {loading ? (
        <div className="text-center text-gray-400 dark:text-gray-600 py-8">Loading sessions...</div>
      ) : sessions.length === 0 ? (
        <div className="text-center text-gray-400 dark:text-gray-600 py-8">No sessions found</div>
      ) : (
        <>
          <table className="w-full text-sm" data-testid="session-table">
            <thead>
              <tr className="text-left text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
                <th className="py-2 font-medium">Date</th>
                <th className="py-2 font-medium">Duration</th>
                <th className="py-2 font-medium">Speakers</th>
                <th className="py-2 font-medium">Transcripts</th>
                <th className="py-2 font-medium">Langs</th>
                <th className="py-2 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((s) => (
                <tr
                  key={s.id}
                  className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50"
                >
                  <td
                    className="py-2.5 text-gray-700 dark:text-gray-300 cursor-pointer"
                    onClick={() => setSelectedId(s.id)}
                  >
                    {new Date(s.started_at).toLocaleString()}
                  </td>
                  <td className="py-2.5 text-gray-600 dark:text-gray-400">{s.duration_sec}s</td>
                  <td className="py-2.5 text-gray-600 dark:text-gray-400">{s.speaker_count}</td>
                  <td className="py-2.5 text-gray-600 dark:text-gray-400">{s.transcript_count}</td>
                  <td className="py-2.5">
                    <div className="flex gap-1">
                      {s.langs.map((l) => (
                        <span key={l} className="px-1.5 py-0.5 text-xs rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 uppercase">
                          {l}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-2.5">
                    <button
                      onClick={() => handleDelete(s.id)}
                      className="text-xs text-red-400 hover:text-red-600"
                      aria-label={`Delete session ${s.id}`}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-4" data-testid="pagination">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="text-xs px-3 py-1.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 disabled:opacity-40"
            >
              Previous
            </button>
            <span className="text-xs text-gray-400 dark:text-gray-500">Page {page + 1}</span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={sessions.length < PAGE_SIZE}
              className="text-xs px-3 py-1.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  )
}
