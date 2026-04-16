import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { AdminPanel } from '../AdminPanel'

// Mock child components to avoid fetch calls
vi.mock('../SessionList', () => ({ SessionList: () => <div data-testid="mock-session-list" /> }))
vi.mock('../StatsPanel', () => ({ StatsPanel: () => <div data-testid="mock-stats-panel" /> }))
vi.mock('../GlossaryManager', () => ({ GlossaryManager: () => <div data-testid="mock-glossary-manager" /> }))

describe('AdminPanel', () => {
  it('renders admin panel with tabs', () => {
    render(<AdminPanel onClose={vi.fn()} />)
    expect(screen.getByTestId('admin-panel')).toBeDefined()
    expect(screen.getByText('Admin Panel')).toBeDefined()
    expect(screen.getByText('Sessions')).toBeDefined()
    expect(screen.getByText('Stats')).toBeDefined()
    expect(screen.getByText('Glossary')).toBeDefined()
  })

  it('shows sessions tab by default', () => {
    render(<AdminPanel onClose={vi.fn()} />)
    expect(screen.getByTestId('mock-session-list')).toBeDefined()
  })

  it('switches to stats tab', () => {
    render(<AdminPanel onClose={vi.fn()} />)
    fireEvent.click(screen.getByText('Stats'))
    expect(screen.getByTestId('mock-stats-panel')).toBeDefined()
  })

  it('switches to glossary tab', () => {
    render(<AdminPanel onClose={vi.fn()} />)
    fireEvent.click(screen.getByText('Glossary'))
    expect(screen.getByTestId('mock-glossary-manager')).toBeDefined()
  })

  it('calls onClose when close clicked', () => {
    const onClose = vi.fn()
    render(<AdminPanel onClose={onClose} />)
    fireEvent.click(screen.getByLabelText('Close admin'))
    expect(onClose).toHaveBeenCalled()
  })
})
