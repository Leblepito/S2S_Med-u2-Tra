import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { LanguageSelector } from '../LanguageSelector'
import type { SupportedLang } from '../../types'

describe('LanguageSelector', () => {
  const defaultProps = {
    sourceLang: 'auto' as const,
    targetLangs: ['en', 'th'] as SupportedLang[],
    onSourceChange: vi.fn(),
    onTargetToggle: vi.fn(),
  }

  it('renders source language selector', () => {
    render(<LanguageSelector {...defaultProps} />)
    expect(screen.getByText('Source')).toBeDefined()
  })

  it('renders target language chips', () => {
    render(<LanguageSelector {...defaultProps} />)
    expect(screen.getByText('Target')).toBeDefined()
  })

  it('shows auto-detect as default source', () => {
    render(<LanguageSelector {...defaultProps} />)
    const select = screen.getByRole('combobox') as HTMLSelectElement
    expect(select.value).toBe('auto')
  })

  it('calls onSourceChange when source changes', () => {
    const onSourceChange = vi.fn()
    render(<LanguageSelector {...defaultProps} onSourceChange={onSourceChange} />)
    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: 'tr' } })
    expect(onSourceChange).toHaveBeenCalledWith('tr')
  })

  it('calls onTargetToggle when target chip clicked', () => {
    const onTargetToggle = vi.fn()
    render(<LanguageSelector {...defaultProps} onTargetToggle={onTargetToggle} />)
    // Click on a non-selected language chip
    const ruButton = screen.getByRole('button', { name: /RU/i })
    fireEvent.click(ruButton)
    expect(onTargetToggle).toHaveBeenCalledWith('ru')
  })

  it('highlights selected target languages', () => {
    render(<LanguageSelector {...defaultProps} />)
    const enButton = screen.getByRole('button', { name: /EN/i })
    const thButton = screen.getByRole('button', { name: /TH/i })
    // Selected ones should have the active class
    expect(enButton.className).toContain('bg-blue')
    expect(thButton.className).toContain('bg-blue')
  })

  it('renders all 7 target language options', () => {
    render(<LanguageSelector {...defaultProps} />)
    const buttons = screen.getAllByRole('button')
    expect(buttons.length).toBe(7)
  })
})
