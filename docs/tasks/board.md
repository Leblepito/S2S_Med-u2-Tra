# Task Board
Son güncelleme: 2026-03-23 16:00

## BACKLOG
- [ ] Task: Azure TTS entegrasyonu (backend)
- [ ] Task: Pipeline orchestrator (backend)
- [ ] Task: Speaker diarization (backend)
- [ ] Task: SpeakerIndicator component (frontend)
- [ ] Task: LatencyIndicator component (frontend)

## MÜHENDİS A (Backend) — AKTİF — PHASE 3
- [x] Task 1: Config + Constants + Exceptions ✅ reviewed
- [x] Task 2: Pydantic Schemas ✅ reviewed
- [x] Task 3-7: WebSocket Audio Pipeline ✅ reviewed (78 test)
- [x] Task 8: Silero VAD entegrasyonu ✅ (8 test)
- [x] Task 9: Faster Whisper ASR engine ✅ (9 test)
- [x] Task 10: Streaming ASR pipeline + handler güncelleme ✅ (5 test)
- [ ] Sonraki: Azure Translator veya TTS (Mimar atasın)

## MÜHENDİS B (Frontend) — AKTİF — PHASE 3
- [x] Phase 2: WebSocket service + Audio capture + hooks + AudioCapture ✅ (58 test)
- [ ] Task 8: TypeScript types + useTranslation hook 🔨
  - `frontend/src/types/protocol.ts` — Backend Pydantic modellerinin TS karşılıkları
  - `frontend/src/hooks/useTranslation.ts` — Translation state yönetimi
  - Partial/final transcript, translation result, error handling
- [ ] Task 9: LanguageSelector component 🔨
  - `frontend/src/components/LanguageSelector.tsx`
  - 7 dil (flag + isim), source dil auto seçeneği, multi-select target
  - Config mesajı oluştur → WebSocket'e gönder
- [ ] Task 10: TranslationDisplay component 🔨
  - `frontend/src/components/TranslationDisplay.tsx`
  - Real-time transcript gösterimi (partial → final geçişi)
  - Çoklu hedef dil çeviri kartları
  - Speaker ID renklendirme

## TAMAMLANDI
- Phase 1: Backend foundation (config, schemas, exceptions) — 42 test
- Phase 2 Backend: WebSocket audio pipeline — 78 test
- Phase 2 Frontend: WebSocket + Audio capture — 58 test
- Phase 3 Backend: VAD + Whisper ASR streaming — 100 test toplam

## BLOKE
- [yoksa boş]
