import { describe, it, expect } from 'vitest'
import { float32ToPcm16, pcm16ToArrayBuffer } from '../audio'

describe('Audio Conversion', () => {
  describe('float32ToPcm16', () => {
    it('converts silence (zeros) correctly', () => {
      const float32 = new Float32Array(480) // 30ms of silence
      const pcm16 = float32ToPcm16(float32)

      expect(pcm16).toBeInstanceOf(Int16Array)
      expect(pcm16.length).toBe(480)
      for (let i = 0; i < pcm16.length; i++) {
        expect(pcm16[i]).toBe(0)
      }
    })

    it('converts full-scale positive correctly', () => {
      const float32 = new Float32Array([1.0])
      const pcm16 = float32ToPcm16(float32)
      expect(pcm16[0]).toBe(32767)
    })

    it('converts full-scale negative correctly', () => {
      const float32 = new Float32Array([-1.0])
      const pcm16 = float32ToPcm16(float32)
      expect(pcm16[0]).toBe(-32768)
    })

    it('clips values beyond ±1.0', () => {
      const float32 = new Float32Array([1.5, -1.5])
      const pcm16 = float32ToPcm16(float32)
      expect(pcm16[0]).toBe(32767) // clamped
      expect(pcm16[1]).toBe(-32768) // clamped
    })

    it('converts 0.5 to approximately half scale', () => {
      const float32 = new Float32Array([0.5])
      const pcm16 = float32ToPcm16(float32)
      expect(pcm16[0]).toBeGreaterThan(16000)
      expect(pcm16[0]).toBeLessThan(17000)
    })

    it('preserves 30ms chunk size (480 samples @ 16kHz)', () => {
      const float32 = new Float32Array(480)
      const pcm16 = float32ToPcm16(float32)
      expect(pcm16.length).toBe(480)
    })
  })

  describe('pcm16ToArrayBuffer', () => {
    it('creates ArrayBuffer of correct size (samples * 2 bytes)', () => {
      const pcm16 = new Int16Array(480)
      const buffer = pcm16ToArrayBuffer(pcm16)
      expect(buffer).toBeInstanceOf(ArrayBuffer)
      expect(buffer.byteLength).toBe(960) // 480 * 2
    })

    it('round-trips through float32 conversion', () => {
      const original = new Float32Array([0.0, 0.5, -0.5, 1.0, -1.0])
      const pcm16 = float32ToPcm16(original)
      const buffer = pcm16ToArrayBuffer(pcm16)

      // Verify buffer contains the PCM16 data
      const view = new DataView(buffer)
      expect(view.getInt16(0, true)).toBe(pcm16[0]) // Little-endian
      expect(view.getInt16(2, true)).toBe(pcm16[1])
    })

    it('produces little-endian PCM16 data', () => {
      const pcm16 = new Int16Array([256]) // 0x0100
      const buffer = pcm16ToArrayBuffer(pcm16)
      const bytes = new Uint8Array(buffer)
      expect(bytes[0]).toBe(0) // LSB first (little-endian)
      expect(bytes[1]).toBe(1) // MSB second
    })
  })
})
