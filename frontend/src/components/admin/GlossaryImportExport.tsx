import { useCallback, useRef, useState } from 'react'
import { API_URL } from '../../config'

interface GlossaryImportExportProps {
  onImportComplete?: () => void
}

export function GlossaryImportExport({ onImportComplete }: GlossaryImportExportProps) {
  const [importing, setImporting] = useState(false)
  const [status, setStatus] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const handleExport = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/admin/glossary/export`)
      if (!res.ok) { setStatus('Export failed'); return }
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'glossary-export.json'
      a.click()
      URL.revokeObjectURL(url)
      setStatus('Exported successfully')
    } catch {
      setStatus('Export failed')
    }
  }, [])

  const handleImport = useCallback(async (file: File) => {
    setImporting(true)
    setStatus('Importing...')
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch(`${API_URL}/api/admin/glossary/import`, {
        method: 'POST',
        body: formData,
      })
      if (res.ok) {
        const result = await res.json()
        setStatus(`Imported ${result.count ?? 0} terms`)
        onImportComplete?.()
      } else {
        setStatus('Import failed')
      }
    } catch {
      setStatus('Import failed')
    }
    setImporting(false)
  }, [onImportComplete])

  return (
    <div className="flex items-center gap-3" data-testid="glossary-import-export">
      <button
        onClick={handleExport}
        className="text-xs px-3 py-1.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
        aria-label="Export glossary"
      >
        Export JSON
      </button>

      <button
        onClick={() => fileRef.current?.click()}
        disabled={importing}
        className="text-xs px-3 py-1.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50"
        aria-label="Import glossary"
      >
        {importing ? 'Importing...' : 'Import JSON'}
      </button>

      <input
        ref={fileRef}
        type="file"
        accept=".json"
        className="hidden"
        data-testid="import-file-input"
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) handleImport(file)
        }}
      />

      {status && (
        <span className="text-xs text-gray-500 dark:text-gray-400" data-testid="import-status">
          {status}
        </span>
      )}
    </div>
  )
}
