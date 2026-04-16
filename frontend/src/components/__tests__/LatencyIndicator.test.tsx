import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LatencyIndicator } from '../LatencyIndicator'

describe('LatencyIndicator', () => {
  it('shows green for low latency (<1000ms)', () => {
    render(<LatencyIndicator latencyMs={500} />)
    expect(screen.getByText('500ms')).toBeDefined()
    const dot = screen.getByTestId('latency-dot')
    expect(dot.className).toContain('bg-green')
  })

  it('shows yellow for medium latency (1000-2000ms)', () => {
    render(<LatencyIndicator latencyMs={1500} />)
    expect(screen.getByText('1500ms')).toBeDefined()
    const dot = screen.getByTestId('latency-dot')
    expect(dot.className).toContain('bg-yellow')
  })

  it('shows red for high latency (>2000ms)', () => {
    render(<LatencyIndicator latencyMs={2500} />)
    expect(screen.getByText('2500ms')).toBeDefined()
    const dot = screen.getByTestId('latency-dot')
    expect(dot.className).toContain('bg-red')
  })

  it('shows dash when no latency data', () => {
    render(<LatencyIndicator latencyMs={null} />)
    expect(screen.getByText('—')).toBeDefined()
  })

  it('shows label text', () => {
    render(<LatencyIndicator latencyMs={800} />)
    expect(screen.getByText('Latency')).toBeDefined()
  })
})
