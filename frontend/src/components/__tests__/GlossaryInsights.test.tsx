import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { GlossaryInsights } from '../GlossaryInsights'

describe('GlossaryInsights', () => {
  it('renders nothing when no terms or notes', () => {
    const { container } = render(<GlossaryInsights />)
    expect(container.innerHTML).toBe('')
  })

  it('renders nothing with empty arrays', () => {
    const { container } = render(<GlossaryInsights detectedTerms={[]} glossaryNotes={[]} />)
    expect(container.innerHTML).toBe('')
  })

  it('renders detected terms as badges', () => {
    render(<GlossaryInsights detectedTerms={['botox', 'rhinoplasty']} />)
    expect(screen.getByTestId('glossary-insights')).toBeDefined()
    const terms = screen.getAllByTestId('detected-term')
    expect(terms).toHaveLength(2)
    expect(terms[0].textContent).toBe('botox')
    expect(terms[1].textContent).toBe('rhinoplasty')
  })

  it('renders glossary notes in italic', () => {
    render(<GlossaryInsights glossaryNotes={["Corrected 'nose job' \u2192 'rhinoplasty'"]} />)
    const notes = screen.getAllByTestId('glossary-note')
    expect(notes).toHaveLength(1)
    expect(notes[0].textContent).toContain('rhinoplasty')
    expect(notes[0].className).toContain('italic')
  })

  it('renders both terms and notes together', () => {
    render(
      <GlossaryInsights
        detectedTerms={['hair transplant']}
        glossaryNotes={['Medical term detected']}
      />,
    )
    expect(screen.getAllByTestId('detected-term')).toHaveLength(1)
    expect(screen.getAllByTestId('glossary-note')).toHaveLength(1)
  })

  it('has blue badge styling on detected terms', () => {
    render(<GlossaryInsights detectedTerms={['botox']} />)
    const term = screen.getByTestId('detected-term')
    expect(term.className).toContain('bg-blue-100')
    expect(term.className).toContain('text-blue-600')
  })
})
