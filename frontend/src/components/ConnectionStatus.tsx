import type { ConnectionStatus as Status } from '../types'

interface ConnectionStatusProps {
  wsStatus: Status
  backendHealthy: boolean
}

export function ConnectionStatus({ wsStatus, backendHealthy }: ConnectionStatusProps) {
  if (!backendHealthy) {
    return (
      <div
        data-testid="connection-banner"
        role="status"
        aria-live="polite"
        className="bg-orange-500 text-white text-center text-sm py-1.5 px-4"
      >
        Backend unavailable
      </div>
    )
  }

  if (wsStatus === 'connected') {
    return (
      <div
        data-testid="connection-banner"
        role="status"
        aria-live="polite"
        className="bg-green-500 text-white text-center text-sm py-1.5 px-4"
      >
        Connected to BabelFlow
      </div>
    )
  }

  return (
    <div
      data-testid="connection-banner"
      role="status"
      aria-live="polite"
      className="bg-red-500 text-white text-center text-sm py-1.5 px-4"
    >
      Connection lost — reconnecting...
    </div>
  )
}
