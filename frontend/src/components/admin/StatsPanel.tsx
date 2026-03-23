import { useEffect, useState } from 'react'
import { API_URL } from '../../config'

interface Stats {
  total_sessions: number
  total_transcripts: number
  avg_duration_sec: number
  lang_usage: Record<string, number>
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
      <div className="text-2xl font-bold text-gray-800 dark:text-gray-100">{value}</div>
      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{label}</div>
    </div>
  )
}

function LangBar({ lang, count, max }: { lang: string; count: number; max: number }) {
  const pct = max > 0 ? (count / max) * 100 : 0
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="w-8 text-gray-500 dark:text-gray-400 uppercase font-mono">{lang}</span>
      <div className="flex-1 bg-gray-100 dark:bg-gray-700 rounded-full h-2.5">
        <div
          className="bg-blue-500 h-2.5 rounded-full transition-all"
          style={{ width: `${pct}%` }}
          data-testid={`bar-${lang}`}
        />
      </div>
      <span className="text-xs text-gray-400 dark:text-gray-500 w-8 text-right">{count}</span>
    </div>
  )
}

export function StatsPanel() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await fetch(`${API_URL}/api/admin/stats`)
        if (res.ok) setStats(await res.json())
      } catch {
        // Network error
      }
      setLoading(false)
    }
    fetchStats()
  }, [])

  if (loading) {
    return <div className="text-center text-gray-400 py-8" data-testid="stats-loading">Loading stats...</div>
  }

  if (!stats) {
    return <div className="text-center text-gray-400 py-8">Failed to load stats</div>
  }

  const langEntries = Object.entries(stats.lang_usage).sort((a, b) => b[1] - a[1])
  const maxLang = langEntries.length > 0 ? langEntries[0][1] : 0

  return (
    <div data-testid="stats-panel">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
        <StatCard label="Total Sessions" value={stats.total_sessions} />
        <StatCard label="Total Transcripts" value={stats.total_transcripts} />
        <StatCard label="Avg Duration" value={`${Math.round(stats.avg_duration_sec)}s`} />
      </div>

      {/* Language Usage Chart */}
      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Language Usage</h3>
      <div className="space-y-2">
        {langEntries.map(([lang, count]) => (
          <LangBar key={lang} lang={lang} count={count} max={maxLang} />
        ))}
      </div>
    </div>
  )
}
