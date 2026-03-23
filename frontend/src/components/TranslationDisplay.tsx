import type { FinalTranscript, TranslationResult } from '../types'
import { SpeakerIndicator, getSpeakerColor } from './SpeakerIndicator'

interface TranslationDisplayProps {
  partialText: string
  transcripts: FinalTranscript[]
  translations: TranslationResult[]
  activeSpeakers?: Set<number>
}

function LangBadge({ lang }: { lang: string }) {
  return (
    <span className="inline-block px-1.5 py-0.5 text-xs font-medium rounded bg-gray-200 text-gray-700 uppercase">
      {lang}
    </span>
  )
}

/** Group consecutive transcripts by speaker_id */
function groupBySpeaker(transcripts: FinalTranscript[]) {
  const groups: { speakerId: number; items: FinalTranscript[] }[] = []

  for (const t of transcripts) {
    const last = groups[groups.length - 1]
    if (last && last.speakerId === t.speaker_id) {
      last.items.push(t)
    } else {
      groups.push({ speakerId: t.speaker_id, items: [t] })
    }
  }

  return groups
}

export function TranslationDisplay({
  partialText,
  transcripts,
  translations,
  activeSpeakers,
}: TranslationDisplayProps) {
  const hasContent = partialText || transcripts.length > 0 || translations.length > 0

  if (!hasContent) {
    return (
      <div className="text-center text-gray-400 py-8">
        Waiting for speech...
      </div>
    )
  }

  const groups = groupBySpeaker(transcripts)
  const hasSpeakers = transcripts.some((t) => t.speaker_id !== transcripts[0]?.speaker_id)

  return (
    <div className="flex flex-col gap-3 p-4 max-h-96 overflow-y-auto">
      {/* Grouped transcripts by speaker */}
      {groups.map((group, gi) => {
        const color = getSpeakerColor(group.speakerId)
        return (
          <div key={`g-${gi}`} className="flex flex-col gap-1">
            {hasSpeakers && (
              <SpeakerIndicator
                speakerId={group.speakerId}
                isActive={activeSpeakers?.has(group.speakerId) ?? false}
              />
            )}
            {group.items.map((t, ti) => (
              <div
                key={`t-${gi}-${ti}`}
                className={`flex items-start gap-2 ${hasSpeakers ? 'ml-4' : ''}`}
              >
                <LangBadge lang={t.lang} />
                <p className={`text-sm ${hasSpeakers ? color.text : 'text-gray-800'}`}>
                  {t.text}
                </p>
              </div>
            ))}
          </div>
        )
      })}

      {/* Partial transcript */}
      {partialText && (
        <div className="flex items-start gap-2 opacity-60">
          <div className="w-2 h-2 mt-1.5 rounded-full bg-blue-400 animate-pulse" />
          <p className="text-gray-600 text-sm italic">{partialText}</p>
        </div>
      )}

      {/* Translations */}
      {translations.map((tr, i) => (
        <div key={`tr-${i}`} className="border-l-2 border-blue-300 pl-3 ml-2">
          {Object.entries(tr.translations).map(([lang, text]) => (
            <div key={lang} className="flex items-start gap-2 mb-1">
              <LangBadge lang={lang} />
              <p className="text-gray-700 text-sm">{text}</p>
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}
