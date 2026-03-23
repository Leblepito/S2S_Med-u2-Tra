"""BabelFlow — FastAPI application."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.constants import SUPPORTED_LANGS
from app.middleware import CORSPreflightCacheMiddleware, RateLimitMiddleware, RequestLoggingMiddleware
from app.websockets.audio_handler import get_metrics, websocket_translate

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Uygulama yaşam döngüsü — startup log."""
    logger.info("=" * 50)
    logger.info("BabelFlow starting...")
    logger.info(f"  USE_MOCKS: {settings.USE_MOCKS}")
    logger.info(f"  GLOSSARY_MODE: {settings.GLOSSARY_MODE}")
    logger.info(f"  WHISPER: {settings.WHISPER_MODEL_SIZE} ({settings.WHISPER_DEVICE})")
    logger.info(f"  CORS: {settings.cors_origin_list}")
    logger.info(f"  Azure Translator: {'configured' if settings.AZURE_TRANSLATOR_KEY else 'not set'}")
    logger.info(f"  Azure Speech: {'configured' if settings.AZURE_SPEECH_KEY else 'not set'}")
    logger.info("=" * 50)
    yield


app = FastAPI(title="BabelFlow", version="0.1.0", lifespan=lifespan)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests_per_minute=120)
app.add_middleware(CORSPreflightCacheMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
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
    return {
        "mock_mode": settings.USE_MOCKS,
        "glossary_mode": settings.GLOSSARY_MODE,
        "whisper_model": settings.WHISPER_MODEL_SIZE,
        "whisper_device": settings.WHISPER_DEVICE,
        "supported_langs": sorted(SUPPORTED_LANGS),
        "cors_origins": settings.cors_origin_list,
        "azure_translator_configured": bool(settings.AZURE_TRANSLATOR_KEY),
        "azure_speech_configured": bool(settings.AZURE_SPEECH_KEY),
    }


@app.get("/api/pipeline/status")
async def pipeline_status() -> dict:
    """Pipeline health — her stage'in durumu."""
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


@app.get("/api/metrics")
async def metrics() -> dict:
    """WebSocket session metrikleri."""
    return get_metrics()
