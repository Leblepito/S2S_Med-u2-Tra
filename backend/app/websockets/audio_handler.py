"""WebSocket audio stream handler — /ws/translate endpoint."""

import json
import logging
import time

from fastapi import WebSocket, WebSocketDisconnect

from app.audio.capture import validate_chunk
from app.config import get_settings
from app.exceptions import AudioFormatError, WebSocketError
from app.pipeline.orchestrator import PipelineOrchestrator
from app.schemas import (
    ConfigMessage,
    ErrorResponse,
    TTSHeader,
    parse_client_message,
    serialize_server_message,
)
from app.websockets.connection_manager import ConnectionManager
from app.websockets.protocol import classify_frame, pack_tts_frame

logger = logging.getLogger(__name__)

manager = ConnectionManager()

# Global session metrics
_total_sessions: int = 0


def get_metrics() -> dict:
    """Global WebSocket metrikleri döndür."""
    return {
        "active_connections": manager.active_count,
        "total_sessions": _total_sessions,
    }


async def websocket_translate(ws: WebSocket) -> None:
    """WebSocket audio translation endpoint."""
    global _total_sessions
    await ws.accept()
    session_start = time.perf_counter()
    chunk_count = 0
    transcript_count = 0
    _total_sessions += 1

    try:
        config = await _receive_config(ws)
        if config is None:
            return
        manager.connect(ws, config)
        settings = get_settings()
        pipeline = PipelineOrchestrator(
            use_mocks=settings.USE_MOCKS,
            target_langs=config.target_langs,
            config_source_lang=config.source_lang,
            azure_key=settings.AZURE_TRANSLATOR_KEY,
            azure_region=settings.AZURE_TRANSLATOR_REGION,
            azure_speech_key=settings.AZURE_SPEECH_KEY,
            azure_speech_region=settings.AZURE_SPEECH_REGION,
            enable_diarization=config.enable_diarization,
            glossary_mode=settings.GLOSSARY_MODE,
        )
        chunk_count, transcript_count = await _pipeline_loop(ws, pipeline)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(ws)
        duration_s = (time.perf_counter() - session_start)
        logger.info(json.dumps({
            "event": "session_end",
            "duration_s": round(duration_s, 2),
            "chunks": chunk_count,
            "transcripts": transcript_count,
            "active": manager.active_count,
        }))


async def _receive_config(ws: WebSocket) -> ConfigMessage | None:
    """İlk mesajı config olarak al."""
    try:
        text = await ws.receive_text()
    except WebSocketDisconnect:
        return None
    except Exception:
        error = ErrorResponse(
            message="İlk mesaj config olmalı", code="CONFIG_REQUIRED"
        )
        await ws.send_text(serialize_server_message(error))
        await ws.close()
        return None
    try:
        return parse_client_message(text)
    except (ValueError, Exception) as e:
        error = ErrorResponse(message=str(e), code="INVALID_CONFIG")
        await ws.send_text(serialize_server_message(error))
        await ws.close()
        return None


async def _pipeline_loop(
    ws: WebSocket, pipeline: PipelineOrchestrator
) -> tuple[int, int]:
    """Audio pipeline loop. Returns (chunk_count, transcript_count)."""
    chunk_count = 0
    transcript_count = 0

    while True:
        msg = await ws.receive()
        if msg["type"] == "websocket.disconnect":
            break
        if "bytes" in msg and msg["bytes"]:
            chunk_count += 1
            tc = await _handle_audio(ws, pipeline, msg["bytes"])
            transcript_count += tc
        elif "text" in msg and msg["text"]:
            await _handle_text(ws, msg["text"])

    return chunk_count, transcript_count


async def _handle_audio(
    ws: WebSocket, pipeline: PipelineOrchestrator, data: bytes
) -> int:
    """Audio chunk → pipeline → mesajlar gönder. Returns transcript count."""
    try:
        validate_chunk(data)
        messages, tts_results = await pipeline.process_chunk(data)
        for message in messages:
            await ws.send_text(serialize_server_message(message))
        for tts in tts_results:
            header = TTSHeader(lang=tts.lang, chunk_index=0)
            frame = pack_tts_frame(header, tts.audio)
            await ws.send_bytes(frame)
        return len([m for m in messages if hasattr(m, "text")])
    except AudioFormatError as e:
        logger.warning(f"[AUDIO] {e}")
        return 0


async def _handle_text(ws: WebSocket, text: str) -> None:
    """JSON mesajını sınıflandır, hata varsa error gönder."""
    try:
        classify_frame(text)
    except WebSocketError as e:
        error = ErrorResponse(message=str(e), code="INVALID_JSON")
        await ws.send_text(serialize_server_message(error))
