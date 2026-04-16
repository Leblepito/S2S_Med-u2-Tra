# BabelFlow Widget SDK — Design Spec

**Date:** 2026-03-24
**Terminal:** S2S (muhendis)
**Scope:** Chunk 1, Tasks 1-4 from integration plan

---

## Goal

Expose BabelFlow real-time translation as a framework-agnostic embeddable widget (`babelflow.js`) that any website can include via a single `<script>` tag. Primary consumer: leblepito.com (ThaiTurk medical tourism platform).

## Architecture

```
Host Page (leblepito.com)
  └─ <script src="https://s2s-backend/widget/babelflow.js">
       └─ BabelFlow.init({ apiUrl, ... })
            ├─ Injects <style> (scoped via .bf- prefix)
            ├─ Creates floating button (56px circle, #2563eb)
            ├─ On click → opens 360px translation panel
            ├─ WebSocket → wss://s2s-backend/ws/translate
            ├─ Mic → AudioContext 16kHz → PCM16 → WS binary
            └─ WS text messages → translation display + callbacks
```

## WebSocket Protocol Compatibility

The widget MUST match the backend's `ConfigMessage` schema exactly:

```json
{
  "type": "config",
  "source_lang": "auto",
  "target_langs": ["tr"],
  "enable_diarization": false
}
```

- `source_lang`: string, default `"auto"` — exposed as `BabelFlow.init({ sourceLang })` option
- `target_langs`: **list** of strings (not singular) — widget wraps single `targetLang` into array
- `enable_diarization`: boolean, default `false`

**Server message types the widget handles:**
- `partial_transcript` → show as live typing indicator in body
- `final_transcript` → show source text bubble
- `translation` → show translated text bubble, fire `onTranslation` callback
- `error` → show error status, fire `onError` callback
- Binary (TTS audio) → play via reusable AudioContext @ 24kHz

## Task Breakdown

### Task 1: Widget Static Serving Infrastructure
- Mount `/widget` as StaticFiles in FastAPI main.py
- Create `backend/app/static/widget/` directory
- Minimal `babelflow.js` placeholder (IIFE, `BabelFlow.init()` stub)
- Add CORS origins to `cors_origin_list`: `leblepito.com`, `www.leblepito.com`, `localhost:3333` (additive to existing `CORS_ORIGINS` env var)
- Test: `backend/tests/test_widget_serve.py`

### Task 2: Widget UI — Floating Button + Translation Panel
- Replace placeholder with full widget in `babelflow.js`
- IIFE pattern, vanilla JS, no framework dependency
- **UI Structure:**
  - Container: `position:fixed`, `z-index:99999`, `font-family:system-ui`
  - Floating button: 56px circle, `#2563eb`, globe icon, scale hover
  - Panel: 360px wide, 500px max-height, 16px border-radius, shadow
  - Header: `#2563eb` bg, white text, "BabelFlow Live Translation", close button
  - Language dropdowns: source (auto + 7 langs) + target (7 langs with flags)
  - Body: scrollable — partial transcripts (italic, gray), source text (gray bubble), translated text (blue bubble)
  - Mic bar: 48px mic button, pulse animation when recording (red `#ef4444`), status text
  - Mobile: 100% width on `<480px` screens via `@media` query
- **Audio:** `getUserMedia({ audio: true })` → `AudioContext({ sampleRate: 16000 })` for resampling → `ScriptProcessor` → PCM16 → WS binary
  - **Tech debt:** ScriptProcessor is deprecated. Future: inline AudioWorklet via Blob URL.
  - **Note:** `getUserMedia` sampleRate constraint is unreliable; `AudioContext({ sampleRate })` is the authoritative resampler.
- **Mic permission UX:**
  - First click: browser permission prompt, status = "Requesting mic access..."
  - Denied: status = "Mic access denied — check browser settings", mic button disabled with visual indicator
  - Revoked mid-session: stop recording, show error status, fire `onError`
