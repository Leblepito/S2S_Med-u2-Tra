import { useCallback, useState } from 'react'
import type {
  FinalTranscript,
  ServerJsonMessage,
  TranslationResult,
} from '../types'
import {
  isPartialTranscript,
  isFinalTranscript,
  isTranslationResult,
} from '../types'

interface UseTranslationReturn {
  partialText: string
  transcripts: FinalTranscript[]
  translations: TranslationResult[]
  activeSpeakers: Set<number>
  speakerTranscripts: Map<number, FinalTranscript[]>
  speakerTranslations: Map<number, TranslationResult[]>
  handleMessage: (msg: ServerJsonMessage) => void
  reset: () => void
}

export function useTranslation(): UseTranslationReturn {
  const [partialText, setPartialText] = useState('')
  const [transcripts, setTranscripts] = useState<FinalTranscript[]>([])
  const [translations, setTranslations] = useState<TranslationResult[]>([])
  const [activeSpeakers, setActiveSpeakers] = useState<Set<number>>(new Set())
  const [speakerTranscripts, setSpeakerTranscripts] = useState<Map<number, FinalTranscript[]>>(new Map())
  const [speakerTranslations, setSpeakerTranslations] = useState<Map<number, TranslationResult[]>>(new Map())

  const handleMessage = useCallback((msg: ServerJsonMessage) => {
    if (isPartialTranscript(msg)) {
      setPartialText(msg.text)
      setActiveSpeakers((prev) => {
        const next = new Set(prev)
        next.add(msg.speaker_id)
        return next
      })
    } else if (isFinalTranscript(msg)) {
      setPartialText('')
      setTranscripts((prev) => [...prev, msg])
      setSpeakerTranscripts((prev) => {
        const next = new Map(prev)
        const existing = next.get(msg.speaker_id) ?? []
        next.set(msg.speaker_id, [...existing, msg])
        return next
      })
      setActiveSpeakers((prev) => {
        const next = new Set(prev)
        next.add(msg.speaker_id)
        return next
      })
    } else if (isTranslationResult(msg)) {
      setTranslations((prev) => [...prev, msg])
      setSpeakerTranslations((prev) => {
        const next = new Map(prev)
        const existing = next.get(msg.speaker_id) ?? []
        next.set(msg.speaker_id, [...existing, msg])
        return next
      })
    }
  }, [])

  const reset = useCallback(() => {
    setPartialText('')
    setTranscripts([])
    setTranslations([])
    setActiveSpeakers(new Set())
    setSpeakerTranscripts(new Map())
    setSpeakerTranslations(new Map())
  }, [])

  return {
    partialText,
    transcripts,
    translations,
    activeSpeakers,
    speakerTranscripts,
    speakerTranslations,
    handleMessage,
    reset,
  }
}
