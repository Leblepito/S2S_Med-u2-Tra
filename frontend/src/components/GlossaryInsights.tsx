interface GlossaryInsightsProps {
  detectedTerms?: string[]
  glossaryNotes?: string[]
}

export function GlossaryInsights({ detectedTerms, glossaryNotes }: GlossaryInsightsProps) {
  const hasTerms = detectedTerms && detectedTerms.length > 0
  const hasNotes = glossaryNotes && glossaryNotes.length > 0

  if (!hasTerms && !hasNotes) return null

  return (
    <div className="mt-1 ml-2" data-testid="glossary-insights">
      {hasTerms && (
        <div className="flex flex-wrap gap-1 mb-0.5">
          {detectedTerms.map((term, i) => (
            <span
              key={i}
              className="inline-block px-1.5 py-0.5 text-xs font-medium rounded-full bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400"
              data-testid="detected-term"
            >
              {term}
            </span>
          ))}
        </div>
      )}
      {hasNotes && (
        <div>
          {glossaryNotes.map((note, i) => (
            <p
              key={i}
              className="text-xs italic text-gray-400 dark:text-gray-500"
              data-testid="glossary-note"
            >
              {note}
            </p>
          ))}
        </div>
      )}
    </div>
  )
}
