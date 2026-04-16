import { SAMPLE_RATE, CHUNK_SAMPLES } from '../types'

/**
 * Convert Float32Array (Web Audio API format, range -1.0 to 1.0)
 * to Int16Array (PCM16 format for WebSocket transmission).
 */
export function float32ToPcm16(float32: Float32Array): Int16Array {
  const pcm16 = new Int16Array(float32.length)
  for (let i = 0; i < float32.length; i++) {
    const clamped = Math.max(-1.0, Math.min(1.0, float32[i]))
    pcm16[i] = clamped < 0 ? clamped * 0x8000 : clamped * 0x7FFF
  }
  return pcm16
}

/**
 * Convert Int16Array to ArrayBuffer for WebSocket binary transmission.
 * Result is little-endian PCM16 (native on most platforms).
 */
export function pcm16ToArrayBuffer(pcm16: Int16Array): ArrayBuffer {
  return pcm16.buffer.slice(pcm16.byteOffset, pcm16.byteOffset + pcm16.byteLength) as ArrayBuffer
}

/**
 * Audio worklet processor script content.
 * Captures mic input and posts PCM16 chunks via message port.
 */
export const WORKLET_PROCESSOR_CODE = `
class BabelFlowProcessor extends AudioWorkletProcessor {
  constructor() {
    super()
    this.buffer = new Float32Array(${CHUNK_SAMPLES})
    this.bufferIndex = 0
  }

  process(inputs) {
    const input = inputs[0]
    if (!input || !input[0]) return true

    const channelData = input[0]
    for (let i = 0; i < channelData.length; i++) {
      this.buffer[this.bufferIndex++] = channelData[i]
      if (this.bufferIndex >= ${CHUNK_SAMPLES}) {
        this.port.postMessage({ type: 'audio', data: this.buffer.slice() })
        this.bufferIndex = 0
      }
    }
    return true
  }
}
registerProcessor('babelflow-processor', BabelFlowProcessor)
`

export interface AudioCaptureCallbacks {
  onChunk: (audioBuffer: ArrayBuffer) => void
  onError: (error: Error) => void
}

/**
 * Start capturing audio from microphone using AudioWorkletNode.
 * Returns a stop function to clean up resources.
 */
export async function startAudioCapture(
  callbacks: AudioCaptureCallbacks,
): Promise<() => void> {
  const audioContext = new AudioContext({ sampleRate: SAMPLE_RATE })
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: {
      channelCount: 1,
      sampleRate: SAMPLE_RATE,
      echoCancellation: true,
      noiseSuppression: true,
    },
  })

  // Create worklet from inline code
  const blob = new Blob([WORKLET_PROCESSOR_CODE], { type: 'application/javascript' })
  const workletUrl = URL.createObjectURL(blob)

  try {
    await audioContext.audioWorklet.addModule(workletUrl)
  } finally {
    URL.revokeObjectURL(workletUrl)
  }

  const source = audioContext.createMediaStreamSource(stream)
  const workletNode = new AudioWorkletNode(audioContext, 'babelflow-processor')

  workletNode.port.onmessage = (event) => {
    if (event.data?.type === 'audio') {
      const pcm16 = float32ToPcm16(event.data.data)
      const buffer = pcm16ToArrayBuffer(pcm16)
      callbacks.onChunk(buffer)
    }
  }

  source.connect(workletNode)
  workletNode.connect(audioContext.destination)

  // Return cleanup function
  return () => {
    workletNode.disconnect()
    source.disconnect()
    for (const track of stream.getTracks()) {
      track.stop()
    }
    audioContext.close().catch(() => {})
  }
}
