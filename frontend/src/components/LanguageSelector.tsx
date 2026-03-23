import { SUPPORTED_LANGS, type SupportedLang } from '../types'

const LANG_LABELS: Record<string, string> = {
  auto: 'Auto Detect',
  tr: 'TR',
  ru: 'RU',
  en: 'EN',
  th: 'TH',
  vi: 'VI',
  zh: 'ZH',
  id: 'ID',
}

export const LANG_FULL_NAMES: Record<string, string> = {
  tr: 'Turkish (T\u00FCrk\u00E7e)',
  ru: 'Russian (\u0420\u0443\u0441\u0441\u043A\u0438\u0439)',
  en: 'English',
  th: 'Thai (\u0E44\u0E17\u0E22)',
  vi: 'Vietnamese (Ti\u1EBFng Vi\u1EC7t)',
  zh: 'Chinese (\u4E2D\u6587)',
  id: 'Indonesian (Bahasa)',
}

interface LanguageSelectorProps {
  sourceLang: SupportedLang | 'auto'
  targetLangs: SupportedLang[]
  onSourceChange: (lang: SupportedLang | 'auto') => void
  onTargetToggle: (lang: SupportedLang) => void
}

export function LanguageSelector({
  sourceLang,
  targetLangs,
  onSourceChange,
  onTargetToggle,
}: LanguageSelectorProps) {
  return (
    <div className="flex flex-col gap-3 p-4" role="group" aria-label="Language selection">
      {/* Source Language */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-gray-500 dark:text-gray-400 w-14" id="source-label">Source</span>
        <select
          value={sourceLang}
          onChange={(e) => onSourceChange(e.target.value as SupportedLang | 'auto')}
          className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-sm bg-white dark:bg-gray-800 dark:text-gray-200 min-h-[44px]"
          aria-labelledby="source-label"
        >
          <option value="auto">Auto Detect</option>
          {SUPPORTED_LANGS.map((lang) => (
            <option key={lang} value={lang}>
              {LANG_FULL_NAMES[lang] ?? LANG_LABELS[lang]}
            </option>
          ))}
        </select>
      </div>

      {/* Target Languages */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-gray-500 dark:text-gray-400 w-14" id="target-label">Target</span>
        <div className="flex flex-wrap gap-2" role="group" aria-labelledby="target-label">
          {SUPPORTED_LANGS.map((lang) => {
            const isSelected = targetLangs.includes(lang)
            return (
              <button
                key={lang}
                onClick={() => onTargetToggle(lang)}
                title={LANG_FULL_NAMES[lang]}
                aria-pressed={isSelected}
                aria-label={`${LANG_FULL_NAMES[lang]} ${isSelected ? '(selected)' : ''}`}
                className={`min-w-[44px] min-h-[44px] px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  isSelected
                    ? 'bg-blue-500 text-white ring-2 ring-blue-400 dark:ring-blue-600 shadow-sm'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {LANG_LABELS[lang]}
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
