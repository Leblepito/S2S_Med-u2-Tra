"""End-to-end entegrasyon testleri."""

import json
import math
import struct

import pytest
from fastapi.testclient import TestClient

from app.constants import CHUNK_BYTES
from app.main import app


class TestIntegration:
    """Full flow entegrasyon testleri."""

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(app)

    def _make_sine_chunk(self, freq: int = 440) -> bytes:
        """30ms sine dalga chunk üret (PCM16, 16kHz)."""
        samples = [
            int(math.sin(2 * math.pi * freq * i / 16000) * 16000)
            for i in range(480)
        ]
        return struct.pack(f"<{len(samples)}h", *samples)

    def test_health_endpoint(self, client: TestClient) -> None:
        """Health endpoint hâlâ çalışmalı."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_full_flow_connect_config_audio_disconnect(
        self, client: TestClient, valid_token: str
    ) -> None:
        """End-to-end: connect → config → 10 audio chunk → disconnect."""
        with client.websocket_connect(f"/ws/translate?token={valid_token}") as ws:
            # 1. Config gönder
            config = {
                "type": "config",
                "source_lang": "auto",
                "target_langs": ["en", "th", "ru"],
                "enable_diarization": True,
            }
            ws.send_json(config)

            # 2. 10 audio chunk gönder
            for _ in range(10):
                chunk = self._make_sine_chunk()
                ws.send_bytes(chunk)

            # 3. Disconnect (context manager çıkışı)

    def test_silence_chunks(self, client: TestClient, valid_token: str) -> None:
        """Sessizlik chunk'ları kabul edilmeli."""
        with client.websocket_connect(f"/ws/translate?token={valid_token}") as ws:
            config = {
                "type": "config",
                "source_lang": "tr",
                "target_langs": ["en"],
            }
            ws.send_json(config)

            # Sessizlik = sıfır byte'lar
            silence = bytes(CHUNK_BYTES)
            for _ in range(5):
                ws.send_bytes(silence)

    def test_mixed_audio_and_json(self, client: TestClient, valid_token: str) -> None:
        """Audio chunk'lar arası JSON mesajı gönderilebilmeli."""
        with client.websocket_connect(f"/ws/translate?token={valid_token}") as ws:
            config = {
                "type": "config",
                "source_lang": "auto",
                "target_langs": ["en"],
            }
            ws.send_json(config)

            ws.send_bytes(self._make_sine_chunk())
            ws.send_json({"type": "config", "target_langs": ["th"]})
            ws.send_bytes(self._make_sine_chunk())

    def test_speech_produces_transcript(self, client: TestClient, valid_token: str) -> None:
        """Yeterli konuşma + sessizlik → partial_transcript mesajı dönmeli."""
        with client.websocket_connect(f"/ws/translate?token={valid_token}") as ws:
            config = {
                "type": "config",
                "source_lang": "auto",
                "target_langs": ["en"],
            }
            ws.send_json(config)

            # 10 chunk konuşma (300ms > 250ms min)
            for _ in range(10):
                ws.send_bytes(self._make_sine_chunk())

            # 12 chunk sessizlik (360ms > 300ms min_silence)
            silence = bytes(CHUNK_BYTES)
            for _ in range(12):
                ws.send_bytes(silence)

            # Transcript mesajı gelmiş olmalı
            response = ws.receive_json()
            assert response["type"] == "partial_transcript"
            assert "text" in response
            assert "lang" in response

            # Translation mesajı da gelmeli (mock transcript text doluysa)
            if response["text"]:
                translation = ws.receive_json()
                assert translation["type"] == "translation"
                assert "translations" in translation

                # TTS binary frame(lar) gelmeli
                tts_frame = ws.receive_bytes()
                assert len(tts_frame) > 4  # min: 4-byte header len
