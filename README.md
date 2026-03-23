# BabelFlow — Real-Time Multi-Language Translator

Real-time speech-to-speech translation system for crowded environments.
Speaker diarization, 7 languages, <2s end-to-end latency target.

## Supported Languages

| Code | Language | TTS Voice |
|------|----------|-----------|
| tr | Turkish | tr-TR-AhmetNeural |
| ru | Russian | ru-RU-DmitryNeural |
| en | English | en-US-JennyNeural |
| th | Thai | th-TH-PremwadeeNeural |
| vi | Vietnamese | vi-VN-HoaiMyNeural |
| zh | Chinese (Mandarin) | zh-CN-XiaoxiaoNeural |
| id | Indonesian | id-ID-ArdiNeural |

## Architecture

```
Audio In (PCM16, 16kHz, mono)
  │
  ▼
┌─────────────────────────────────────────────────────┐
│ WebSocket /ws/translate                             │
│                                                     │
│  Audio Chunk (960 bytes, 30ms)                      │
│    │                                                │
│    ▼                                                │
│  Silero VAD ──→ Speech Segment Detection            │
│    │              (min 250ms speech, 300ms silence)  │
│    ▼                                                │
│  Faster Whisper ASR (large-v3)                      │
│    │  → PartialTranscript {text, lang, speaker_id}  │
│    ▼                                                │
│  Speaker Diarization (pyannote / mock)              │
│    │  → speaker_id assignment                       │
│    ▼                                                │
│  [Glossary Pre-processor] (passthrough MVP)         │
│    │                                                │
│    ▼                                                │
│  Azure Translator (batch, cached)                   │
│    │  → TranslationResult {translations: {lang: text}} │
│    ▼                                                │
│  [Glossary Post-processor] (passthrough MVP)        │
│    │                                                │
│    ▼                                                │
│  [Context Enricher] (passthrough MVP)               │
│    │                                                │
│    ▼                                                │
│  Azure TTS (per target language)                    │
│    │  → Binary TTS frame (PCM16, 24kHz)             │
│    ▼                                                │
│  WebSocket → Client                                 │
└─────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, WebSockets, Uvicorn |
| Frontend | React 18+, TypeScript, Vite, Tailwind CSS |
| ASR | Faster Whisper (CTranslate2) |
| Translation | Azure Translator REST API |
| TTS | Azure Cognitive Services Speech |
| VAD | Silero VAD |
| Diarization | pyannote.audio |
| Cache | In-memory (Redis planned) |
| Infra | Docker, Railway |

## Quick Start

### Backend (mock mode — no API keys needed)

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --port 3000
```

### Docker

```bash
docker-compose up
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health check |
| GET | `/api/config` | Active config summary |
| GET | `/api/pipeline/status` | Pipeline stage statuses |
| GET | `/api/latency` | Latency statistics |
| WS | `/ws/translate` | Audio translation WebSocket |

## WebSocket Protocol

### Client → Server

1. **First message (required):** JSON config
```json
{"type": "config", "source_lang": "auto", "target_langs": ["en", "th"], "enable_diarization": true}
```

2. **Audio chunks:** Binary PCM16 LE, 16kHz, mono, 960 bytes (30ms)

### Server → Client

- `partial_transcript` — ASR result (JSON)
- `translation` — Translation result (JSON)
- `tts_audio` — TTS binary frame (4-byte length + JSON header + PCM16 24kHz audio)
- `error` — Error message (JSON)

## Project Structure

```
realtime-translator/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, endpoints
│   │   ├── config.py            # Pydantic Settings
│   │   ├── constants.py         # Audio constants, supported langs
│   │   ├── exceptions.py        # Exception hierarchy
│   │   ├── schemas.py           # Pydantic V2 message models
│   │   ├── audio/
│   │   │   ├── capture.py       # PCM16 validation, AudioBuffer
│   │   │   ├── vad.py           # Silero VAD wrapper
│   │   │   ├── diarization.py   # Speaker diarization
│   │   │   └── speaker_cache.py # Speaker embedding cache
│   │   ├── transcription/
│   │   │   ├── whisper_engine.py # Faster Whisper wrapper
│   │   │   └── streaming.py     # VAD + Whisper pipeline
│   │   ├── translation/
│   │   │   ├── mock_translator.py  # Mock + Protocol + factory
│   │   │   ├── azure_translator.py # Azure Translator API
│   │   │   ├── cache.py            # Translation cache (TTL)
│   │   │   └── language_detect.py  # Source language resolution
│   │   ├── tts/
│   │   │   ├── voice_map.py     # 7-language voice mapping
│   │   │   └── mock_tts.py      # Mock + Azure TTS + factory
│   │   ├── glossary/
│   │   │   ├── base.py          # ABC hooks (pre/post/enrich)
│   │   │   ├── passthrough.py   # MVP passthrough
│   │   │   └── factory.py       # Processor factory
│   │   ├── pipeline/
│   │   │   ├── orchestrator.py  # Full pipeline orchestration
│   │   │   └── latency_monitor.py # Stage latency tracking
│   │   └── websockets/
│   │       ├── protocol.py      # Frame classification, TTS packing
│   │       ├── connection_manager.py
│   │       └── audio_handler.py # WebSocket endpoint handler
│   ├── tests/                   # 205 tests, mirrors app/ structure
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-deploy.txt  # Lightweight deploy deps
│   └── railway.json
├── frontend/                    # React + TypeScript + Vite
├── docs/
│   ├── websocket-protocol.md
│   ├── latency-budget.md
│   ├── plans/                   # Phase plans
│   └── tasks/                   # Kanban board + handoff
├── docker-compose.yml
└── CLAUDE.md
```

## Environment Variables

See `backend/.env.example` for full list. Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_MOCKS` | `true` | Mock mode (no Azure keys needed) |
| `AZURE_TRANSLATOR_KEY` | — | Azure Translator subscription key |
| `AZURE_SPEECH_KEY` | — | Azure Speech subscription key |
| `WHISPER_MODEL_SIZE` | `large-v3` | Whisper model size |
| `WHISPER_DEVICE` | `cuda` | Whisper device (cuda/cpu) |
| `GLOSSARY_MODE` | `passthrough` | Glossary processor mode |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed CORS origins |

## Latency Budget

| Stage | Target | Max |
|-------|--------|-----|
| Audio Capture + VAD | 100ms | 200ms |
| Streaming ASR | 200ms | 500ms |
| Translation | 100ms | 300ms |
| TTS | 100ms | 200ms |
| Network | 50ms | 100ms |
| **Total** | **550ms** | **1300ms** |

## Tests

```bash
cd backend
pytest tests/ -v          # 205 tests
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Deployment

### Railway

Backend is deployed at: `https://motivated-tranquility-production-5ed2.up.railway.app`

```bash
cd backend
railway login
railway up -s motivated-tranquility
```

## Development Model

Three-terminal setup: Senior Architect (plan + review) + Engineer A (backend) + Engineer B (frontend). Coordination via `docs/tasks/board.md` and git commits.

## License

Private — All rights reserved.
