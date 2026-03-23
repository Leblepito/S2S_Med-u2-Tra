import { describe, it, expect } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useTranslation } from '../useTranslation'
import type { PartialTranscript, FinalTranscript, TranslationResult } from '../../types'

describe('useTranslation', () => {
  it('initializes with empty state', () => {
    const { result } = renderHook(() => useTranslation())
    expect(result.current.partialText).toBe('')
    expect(result.current.transcripts).toEqual([])
    expect(result.current.translations).toEqual([])
    expect(result.current.activeSpeakers.size).toBe(0)
    expect(result.current.speakerTranscripts.size).toBe(0)
    expect(result.current.speakerTranslations.size).toBe(0)
  })

  it('updates partialText on partial transcript', () => {
    const { result } = renderHook(() => useTranslation())
    const msg: PartialTranscript = {
      type: 'partial_transcript',
      text: 'Merhaba nasil...',
      lang: 'tr',
      speaker_id: 0,
      confidence: 0.8,
    }
    act(() => {
      result.current.handleMessage(msg)
    })
    expect(result.current.partialText).toBe('Merhaba nasil...')
  })

  it('adds to transcripts on final transcript and clears partial', () => {
    const { result } = renderHook(() => useTranslation())

    // First partial
    act(() => {
      result.current.handleMessage({
        type: 'partial_transcript',
        text: 'Merhaba',
        lang: 'tr',
        speaker_id: 0,
        confidence: 0.9,
      })
    })
    expect(result.current.partialText).toBe('Merhaba')

    // Then final
    const final: FinalTranscript = {
      type: 'final_transcript',
      text: 'Merhaba nasilsiniz',
      lang: 'tr',
      speaker_id: 0,
      confidence: 0.98,
    }
    act(() => {
      result.current.handleMessage(final)
    })
    expect(result.current.partialText).toBe('')
    expect(result.current.transcripts).toHaveLength(1)
    expect(result.current.transcripts[0].text).toBe('Merhaba nasilsiniz')
  })

  it('adds translation results', () => {
    const { result } = renderHook(() => useTranslation())
    const translation: TranslationResult = {
      type: 'translation',
      source_text: 'Merhaba nasilsiniz',
      source_lang: 'tr',
      translations: { en: 'Hello how are you', th: 'สวัสดี' },
      speaker_id: 0,
    }
    act(() => {
      result.current.handleMessage(translation)
    })
    expect(result.current.translations).toHaveLength(1)
    expect(result.current.translations[0].translations.en).toBe('Hello how are you')
  })

  it('handles multiple transcripts in sequence', () => {
    const { result } = renderHook(() => useTranslation())

    act(() => {
      result.current.handleMessage({
        type: 'final_transcript',
        text: 'Birinci cumle',
        lang: 'tr',
        speaker_id: 0,
        confidence: 0.95,
      })
    })
    act(() => {
      result.current.handleMessage({
        type: 'final_transcript',
        text: 'Ikinci cumle',
        lang: 'tr',
        speaker_id: 0,
        confidence: 0.93,
      })
    })

    expect(result.current.transcripts).toHaveLength(2)
  })

  it('clears all state on reset', () => {
    const { result } = renderHook(() => useTranslation())

    act(() => {
      result.current.handleMessage({
        type: 'final_transcript',
        text: 'Test',
        lang: 'tr',
        speaker_id: 0,
        confidence: 0.9,
      })
    })
    act(() => {
      result.current.handleMessage({
        type: 'translation',
        source_text: 'Test',
        source_lang: 'tr',
        translations: { en: 'Test' },
        speaker_id: 0,
      })
    })

    act(() => {
      result.current.reset()
    })

    expect(result.current.partialText).toBe('')
    expect(result.current.transcripts).toEqual([])
    expect(result.current.translations).toEqual([])
    expect(result.current.activeSpeakers.size).toBe(0)
    expect(result.current.speakerTranscripts.size).toBe(0)
    expect(result.current.speakerTranslations.size).toBe(0)
  })

  // ── Speaker Diarization Tests ──

  it('tracks active speakers from partial transcripts', () => {
    const { result } = renderHook(() => useTranslation())

    act(() => {
      result.current.handleMessage({
        type: 'partial_transcript',
        text: 'Hello',
        lang: 'en',
        speaker_id: 0,
        confidence: 0.8,
      })
    })
    expect(result.current.activeSpeakers.has(0)).toBe(true)

    act(() => {
      result.current.handleMessage({
        type: 'partial_transcript',
        text: 'Merhaba',
        lang: 'tr',
        speaker_id: 1,
        confidence: 0.85,
      })
    })
    expect(result.current.activeSpeakers.has(0)).toBe(true)
    expect(result.current.activeSpeakers.has(1)).toBe(true)
  })

  it('groups transcripts by speaker_id', () => {
    const { result } = renderHook(() => useTranslation())

    act(() => {
      result.current.handleMessage({
        type: 'final_transcript',
        text: 'Speaker zero first',
        lang: 'en',
        speaker_id: 0,
        confidence: 0.95,
      })
    })
    act(() => {
      result.current.handleMessage({
        type: 'final_transcript',
        text: 'Speaker one speaks',
        lang: 'tr',
        speaker_id: 1,
        confidence: 0.92,
      })
    })
    act(() => {
      result.current.handleMessage({
        type: 'final_transcript',
        text: 'Speaker zero again',
        lang: 'en',
        speaker_id: 0,
        confidence: 0.93,
      })
    })

    const s0 = result.current.speakerTranscripts.get(0)
    const s1 = result.current.speakerTranscripts.get(1)

    expect(s0).toHaveLength(2)
    expect(s0![0].text).toBe('Speaker zero first')
    expect(s0![1].text).toBe('Speaker zero again')
    expect(s1).toHaveLength(1)
    expect(s1![0].text).toBe('Speaker one speaks')
  })

  it('groups translations by speaker_id', () => {
    const { result } = renderHook(() => useTranslation())

    act(() => {
      result.current.handleMessage({
        type: 'translation',
        source_text: 'Hello',
        source_lang: 'en',
        translations: { tr: 'Merhaba' },
        speaker_id: 0,
      })
    })
    act(() => {
      result.current.handleMessage({
        type: 'translation',
        source_text: 'Nasilsin',
        source_lang: 'tr',
        translations: { en: 'How are you' },
        speaker_id: 1,
      })
    })

    expect(result.current.speakerTranslations.get(0)).toHaveLength(1)
    expect(result.current.speakerTranslations.get(1)).toHaveLength(1)
    expect(result.current.speakerTranslations.get(0)![0].translations.tr).toBe('Merhaba')
    expect(result.current.speakerTranslations.get(1)![0].translations.en).toBe('How are you')
  })
})
