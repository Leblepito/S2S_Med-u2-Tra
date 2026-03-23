"""WebSocket audio stream handler — /ws/translate endpoint."""

import logging

from fastapi import WebSocket, WebSocketDisconnect

from app.audio.capture import validate_chunk
from app.config import get_settings
from app.exceptions import AudioFormatError, WebSocketError
from app.schemas import (
    ConfigMessage,
    ErrorResponse,
    parse_client_message,
    serialize_server_message,
)
from app.transcription.streaming import StreamingTranscriber
from app.websockets.connection_manager import ConnectionManager
from app.websockets.protocol import classify_frame

logger = logging.getLogger(__name__)

manager = ConnectionManager()


async def websocket_translate(ws: WebSocket) -> None:
    """WebSocket audio translation endpoint.

    Flow: accept → config bekle → audio loop → cleanup.
    """
    await ws.accept()
    try:
        config = await _receive_config(ws)
        if config is None:
            return
        manager.connect(ws, config)
        settings = get_settings()
        transcriber = StreamingTranscriber(use_mocks=settings.USE_MOCKS)
        await _audio_loop(ws, transcriber)
    except WebSocketDisconnect:
        logger.info("[WS] Client disconnected")
    finally:
        manager.disconnect(ws)


async def _receive_config(ws: WebSocket) -> ConfigMessage | None:
    """İlk mesajı config olarak al. Değilse error gönder."""
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


async def _audio_loop(
    ws: WebSocket, transcriber: StreamingTranscriber
) -> None:
    """Audio chunk'ları al, VAD+Whisper ile işle, sonuç gönder."""
    while True:
        msg = await ws.receive()
        if msg["type"] == "websocket.disconnect":
            break
        if "bytes" in msg and msg["bytes"]:
            await _handle_audio(ws, transcriber, msg["bytes"])
        elif "text" in msg and msg["text"]:
            await _handle_text(ws, msg["text"])


async def _handle_audio(
    ws: WebSocket, transcriber: StreamingTranscriber, data: bytes
) -> None:
    """Audio chunk'ı işle, transcript varsa gönder."""
    try:
        validate_chunk(data)
        transcript = transcriber.process_chunk(data)
        if transcript is not None:
            await ws.send_text(serialize_server_message(transcript))
    except AudioFormatError as e:
        logger.warning(f"[AUDIO] {e}")


async def _handle_text(ws: WebSocket, text: str) -> None:
    """JSON mesajını sınıflandır, hata varsa error gönder."""
    try:
        classify_frame(text)
    except WebSocketError as e:
        error = ErrorResponse(message=str(e), code="INVALID_JSON")
        await ws.send_text(serialize_server_message(error))
