"""WebSocket audio stream handler — /ws/translate endpoint."""

import logging

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
_tts_chunk_counter: dict[int, int] = {}


async def websocket_translate(ws: WebSocket) -> None:
    """WebSocket audio translation endpoint."""
    await ws.accept()
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
        )
        await _pipeline_loop(ws, pipeline)
    except WebSocketDisconnect:
        logger.info("[WS] Client disconnected")
    finally:
        manager.disconnect(ws)


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
) -> None:
    """Audio → VAD → ASR → Translation → TTS pipeline loop."""
    while True:
        msg = await ws.receive()
        if msg["type"] == "websocket.disconnect":
            break
        if "bytes" in msg and msg["bytes"]:
            await _handle_audio(ws, pipeline, msg["bytes"])
        elif "text" in msg and msg["text"]:
            await _handle_text(ws, msg["text"])


async def _handle_audio(
    ws: WebSocket, pipeline: PipelineOrchestrator, data: bytes
) -> None:
    """Audio chunk → pipeline → JSON + binary mesajlar gönder."""
    try:
        validate_chunk(data)
        messages, tts_results = await pipeline.process_chunk(data)
        for message in messages:
            await ws.send_text(serialize_server_message(message))
        for tts in tts_results:
            header = TTSHeader(lang=tts.lang, chunk_index=0)
            frame = pack_tts_frame(header, tts.audio)
            await ws.send_bytes(frame)
    except AudioFormatError as e:
        logger.warning(f"[AUDIO] {e}")


async def _handle_text(ws: WebSocket, text: str) -> None:
    """JSON mesajını sınıflandır, hata varsa error gönder."""
    try:
        classify_frame(text)
    except WebSocketError as e:
        error = ErrorResponse(message=str(e), code="INVALID_JSON")
        await ws.send_text(serialize_server_message(error))
