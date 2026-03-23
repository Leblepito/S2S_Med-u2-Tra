import { describe, it, expect, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useConversationHistory, type HistoryEntry } from '../useConversationHistory'

const mockEntry = (overrides: Partial<HistoryEntry> = {}): HistoryEntry => ({
  timestamp: Date.now(),
  type: 'transcript',
  speaker_id: 0,
  text: 'Hello',
  ...overrides,
})

describe('useConversationHistory', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('initializes with empty entries and a sessionId', () => {
    const { result } = renderHook(() => useConversationHistory())
    expect(result.current.entries).toEqual([])
    expect(result.current.sessionId).toBeTruthy()
  })

  it('adds entries', () => {
    const { result } = renderHook(() => useConversationHistory())
    act(() => {
      result.current.addEntry(mockEntry({ text: 'First' }))
    })
    act(() => {
      result.current.addEntry(mockEntry({ text: 'Second' }))
    })
    expect(result.current.entries).toHaveLength(2)
    expect(result.current.entries[0].text).toBe('First')
    expect(result.current.entries[1].text).toBe('Second')
  })

  it('clears session and generates new sessionId', () => {
    const { result } = renderHook(() => useConversationHistory())
    const oldId = result.current.sessionId

    act(() => {
      result.current.addEntry(mockEntry())
    })
    act(() => {
      result.current.clearSession()
    })

    expect(result.current.entries).toEqual([])
    expect(result.current.sessionId).not.toBe(oldId)
  })

  it('saves to localStorage', () => {
    const { result } = renderHook(() => useConversationHistory())
    act(() => {
      result.current.addEntry(mockEntry({ text: 'Saved' }))
    })
    const stored = localStorage.getItem('babelflow_sessions')
    expect(stored).toBeTruthy()
    const parsed = JSON.parse(stored!)
    expect(parsed.length).toBeGreaterThanOrEqual(1)
  })

  it('loads sessions from localStorage', () => {
    const session = { id: 'test-id', startedAt: Date.now(), entries: [mockEntry()] }
    localStorage.setItem('babelflow_sessions', JSON.stringify([session]))

    const { result } = renderHook(() => useConversationHistory())
    expect(result.current.sessions).toHaveLength(1)
    expect(result.current.sessions[0].id).toBe('test-id')
  })

  it('deletes a session', () => {
    const session = { id: 'del-me', startedAt: Date.now(), entries: [mockEntry()] }
    localStorage.setItem('babelflow_sessions', JSON.stringify([session]))

    const { result } = renderHook(() => useConversationHistory())
    expect(result.current.sessions).toHaveLength(1)

    act(() => {
      result.current.deleteSession('del-me')
    })
    expect(result.current.sessions).toHaveLength(0)
  })

  it('clears all sessions', () => {
    const sessions = [
      { id: 'a', startedAt: Date.now(), entries: [mockEntry()] },
      { id: 'b', startedAt: Date.now(), entries: [mockEntry()] },
    ]
    localStorage.setItem('babelflow_sessions', JSON.stringify(sessions))

    const { result } = renderHook(() => useConversationHistory())
    act(() => {
      result.current.clearAll()
    })
    expect(result.current.sessions).toEqual([])
    expect(localStorage.getItem('babelflow_sessions')).toBeNull()
  })

  it('enforces max 50 sessions', () => {
    const old = Array.from({ length: 55 }, (_, i) => ({
      id: `s-${i}`,
      startedAt: Date.now(),
      entries: [mockEntry()],
    }))
    localStorage.setItem('babelflow_sessions', JSON.stringify(old))

    const { result } = renderHook(() => useConversationHistory())
    act(() => {
      result.current.addEntry(mockEntry())
    })

    const stored = JSON.parse(localStorage.getItem('babelflow_sessions')!)
    expect(stored.length).toBeLessThanOrEqual(50)
  })

  it('exportAsText formats transcript entries', () => {
    const { result } = renderHook(() => useConversationHistory())
    act(() => {
      result.current.addEntry(mockEntry({ speaker_id: 0, text: 'Hello' }))
    })
    const text = result.current.exportAsText()
    expect(text).toContain('Speaker 0: Hello')
  })

  it('exportAsText formats translation entries with arrows', () => {
    const { result } = renderHook(() => useConversationHistory())
    act(() => {
      result.current.addEntry(mockEntry({
        type: 'translation',
        speaker_id: 1,
        text: 'Merhaba',
        translations: { en: 'Hello', th: 'สวัสดี' },
      }))
    })
    const text = result.current.exportAsText()
    expect(text).toContain('Speaker 1: Merhaba')
    expect(text).toContain('\u2192 EN: Hello')
    expect(text).toContain('\u2192 TH: สวัสดี')
  })

  it('exportAsJSON returns valid JSON', () => {
    const { result } = renderHook(() => useConversationHistory())
    act(() => {
      result.current.addEntry(mockEntry({ text: 'Test' }))
    })
    const json = result.current.exportAsJSON()
    const parsed = JSON.parse(json)
    expect(parsed).toHaveLength(1)
    expect(parsed[0].text).toBe('Test')
  })
})
