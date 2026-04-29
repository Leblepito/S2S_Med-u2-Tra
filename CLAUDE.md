# BabelFlow — Real-Time Multi-Language Translator

## Proje Özeti
Kalabalık ortamlarda bile çoklu konuşmacıyı ayırt edip anlık çeviri yapan sistem.
7 dil: Türkçe, Rusça, İngilizce, Tayca, Vietnamca, Çince (Mandarin), Endonezyaca.

## Tech Stack
- **Frontend:** React 19 + TypeScript + Vite + Tailwind CSS 4 → **Vercel Static Deploy**
- **Backend:** Python 3.12 + FastAPI + WebSockets → **Vercel Python Serverless** (api/ routes)
- **ASR:** Faster Whisper (CTranslate2)
- **Translation:** Azure Translator (7 dil)
- **TTS:** Azure Cognitive Services
- **Audio:** WebRTC, Web Audio API, VAD (Silero)
- **Database:** Supabase PostgreSQL (sessions, history)
- **Deploy: Vercel (frontend + API) + Supabase — NO Railway, NO Docker in prod**

## Deploy Architecture
```
frontend/        → Vercel Static (npm run build → dist/)
backend/api/     → Vercel Python serverless (/api/*.py)
backend/ws/      → Vercel Edge Functions (WebSocket via Supabase Realtime)
database/        → Supabase PostgreSQL
```

## Environment Variables
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
AZURE_TRANSLATOR_KEY=
AZURE_TRANSLATOR_REGION=southeastasia
AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=southeastasia
VITE_API_URL=https://your-app.vercel.app
```

## vercel.json (root)
Frontend build + Python API routes birlikte deploy edilir.

## Git Flow
- Branch: `feat/<feature>` | `fix/<bug>`
- Commit: `feat(frontend): add language selector`
- PR → main
