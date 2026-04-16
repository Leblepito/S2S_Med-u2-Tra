# BabelFlow API Reference

Base URL: `https://motivated-tranquility-production-5ed2.up.railway.app`

## REST Endpoints

### GET /health
Service health check.

```bash
curl https://motivated-tranquility-production-5ed2.up.railway.app/health
```
```json
{"status": "ok", "service": "babelflow"}
```

### GET /api/config
Active configuration summary.

```bash
curl https://motivated-tranquility-production-5ed2.up.railway.app/api/config
```
```json
{
  "mock_mode": true,
  "glossary_mode": "passthrough",
  "whisper_model": "large-v3",
  "whisper_device": "cpu",
  "supported_langs": ["en", "id", "ru", "th", "tr", "vi", "zh"],
  "cors_origins": ["*"],
  "azure_translator_configured": false,
  "azure_speech_configured": false
}
```

### GET /api/pipeline/status
Pipeline stage health.

```bash
curl https://motivated-tranquility-production-5ed2.up.railway.app/api/pipeline/status
```
```json
{
  "status": "ok",
  "stages": {
    "vad": "mock",
    "asr": "mock",
    "translation": "mock",
    "tts": "mock",
    "glossary": "passthrough",
    "diarization": "mock"
  }
}
```

### GET /api/metrics
WebSocket session metrics.

```bash
curl https://motivated-tranquility-production-5ed2.up.railway.app/api/metrics
```
```json
{
  "active_connections": 0,
  "total_sessions": 5
}
```

### GET /api/latency
Pipeline latency statistics (per-connection via WebSocket).

```bash
curl https://motivated-tranquility-production-5ed2.up.railway.app/api/latency
```

## WebSocket Protocol

### Endpoint
```
wss://motivated-tranquility-production-5ed2.up.railway.app/ws/translate
```

### Connection Flow

```
Client                          Server
  │                               │
  │──── WebSocket Connect ────────►│
  │                               │
  │──── Config (JSON) ────────────►│  (REQUIRED as first message)
  │                               │
  │──── Audio Chunks (binary) ────►│  (960 bytes each, 30ms)
  │──── Audio Chunks (binary) ────►│
  │──── Audio Chunks (binary) ────►│
  │                               │
  │◄──── partial_transcript (JSON)─│  (when speech segment detected)
  │◄──── translation (JSON) ──────│  (translation results)
  │◄──── tts_audio (binary) ──────│  (TTS audio frame)
  │                               │
  │──── Disconnect ───────────────►│
```

### Client → Server Messages

#### 1. Config Message (JSON, required first)

```json
{
  "type": "config",
  "source_lang": "auto",
  "target_langs": ["en", "th"],
  "enable_diarization": true
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| type | string | yes | "config" | Must be "config" |
| source_lang | string | no | "auto" | Source language or "auto" |
| target_langs | string[] | yes | — | Target languages (min 1) |
| enable_diarization | bool | no | false | Speaker diarization |

Valid languages: `tr`, `ru`, `en`, `th`, `vi`, `zh`, `id`

#### 2. Audio Chunks (Binary)

- Format: PCM16 Little-Endian
- Sample rate: 16kHz
- Channels: Mono
- Chunk size: 960 bytes (480 samples, 30ms)

### Server → Client Messages

#### partial_transcript (JSON)

```json
{
  "type": "partial_transcript",
  "text": "Merhaba nasılsınız",
  "lang": "tr",
  "speaker_id": 0,
  "confidence": 0.92
}
```

#### translation (JSON)

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

#### tts_audio (Binary Frame)

Format: `[4-byte LE length][JSON header][PCM16 audio data]`

JSON header:
```json
{"type": "tts_audio", "lang": "en", "chunk_index": 0}
```

Audio: PCM16 Little-Endian, 24kHz, Mono

#### error (JSON)

```json
{
  "type": "error",
  "message": "Description of error",
  "code": "ERROR_CODE"
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `CONFIG_REQUIRED` | First message must be config |
| `INVALID_CONFIG` | Config validation failed |
| `INVALID_JSON` | JSON parse error |
