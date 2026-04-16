const SPEAKER_COLORS: Record<number, { bg: string; text: string; ring: string }> = {
  0: { bg: 'bg-blue-100', text: 'text-blue-700', ring: 'ring-blue-400' },
  1: { bg: 'bg-green-100', text: 'text-green-700', ring: 'ring-green-400' },
  2: { bg: 'bg-orange-100', text: 'text-orange-700', ring: 'ring-orange-400' },
  3: { bg: 'bg-purple-100', text: 'text-purple-700', ring: 'ring-purple-400' },
}

const DEFAULT_COLOR = { bg: 'bg-gray-100', text: 'text-gray-700', ring: 'ring-gray-400' }

export function getSpeakerColor(speakerId: number) {
  return SPEAKER_COLORS[speakerId] ?? DEFAULT_COLOR
}

interface SpeakerIndicatorProps {
  speakerId: number
  isActive: boolean
}

export function SpeakerIndicator({ speakerId, isActive }: SpeakerIndicatorProps) {
  const color = getSpeakerColor(speakerId)

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${color.bg} ${color.text}`}
      data-testid={`speaker-${speakerId}`}
    >
      <span
        className={`w-2 h-2 rounded-full ${color.ring} ring-1 ${isActive ? 'animate-pulse' : ''}`}
        style={{ backgroundColor: 'currentColor' }}
      />
      Speaker {speakerId}
    </span>
  )
}
