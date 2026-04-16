# Plan: WebSocket + Audio Capture Pipeline
Tarih: 2026-03-23
Durum: Onaylı

## Mimari Karar
FastAPI native WebSocket + binary/JSON multiplexing. Audio chunk'lar binary frame olarak, config/control mesajları JSON frame olarak gelecek. Protocol layer bu ayrımı yapar, handler sadece orchestrate eder.

Alternatifler:
- Socket.IO: overhead fazla, binary desteği kötü — elendi
- gRPC streaming: client tarafında browser desteği zayıf — elendi
- **Native WebSocket + protocol layer**: basit, hızlı, browser-native — SEÇİLDİ

## Ön Koşullar
- [x] Proje iskeleti kurulmuş (Phase 1)
- [x] Frontend Vite + React + TS hazır (21 test geçiyor)
- [x] docs/websocket-protocol.md yazılmış

## Task'lar (Backend — Mühendis)

### Task 1: Config + Constants + Exceptions — Tahmini: 5 dk
- Dosyalar:
  - `backend/app/config.py` (yeni)
  - `backend/app/constants.py` (yeni)
  - `backend/app/exceptions.py` (yeni)
  - `backend/tests/test_config.py` (yeni)
- Ne yapılacak:
  - `config.py`: Pydantic Settings — WHISPER_MODEL_SIZE (default "large-v3"), WHISPER_DEVICE (default "cuda"), AZURE_TRANSLATOR_KEY, AZURE_TRANSLATOR_REGION (default "southeastasia"), AZURE_SPEECH_KEY, AZURE_SPEECH_REGION, REDIS_URL (default "redis://localhost:6379"), USE_MOCKS (default True), LOG_LEVEL (default "INFO")
  - `constants.py`: SUPPORTED_LANGS = frozenset({"tr","ru","en","th","vi","zh","id"}), SAMPLE_RATE=16000, CHANNELS=1, CHUNK_SAMPLES=480, CHUNK_BYTES=960, TTS_SAMPLE_RATE=24000
  - `exceptions.py`: BabelFlowError(Exception), AudioFormatError, TranscriptionError, TranslationError, TTSError, WebSocketError — hepsi BabelFlowError'dan türesin
- Test senaryoları:
  - Config env'den yükleniyor (mock env vars ile)
  - Default değerler doğru
  - Constants değerleri doğru (CHUNK_BYTES = CHUNK_SAMPLES * 2)
- Kabul kriteri: pytest geçiyor, type hints eksiksiz

### Task 2: Pydantic Schemas — Tahmini: 5 dk
- Dosyalar:
  - `backend/app/schemas.py` (yeni)
  - `backend/tests/test_schemas.py` (yeni)
- Ne yapılacak:
  - ConfigMessage(type="config", source_lang, target_langs, enable_diarization)
  - PartialTranscript(type="partial_transcript", text, lang, speaker_id, confidence)
  - FinalTranscript(type="final_transcript", text, lang, speaker_id, confidence)
  - TranslationResult(type="translation", source_text, source_lang, translations: dict[str,str], speaker_id)
  - TTSHeader(type="tts_audio", lang, chunk_index)
  - ErrorResponse(type="error", message, code: Optional)
  - `parse_client_message(data: str) -> ConfigMessage` — JSON parse + validation
  - `serialize_server_message(msg) -> str` — JSON serialize
- Test senaryoları:
  - Her model doğru serialize/deserialize
  - ConfigMessage validation (invalid lang reddedilmeli)
  - parse_client_message valid/invalid JSON
  - serialize_server_message round-trip
- Kabul kriteri: pytest geçiyor, docs/websocket-protocol.md ile uyumlu

### Task 3: WebSocket Protocol Layer — Tahmini: 5 dk
- Dosyalar:
  - `backend/app/websockets/protocol.py` (yeni)
  - `backend/tests/websockets/__init__.py` (yeni)
  - `backend/tests/websockets/test_protocol.py` (yeni)
- Ne yapılacak:
  - `classify_frame(data: bytes | str) -> tuple[str, Any]` — "audio" + bytes veya "json" + parsed dict
  - `pack_tts_frame(header: TTSHeader, audio: bytes) -> bytes` — 4-byte JSON length + JSON header + audio
  - `unpack_tts_frame(data: bytes) -> tuple[TTSHeader, bytes]` — parse
- Test senaryoları:
  - Binary frame → ("audio", raw_bytes)
  - JSON string frame → ("json", parsed_dict)
  - Invalid JSON → WebSocketError
  - TTS frame pack/unpack round-trip
  - 4-byte length prefix doğru
