import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ErrorBoundary } from '../ErrorBoundary'

function GoodChild() {
  return <div>All good</div>
}

function BadChild(): never {
  throw new Error('Test crash')
}

describe('ErrorBoundary', () => {
  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <GoodChild />
      </ErrorBoundary>,
    )
    expect(screen.getByText('All good')).toBeDefined()
  })

  it('renders fallback UI when child crashes', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})

    render(
      <ErrorBoundary>
        <BadChild />
      </ErrorBoundary>,
    )
    expect(screen.getByTestId('error-fallback')).toBeDefined()
    expect(screen.getByText('Something went wrong')).toBeDefined()
    expect(screen.getByText('Retry')).toBeDefined()

    vi.restoreAllMocks()
  })

  it('recovers when Retry is clicked and child no longer crashes', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})

    let shouldCrash = true
    function MaybeChild() {
      if (shouldCrash) throw new Error('crash')
      return <div>Recovered</div>
    }

    const { rerender } = render(
      <ErrorBoundary>
        <MaybeChild />
      </ErrorBoundary>,
    )
    expect(screen.getByText('Something went wrong')).toBeDefined()

    shouldCrash = false
    fireEvent.click(screen.getByText('Retry'))

    rerender(
      <ErrorBoundary>
        <MaybeChild />
      </ErrorBoundary>,
    )
    expect(screen.getByText('Recovered')).toBeDefined()

    vi.restoreAllMocks()
  })

  it('logs error to console', () => {
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    render(
      <ErrorBoundary>
        <BadChild />
      </ErrorBoundary>,
    )

    const calls = errorSpy.mock.calls.flat().map(String)
    const found = calls.some((c) => c.includes('ErrorBoundary caught'))
    expect(found).toBe(true)

    vi.restoreAllMocks()
  })
})
