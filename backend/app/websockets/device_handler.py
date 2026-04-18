"""WebSocket handler optimized for ESP32-S3 devices.

Audio format: PCM16, 8kHz, mono (upsampled to 16kHz for Whisper).
"""

import json
import logging
import time
from typing import Any

import numpy as np
from fastapi import Query, WebSocket, WebSocketDisconnect
from app.auth import verify_token

logger = logging.getLogger(__name__)

# In-memory device sessions (production: Redis)
_device_sessions: dict[str, dict[str, Any]] = {}


def get_device_sessions() -> dict[str, dict[str, Any]]:
    """Return current device sessions for monitoring."""
    return dict(_device_sessions)


async def device_websocket_handler(
    websocket: WebSocket,
    device_id: str,
    token: str = Query(default=""),
) -> None:
    """WebSocket handler for ESP32-S3 devices.

    Accepts 8kHz mono PCM16 audio, upsamples to 16kHz for pipeline.
    Supports heartbeat ping/pong for WiFi connection tracking.
    """
    if not token:
        await websocket.close(code=4003, reason="Missing device token")
        return

    payload = verify_token(token)
    if not payload:
        await websocket.close(code=4003, reason="Invalid device token")
        return

    await websocket.accept()
    logger.info("[device:%s] Connected", device_id)

    _device_sessions[device_id] = {
        "connected_at": time.monotonic(),
        "last_seen": time.monotonic(),
        "translations": 0,
    }

    try:
        while True:
            data = await websocket.receive()

            if data.get("type") == "websocket.disconnect":
                break

            if "text" in data and data["text"]:
                msg = json.loads(data["text"])
                msg_type = msg.get("type", "")

                if msg_type == "config":
                    logger.info(
                        "[device:%s] Config: target=%s",
                        device_id,
                        msg.get("target_language"),
                    )
                elif msg_type == "heartbeat":
                    _device_sessions[device_id]["last_seen"] = time.monotonic()
                    await websocket.send_text(
                        json.dumps({"type": "heartbeat_ack"})
                    )

            elif "bytes" in data and data["bytes"]:
                audio_8khz = np.frombuffer(data["bytes"], dtype=np.int16)
                # Upsample 8kHz -> 16kHz (linear interpolation)
                audio_16khz = np.interp(
                    np.linspace(0, len(audio_8khz), len(audio_8khz) * 2),
                    np.arange(len(audio_8khz)),
                    audio_8khz.astype(np.float32),
                ).astype(np.int16)

                logger.debug(
                    "[device:%s] Audio: %d -> %d samples",
                    device_id,
                    len(audio_8khz),
                    len(audio_16khz),
                )
                # TODO: Feed audio_16khz to pipeline (reuse existing orchestrator)

    except WebSocketDisconnect:
        logger.info("[device:%s] Disconnected", device_id)
    finally:
        _device_sessions.pop(device_id, None)
