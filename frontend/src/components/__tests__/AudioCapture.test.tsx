import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AudioCapture } from '../AudioCapture'
import type { ConfigMessage } from '../../types'

// Mock hooks with vi.hoisted to avoid hoisting issues
const mockConnect = vi.fn()
const mockDisconnect = vi.fn()
const mockSendAudio = vi.fn()
const mockStartCapture = vi.fn()
const mockStopCapture = vi.fn()

let mockStatus = 'disconnected'
let mockIsCapturing = false
let mockError: string | null = null

vi.mock('../../hooks/useWebSocket', () => ({
  useWebSocket: () => ({
    status: mockStatus,
    connect: mockConnect,
    disconnect: mockDisconnect,
    sendAudio: mockSendAudio,
    lastMessage: null,
    lastTtsAudio: null,
  }),
}))

vi.mock('../../hooks/useAudioStream', () => ({
  useAudioStream: () => ({
    isCapturing: mockIsCapturing,
    error: mockError,
    startCapture: mockStartCapture,
    stopCapture: mockStopCapture,
  }),
}))

const defaultConfig: ConfigMessage = {
  type: 'config',
  source_lang: 'auto',
  target_langs: ['en', 'th'],
  enable_diarization: false,
}

describe('AudioCapture', () => {
  beforeEach(() => {
    mockStatus = 'disconnected'
    mockIsCapturing = false
    mockError = null
    vi.clearAllMocks()
  })

  it('renders start button when not capturing', () => {
    render(<AudioCapture config={defaultConfig} />)
    expect(screen.getByText('Start')).toBeDefined()
  })

  it('shows disconnected status by default', () => {
    render(<AudioCapture config={defaultConfig} />)
    expect(screen.getByText('Disconnected')).toBeDefined()
  })

  it('shows stop button when capturing', () => {
    mockIsCapturing = true
    render(<AudioCapture config={defaultConfig} />)
    expect(screen.getByText('Stop')).toBeDefined()
    expect(screen.getByText('Listening...')).toBeDefined()
  })

  it('shows error message', () => {
    mockError = 'Microphone access denied'
    render(<AudioCapture config={defaultConfig} />)
    expect(screen.getByText('Microphone access denied')).toBeDefined()
  })

  it('shows connected status', () => {
    mockStatus = 'connected'
    render(<AudioCapture config={defaultConfig} />)
    expect(screen.getByText('Connected')).toBeDefined()
  })
})
