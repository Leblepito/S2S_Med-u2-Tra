import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { StatsPanel } from '../StatsPanel'

const mockStats = {
  total_sessions: 42,
  total_transcripts: 350,
  avg_duration_sec: 185,
  lang_usage: { tr: 120, en: 100, th: 50, ru: 30 },
}

describe('StatsPanel', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('shows loading state', () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => new Promise(() => {}))
    render(<StatsPanel />)
    expect(screen.getByTestId('stats-loading')).toBeDefined()
  })

  it('renders stats cards after fetch', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify(mockStats), { status: 200 }))
    render(<StatsPanel />)
    await waitFor(() => {
      expect(screen.getByTestId('stats-panel')).toBeDefined()
    })
    expect(screen.getByText('42')).toBeDefined()
    expect(screen.getByText('350')).toBeDefined()
    expect(screen.getByText('185s')).toBeDefined()
  })

  it('renders language bars', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify(mockStats), { status: 200 }))
    render(<StatsPanel />)
    await waitFor(() => {
      expect(screen.getByTestId('bar-tr')).toBeDefined()
      expect(screen.getByTestId('bar-en')).toBeDefined()
    })
  })
})
