import { useCallback, useEffect, useState } from 'react'
import { AudioCapture } from './components/AudioCapture'
import { ConnectionStatus } from './components/ConnectionStatus'
import { ConversationHistory } from './components/ConversationHistory'
import { ErrorBoundary } from './components/ErrorBoundary'
import { Header } from './components/Header'
import { LanguageSelector } from './components/LanguageSelector'
import { LoadingSkeleton } from './components/LoadingSkeleton'
import { SessionControls } from './components/SessionControls'
import { TranslationDisplay } from './components/TranslationDisplay'
import { WS_URL, API_URL, LATENCY_URL } from './config'
import { useBackendHealth } from './hooks/useBackendHealth'
import { useConversationHistory } from './hooks/useConversationHistory'
import { useDarkMode } from './hooks/useDarkMode'
import { useWebSocket } from './hooks/useWebSocket'
import { useTranslation } from './hooks/useTranslation'
import { useTtsPlayback } from './hooks/useTtsPlayback'
import { useLatency } from './hooks/useLatency'
import type { ConfigMessage, SupportedLang } from './types'
import { isFinalTranscript, isTranslationResult } from './types'
import './index.css'

function App() {
  const [sourceLang, setSourceLang] = useState<SupportedLang | 'auto'>('auto')
  const [targetLangs, setTargetLangs] = useState<SupportedLang[]>(['en', 'th'])
  const [darkMode, toggleDark] = useDarkMode()
  const [showHistory, setShowHistory] = useState(false)
  const { status: wsStatus, lastMessage, lastTtsAudio } = useWebSocket(WS_URL)
  const { partialText, transcripts, translations, activeSpeakers, handleMessage, reset } = useTranslation()
  const { isMuted, enqueue, toggleMute } = useTtsPlayback()
  const latencyMs = useLatency(LATENCY_URL)
  const { isHealthy: backendHealthy, lastChecked } = useBackendHealth(API_URL)
  const {
    sessions,
    addEntry,
    clearSession,
    deleteSession,
    clearAll,
    exportAsText,
    exportAsJSON,
  } = useConversationHistory()

  // Route messages to both translation state and conversation history
  useEffect(() => {
    if (!lastMessage) return
    handleMessage(lastMessage)

    if (isFinalTranscript(lastMessage)) {
      addEntry({
        timestamp: Date.now(),
        type: 'transcript',
        speaker_id: lastMessage.speaker_id,
        text: lastMessage.text,
        lang: lastMessage.lang,
      })
    } else if (isTranslationResult(lastMessage)) {
      addEntry({
        timestamp: Date.now(),
        type: 'translation',
        speaker_id: lastMessage.speaker_id,
        text: lastMessage.source_text,
        translations: lastMessage.translations as Record<string, string>,
      })
    }
  }, [lastMessage, handleMessage, addEntry])

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

  const handleNewSession = useCallback(() => {
    clearSession()
    reset()
  }, [clearSession, reset])

  const config: ConfigMessage = {
    type: 'config',
    source_lang: sourceLang,
    target_langs: targetLangs,
    enable_diarization: false,
  }

  const isLoading = lastChecked === null
  const speakerCount = new Set(transcripts.map((t) => t.speaker_id)).size

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <Header
        latencyMs={latencyMs}
        isMuted={isMuted}
        onToggleMute={toggleMute}
        darkMode={darkMode}
        onToggleDark={toggleDark}
      />

      <ConnectionStatus wsStatus={wsStatus} backendHealthy={backendHealthy} />

      <ErrorBoundary>
        {isLoading ? (
          <LoadingSkeleton />
        ) : (
          <main className="max-w-2xl lg:max-w-2xl md:max-w-lg mx-auto py-4 sm:py-6 px-2 sm:px-4 flex flex-col gap-3 sm:gap-4">
            {/* Session Controls */}
            <div className="flex justify-end">
              <SessionControls
                isCapturing={wsStatus === 'connected'}
                transcriptCount={transcripts.length}
                speakerCount={speakerCount}
                onNewSession={handleNewSession}
                onToggleHistory={() => setShowHistory((p) => !p)}
              />
            </div>

            {/* Language Selection */}
            <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <LanguageSelector
                sourceLang={sourceLang}
                targetLangs={targetLangs}
                onSourceChange={setSourceLang}
                onTargetToggle={handleTargetToggle}
              />
            </section>

            {/* Audio Capture */}
            <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <AudioCapture config={config} />
            </section>

            {/* Translation Output */}
            <section className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 min-h-48">
              <div className="flex items-center justify-between px-4 pt-3">
                <h2 className="text-sm font-medium text-gray-500 dark:text-gray-400">Output</h2>
                {transcripts.length > 0 && (
                  <button
                    onClick={reset}
                    className="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
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
        )}
      </ErrorBoundary>

      {/* History Sidebar */}
      {showHistory && (
        <ConversationHistory
          sessions={sessions}
          currentExportText={exportAsText}
          currentExportJSON={exportAsJSON}
          onDeleteSession={deleteSession}
          onClearAll={clearAll}
          onClose={() => setShowHistory(false)}
        />
      )}
    </div>
  )
}

export default App
