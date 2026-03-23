# Handoff Noktaları

## Backend → Frontend
- WebSocket endpoint: `ws://localhost:8000/ws/translate`
- WebSocket protocol: docs/websocket-protocol.md (güncel)
- Pydantic modeller: backend/app/schemas.py
  - ConfigMessage, PartialTranscript, FinalTranscript, TranslationResult, TTSHeader, ErrorResponse
  → Frontend bu modellerin TypeScript karşılığını yazmalı
- Binary TTS frame format: 4-byte LE length + JSON header + PCM16 audio (24kHz)
  → Protocol: backend/app/websockets/protocol.py (pack_tts_frame / unpack_tts_frame)
- Exception types: backend/app/exceptions.py
  → ErrorResponse.code değerleri: CONFIG_REQUIRED, INVALID_CONFIG, INVALID_JSON

## Frontend → Backend
- Audio format: PCM16 Little-Endian, 16kHz, Mono, 480 samples (30ms) = 960 bytes/chunk
- Config mesajı (ilk mesaj olarak gönderilmeli):
  ```json
  {"type": "config", "source_lang": "auto", "target_langs": ["en", "th"], "enable_diarization": false}
  ```
- Desteklenen diller: tr, ru, en, th, vi, zh, id
- İlk mesaj config olmazsa → ErrorResponse + connection close

## Paylaşılan Sabitler
- SAMPLE_RATE: 16000 (input)
- TTS_SAMPLE_RATE: 24000 (output)
- CHUNK_SAMPLES: 480
- CHUNK_BYTES: 960
- SUPPORTED_LANGS: {"tr", "ru", "en", "th", "vi", "zh", "id"}
