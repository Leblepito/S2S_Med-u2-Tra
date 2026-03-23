// BabelFlow WebSocket Protocol Types
// Mirrors backend schemas.py — keep in sync with docs/websocket-protocol.md

// ── Supported Languages ──

export const SUPPORTED_LANGS = ['tr', 'ru', 'en', 'th', 'vi', 'zh', 'id'] as const
export type SupportedLang = (typeof SUPPORTED_LANGS)[number]

// ── Audio Constants ──

export const SAMPLE_RATE = 16_000
export const CHANNELS = 1
export const CHUNK_SAMPLES = 480 // 30ms @ 16kHz
export const TTS_SAMPLE_RATE = 24_000

// ── Client → Server Messages ──

export interface ConfigMessage {
  type: 'config'
  source_lang: SupportedLang | 'auto'
  target_langs: SupportedLang[]
  enable_diarization: boolean
}

// Binary audio: PCM16 Little-Endian, 16kHz, Mono (sent as ArrayBuffer)

// ── Server → Client Messages ──

export interface PartialTranscript {
  type: 'partial_transcript'
  text: string
  lang: SupportedLang
  speaker_id: number
  confidence: number
  detected_terms?: string[]
}

export interface FinalTranscript {
  type: 'final_transcript'
  text: string
  lang: SupportedLang
  speaker_id: number
  confidence: number
  detected_terms?: string[]
}

export interface TranslationResult {
  type: 'translation'
  source_text: string
  source_lang: SupportedLang
  translations: Partial<Record<SupportedLang, string>>
  speaker_id: number
  glossary_notes?: string[]
}

export interface TTSHeader {
  type: 'tts_audio'
  lang: SupportedLang
  chunk_index: number
}

export interface ErrorMessage {
  type: 'error'
  message: string
  code?: string
}

// ── Union Types ──

export type ClientMessage = ConfigMessage

export type ServerJsonMessage =
  | PartialTranscript
  | FinalTranscript
  | TranslationResult
  | TTSHeader
  | ErrorMessage

export type ServerMessageType = ServerJsonMessage['type']

// ── Type Guards ──

export function isPartialTranscript(msg: ServerJsonMessage): msg is PartialTranscript {
  return msg.type === 'partial_transcript'
}

export function isFinalTranscript(msg: ServerJsonMessage): msg is FinalTranscript {
  return msg.type === 'final_transcript'
}

export function isTranslationResult(msg: ServerJsonMessage): msg is TranslationResult {
  return msg.type === 'translation'
}

export function isTTSHeader(msg: ServerJsonMessage): msg is TTSHeader {
  return msg.type === 'tts_audio'
}

export function isErrorMessage(msg: ServerJsonMessage): msg is ErrorMessage {
  return msg.type === 'error'
}

export function isSupportedLang(lang: string): lang is SupportedLang {
  return (SUPPORTED_LANGS as readonly string[]).includes(lang)
}

// ── WebSocket Connection State ──

export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error'
