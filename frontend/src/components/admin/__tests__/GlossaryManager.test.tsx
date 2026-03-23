import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { GlossaryManager } from '../GlossaryManager'

const mockDomains = [
  { id: 'd1', name: 'Medical', term_count: 15 },
  { id: 'd2', name: 'Tourism', term_count: 8 },
]

const mockTerms = [
  { id: 't1', canonical_term: 'hair transplant', category: 'procedure', translations: { tr: 'sa\u00E7 ekimi', en: 'hair transplant' } },
  { id: 't2', canonical_term: 'rhinoplasty', category: 'procedure', translations: { tr: 'burun estetigi', en: 'rhinoplasty' } },
]

describe('GlossaryManager', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders domain list after fetch', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify(mockDomains), { status: 200 }))
    render(<GlossaryManager />)
    await waitFor(() => {
      expect(screen.getByTestId('glossary-manager')).toBeDefined()
    })
    expect(screen.getByText('Medical')).toBeDefined()
    expect(screen.getByText('Tourism')).toBeDefined()
    expect(screen.getByText('15 terms')).toBeDefined()
  })

  it('shows add domain form when button clicked', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify(mockDomains), { status: 200 }))
    render(<GlossaryManager />)
    await waitFor(() => {
      expect(screen.getByText('Add Domain')).toBeDefined()
    })
    fireEvent.click(screen.getByText('Add Domain'))
    expect(screen.getByTestId('add-domain-form')).toBeDefined()
    expect(screen.getByPlaceholderText('Domain name')).toBeDefined()
  })

  it('navigates to term list when domain clicked', async () => {
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response(JSON.stringify(mockDomains), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(mockTerms), { status: 200 }))

    render(<GlossaryManager />)
    await waitFor(() => {
      expect(screen.getByText('Medical')).toBeDefined()
    })
    fireEvent.click(screen.getByText('Medical'))
    await waitFor(() => {
      expect(screen.getByText(/Back to domains/)).toBeDefined()
    })
    expect(screen.getByText('Add Term')).toBeDefined()
  })

  it('shows add term form', async () => {
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response(JSON.stringify(mockDomains), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify([]), { status: 200 }))

    render(<GlossaryManager />)
    await waitFor(() => {
      fireEvent.click(screen.getByText('Medical'))
    })
    await waitFor(() => {
      expect(screen.getByText('Add Term')).toBeDefined()
    })
    fireEvent.click(screen.getByText('Add Term'))
    expect(screen.getByTestId('add-term-form')).toBeDefined()
    expect(screen.getByPlaceholderText('Canonical term')).toBeDefined()
    expect(screen.getByPlaceholderText('Category')).toBeDefined()
  })

  it('filters terms by search query', async () => {
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response(JSON.stringify(mockDomains), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(mockTerms), { status: 200 }))

    render(<GlossaryManager />)
    await waitFor(() => {
      fireEvent.click(screen.getByText('Medical'))
    })
    await waitFor(() => {
      expect(screen.getByText('hair transplant')).toBeDefined()
    })

    const search = screen.getByTestId('term-search')
    fireEvent.change(search, { target: { value: 'rhino' } })
    expect(screen.getByText('rhinoplasty')).toBeDefined()
    expect(screen.queryByText('hair transplant')).toBeNull()
  })

  it('shows no matching terms message when search has no results', async () => {
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response(JSON.stringify(mockDomains), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(mockTerms), { status: 200 }))

    render(<GlossaryManager />)
    await waitFor(() => {
      fireEvent.click(screen.getByText('Medical'))
    })
    await waitFor(() => {
      expect(screen.getByTestId('term-search')).toBeDefined()
    })

    fireEvent.change(screen.getByTestId('term-search'), { target: { value: 'zzzzz' } })
    expect(screen.getByText('No matching terms')).toBeDefined()
  })

  it('shows edit form when term clicked', async () => {
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response(JSON.stringify(mockDomains), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(mockTerms), { status: 200 }))

    render(<GlossaryManager />)
    await waitFor(() => {
      fireEvent.click(screen.getByText('Medical'))
    })
    await waitFor(() => {
      expect(screen.getByText('hair transplant')).toBeDefined()
    })

    fireEvent.click(screen.getByLabelText('Edit term hair transplant'))
    expect(screen.getByTestId('edit-form-t1')).toBeDefined()
    expect(screen.getByLabelText('Edit canonical term')).toBeDefined()
  })

  it('deletes a term', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response(JSON.stringify(mockDomains), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(mockTerms), { status: 200 }))
      .mockResolvedValueOnce(new Response('ok', { status: 200 }))

    render(<GlossaryManager />)
    await waitFor(() => {
      fireEvent.click(screen.getByText('Medical'))
    })
    await waitFor(() => {
      expect(screen.getByText('hair transplant')).toBeDefined()
    })

    fireEvent.click(screen.getByLabelText('Delete term hair transplant'))
    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledTimes(3)
    })
  })

  it('has proper aria labels on domains', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify(mockDomains), { status: 200 }))
    render(<GlossaryManager />)
    await waitFor(() => {
      expect(screen.getByLabelText('Open domain Medical')).toBeDefined()
      expect(screen.getByLabelText('Add new domain')).toBeDefined()
    })
  })
})
