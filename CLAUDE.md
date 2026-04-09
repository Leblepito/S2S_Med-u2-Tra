# BabelFlow — Real-Time Multi-Language Translator

## Proje Özeti
Kalabalık ortamlarda bile çoklu konuşmacıyı ayırt edip anlık çeviri yapan sistem.
7 dil: Türkçe, Rusça, İngilizce, Tayca, Vietnamca, Çince (Mandarin), Endonezyaca.

## Tech Stack
- **Backend:** Python 3.12, FastAPI, Uvicorn, WebSockets
- **Frontend:** React 19.2.4, TypeScript 5.9.3, Vite 8.0.1, Tailwind CSS 4.2.2
- **ASR (Speech-to-Text):** Faster Whisper (CTranslate2)
- **Translation:** Azure Translator (7 dil tam destek)
- **TTS (Text-to-Speech):** Azure Cognitive Services TTS
- **Audio:** WebRTC, Web Audio API (AudioWorkletNode), VAD (Silero)
- **Infra:** Docker, docker-compose, PostgreSQL (user/session data), Redis (cache)

## Metodoloji
Bu proje **superpowers** framework ile geliştirilir. Her görev için:
1. Brainstorm → 2. Plan yaz (2-5 dk'lık task'lar) → 3. TDD ile implement et → 4. Review → 5. Verify

## Komutlar
```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
pytest tests/ -v

# Frontend
cd frontend && npm install
npm run dev -- --port 3000
npm run test
```

## Proje Yapısı
```
realtime-translator/
├── CLAUDE.md
├── backend/
│   ├── CLAUDE.md              # Backend-specific kurallar
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, middleware
│   │   ├── config.py          # Env vars, API keys
│   │   ├── websockets/
│   │   │   ├── audio_handler.py    # WebSocket audio stream handler
│   │   │   └── protocol.py         # Message types, serialization
│   │   ├── audio/
│   │   │   ├── capture.py          # Audio format conversion (PCM16, 16kHz)
│   │   │   ├── vad.py              # Voice Activity Detection (Silero)
│   │   │   └── diarization.py      # Speaker diarization (pyannote)
│   │   ├── transcription/
│   │   │   ├── whisper_engine.py   # Faster Whisper wrapper
│   │   │   └── streaming.py        # Streaming ASR with partial results
│   │   ├── translation/
│   │   │   ├── azure_translator.py # Azure Translator API
│   │   │   └── language_detect.py  # Auto language detection
│   │   ├── tts/
│   │   │   ├── azure_tts.py        # Azure Cognitive Services TTS
│   │   │   └── voice_map.py        # Dil → ses eşlemesi
│   │   └── pipeline/
│   │       ├── orchestrator.py     # ASR → Translation → TTS pipeline
│   │       └── latency_monitor.py  # Pipeline latency tracking
│   ├── tests/                      # app/ yapısını mirror eder
│   └── requirements.txt
├── frontend/
│   ├── CLAUDE.md
│   └── src/
│       ├── components/
│       │   ├── AudioCapture.tsx     # Mikrofon erişimi + audio stream
│       │   ├── LanguageSelector.tsx  # Dil seçim UI
│       │   ├── TranslationDisplay.tsx # Anlık çeviri gösterimi
│       │   ├── SpeakerIndicator.tsx   # Konuşmacı ayrımı gösterimi
│       │   └── LatencyIndicator.tsx   # Gecikme göstergesi
│       ├── hooks/
│       │   ├── useWebSocket.ts       # WebSocket connection management
│       │   ├── useAudioStream.ts     # Audio capture + streaming
│       │   └── useTranslation.ts     # Translation state management
│       └── services/
│           ├── websocket.ts          # WebSocket client
│           └── audio.ts              # AudioWorklet processor
├── docs/
│   ├── architecture.md              # Sistem mimarisi
│   ├── websocket-protocol.md        # Binary audio protocol spec
│   ├── latency-budget.md            # Hedef: <2s end-to-end
│   └── plans/                       # Superpowers plan dosyaları
└── docker-compose.yml
```

## Latency Budget (Hedef: <2 saniye toplam)
| Aşama | Hedef | Max |
|-------|-------|-----|
| Audio Capture + VAD | 100ms | 200ms |
| Streaming ASR | 200ms | 500ms |
| Translation API | 100ms | 300ms |
| TTS Synthesis | 100ms | 200ms |
| Network | 50ms | 100ms |
| **Toplam** | **550ms** | **1300ms** |

## WebSocket Protocol
- Client → Server: Binary PCM16 audio (16kHz, mono) + JSON config messages
- Server → Client: JSON (partial_transcript, final_transcript, translation, speaker_id) + Binary TTS audio
- Pivot language: İngilizce (direkt çeviri olmayan dil çiftleri için)

## Kritik Kurallar
- Tüm I/O async/await olmalı
- Pydantic V2 kullan (schema validation)
- Her yeni özellik TDD ile: önce test yaz, sonra implement et
- WebSocket handler'lar max 50 satır — logic'i service layer'a taşı
- Audio buffer size: 480 samples (30ms @ 16kHz)
- Partial results downstream'e hemen gönderilmeli (sentence completion bekleme)

## Son Eklenen Özellikler (2026-04)
- **ESP32 entegrasyonu:** `/ws/device/{device_id}` WebSocket handler, 8kHz upsample + heartbeat
- **BabelFlow Widget SDK:** `/embed/sdk.js` embeddable widget (mic, translation, lang selector)
- **Glossary sistemi:** Medikal/turizm terminoloji sözlüğü (35 terim × 7 dil), UI import/export
- **Admin paneli:** Session listesi, istatistikler, glossary yönetimi
- **Session persistence:** Redis cache + SQLite DB

## Agent Kullanımı
`.claude/agents/` altında:
- **React Component Architect** → Frontend componentler
- **Backend Developer** → FastAPI endpoints
- **API Architect** → WebSocket protocol design
- **Code Reviewer** → Her PR öncesi review
- **Performance Optimizer** → Latency bottleneck analizi
