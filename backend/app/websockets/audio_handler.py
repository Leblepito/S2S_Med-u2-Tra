"""WebSocket audio stream handler — /ws/translate endpoint."""

import logging

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from app.audio.capture import AudioBuffer, validate_chunk
from app.exceptions import AudioFormatError, WebSocketError
from app.schemas import (
    ConfigMessage,
    ErrorResponse,
    parse_client_message,
    serialize_server_message,
)
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
        buffer = AudioBuffer()
        await _audio_loop(ws, buffer)
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


async def _audio_loop(ws: WebSocket, buffer: AudioBuffer) -> None:
    """Audio chunk'ları al, buffer'a ekle, JSON mesajları işle."""
    while True:
        msg = await ws.receive()
        if msg["type"] == "websocket.disconnect":
            break
        if "bytes" in msg and msg["bytes"]:
            try:
                validate_chunk(msg["bytes"])
                buffer.add_chunk(msg["bytes"])
            except AudioFormatError as e:
                logger.warning(f"[AUDIO] {e}")
        elif "text" in msg and msg["text"]:
            try:
                classify_frame(msg["text"])
            except WebSocketError as e:
                error = ErrorResponse(message=str(e), code="INVALID_JSON")
                await ws.send_text(serialize_server_message(error))
