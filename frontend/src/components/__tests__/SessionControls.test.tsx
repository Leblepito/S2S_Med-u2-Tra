import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { SessionControls, formatTime } from '../SessionControls'

describe('formatTime', () => {
  it('formats 0 as 00:00', () => {
    expect(formatTime(0)).toBe('00:00')
  })

  it('formats 65 as 01:05', () => {
    expect(formatTime(65)).toBe('01:05')
  })

  it('formats 3661 as 61:01', () => {
    expect(formatTime(3661)).toBe('61:01')
  })
})

describe('SessionControls', () => {
  const defaultProps = {
    isCapturing: false,
    transcriptCount: 0,
    speakerCount: 0,
    onNewSession: vi.fn(),
    onToggleHistory: vi.fn(),
  }

  it('renders session controls', () => {
    render(<SessionControls {...defaultProps} />)
    expect(screen.getByTestId('session-controls')).toBeDefined()
  })

  it('shows timer starting at 00:00', () => {
    render(<SessionControls {...defaultProps} />)
    expect(screen.getByTestId('session-timer').textContent).toBe('00:00')
  })

  it('shows transcript and speaker count when available', () => {
    render(<SessionControls {...defaultProps} transcriptCount={5} speakerCount={2} />)
    expect(screen.getByText('5 transcripts, 2 speakers')).toBeDefined()
  })

  it('calls onNewSession when New clicked', () => {
    const onNew = vi.fn()
    render(<SessionControls {...defaultProps} onNewSession={onNew} />)
    fireEvent.click(screen.getByText('New'))
    expect(onNew).toHaveBeenCalled()
  })

  it('calls onToggleHistory when History clicked', () => {
    const onToggle = vi.fn()
    render(<SessionControls {...defaultProps} onToggleHistory={onToggle} />)
    fireEvent.click(screen.getByText('History'))
    expect(onToggle).toHaveBeenCalled()
  })

  it('shows red timer color when capturing', () => {
    render(<SessionControls {...defaultProps} isCapturing={true} />)
    const timer = screen.getByTestId('session-timer')
    expect(timer.className).toContain('text-red-500')
  })
})
