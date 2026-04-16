# Latency Budget

Hedef: Toplam pipeline <2 saniye

| Aşama | Hedef | Max | Teknik |
|-------|-------|-----|--------|
| Audio Capture + VAD | 100ms | 200ms | Silero VAD, 30ms chunks |
| Streaming ASR | 200ms | 500ms | Faster Whisper large-v3, streaming |
| Translation | 100ms | 300ms | Azure Translator, batch |
| TTS | 100ms | 200ms | Azure TTS, streaming |
| Network | 50ms | 100ms | WebSocket, binary protocol |
| **Toplam** | **550ms** | **1300ms** | |