- **WebSocket lifecycle:**
  - Connect on panel open, disconnect on panel close (cleanup resources)
  - Reconnect on unexpected close: exponential backoff (1s, 2s, 4s, 8s, 16s), max 5 retries, then `onError("connection_failed")`
  - On re-open panel: fresh connection
- **TTS Playback:** Reuse single `AudioContext({ sampleRate: 24000 })` for all TTS, decode PCM16, queue playback
- **Callbacks:** `onTranslation`, `onSessionStart`, `onSessionEnd`, `onError`
- **API:** `BabelFlow.init(config)`, `BabelFlow.toggle()`, `BabelFlow.destroy()` (teardown: stop recording, close WS, remove DOM)
- **Dark mode:** `.bf-panel.dark` class, toggled via `config.theme`
- Test: Manual browser test via `test.html`

### Task 3: Widget Config API
- Create `backend/app/routers/widget.py` with `GET /api/widget/config`
  - Note: using `routers/` directory (new pattern) per plan, not `admin/routes.py` pattern
- Returns: `supported_languages` (7 items), `default_language` ("en"), `version`, `features`
- Register router in `main.py`
- Test: `backend/tests/test_widget_api.py`

### Task 4: Device WebSocket Handler (ESP32 stub)
- Create `backend/app/websockets/device_handler.py`
- Endpoint: `/ws/device/{device_id}?token=xxx`
- Token auth: reject if missing (close 4003)
- Accept: process text (config, heartbeat) and binary (8kHz audio → upsample to 16kHz via numpy interpolation)
- In-memory device session tracking with `time.monotonic()` timestamps
- Heartbeat: respond with `heartbeat_ack`
- Register route in `main.py`
- Test: `backend/tests/test_device_ws.py` — use `starlette.testclient.TestClient.websocket_connect()` for proper WS testing

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Widget pattern | IIFE single file | No build step, framework-agnostic, simple embed |
| CSS scoping | `.bf-` prefix | Avoid host page conflicts |
| Audio capture | ScriptProcessor (tech debt: migrate to Blob AudioWorklet) | Simpler for single-file widget |
| Audio resampling | AudioContext sampleRate param | Reliable cross-browser resampling |
| TTS AudioContext | Single reused instance | Browsers limit concurrent AudioContexts (6-8) |
| Static serving | FastAPI StaticFiles mount | Co-located with backend, single deploy |
| CORS | Env var (additive) + hardcoded leblepito origins | Flexible for dev, locked for prod |
| WS lifecycle | Connect on open, disconnect on close | Clean resource management |
| Reconnection | Exponential backoff, max 5 retries | Prevent infinite reconnect loops |
| Device auth | Query param token | ESP32 can't set WS headers easily |
| Device audio | 8kHz → 16kHz upsample | ESP32 I2S DAC limitation |
| Device timestamps | time.monotonic() | Avoids deprecated asyncio.get_event_loop() |

## Files Created/Modified

| File | Action |
|------|--------|
| `backend/app/static/widget/babelflow.js` | Create |
| `backend/app/static/widget/test.html` | Create |
| `backend/app/routers/__init__.py` | Create |
| `backend/app/routers/widget.py` | Create |
| `backend/app/websockets/device_handler.py` | Create |
| `backend/app/main.py` | Modify (static mount, CORS, widget router, device WS route) |
| `backend/tests/test_widget_serve.py` | Create |
| `backend/tests/test_widget_api.py` | Create |
| `backend/tests/test_device_ws.py` | Create |

## CORS Origins (Final List)

Merged from `CORS_ORIGINS` env var + hardcoded widget origins:

```
{existing CORS_ORIGINS values}
https://leblepito.com
https://www.leblepito.com
http://localhost:3333
```

## URLs (for ThaiTurk terminal)

- **Dev:** `http://localhost:8000/widget/babelflow.js`
- **Prod:** `https://frontend-production-f105.up.railway.app/widget/babelflow.js`
- **Config API:** `GET /api/widget/config`
- **Device WS:** `ws://host/ws/device/{device_id}?token=xxx`