- Kabul kriteri: pytest geçiyor, fonksiyonlar max 15 satır

### Task 4: Audio Capture Handler — Tahmini: 5 dk
- Dosyalar:
  - `backend/app/audio/capture.py` (yeni)
  - `backend/tests/audio/__init__.py` (yeni)
  - `backend/tests/audio/test_capture.py` (yeni)
- Ne yapılacak:
  - `validate_chunk(data: bytes) -> None` — 960 bytes kontrolü, hata: AudioFormatError
  - `bytes_to_samples(data: bytes) -> np.ndarray` — PCM16 LE → int16 numpy array
  - `AudioBuffer` class: chunk biriktir, threshold'a ulaşınca segment ver
    - `add_chunk(data: bytes) -> Optional[np.ndarray]`
    - Buffer size configurable (default: 16000 samples = 1 saniye)
- Test senaryoları:
  - Valid 960-byte chunk kabul
  - Invalid size → AudioFormatError
  - bytes_to_samples doğru dönüşüm (bilinen değerlerle)
  - AudioBuffer: chunk biriktirme, segment verme, reset
- Kabul kriteri: pytest geçiyor, numpy array dtype=int16

### Task 5: Connection Manager — Tahmini: 3 dk
- Dosyalar:
  - `backend/app/websockets/connection_manager.py` (yeni)
  - `backend/tests/websockets/test_connection_manager.py` (yeni)
- Ne yapılacak:
  - `ConnectionManager` class:
    - `connect(ws: WebSocket, config: ConfigMessage)` — kaydet
    - `disconnect(ws: WebSocket)` — kaldır
    - `get_config(ws: WebSocket) -> ConfigMessage`
    - `active_count -> int`
  - Thread-safe (asyncio Lock)
- Test senaryoları:
  - Connect → active_count artıyor
  - Disconnect → active_count azalıyor
  - Config doğru dönüyor
  - Olmayan bağlantı → KeyError
- Kabul kriteri: pytest geçiyor

### Task 6: WebSocket Audio Handler — Tahmini: 5 dk
- Dosyalar:
  - `backend/app/websockets/audio_handler.py` (yeni)
  - `backend/tests/websockets/test_audio_handler.py` (yeni)
  - `backend/app/main.py` (düzenleme — route ekle)
- Ne yapılacak:
  - `websocket_translate(ws: WebSocket)` — MAX 50 SATIR
    1. Accept connection
    2. İlk mesajı bekle → config olmalı (değilse error + close)
    3. ConnectionManager'a kaydet
    4. Loop: binary → validate + buffer, JSON → log
    5. Disconnect → cleanup
  - main.py'ye `app.websocket("/ws/translate")(websocket_translate)` ekle
- Test senaryoları:
  - Connect + config → bağlantı kabul
  - Config olmadan binary gönder → error mesajı + close
  - Valid binary chunk → buffer'a ekleniyor (log ile doğrula)
  - Disconnect → cleanup yapılıyor
  - Invalid JSON → error mesajı
- Kabul kriteri: pytest geçiyor, handler ≤50 satır, /ws/translate endpoint çalışıyor

### Task 7: Entegrasyon Testi — Tahmini: 5 dk
- Dosyalar:
  - `backend/tests/test_integration.py` (yeni)
- Ne yapılacak:
  - Full flow test: connect → config → binary chunks → disconnect
  - httpx + WebSocket test client kullan
  - Synthetic PCM16 audio chunk oluştur (sessizlik veya sinüs dalgası)
- Test senaryoları:
  - End-to-end: connect, send config, send 10 audio chunks, disconnect
  - Health endpoint hâlâ çalışıyor
- Kabul kriteri: pytest geçiyor, tüm testler yeşil

## Task'lar (Frontend — Mimar)
Mimar (ben) paralel olarak frontend'i implement edecek:
- services/websocket.ts — WebSocket client
- services/audio.ts — AudioWorklet mic capture
- hooks/useWebSocket.ts, useAudioStream.ts
- components/AudioCapture.tsx

## Riskler
- WebSocket test client davranışı farklı olabilir (httpx vs gerçek browser) → integration test'te dikkatli ol
- AudioBuffer threshold'u VAD ile çakışabilir → Phase 3'te refactor edilebilir
- Binary frame detection: FastAPI text vs bytes ayrımı doğru çalışmalı → test et

## Mühendisin İtiraz Alanı
[Mühendis buraya itirazlarını yazar — Mimar cevaplar]
