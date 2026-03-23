"""BabelFlow — FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.constants import SUPPORTED_LANGS
from app.websockets.audio_handler import websocket_translate

app = FastAPI(title="BabelFlow", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.websocket("/ws/translate")(websocket_translate)


@app.get("/health")
async def health() -> dict:
    """Service health check."""
    return {"status": "ok", "service": "babelflow"}


@app.get("/api/config")
async def config_summary() -> dict:
    """Aktif config özeti."""
    settings = get_settings()
    return {
        "mock_mode": settings.USE_MOCKS,
        "glossary_mode": settings.GLOSSARY_MODE,
        "whisper_model": settings.WHISPER_MODEL_SIZE,
        "whisper_device": settings.WHISPER_DEVICE,
        "supported_langs": sorted(SUPPORTED_LANGS),
        "azure_translator_configured": bool(settings.AZURE_TRANSLATOR_KEY),
        "azure_speech_configured": bool(settings.AZURE_SPEECH_KEY),
    }


@app.get("/api/pipeline/status")
async def pipeline_status() -> dict:
    """Pipeline health — her stage'in durumu."""
    settings = get_settings()
    stages = {
        "vad": "mock" if settings.USE_MOCKS else "silero",
        "asr": "mock" if settings.USE_MOCKS else f"whisper-{settings.WHISPER_MODEL_SIZE}",
        "translation": "mock" if settings.USE_MOCKS else "azure",
        "tts": "mock" if settings.USE_MOCKS else "azure",
        "glossary": settings.GLOSSARY_MODE,
        "diarization": "mock" if settings.USE_MOCKS else "pyannote",
    }
    return {"status": "ok", "stages": stages}


@app.get("/api/latency")
async def latency() -> dict:
    """Pipeline latency istatistikleri."""
    return {"stats": {}, "note": "Per-connection stats via WebSocket"}
