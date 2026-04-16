# Handoff Noktaları

## Backend → Frontend

### WebSocket Endpoint
- URL: `ws://localhost:8000/ws/translate`
- İlk mesaj: ConfigMessage (JSON)
- Sonra: binary PCM16 audio chunks (960 bytes)

### Pydantic Modeller (backend/app/schemas.py)
Frontend bu modellerin TypeScript karşılığını `frontend/src/types/protocol.ts` içinde yazmalı:

| Pydantic (Python) | TypeScript | Yön |
|---|---|---|
| `ConfigMessage` | `ConfigMessage` | Client → Server |
| `PartialTranscript` | `PartialTranscript` | Server → Client |
| `FinalTranscript` | `FinalTranscript` | Server → Client |
| `TranslationResult` | `TranslationResult` | Server → Client |
| `TTSHeader` | `TTSHeader` | Server → Client (binary frame) |
| `ErrorResponse` | `ErrorResponse` | Server → Client |

### Phase 3 Yeni Mesajlar (Backend'den gelecek)
- `PartialTranscript` — ASR partial sonuçları (her 200-500ms)
  - `{type: "partial_transcript", text: "merhaba", lang: "tr", speaker_id: 0, confidence: 0.85}`
- `FinalTranscript` — ASR final sonuçları (cümle bitti)
  - `{type: "final_transcript", text: "merhaba nasılsınız", lang: "tr", speaker_id: 0, confidence: 0.95}`
- `TranslationResult` — Çeviri sonuçları (FinalTranscript sonrası gelir)
  - `{type: "translation", source_text: "merhaba", source_lang: "tr", translations: {"en": "hello", "th": "สวัสดี"}, speaker_id: 0}`

### Binary TTS Frame Format
- 4-byte LE length + JSON header + PCM16 audio (24kHz)
- Protocol: `backend/app/websockets/protocol.py` → `pack_tts_frame` / `unpack_tts_frame`

### Error Codes
- `CONFIG_REQUIRED` — İlk mesaj config değilse
- `INVALID_CONFIG` — Config validation başarısız
- `INVALID_JSON` — JSON parse hatası
- `ASR_ERROR` — Whisper transcription hatası (Phase 3 yeni)
- `VAD_ERROR` — Voice activity detection hatası (Phase 3 yeni)

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

## Phase 3 Entegrasyon Noktaları
1. **useTranslation hook** → WebSocket'ten gelen `partial_transcript`, `final_transcript`, `translation` mesajlarını dinler
2. **LanguageSelector** → `ConfigMessage` oluşturur → WebSocket'e JSON olarak gönderir
3. **TranslationDisplay** → useTranslation hook'undan gelen state'i render eder
4. **Backend streaming ASR** → Her speech segment sonrası partial → final → translation sırası ile mesaj gönderir
