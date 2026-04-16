import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { GlossaryImportExport } from '../GlossaryImportExport'

describe('GlossaryImportExport', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders export and import buttons', () => {
    render(<GlossaryImportExport />)
    expect(screen.getByTestId('glossary-import-export')).toBeDefined()
    expect(screen.getByText('Export JSON')).toBeDefined()
    expect(screen.getByText('Import JSON')).toBeDefined()
  })

  it('triggers export fetch on click', async () => {
    const blob = new Blob(['{}'], { type: 'application/json' })
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(blob, { status: 200 }))

    // Mock URL.createObjectURL and revokeObjectURL
    const createURL = vi.fn(() => 'blob:test')
    const revokeURL = vi.fn()
    globalThis.URL.createObjectURL = createURL
    globalThis.URL.revokeObjectURL = revokeURL

    render(<GlossaryImportExport />)
    fireEvent.click(screen.getByText('Export JSON'))

    await vi.waitFor(() => {
      expect(fetchSpy).toHaveBeenCalled()
    })
  })

  it('has file input for import', () => {
    render(<GlossaryImportExport />)
    const fileInput = screen.getByTestId('import-file-input') as HTMLInputElement
    expect(fileInput.type).toBe('file')
    expect(fileInput.accept).toBe('.json')
  })

  it('has proper aria labels', () => {
    render(<GlossaryImportExport />)
    expect(screen.getByLabelText('Export glossary')).toBeDefined()
    expect(screen.getByLabelText('Import glossary')).toBeDefined()
  })
})
