import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ConnectionStatus } from '../ConnectionStatus'
import { TranslationDisplay } from '../TranslationDisplay'
import { LanguageSelector, LANG_FULL_NAMES } from '../LanguageSelector'
import type { SupportedLang, FinalTranscript } from '../../types'

describe('Accessibility', () => {
  describe('ConnectionStatus', () => {
    it('has role="status" on banner', () => {
      render(<ConnectionStatus wsStatus="connected" backendHealthy={true} />)
      const banner = screen.getByTestId('connection-banner')
      expect(banner.getAttribute('role')).toBe('status')
    })

    it('has aria-live="polite"', () => {
      render(<ConnectionStatus wsStatus="disconnected" backendHealthy={true} />)
      const banner = screen.getByTestId('connection-banner')
      expect(banner.getAttribute('aria-live')).toBe('polite')
    })
  })

  describe('TranslationDisplay', () => {
    it('has aria-live on output container', () => {
      const transcripts: FinalTranscript[] = [
        { type: 'final_transcript', text: 'Hello', lang: 'en', speaker_id: 0, confidence: 0.9 },
      ]
      render(<TranslationDisplay partialText="" transcripts={transcripts} translations={[]} />)
      const container = screen.getByLabelText('Translation output')
      expect(container.getAttribute('aria-live')).toBe('polite')
    })
  })

  describe('LanguageSelector', () => {
    const defaultProps = {
      sourceLang: 'auto' as const,
      targetLangs: ['en', 'th'] as SupportedLang[],
      onSourceChange: vi.fn(),
      onTargetToggle: vi.fn(),
    }

    it('has title tooltip with full language name', () => {
      render(<LanguageSelector {...defaultProps} />)
      const trButton = screen.getByRole('button', { name: /Turkish/ })
      expect(trButton.getAttribute('title')).toBe(LANG_FULL_NAMES['tr'])
    })

    it('has aria-pressed on selected targets', () => {
      render(<LanguageSelector {...defaultProps} />)
      const enButton = screen.getByRole('button', { name: /English/ })
      expect(enButton.getAttribute('aria-pressed')).toBe('true')
    })

    it('has aria-pressed=false on unselected targets', () => {
      render(<LanguageSelector {...defaultProps} />)
      const ruButton = screen.getByRole('button', { name: /Russian/ })
      expect(ruButton.getAttribute('aria-pressed')).toBe('false')
    })

    it('has role="group" on language selection', () => {
      render(<LanguageSelector {...defaultProps} />)
      expect(screen.getByRole('group', { name: /Language selection/ })).toBeDefined()
    })
  })
})
