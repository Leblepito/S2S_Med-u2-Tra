import { useState } from 'react'
import type { Session } from '../hooks/useConversationHistory'

interface ConversationHistoryProps {
  sessions: Session[]
  currentExportText: () => string
  currentExportJSON: () => string
  onDeleteSession: (id: string) => void
  onClearAll: () => void
  onClose: () => void
}

function formatDate(ts: number) {
  return new Date(ts).toLocaleString()
}

function getSpeakerCount(session: Session): number {
  return new Set(session.entries.map((e) => e.speaker_id)).size
}

function getLangs(session: Session): string[] {
  const langs = new Set<string>()
  session.entries.forEach((e) => {
    if (e.lang) langs.add(e.lang)
    if (e.translations) Object.keys(e.translations).forEach((l) => langs.add(l))
  })
  return [...langs]
}

export function ConversationHistory({
  sessions,
  currentExportText,
  currentExportJSON,
  onDeleteSession,
  onClearAll,
  onClose,
}: ConversationHistoryProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const selected = sessions.find((s) => s.id === selectedId)

  const handleCopyText = () => {
    navigator.clipboard?.writeText(currentExportText())
  }

  const handleDownloadJSON = () => {
    const blob = new Blob([currentExportJSON()], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'babelflow-session.json'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div
      data-testid="history-panel"
      className="fixed inset-y-0 right-0 w-80 sm:w-96 bg-white dark:bg-gray-800 shadow-xl border-l border-gray-200 dark:border-gray-700 z-50 flex flex-col"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-sm font-semibold text-gray-800 dark:text-gray-100">History</h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-lg"
          aria-label="Close history"
        >
          {'\u2715'}
        </button>
      </div>

      {/* Export current session */}
      <div className="flex gap-2 px-4 py-2 border-b border-gray-100 dark:border-gray-700">
        <button
          onClick={handleCopyText}
          className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
        >
          Copy Text
        </button>
        <button
          onClick={handleDownloadJSON}
          className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
        >
          Download JSON
        </button>
        {sessions.length > 0 && (
          <button
            onClick={onClearAll}
            className="text-xs px-2 py-1 rounded bg-red-50 dark:bg-red-900/30 text-red-500 hover:bg-red-100 dark:hover:bg-red-900/50 ml-auto"
          >
            Clear All
          </button>
        )}
      </div>

      {/* Session list or detail */}
      <div className="flex-1 overflow-y-auto">
        {selected ? (
          <div className="p-4">
            <button
              onClick={() => setSelectedId(null)}
              className="text-xs text-blue-500 hover:text-blue-600 mb-3"
            >
              {'\u2190'} Back to list
            </button>
            <div className="space-y-2">
              {selected.entries.map((e, i) => (
                <div key={i} className="text-sm">
                  <span className="font-medium text-gray-700 dark:text-gray-300">
                    Speaker {e.speaker_id}:
                  </span>{' '}
                  <span className="text-gray-600 dark:text-gray-400">{e.text}</span>
                  {e.translations && (
                    <div className="ml-4 mt-0.5">
                      {Object.entries(e.translations).map(([lang, text]) => (
                        <div key={lang} className="text-xs text-gray-500 dark:text-gray-500">
                          {'\u2192'} {lang.toUpperCase()}: {text}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : sessions.length === 0 ? (
          <div className="text-center text-gray-400 dark:text-gray-600 py-8 text-sm">
            No sessions yet
          </div>
        ) : (
          <div className="divide-y divide-gray-100 dark:divide-gray-700">
            {[...sessions].reverse().map((session) => (
              <div
                key={session.id}
                className="px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer flex items-center justify-between"
              >
                <div onClick={() => setSelectedId(session.id)} className="flex-1">
                  <div className="text-sm text-gray-700 dark:text-gray-300">
                    {formatDate(session.startedAt)}
                  </div>
                  <div className="text-xs text-gray-400 dark:text-gray-500 flex gap-2 mt-0.5">
                    <span>{session.entries.length} entries</span>
                    <span>{getSpeakerCount(session)} speakers</span>
                    {getLangs(session).map((l) => (
                      <span key={l} className="uppercase">{l}</span>
                    ))}
                  </div>
                </div>
                <button
                  onClick={() => onDeleteSession(session.id)}
                  className="text-gray-300 hover:text-red-500 dark:text-gray-600 dark:hover:text-red-400 text-sm ml-2"
                  aria-label="Delete session"
                >
                  {'\u2715'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
