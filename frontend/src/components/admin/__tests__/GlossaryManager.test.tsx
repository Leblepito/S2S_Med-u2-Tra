import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { GlossaryManager } from '../GlossaryManager'

const mockDomains = [
  { id: 'd1', name: 'Medical', term_count: 15 },
  { id: 'd2', name: 'Tourism', term_count: 8 },
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
      .mockResolvedValueOnce(new Response('[]', { status: 200 }))

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
      .mockResolvedValueOnce(new Response('[]', { status: 200 }))

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
})
