# Plan: Faster Whisper ASR Entegrasyonu
Tarih: 2026-03-23
Durum: Devam Ediyor

## Mimari Karar
Silero VAD + Faster Whisper large-v3. VAD speech segment'leri tespit eder, tamamlanan segment Whisper'a gönderilir. USE_MOCKS=true iken mock model kullanılır.

## Task'lar

### Task 1: Silero VAD wrapper — backend/app/audio/vad.py
- is_speech(chunk) -> bool
- SpeechSegmentDetector: chunk biriktir, speech başlangıç/bitiş tespit et
- min_speech_ms=250, min_silence_ms=300
- Test: tests/audio/test_vad.py

### Task 2: Faster Whisper wrapper — backend/app/transcription/whisper_engine.py
- WhisperEngine class (singleton)
- transcribe(audio: np.ndarray) -> TranscriptionResult
- USE_MOCKS=true → mock model
- Test: tests/transcription/test_whisper_engine.py

### Task 3: Streaming transcription — backend/app/transcription/streaming.py
- StreamingTranscriber: VAD + Whisper entegrasyonu
- process_chunk(chunk) -> Optional[PartialTranscript]
- Latency tracking (<500ms hedef)
- Test: tests/transcription/test_streaming.py

### Task 4: audio_handler.py güncelleme
- AudioBuffer → StreamingTranscriber
- Transcript → client'a partial_transcript JSON
- Test: integration test güncelle

## Mühendisin İtiraz Alanı
[Boş]
