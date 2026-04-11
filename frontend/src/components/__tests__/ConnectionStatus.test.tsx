import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ConnectionStatus } from '../ConnectionStatus'

describe('ConnectionStatus', () => {
  it('shows green banner when connected', () => {
    render(<ConnectionStatus wsStatus="connected" backendHealthy={true} />)
    const banner = screen.getByTestId('connection-banner')
    expect(banner.textContent).toBe('Connected to BabelFlow')
    expect(banner.className).toContain('bg-green-500')
  })

  it('shows red banner when disconnected', () => {
    render(<ConnectionStatus wsStatus="disconnected" backendHealthy={true} />)
    const banner = screen.getByTestId('connection-banner')
    expect(banner.textContent).toContain('Connection lost')
    expect(banner.className).toContain('bg-red-500')
  })

  it('shows red banner when connecting', () => {
    render(<ConnectionStatus wsStatus="connecting" backendHealthy={true} />)
    const banner = screen.getByTestId('connection-banner')
    expect(banner.textContent).toContain('Connection lost')
    expect(banner.className).toContain('bg-red-500')
  })

  it('shows red banner on error status', () => {
    render(<ConnectionStatus wsStatus="error" backendHealthy={true} />)
    const banner = screen.getByTestId('connection-banner')
    expect(banner.className).toContain('bg-red-500')
  })

  it('shows orange banner when backend unhealthy (overrides ws status)', () => {
    render(<ConnectionStatus wsStatus="connected" backendHealthy={false} />)
    const banner = screen.getByTestId('connection-banner')
    expect(banner.textContent).toBe('Backend unavailable')
    expect(banner.className).toContain('bg-orange-500')
  })
})
