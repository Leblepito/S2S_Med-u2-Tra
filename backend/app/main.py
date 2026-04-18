"""BabelFlow — FastAPI application."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.admin.routes import router as admin_router
from app.routers.widget import router as widget_router
from app.config import get_settings
from app.constants import SUPPORTED_LANGS
from app.database.connection import create_tables, get_session_factory
from app.glossary.seed import seed_glossary_data
from app.middleware import CORSPreflightCacheMiddleware, RateLimitMiddleware, RequestLoggingMiddleware
from app.rate_limit_backend import make_backend
from app.websockets.audio_handler import get_metrics, websocket_translate
from app.websockets.device_handler import device_websocket_handler

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
    logger.info(f"  Database: {settings.DATABASE_URL}")
    logger.info("=" * 50)
    await create_tables()
    try:
        factory = get_session_factory()
        async with factory() as db:
            await seed_glossary_data(db)
    except Exception as e:
        logger.warning(f"[SEED] Glossary seed failed: {e}")
    yield


app = FastAPI(title="BabelFlow", version="0.1.0", lifespan=lifespan)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    max_requests_per_minute=120,
    backend=make_backend(settings.RATE_LIMIT_BACKEND, redis_url=settings.REDIS_URL),
)
app.add_middleware(CORSPreflightCacheMiddleware)
_WIDGET_CORS_ORIGINS = [
    "https://leblepito.com",
    "https://www.leblepito.com",
    "http://localhost:3333",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.validated_cors_origins(_WIDGET_CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
)

from app.auth import create_access_token
@app.get("/api/auth/token")
async def get_test_token():
    """Generate a test token (temporary for development)."""
    return {"token": create_access_token({"sub": "test-user", "role": "admin"})}

app.include_router(admin_router)
app.include_router(widget_router)
app.websocket("/ws/translate")(websocket_translate)
app.add_api_websocket_route("/ws/device/{device_id}", device_websocket_handler)

_WIDGET_DIR = Path(__file__).parent / "static" / "widget"
_WIDGET_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/widget", StaticFiles(directory=str(_WIDGET_DIR)), name="widget")


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
