import { useCallback, useEffect, useState } from 'react'
import { AudioCapture } from './components/AudioCapture'
import { LanguageSelector } from './components/LanguageSelector'
import { LatencyIndicator } from './components/LatencyIndicator'
import { TranslationDisplay } from './components/TranslationDisplay'
import { useWebSocket } from './hooks/useWebSocket'
import { useTranslation } from './hooks/useTranslation'
import { useTtsPlayback } from './hooks/useTtsPlayback'
import { useLatency } from './hooks/useLatency'
import type { ConfigMessage, SupportedLang } from './types'
import './index.css'

const WS_URL = 'ws://localhost:8000/ws/translate'
const LATENCY_URL = 'http://localhost:8000/api/latency'

function App() {
  const [sourceLang, setSourceLang] = useState<SupportedLang | 'auto'>('auto')
  const [targetLangs, setTargetLangs] = useState<SupportedLang[]>(['en', 'th'])
  const { lastMessage, lastTtsAudio } = useWebSocket(WS_URL)
  const { partialText, transcripts, translations, activeSpeakers, handleMessage, reset } = useTranslation()
  const { isMuted, enqueue, toggleMute } = useTtsPlayback()
  const latencyMs = useLatency(LATENCY_URL)

  useEffect(() => {
    if (lastMessage) handleMessage(lastMessage)
  }, [lastMessage, handleMessage])

  useEffect(() => {
    if (lastTtsAudio) enqueue(lastTtsAudio)
  }, [lastTtsAudio, enqueue])

  const handleTargetToggle = useCallback((lang: SupportedLang) => {
    setTargetLangs((prev) =>
      prev.includes(lang)
        ? prev.filter((l) => l !== lang)
        : [...prev, lang],
    )
  }, [])

  const config: ConfigMessage = {
    type: 'config',
    source_lang: sourceLang,
    target_langs: targetLangs,
    enable_diarization: false,
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-800">
          BabelFlow
          <span className="text-sm font-normal text-gray-400 ml-2">
            Real-Time Translation
          </span>
        </h1>
        <div className="flex items-center gap-4">
          <LatencyIndicator latencyMs={latencyMs} />
          <button
            onClick={toggleMute}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              isMuted
                ? 'bg-gray-200 text-gray-500'
                : 'bg-blue-100 text-blue-700'
            }`}
          >
            {isMuted ? 'Unmute TTS' : 'Mute TTS'}
          </button>
        </div>
      </header>

      <main className="max-w-2xl mx-auto py-6 px-4 flex flex-col gap-4">
        {/* Language Selection */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200">
          <LanguageSelector
            sourceLang={sourceLang}
            targetLangs={targetLangs}
            onSourceChange={setSourceLang}
            onTargetToggle={handleTargetToggle}
          />
        </section>

        {/* Audio Capture */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200">
          <AudioCapture config={config} />
        </section>

        {/* Translation Output */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 min-h-48">
          <div className="flex items-center justify-between px-4 pt-3">
            <h2 className="text-sm font-medium text-gray-500">Output</h2>
            {transcripts.length > 0 && (
              <button
                onClick={reset}
                className="text-xs text-gray-400 hover:text-gray-600"
              >
                Clear
              </button>
            )}
          </div>
          <TranslationDisplay
            partialText={partialText}
            transcripts={transcripts}
            translations={translations}
            activeSpeakers={activeSpeakers}
          />
        </section>
      </main>
    </div>
  )
}

export default App
