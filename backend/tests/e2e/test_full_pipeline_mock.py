"""Full pipeline E2E testi — mock modda tüm stage'ler."""

import json
import math
import struct

import pytest
from fastapi.testclient import TestClient

from app.constants import CHUNK_BYTES
from app.main import app
from app.websockets.protocol import unpack_tts_frame


def _sine_chunk(freq: int = 440) -> bytes:
    """30ms sine dalga chunk (PCM16, 16kHz)."""
    samples = [
        int(math.sin(2 * math.pi * freq * i / 16000) * 16000)
        for i in range(480)
    ]
    return struct.pack(f"<{len(samples)}h", *samples)


class TestFullPipelineMock:
    """Full E2E pipeline testi — mock mode."""

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(app)

    def test_full_flow_transcript_translation_tts(
        self, client: TestClient, valid_token: str
    ) -> None:
        """Audio → transcript → translation → TTS binary frame."""
        with client.websocket_connect(f"/ws/translate?token={valid_token}") as ws:
            ws.send_json({
                "type": "config",
                "source_lang": "auto",
                "target_langs": ["en"],
            })

            # 10 chunk konuşma
            for _ in range(10):
                ws.send_bytes(_sine_chunk())
            # 12 chunk sessizlik → pipeline tetiklenir
            for _ in range(12):
                ws.send_bytes(bytes(CHUNK_BYTES))

            # 1. partial_transcript JSON
            transcript = ws.receive_json()
            assert transcript["type"] == "partial_transcript"
            assert transcript["lang"] in {"tr", "ru", "en", "th", "vi", "zh", "id"}

            if transcript["text"]:
                # 2. translation JSON
                translation = ws.receive_json()
                assert translation["type"] == "translation"
                assert "en" in translation["translations"]
                assert translation["speaker_id"] >= 0

                # 3. TTS binary frame
                tts_frame = ws.receive_bytes()
                assert len(tts_frame) > 4
                header, audio = unpack_tts_frame(tts_frame)
                assert header.type == "tts_audio"
                assert header.lang == "en"
                assert len(audio) > 0

    def test_diarization_enabled(self, client: TestClient, valid_token: str) -> None:
        """Diarization açık → speaker_id atanıyor."""
        with client.websocket_connect(f"/ws/translate?token={valid_token}") as ws:
            ws.send_json({
                "type": "config",
                "source_lang": "auto",
                "target_langs": ["en"],
                "enable_diarization": True,
            })

            for _ in range(10):
                ws.send_bytes(_sine_chunk())
            for _ in range(12):
                ws.send_bytes(bytes(CHUNK_BYTES))

            transcript = ws.receive_json()
            assert transcript["speaker_id"] >= 0

    def test_multiple_target_langs(self, client: TestClient, valid_token: str) -> None:
        """Birden fazla hedef dil → her biri için TTS frame."""
        with client.websocket_connect(f"/ws/translate?token={valid_token}") as ws:
            ws.send_json({
                "type": "config",
                "source_lang": "auto",
                "target_langs": ["en", "th"],
            })

            for _ in range(10):
                ws.send_bytes(_sine_chunk())
            for _ in range(12):
                ws.send_bytes(bytes(CHUNK_BYTES))

            transcript = ws.receive_json()
            assert transcript["type"] == "partial_transcript"

            if transcript["text"]:
                translation = ws.receive_json()
                assert "en" in translation["translations"]
                assert "th" in translation["translations"]

                # 2 TTS frame (en + th)
                frame1 = ws.receive_bytes()
                frame2 = ws.receive_bytes()
                h1, _ = unpack_tts_frame(frame1)
                h2, _ = unpack_tts_frame(frame2)
                langs = {h1.lang, h2.lang}
                assert "en" in langs
                assert "th" in langs
