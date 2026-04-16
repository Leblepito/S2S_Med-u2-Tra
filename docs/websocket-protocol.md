# WebSocket Protocol Spec

## Endpoint
`ws://localhost:8000/ws/translate`

## Client → Server

### Binary: Audio Data
PCM16 Little-Endian, 16kHz, Mono
Buffer size: 480 samples (30ms)

### JSON: Configuration
```json
{
  "type": "config",
  "source_lang": "auto",
  "target_langs": ["en", "th"],
  "enable_diarization": true
}
```

## Server → Client

### JSON: Transcription
```json
{
  "type": "partial_transcript",
  "text": "Merhaba nasıl...",
  "lang": "tr",
  "speaker_id": 0,
  "confidence": 0.92
}
```

### JSON: Translation
```json
{
  "type": "translation",
  "source_text": "Merhaba nasılsınız",
  "source_lang": "tr",
  "translations": {
    "en": "Hello how are you",
    "th": "สวัสดีครับ สบายดีไหม"
  },
  "speaker_id": 0
}
```

### Binary: TTS Audio
PCM16 Little-Endian, 24kHz, Mono
Prefixed with 4-byte JSON length + JSON header:
```json
{"type": "tts_audio", "lang": "en", "chunk_index": 0}
```
