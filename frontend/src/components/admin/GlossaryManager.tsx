import { useCallback, useEffect, useState } from 'react'
import { API_URL } from '../../config'
import { SUPPORTED_LANGS } from '../../types'

interface GlossaryTerm {
  id: string
  canonical_term: string
  category: string
  translations: Record<string, string>
}

interface Domain {
  id: string
  name: string
  term_count: number
}

export function GlossaryManager() {
  const [domains, setDomains] = useState<Domain[]>([])
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null)
  const [terms, setTerms] = useState<GlossaryTerm[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddDomain, setShowAddDomain] = useState(false)
  const [showAddTerm, setShowAddTerm] = useState(false)
  const [newDomainName, setNewDomainName] = useState('')
  const [newTerm, setNewTerm] = useState({ canonical_term: '', category: '', translations: {} as Record<string, string> })
  const [searchQuery, setSearchQuery] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editData, setEditData] = useState<GlossaryTerm | null>(null)

  useEffect(() => {
    async function fetchDomains() {
      try {
        const res = await fetch(`${API_URL}/api/admin/glossary/domains`)
        if (res.ok) setDomains(await res.json())
      } catch {
        // Network error
      }
      setLoading(false)
    }
    fetchDomains()
  }, [])

  useEffect(() => {
    if (!selectedDomain) return
    async function fetchTerms() {
      try {
        const res = await fetch(`${API_URL}/api/admin/glossary/domains/${selectedDomain}/terms`)
        if (res.ok) setTerms(await res.json())
      } catch {
        // Network error
      }
    }
    fetchTerms()
  }, [selectedDomain])

  const handleAddDomain = useCallback(async () => {
    if (!newDomainName.trim()) return
    try {
      const res = await fetch(`${API_URL}/api/admin/glossary/domains`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newDomainName }),
      })
      if (res.ok) {
        const domain = await res.json()
        setDomains((prev) => [...prev, domain])
        setNewDomainName('')
        setShowAddDomain(false)
      }
    } catch {
      // Network error
    }
  }, [newDomainName])

  const handleAddTerm = useCallback(async () => {
    if (!selectedDomain || !newTerm.canonical_term.trim()) return
    try {
      const res = await fetch(`${API_URL}/api/admin/glossary/domains/${selectedDomain}/terms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTerm),
      })
      if (res.ok) {
        const term = await res.json()
        setTerms((prev) => [...prev, term])
        setNewTerm({ canonical_term: '', category: '', translations: {} })
        setShowAddTerm(false)
      }
    } catch {
      // Network error
    }
  }, [selectedDomain, newTerm])

  const handleDeleteTerm = useCallback(async (termId: string) => {
    if (!selectedDomain) return
    try {
      await fetch(`${API_URL}/api/admin/glossary/domains/${selectedDomain}/terms/${termId}`, { method: 'DELETE' })
      setTerms((prev) => prev.filter((t) => t.id !== termId))
    } catch {
      // Network error
    }
  }, [selectedDomain])

  const handleStartEdit = useCallback((term: GlossaryTerm) => {
    setEditingId(term.id)
    setEditData({ ...term, translations: { ...term.translations } })
  }, [])

  const handleSaveEdit = useCallback(async () => {
    if (!selectedDomain || !editData) return
    try {
      const res = await fetch(`${API_URL}/api/admin/glossary/domains/${selectedDomain}/terms/${editData.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editData),
      })
      if (res.ok) {
        setTerms((prev) => prev.map((t) => t.id === editData.id ? editData : t))
      }
    } catch {
      // Network error
    }
    setEditingId(null)
    setEditData(null)
  }, [selectedDomain, editData])

  const filteredTerms = searchQuery
    ? terms.filter((t) =>
        t.canonical_term.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.category.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : terms

  if (loading) {
    return <div className="text-center text-gray-400 py-8">Loading glossary...</div>
  }

  return (
    <div data-testid="glossary-manager">
      {selectedDomain ? (
        <div>
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => { setSelectedDomain(null); setTerms([]); setSearchQuery('') }}
              className="text-xs text-blue-500 hover:text-blue-600"
              aria-label="Back to domains"
            >
              {'\u2190'} Back to domains
            </button>
            <button
              onClick={() => setShowAddTerm(true)}
              className="text-xs px-3 py-1.5 rounded bg-blue-500 text-white hover:bg-blue-600"
              aria-label="Add new term"
            >
              Add Term
            </button>
          </div>

          {/* Search */}
          <input
            placeholder="Search terms..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 dark:text-gray-200 mb-4"
            data-testid="term-search"
            aria-label="Search terms"
          />

          {showAddTerm && (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-4" data-testid="add-term-form">
              <div className="grid grid-cols-2 gap-3 mb-3">
                <input
                  placeholder="Canonical term"
                  value={newTerm.canonical_term}
                  onChange={(e) => setNewTerm((prev) => ({ ...prev, canonical_term: e.target.value }))}
                  className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-900 dark:text-gray-200"
                />
                <input
                  placeholder="Category"
                  value={newTerm.category}
                  onChange={(e) => setNewTerm((prev) => ({ ...prev, category: e.target.value }))}
                  className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-900 dark:text-gray-200"
                />
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3">
                {SUPPORTED_LANGS.map((lang) => (
                  <input
                    key={lang}
                    placeholder={lang.toUpperCase()}
                    value={newTerm.translations[lang] ?? ''}
                    onChange={(e) => setNewTerm((prev) => ({
                      ...prev,
                      translations: { ...prev.translations, [lang]: e.target.value },
                    }))}
                    className="px-2 py-1.5 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-900 dark:text-gray-200"
                  />
                ))}
              </div>
              <div className="flex gap-2">
                <button onClick={handleAddTerm} className="text-xs px-3 py-1.5 rounded bg-blue-500 text-white" aria-label="Save term">Save</button>
                <button onClick={() => setShowAddTerm(false)} className="text-xs px-3 py-1.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300" aria-label="Cancel add term">Cancel</button>
              </div>
            </div>
          )}

          {filteredTerms.length === 0 ? (
            <div className="text-center text-gray-400 py-8 text-sm">
              {searchQuery ? 'No matching terms' : 'No terms yet'}
            </div>
          ) : (
            <div className="space-y-2">
              {filteredTerms.map((t) => (
                <div key={t.id} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-3">
                  {editingId === t.id && editData ? (
                    <div data-testid={`edit-form-${t.id}`}>
                      <div className="grid grid-cols-2 gap-2 mb-2">
                        <input
                          value={editData.canonical_term}
                          onChange={(e) => setEditData({ ...editData, canonical_term: e.target.value })}
                          className="px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-900 dark:text-gray-200"
                          aria-label="Edit canonical term"
                        />
                        <input
                          value={editData.category}
                          onChange={(e) => setEditData({ ...editData, category: e.target.value })}
                          className="px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-900 dark:text-gray-200"
                          aria-label="Edit category"
                        />
                      </div>
                      <div className="grid grid-cols-4 gap-1 mb-2">
                        {SUPPORTED_LANGS.map((lang) => (
                          <input
                            key={lang}
                            placeholder={lang.toUpperCase()}
                            value={editData.translations[lang] ?? ''}
                            onChange={(e) => setEditData({
                              ...editData,
                              translations: { ...editData.translations, [lang]: e.target.value },
                            })}
                            className="px-1 py-0.5 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-900 dark:text-gray-200"
                          />
                        ))}
                      </div>
                      <div className="flex gap-2">
                        <button onClick={handleSaveEdit} className="text-xs px-2 py-1 rounded bg-green-500 text-white" aria-label="Save edit">Save</button>
                        <button onClick={() => { setEditingId(null); setEditData(null) }} className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300" aria-label="Cancel edit">Cancel</button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <span
                            className="font-medium text-sm text-gray-800 dark:text-gray-200 cursor-pointer hover:text-blue-500"
                            onClick={() => handleStartEdit(t)}
                            role="button"
                            tabIndex={0}
                            aria-label={`Edit term ${t.canonical_term}`}
                          >
                            {t.canonical_term}
                          </span>
                          <span className="text-xs px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-500">{t.category}</span>
                        </div>
                        <button
                          onClick={() => handleDeleteTerm(t.id)}
                          className="text-xs text-red-400 hover:text-red-600"
                          aria-label={`Delete term ${t.canonical_term}`}
                        >
                          Delete
                        </button>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(t.translations).map(([lang, text]) => (
                          <span key={lang} className="text-xs text-gray-500 dark:text-gray-400">
                            <span className="uppercase font-medium">{lang}</span>: {text}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Domains</h3>
            <button
              onClick={() => setShowAddDomain(true)}
              className="text-xs px-3 py-1.5 rounded bg-blue-500 text-white hover:bg-blue-600"
              aria-label="Add new domain"
            >
              Add Domain
            </button>
          </div>

          {showAddDomain && (
            <div className="flex gap-2 mb-4" data-testid="add-domain-form">
              <input
                placeholder="Domain name"
                value={newDomainName}
                onChange={(e) => setNewDomainName(e.target.value)}
                className="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-900 dark:text-gray-200"
                aria-label="Domain name input"
              />
              <button onClick={handleAddDomain} className="text-xs px-3 py-1.5 rounded bg-blue-500 text-white" aria-label="Save domain">Save</button>
              <button onClick={() => setShowAddDomain(false)} className="text-xs px-3 py-1.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300" aria-label="Cancel add domain">Cancel</button>
            </div>
          )}

          {domains.length === 0 ? (
            <div className="text-center text-gray-400 py-8 text-sm">No domains yet</div>
          ) : (
            <div className="space-y-2">
              {domains.map((d) => (
                <div
                  key={d.id}
                  onClick={() => setSelectedDomain(d.id)}
                  className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 flex items-center justify-between"
                  role="button"
                  tabIndex={0}
                  aria-label={`Open domain ${d.name}`}
                >
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{d.name}</span>
                  <span className="text-xs text-gray-400">{d.term_count} terms</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
