import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ConversationHistory } from '../ConversationHistory'
import type { Session } from '../../hooks/useConversationHistory'

const mockSession: Session = {
  id: 'test-1',
  startedAt: Date.now(),
  entries: [
    { timestamp: Date.now(), type: 'transcript', speaker_id: 0, text: 'Hello', lang: 'en' },
    { timestamp: Date.now(), type: 'translation', speaker_id: 0, text: 'Hello', translations: { tr: 'Merhaba' } },
  ],
}

const defaultProps = {
  sessions: [mockSession],
  currentExportText: () => 'Speaker 0: Hello',
  currentExportJSON: () => '[]',
  onDeleteSession: vi.fn(),
  onClearAll: vi.fn(),
  onClose: vi.fn(),
}

describe('ConversationHistory', () => {
  it('renders history panel', () => {
    render(<ConversationHistory {...defaultProps} />)
    expect(screen.getByTestId('history-panel')).toBeDefined()
    expect(screen.getByText('History')).toBeDefined()
  })

  it('shows session list with entry count', () => {
    render(<ConversationHistory {...defaultProps} />)
    expect(screen.getByText('2 entries')).toBeDefined()
    expect(screen.getByText('1 speakers')).toBeDefined()
  })

  it('shows empty state when no sessions', () => {
    render(<ConversationHistory {...defaultProps} sessions={[]} />)
    expect(screen.getByText('No sessions yet')).toBeDefined()
  })

  it('shows detail view when session clicked', () => {
    render(<ConversationHistory {...defaultProps} />)
    fireEvent.click(screen.getByText('2 entries'))
    const speakers = screen.getAllByText('Speaker 0:')
    expect(speakers.length).toBe(2)
    expect(screen.getByText(/Back to list/)).toBeDefined()
  })

  it('shows export buttons', () => {
    render(<ConversationHistory {...defaultProps} />)
    expect(screen.getByText('Copy Text')).toBeDefined()
    expect(screen.getByText('Download JSON')).toBeDefined()
  })

  it('calls onDeleteSession when delete clicked', () => {
    const onDelete = vi.fn()
    render(<ConversationHistory {...defaultProps} onDeleteSession={onDelete} />)
    const deleteBtn = screen.getByLabelText('Delete session')
    fireEvent.click(deleteBtn)
    expect(onDelete).toHaveBeenCalledWith('test-1')
  })

  it('calls onClearAll when clear all clicked', () => {
    const onClearAll = vi.fn()
    render(<ConversationHistory {...defaultProps} onClearAll={onClearAll} />)
    fireEvent.click(screen.getByText('Clear All'))
    expect(onClearAll).toHaveBeenCalled()
  })

  it('calls onClose when close clicked', () => {
    const onClose = vi.fn()
    render(<ConversationHistory {...defaultProps} onClose={onClose} />)
    fireEvent.click(screen.getByLabelText('Close history'))
    expect(onClose).toHaveBeenCalled()
  })
})
