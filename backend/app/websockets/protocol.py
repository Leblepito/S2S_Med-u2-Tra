"""WebSocket frame sınıflandırma ve TTS binary protocol."""

import json
import struct
from typing import Any

from app.exceptions import WebSocketError
from app.schemas import TTSHeader


def classify_frame(data: bytes | str) -> tuple[str, Any]:
    """WebSocket frame'ini sınıflandır: audio binary veya JSON mesaj.

    Args:
        data: WebSocket'ten gelen raw frame.

    Returns:
        ("audio", bytes) veya ("json", dict).

    Raises:
        WebSocketError: String frame geçerli JSON değilse.
    """
    if isinstance(data, bytes):
        return "audio", data

    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        msg = f"Geçersiz JSON frame: {e}"
        raise WebSocketError(msg) from e
    return "json", parsed


def pack_tts_frame(header: TTSHeader, audio: bytes) -> bytes:
    """TTS audio frame'i binary formatına paketle.

    Format: [4-byte JSON length (LE)] + [JSON header] + [audio bytes]

    Args:
        header: TTS header metadata.
        audio: PCM16 audio bytes.

    Returns:
        Paketlenmiş binary frame.
    """
    json_bytes = header.model_dump_json().encode("utf-8")
    length_prefix = struct.pack("<I", len(json_bytes))
    return length_prefix + json_bytes + audio


def unpack_tts_frame(data: bytes) -> tuple[TTSHeader, bytes]:
    """Binary TTS frame'ini parse et.

    Args:
        data: Paketlenmiş binary frame.

    Returns:
        (TTSHeader, audio_bytes) tuple.

    Raises:
        WebSocketError: Frame formatı bozuksa.
    """
    if len(data) < 4:
        msg = f"TTS frame çok kısa: {len(data)} bytes"
        raise WebSocketError(msg)

    json_len = struct.unpack("<I", data[:4])[0]
    json_end = 4 + json_len

    if len(data) < json_end:
        msg = f"TTS frame eksik: beklenen {json_end}, gelen {len(data)}"
        raise WebSocketError(msg)

    try:
        header_dict = json.loads(data[4:json_end])
        header = TTSHeader(**header_dict)
    except (json.JSONDecodeError, Exception) as e:
        msg = f"TTS header parse hatası: {e}"
        raise WebSocketError(msg) from e

    return header, data[json_end:]
