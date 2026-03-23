"""WebSocket protocol layer testleri."""

import json
import struct

import pytest

from app.exceptions import WebSocketError
from app.schemas import TTSHeader
from app.websockets.protocol import (
    classify_frame,
    pack_tts_frame,
    unpack_tts_frame,
)


class TestClassifyFrame:
    """classify_frame fonksiyonu testleri."""

    def test_binary_frame(self) -> None:
        """Binary data → ('audio', raw_bytes) dönmeli."""
        raw = bytes(960)
        frame_type, data = classify_frame(raw)
        assert frame_type == "audio"
        assert data == raw

    def test_json_string_frame(self) -> None:
        """JSON string → ('json', parsed_dict) dönmeli."""
        payload = {"type": "config", "source_lang": "auto"}
        raw = json.dumps(payload)
        frame_type, data = classify_frame(raw)
        assert frame_type == "json"
        assert data == payload

    def test_invalid_json_string(self) -> None:
        """Geçersiz JSON string → WebSocketError."""
        with pytest.raises(WebSocketError, match="JSON"):
            classify_frame("not valid json{{{")

    def test_empty_binary(self) -> None:
        """Boş binary → ('audio', b'') dönmeli."""
        frame_type, data = classify_frame(b"")
        assert frame_type == "audio"
        assert data == b""


class TestPackTtsFrame:
    """pack_tts_frame fonksiyonu testleri."""

    def test_pack_format(self) -> None:
        """4-byte length prefix + JSON header + audio data."""
        header = TTSHeader(lang="en", chunk_index=0)
        audio = bytes(1024)
        packed = pack_tts_frame(header, audio)

        # İlk 4 byte: JSON header uzunluğu (little-endian)
        json_len = struct.unpack("<I", packed[:4])[0]
        json_bytes = packed[4 : 4 + json_len]
        audio_bytes = packed[4 + json_len :]

        parsed_header = json.loads(json_bytes)
        assert parsed_header["type"] == "tts_audio"
        assert parsed_header["lang"] == "en"
        assert parsed_header["chunk_index"] == 0
        assert audio_bytes == audio

    def test_length_prefix_correct(self) -> None:
        """Length prefix JSON header boyutuyla eşleşmeli."""
        header = TTSHeader(lang="th", chunk_index=5)
        audio = b"\x01\x02\x03"
        packed = pack_tts_frame(header, audio)

        json_len = struct.unpack("<I", packed[:4])[0]
        json_str = header.model_dump_json()
        assert json_len == len(json_str.encode("utf-8"))


class TestUnpackTtsFrame:
    """unpack_tts_frame fonksiyonu testleri."""

    def test_round_trip(self) -> None:
        """pack → unpack round-trip doğru çalışmalı."""
        original_header = TTSHeader(lang="tr", chunk_index=3)
        original_audio = bytes(range(256)) * 4  # 1024 bytes
        packed = pack_tts_frame(original_header, original_audio)

        header, audio = unpack_tts_frame(packed)
        assert header.type == "tts_audio"
        assert header.lang == "tr"
        assert header.chunk_index == 3
        assert audio == original_audio

    def test_truncated_data(self) -> None:
        """Kısa data → WebSocketError."""
        with pytest.raises(WebSocketError):
            unpack_tts_frame(b"\x00\x01")  # 4 byte'dan kısa

    def test_invalid_json_header(self) -> None:
        """Bozuk JSON header → WebSocketError."""
        bad_json = b"not json"
        length_prefix = struct.pack("<I", len(bad_json))
        with pytest.raises(WebSocketError):
            unpack_tts_frame(length_prefix + bad_json)
