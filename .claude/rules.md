# BabelFlow — Ortak Kurallar

## Metodoloji
- Superpowers: brainstorm → plan → TDD → review → verify
- Her task 2-5 dakikalık olmalı
- Test ÖNCE yazılır, sonra implement edilir

## Kod Kuralları
- Tüm I/O async/await
- Type hints zorunlu (Python + TypeScript)
- Pydantic V2 (BaseModel) tüm data yapılarında
- WebSocket handler max 50 satır — logic service layer'da
- Fonksiyon max 30 satır, dosya max 200 satır
- `logger` kullan, `print()` YASAK
- Bare `except:` YASAK — spesifik exception
- `any` YASAK (TypeScript)
- `var` YASAK (TypeScript) — const/let kullan

## Audio Standartları
- Input: PCM16 Little-Endian, 16kHz, Mono, 480 samples (30ms)
- TTS Output: PCM16 Little-Endian, 24kHz, Mono
- AudioWorkletNode kullan (ScriptProcessorNode YASAK — deprecated)

## Git
- Conventional Commits: feat:, fix:, refactor:, test:, docs:
- .env dosyaları ASLA commit edilmez
- Her task tamamlanınca commit

## İletişim
- docs/plans/ — Mimar ↔ Mühendis plan/task iletişimi
- docs/decisions/ — ADR'ler
- İtirazlar plan dosyasının "Mühendisin İtiraz Alanı" bölümünde
- Review sonuçları task raporlarına eklenir

## Desteklenen Diller
tr, ru, en, th, vi, zh, id (7 dil)

## Latency Hedefleri
- Audio Capture + VAD: <200ms
- ASR (Whisper): <500ms
- Translation: <300ms
- TTS: <200ms
- Network: <100ms
- **Toplam: <2000ms**
