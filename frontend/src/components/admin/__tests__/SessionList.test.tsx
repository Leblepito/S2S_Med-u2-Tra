import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { SessionList } from '../SessionList'

const mockSessions = [
  { id: 's1', started_at: '2026-03-23T10:00:00Z', duration_sec: 120, speaker_count: 2, transcript_count: 5, langs: ['tr', 'en'] },
  { id: 's2', started_at: '2026-03-23T11:00:00Z', duration_sec: 60, speaker_count: 1, transcript_count: 3, langs: ['en'] },
]

describe('SessionList', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('shows loading state initially', () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => new Promise(() => {}))
    render(<SessionList />)
    expect(screen.getByText('Loading sessions...')).toBeDefined()
  })

  it('renders session table after fetch', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify(mockSessions), { status: 200 }))
    render(<SessionList />)
    await waitFor(() => {
      expect(screen.getByTestId('session-table')).toBeDefined()
    })
    expect(screen.getByText('120s')).toBeDefined()
    expect(screen.getByText('60s')).toBeDefined()
  })

  it('shows empty state when no sessions', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('[]', { status: 200 }))
    render(<SessionList />)
    await waitFor(() => {
      expect(screen.getByText('No sessions found')).toBeDefined()
    })
  })

  it('shows pagination controls', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify(mockSessions), { status: 200 }))
    render(<SessionList />)
    await waitFor(() => {
      expect(screen.getByTestId('pagination')).toBeDefined()
    })
    expect(screen.getByText('Page 1')).toBeDefined()
    expect(screen.getByText('Previous')).toBeDefined()
    expect(screen.getByText('Next')).toBeDefined()
  })

  it('deletes a session', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response(JSON.stringify(mockSessions), { status: 200 }))
      .mockResolvedValueOnce(new Response('ok', { status: 200 }))

    render(<SessionList />)
    await waitFor(() => {
      expect(screen.getByTestId('session-table')).toBeDefined()
    })

    const deleteBtns = screen.getAllByText('Delete')
    fireEvent.click(deleteBtns[0])

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledTimes(2)
    })
  })
})
