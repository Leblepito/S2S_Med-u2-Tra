import { describe, it, expect } from 'vitest'
import {
  SUPPORTED_LANGS,
  SAMPLE_RATE,
  CHANNELS,
  CHUNK_SAMPLES,
  TTS_SAMPLE_RATE,
  isPartialTranscript,
  isFinalTranscript,
  isTranslationResult,
  isTTSHeader,
  isErrorMessage,
  isSupportedLang,
  type ConfigMessage,
  type PartialTranscript,
  type FinalTranscript,
  type TranslationResult,
  type TTSHeader,
  type ErrorMessage,
  type ServerJsonMessage,
} from '../types'

describe('Audio Constants', () => {
  it('should have correct sample rate', () => {
    expect(SAMPLE_RATE).toBe(16_000)
  })

  it('should be mono channel', () => {
    expect(CHANNELS).toBe(1)
  })

  it('should have 480 samples per chunk (30ms @ 16kHz)', () => {
    expect(CHUNK_SAMPLES).toBe(480)
  })

  it('should have 24kHz TTS sample rate', () => {
    expect(TTS_SAMPLE_RATE).toBe(24_000)
  })
})

describe('Supported Languages', () => {
  it('should support exactly 7 languages', () => {
    expect(SUPPORTED_LANGS).toHaveLength(7)
  })

  it('should include all required languages', () => {
    const required = ['tr', 'ru', 'en', 'th', 'vi', 'zh', 'id']
    for (const lang of required) {
      expect(SUPPORTED_LANGS).toContain(lang)
    }
  })

  it('isSupportedLang returns true for valid languages', () => {
    expect(isSupportedLang('tr')).toBe(true)
    expect(isSupportedLang('en')).toBe(true)
    expect(isSupportedLang('zh')).toBe(true)
  })

  it('isSupportedLang returns false for invalid languages', () => {
    expect(isSupportedLang('xx')).toBe(false)
    expect(isSupportedLang('fr')).toBe(false)
    expect(isSupportedLang('')).toBe(false)
  })
})

describe('ConfigMessage type', () => {
  it('should accept valid config with auto source', () => {
    const msg: ConfigMessage = {
      type: 'config',
      source_lang: 'auto',
      target_langs: ['en', 'th'],
      enable_diarization: true,
    }
    expect(msg.type).toBe('config')
    expect(msg.source_lang).toBe('auto')
    expect(msg.target_langs).toEqual(['en', 'th'])
    expect(msg.enable_diarization).toBe(true)
  })

  it('should accept valid config with specific source', () => {
    const msg: ConfigMessage = {
      type: 'config',
      source_lang: 'tr',
      target_langs: ['en', 'ru', 'th'],
      enable_diarization: false,
    }
    expect(msg.source_lang).toBe('tr')
    expect(msg.target_langs).toHaveLength(3)
  })
})

describe('Type Guards', () => {
  const partialTranscript: PartialTranscript = {
    type: 'partial_transcript',
    text: 'Merhaba nasil...',
    lang: 'tr',
    speaker_id: 0,
    confidence: 0.92,
  }

  const finalTranscript: FinalTranscript = {
    type: 'final_transcript',
    text: 'Merhaba nasilsiniz',
    lang: 'tr',
    speaker_id: 0,
    confidence: 0.98,
  }

  const translation: TranslationResult = {
    type: 'translation',
    source_text: 'Merhaba nasilsiniz',
    source_lang: 'tr',
    translations: {
      en: 'Hello how are you',
      th: 'สวัสดีครับ สบายดีไหม',
    },
    speaker_id: 0,
  }

  const ttsHeader: TTSHeader = {
    type: 'tts_audio',
    lang: 'en',
    chunk_index: 0,
  }

  const errorMsg: ErrorMessage = {
    type: 'error',
    message: 'Connection timeout',
    code: 'TIMEOUT',
  }

  const allMessages: ServerJsonMessage[] = [
    partialTranscript,
    finalTranscript,
    translation,
    ttsHeader,
    errorMsg,
  ]

  describe('isPartialTranscript', () => {
    it('returns true for partial transcript', () => {
      expect(isPartialTranscript(partialTranscript)).toBe(true)
    })
    it('returns false for other types', () => {
      for (const msg of allMessages.filter((m) => m !== partialTranscript)) {
        expect(isPartialTranscript(msg)).toBe(false)
      }
    })
  })

  describe('isFinalTranscript', () => {
    it('returns true for final transcript', () => {
      expect(isFinalTranscript(finalTranscript)).toBe(true)
    })
    it('returns false for other types', () => {
      for (const msg of allMessages.filter((m) => m !== finalTranscript)) {
        expect(isFinalTranscript(msg)).toBe(false)
      }
    })
  })

  describe('isTranslationResult', () => {
    it('returns true for translation', () => {
      expect(isTranslationResult(translation)).toBe(true)
    })
    it('returns false for other types', () => {
      for (const msg of allMessages.filter((m) => m !== translation)) {
        expect(isTranslationResult(msg)).toBe(false)
      }
    })
  })

  describe('isTTSHeader', () => {
    it('returns true for TTS header', () => {
      expect(isTTSHeader(ttsHeader)).toBe(true)
    })
    it('returns false for other types', () => {
      for (const msg of allMessages.filter((m) => m !== ttsHeader)) {
        expect(isTTSHeader(msg)).toBe(false)
      }
    })
  })

  describe('isErrorMessage', () => {
    it('returns true for error message', () => {
      expect(isErrorMessage(errorMsg)).toBe(true)
    })
    it('returns false for other types', () => {
      for (const msg of allMessages.filter((m) => m !== errorMsg)) {
        expect(isErrorMessage(msg)).toBe(false)
      }
    })
  })

  describe('ErrorMessage optional code', () => {
    it('accepts error without code', () => {
      const err: ErrorMessage = { type: 'error', message: 'Unknown error' }
      expect(isErrorMessage(err)).toBe(true)
      expect(err.code).toBeUndefined()
    })
  })
})
