import { useState } from 'react'
import { SessionList } from './SessionList'
import { StatsPanel } from './StatsPanel'
import { GlossaryManager } from './GlossaryManager'

type Tab = 'sessions' | 'stats' | 'glossary'

const TABS: { id: Tab; label: string }[] = [
  { id: 'sessions', label: 'Sessions' },
  { id: 'stats', label: 'Stats' },
  { id: 'glossary', label: 'Glossary' },
]

interface AdminPanelProps {
  onClose: () => void
}

export function AdminPanel({ onClose }: AdminPanelProps) {
  const [activeTab, setActiveTab] = useState<Tab>('sessions')

  return (
    <div
      data-testid="admin-panel"
      className="fixed inset-0 z-50 bg-gray-50 dark:bg-gray-900 overflow-y-auto"
    >
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 sm:px-6 py-3 shadow-sm">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Admin Panel</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-lg"
            aria-label="Close admin"
          >
            {'\u2715'}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-4xl mx-auto flex">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto py-4 px-4 sm:px-6">
        {activeTab === 'sessions' && <SessionList />}
        {activeTab === 'stats' && <StatsPanel />}
        {activeTab === 'glossary' && <GlossaryManager />}
      </div>
    </div>
  )
}
