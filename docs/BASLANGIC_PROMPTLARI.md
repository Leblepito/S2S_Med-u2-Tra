# BabelFlow — Claude Code Başlangıç Promptları

## ÖNCELİK SIRASI

Claude Code'a bu promptları sırayla ver. Her biri bir session.

---

## PROMPT 1: Proje Kurulumu (İlk Session)

```
Bu proje klasöründe BabelFlow adlı bir real-time çok dilli çeviri sistemi geliştiriyoruz.

Önce şunları yap:
1. CLAUDE.md dosyasını oku ve projeyi anla
2. .superpowers-ref/ klasöründeki superpowers framework'ü incele — özellikle skills/ altındaki SKILL.md dosyalarını oku
3. .awesome-agents-ref/ klasöründeki agent tanımlarını incele
4. .claude/agents/ altına bu projede işe yarayacak agent'ları düzenle/ekle

Superpowers'ın brainstorming skill'ini kullanarak backend audio pipeline mimarisini brainstorm et. Sonucu docs/architecture.md'ye yaz.

Kurallar:
- Superpowers methodology'sine uy (brainstorm → plan → TDD → review → verify)
- Her dosya değişikliğinde test yaz
- Türkçe yorum ve commit mesajları
```

---

## PROMPT 2: WebSocket + Audio Capture (İkinci Session)

```
CLAUDE.md ve docs/ klasörünü oku.

Superpowers planning skill'ini kullanarak şu özelliği planla ve implement et:

HEDEF: Client'tan mikrofon audio'su alıp WebSocket üzerinden backend'e stream etmek.

Backend tarafı:
- FastAPI WebSocket endpoint: /ws/translate
- Binary PCM16 audio alımı (16kHz, mono)
- JSON config mesajı alımı (source_lang, target_langs)
- Bağlantı yönetimi (connect, disconnect, error handling)

Frontend tarafı:
- AudioWorkletNode ile mikrofon capture (ScriptProcessorNode KULLANMA)
- PCM16 formatına çevir
- WebSocket üzerinden stream et
- Bağlantı durumu göstergesi

TDD: Önce test yaz, sonra implement et. Her task 2-5 dakikalık olsun.
docs/plans/ altına planı kaydet.
```

---

## PROMPT 3: Faster Whisper ASR Entegrasyonu (Üçüncü Session)

```
CLAUDE.md ve docs/ klasörünü oku.

Superpowers planning skill'ini kullanarak şu özelliği planla ve implement et:

HEDEF: WebSocket'ten gelen audio stream'i Faster Whisper ile real-time transcribe etmek.

İmplementasyon:
- Silero VAD ile konuşma/sessizlik ayrımı
- Faster Whisper large-v3 modeli ile streaming transcription
- 7 dil auto-detect (tr, ru, en, th, vi, zh, id)
- Partial results (tam cümle bitmeden) client'a gönder
- Latency monitoring (hedef: ASR <500ms)

Test senaryoları:
- Sessizlikte transcription tetiklenmemeli
- Kısa cümle (2-3 kelime) doğru transcribe edilmeli
- Dil tespiti doğru çalışmalı
- Partial results latency <500ms olmalı
```

---

## PROMPT 4: Azure Translator Entegrasyonu (Dördüncü Session)

```
CLAUDE.md ve docs/ klasörünü oku.

HEDEF: Transcribe edilen metni hedef dillere anlık çevirmek.

İmplementasyon:
- Azure Translator API entegrasyonu
- 7 dil: tr, ru, en, th, vi, zh, id
- Pivot language olarak İngilizce kullan (direkt çeviri yoksa: source → en → target)
- Batch translation (birden fazla hedef dil tek API call'da)
- Cache layer (Redis) — aynı cümle tekrar çevrilmesin
- Translation result'ı WebSocket üzerinden client'a gönder

Latency hedefi: Translation <300ms
```

---

## PROMPT 5: TTS + Full Pipeline (Beşinci Session)

```
CLAUDE.md ve docs/ klasörünü oku.

HEDEF: Çevrilen metni sesli okuma + tüm pipeline'ı birleştirme.

İmplementasyon:
- Azure Cognitive Services TTS entegrasyonu
- Her dil için uygun ses seçimi (voice_map.py)
- Streaming TTS (tam cümle bitmeden audio chunk göndermeye başla)
- Pipeline orchestrator: Audio → VAD → ASR → Translation → TTS
- End-to-end latency tracking ve logging

Frontend:
- Çeviri metnini göster (TranslationDisplay component)
- TTS audio'yu çal (Web Audio API)
- Konuşmacı göstergesi
- Dil seçim paneli

Test: Full pipeline integration test — Türkçe audio in → İngilizce text + audio out
```

---

## PROMPT 6: Speaker Diarization — Kalabalık Ortam (Altıncı Session)

```
CLAUDE.md ve docs/ klasörünü oku.

HEDEF: Kalabalık ortamda birden fazla konuşmacıyı ayırt etmek.

İmplementasyon:
- pyannote.audio ile speaker diarization
- Her konuşmacıya speaker_id ata
- Farklı konuşmacıların farklı dillerde konuşabileceğini destekle
- Speaker embedding cache (aynı kişi tekrar konuşunca tanı)
- Frontend'de konuşmacı bazlı çeviri gösterimi (renk kodlu)

Bu en zor kısım — iteratif geliştir:
1. Önce 2 konuşmacı ile test et
2. Sonra 3-5 konuşmacıya çıkar
3. Gürültülü ortam testleri ekle
```

---

## NOTLAR

- Her session başında Claude Code'a "CLAUDE.md oku" de
- Her session sonunda `git add -A && git commit` yap
- Plan dosyaları docs/plans/ altında birikecek
- Sorun çıkarsa Claude Chat'e (buraya) gel, birlikte debug ederiz
- Azure API key'leri almadan Prompt 4-5'e geçme
