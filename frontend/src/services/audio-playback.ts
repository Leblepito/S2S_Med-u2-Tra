import { TTS_SAMPLE_RATE } from '../types'

/**
 * Queued audio playback for TTS output.
 * Receives PCM16 ArrayBuffers, queues them, plays sequentially.
 */
export class AudioPlaybackQueue {
  private queue: ArrayBuffer[] = []
  private playing = false
  private audioContext: AudioContext | null = null

  get queueLength(): number {
    return this.queue.length
  }

  get isPlaying(): boolean {
    return this.playing
  }

  enqueue(pcm16Data: ArrayBuffer): void {
    this.queue.push(pcm16Data)
    if (!this.playing) {
      this.playNext()
    }
  }

  clear(): void {
    this.queue = []
    this.playing = false
  }

  dispose(): void {
    this.clear()
    this.audioContext?.close().catch(() => {})
    this.audioContext = null
  }

  private getContext(): AudioContext {
    if (!this.audioContext) {
      this.audioContext = new AudioContext({ sampleRate: TTS_SAMPLE_RATE })
    }
    return this.audioContext
  }

  private playNext(): void {
    if (this.queue.length === 0) {
      this.playing = false
      return
    }

    this.playing = true
    const data = this.queue.shift()!
    const ctx = this.getContext()

    // Convert PCM16 to Float32 for Web Audio API
    const pcm16 = new Int16Array(data)
    const float32 = new Float32Array(pcm16.length)
    for (let i = 0; i < pcm16.length; i++) {
      float32[i] = pcm16[i] / 32768
    }

    const buffer = ctx.createBuffer(1, float32.length, TTS_SAMPLE_RATE)
    buffer.getChannelData(0).set(float32)

    const source = ctx.createBufferSource()
    source.buffer = buffer
    source.connect(ctx.destination)
    source.onended = () => this.playNext()
    source.start()
  }
}
