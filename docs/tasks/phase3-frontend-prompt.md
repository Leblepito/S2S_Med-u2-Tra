# Phase 3 Frontend — Mühendis B Prompt

Terminal 3'e yapıştır:

---

```
Sen BabelFlow projesinin Senior Frontend Mühendisisin.

ÇALIŞMA ALANI: Sadece frontend/ klasörü. backend/'a DOKUNMA.

## SESSION BAŞLANGIÇ
1. CLAUDE.md oku (proje root)
2. git pull
3. docs/tasks/board.md oku → "MÜHENDİS B" altındaki aktif task'ını bul
4. docs/tasks/handoff.md oku → backend'ten gelen mesaj formatlarını kontrol et
5. backend/app/schemas.py oku → Pydantic modellerin TS karşılığını yaz

## PHASE 3 TASK'LARI (Sırayla implement et)

### Task 8: TypeScript Types + useTranslation Hook
Dosyalar:
- frontend/src/types/protocol.ts
- frontend/src/hooks/useTranslation.ts

protocol.ts — Backend Pydantic modellerinin birebir TypeScript karşılıkları:
- ConfigMessage: {type: "config", source_lang: string, target_langs: string[], enable_diarization: boolean}
- PartialTranscript: {type: "partial_transcript", text: string, lang: string, speaker_id: number, confidence: number}
- FinalTranscript: {type: "final_transcript", text: string, lang: string, speaker_id: number, confidence: number}
- TranslationResult: {type: "translation", source_text: string, source_lang: string, translations: Record<string, string>, speaker_id: number}
- TTSHeader: {type: "tts_audio", lang: string, chunk_index: number}
- ErrorResponse: {type: "error", message: string, code?: string}
- ServerMessage = PartialTranscript | FinalTranscript | TranslationResult | ErrorResponse
- Type guard fonksiyonları: isPartialTranscript(), isFinalTranscript(), isTranslation(), isError()

useTranslation.ts — Translation state yönetimi hook'u:
- State: partialText (string), transcripts (FinalTranscript[]), translations (TranslationResult[]), error (string | null)
- WebSocket onMessage callback'i alır → mesaj type'ına göre state günceller
- partial_transcript → partialText güncelle (üzerine yaz, append değil)
- final_transcript → partialText temizle, transcripts dizisine ekle
- translation → translations dizisine ekle
- error → error state'i set et
- clearError(), clearTranscripts() fonksiyonları
- Return: {partialText, transcripts, translations, error, handleMessage, clearError, clearTranscripts}

Test: Her type guard, her state transition, edge case'ler (boş mesaj, bilinmeyen type)

### Task 9: LanguageSelector Component
Dosya: frontend/src/components/LanguageSelector.tsx

Props:
- sourceLang: string (default "auto")
- targetLangs: string[] (default ["en"])
- onConfigChange: (config: ConfigMessage) => void
- disabled?: boolean

Özellikler:
- 7 dil listesi: TR 🇹🇷, RU 🇷🇺, EN 🇬🇧, TH 🇹🇭, VI 🇻🇳, ZH 🇨🇳, ID 🇮🇩
- Source dil: dropdown (7 dil + "auto" seçeneği)
- Target diller: multi-select checkbox/chip (en az 1 zorunlu)
- Source = target aynı olamaz (otomatik filtrele)
- Her değişiklikte onConfigChange callback'ini çağır
- Tailwind CSS ile stillendir

Test: Render, dil seçimi, multi-select, validation, callback çağrıları

### Task 10: TranslationDisplay Component
Dosya: frontend/src/components/TranslationDisplay.tsx

Props:
- partialText: string
- transcripts: FinalTranscript[]
- translations: TranslationResult[]
- targetLangs: string[]

Özellikler:
- Üstte: aktif partial transcript (yanıp sönen cursor efekti)
- Ortada: finalize olmuş transcript listesi (son 10, scroll)
- Altta: her hedef dil için çeviri kartı
  - Kart başlığı: dil flag + isim
  - Kart içeriği: son çeviri text'i
  - Birden fazla hedef dil varsa yan yana grid
- Speaker ID'ye göre renk atama (speaker_id 0 → mavi, 1 → yeşil, 2 → turuncu...)
- Boş state: "Konuşmaya başlayın..." placeholder
- Tailwind CSS ile stillendir

Test: Render, partial→final geçişi, çoklu dil kartları, speaker renkleri, boş state

## COMMIT KURALI
- git add frontend/ — sadece kendi dosyaların
- git add docs/tasks/board.md — sadece kendi satırını güncelle (MÜHENDİS B bölümü)
- backend/ klasörüne commit ATMA
- Her task bitince commit + push

## BİTİNCE
- docs/tasks/board.md'de kendi task'larını ✅ işaretle
- git commit + push
- "Mimar review bekliyor" de
```
