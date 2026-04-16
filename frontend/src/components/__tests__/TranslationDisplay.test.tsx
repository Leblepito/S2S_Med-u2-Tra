import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TranslationDisplay } from '../TranslationDisplay'
import type { FinalTranscript, TranslationResult } from '../../types'

describe('TranslationDisplay', () => {
  it('renders empty state message when no data', () => {
    render(
      <TranslationDisplay
        partialText=""
        transcripts={[]}
        translations={[]}
      />,
    )
    expect(screen.getByText(/waiting/i)).toBeDefined()
  })

  it('shows partial transcript with pulsing indicator', () => {
    render(
      <TranslationDisplay
        partialText="Merhaba nasil..."
        transcripts={[]}
        translations={[]}
      />,
    )
    expect(screen.getByText('Merhaba nasil...')).toBeDefined()
  })

  it('shows final transcript', () => {
    const transcripts: FinalTranscript[] = [
      {
        type: 'final_transcript',
        text: 'Merhaba nasilsiniz',
        lang: 'tr',
        speaker_id: 0,
        confidence: 0.98,
      },
    ]
    render(
      <TranslationDisplay
        partialText=""
        transcripts={transcripts}
        translations={[]}
      />,
    )
    expect(screen.getByText('Merhaba nasilsiniz')).toBeDefined()
    expect(screen.getByText('tr')).toBeDefined()
  })

  it('shows translation results', () => {
    const translations: TranslationResult[] = [
      {
        type: 'translation',
        source_text: 'Merhaba',
        source_lang: 'tr',
        translations: { en: 'Hello', th: 'สวัสดี' },
        speaker_id: 0,
      },
    ]
    render(
      <TranslationDisplay
        partialText=""
        transcripts={[]}
        translations={translations}
      />,
    )
    expect(screen.getByText('Hello')).toBeDefined()
    expect(screen.getByText('สวัสดี')).toBeDefined()
  })

  it('shows language badges on translations', () => {
    const translations: TranslationResult[] = [
      {
        type: 'translation',
        source_text: 'Test',
        source_lang: 'tr',
        translations: { en: 'Test EN', ru: 'Тест' },
        speaker_id: 0,
      },
    ]
    render(
      <TranslationDisplay
        partialText=""
        transcripts={[]}
        translations={translations}
      />,
    )
    expect(screen.getByText('en')).toBeDefined()
    expect(screen.getByText('ru')).toBeDefined()
  })

  it('shows multiple transcript entries', () => {
    const transcripts: FinalTranscript[] = [
      { type: 'final_transcript', text: 'First', lang: 'en', speaker_id: 0, confidence: 0.9 },
      { type: 'final_transcript', text: 'Second', lang: 'en', speaker_id: 0, confidence: 0.9 },
    ]
    render(
      <TranslationDisplay
        partialText=""
        transcripts={transcripts}
        translations={[]}
      />,
    )
    expect(screen.getByText('First')).toBeDefined()
    expect(screen.getByText('Second')).toBeDefined()
  })

  // ── Multi-Speaker Tests ──

  it('shows SpeakerIndicator badges when multiple speakers exist', () => {
    const transcripts: FinalTranscript[] = [
      { type: 'final_transcript', text: 'Hello', lang: 'en', speaker_id: 0, confidence: 0.9 },
      { type: 'final_transcript', text: 'Merhaba', lang: 'tr', speaker_id: 1, confidence: 0.9 },
    ]
    render(
      <TranslationDisplay
        partialText=""
        transcripts={transcripts}
        translations={[]}
      />,
    )
    expect(screen.getByTestId('speaker-0')).toBeDefined()
    expect(screen.getByTestId('speaker-1')).toBeDefined()
    expect(screen.getByText('Speaker 0')).toBeDefined()
    expect(screen.getByText('Speaker 1')).toBeDefined()
  })

  it('does not show speaker badges when single speaker', () => {
    const transcripts: FinalTranscript[] = [
      { type: 'final_transcript', text: 'Hello', lang: 'en', speaker_id: 0, confidence: 0.9 },
      { type: 'final_transcript', text: 'World', lang: 'en', speaker_id: 0, confidence: 0.9 },
    ]
    render(
      <TranslationDisplay
        partialText=""
        transcripts={transcripts}
        translations={[]}
      />,
    )
    expect(screen.queryByTestId('speaker-0')).toBeNull()
  })

  it('groups consecutive same-speaker transcripts together', () => {
    const transcripts: FinalTranscript[] = [
      { type: 'final_transcript', text: 'A1', lang: 'en', speaker_id: 0, confidence: 0.9 },
      { type: 'final_transcript', text: 'A2', lang: 'en', speaker_id: 0, confidence: 0.9 },
      { type: 'final_transcript', text: 'B1', lang: 'tr', speaker_id: 1, confidence: 0.9 },
      { type: 'final_transcript', text: 'A3', lang: 'en', speaker_id: 0, confidence: 0.9 },
    ]
    render(
      <TranslationDisplay
        partialText=""
        transcripts={transcripts}
        translations={[]}
      />,
    )
    // 3 groups: [0: A1,A2], [1: B1], [0: A3]
    // So we should see "Speaker 0" twice and "Speaker 1" once
    const speaker0Badges = screen.getAllByText('Speaker 0')
    expect(speaker0Badges).toHaveLength(2)
    expect(screen.getByText('Speaker 1')).toBeDefined()
    // All texts rendered
    expect(screen.getByText('A1')).toBeDefined()
    expect(screen.getByText('A2')).toBeDefined()
    expect(screen.getByText('B1')).toBeDefined()
    expect(screen.getByText('A3')).toBeDefined()
  })

  it('shows active pulse on speaker badge when activeSpeakers set provided', () => {
    const transcripts: FinalTranscript[] = [
      { type: 'final_transcript', text: 'Hello', lang: 'en', speaker_id: 0, confidence: 0.9 },
      { type: 'final_transcript', text: 'Hi', lang: 'en', speaker_id: 1, confidence: 0.9 },
    ]
    const activeSpeakers = new Set([0])
    render(
      <TranslationDisplay
        partialText=""
        transcripts={transcripts}
        translations={[]}
        activeSpeakers={activeSpeakers}
      />,
    )
    const speaker0 = screen.getByTestId('speaker-0')
    const dot0 = speaker0.querySelector('span')
    expect(dot0?.className).toContain('animate-pulse')

    const speaker1 = screen.getByTestId('speaker-1')
    const dot1 = speaker1.querySelector('span')
    expect(dot1?.className).not.toContain('animate-pulse')
  })
})
