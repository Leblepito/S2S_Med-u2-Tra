import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SpeakerIndicator, getSpeakerColor } from '../SpeakerIndicator'

describe('SpeakerIndicator', () => {
  it('renders speaker label with correct id', () => {
    render(<SpeakerIndicator speakerId={0} isActive={false} />)
    expect(screen.getByText('Speaker 0')).toBeDefined()
  })

  it('renders with correct test id', () => {
    render(<SpeakerIndicator speakerId={2} isActive={false} />)
    expect(screen.getByTestId('speaker-2')).toBeDefined()
  })

  it('applies blue color for speaker 0', () => {
    render(<SpeakerIndicator speakerId={0} isActive={false} />)
    const badge = screen.getByTestId('speaker-0')
    expect(badge.className).toContain('bg-blue-100')
    expect(badge.className).toContain('text-blue-700')
  })

  it('applies green color for speaker 1', () => {
    render(<SpeakerIndicator speakerId={1} isActive={false} />)
    const badge = screen.getByTestId('speaker-1')
    expect(badge.className).toContain('bg-green-100')
    expect(badge.className).toContain('text-green-700')
  })

  it('applies orange color for speaker 2', () => {
    render(<SpeakerIndicator speakerId={2} isActive={false} />)
    const badge = screen.getByTestId('speaker-2')
    expect(badge.className).toContain('bg-orange-100')
  })

  it('applies purple color for speaker 3', () => {
    render(<SpeakerIndicator speakerId={3} isActive={false} />)
    const badge = screen.getByTestId('speaker-3')
    expect(badge.className).toContain('bg-purple-100')
  })

  it('applies gray fallback for speaker 4+', () => {
    render(<SpeakerIndicator speakerId={5} isActive={false} />)
    const badge = screen.getByTestId('speaker-5')
    expect(badge.className).toContain('bg-gray-100')
    expect(badge.className).toContain('text-gray-700')
  })

  it('shows pulse animation when active', () => {
    render(<SpeakerIndicator speakerId={0} isActive={true} />)
    const badge = screen.getByTestId('speaker-0')
    const dot = badge.querySelector('span')
    expect(dot?.className).toContain('animate-pulse')
  })

  it('does not show pulse animation when inactive', () => {
    render(<SpeakerIndicator speakerId={0} isActive={false} />)
    const badge = screen.getByTestId('speaker-0')
    const dot = badge.querySelector('span')
    expect(dot?.className).not.toContain('animate-pulse')
  })
})

describe('getSpeakerColor', () => {
  it('returns blue for speaker 0', () => {
    expect(getSpeakerColor(0).bg).toBe('bg-blue-100')
  })

  it('returns gray for unknown speaker ids', () => {
    expect(getSpeakerColor(99).bg).toBe('bg-gray-100')
  })
})
