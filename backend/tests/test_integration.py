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
        self, client: TestClient
    ) -> None:
        """End-to-end: connect → config → 10 audio chunk → disconnect."""
        with client.websocket_connect("/ws/translate") as ws:
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

    def test_silence_chunks(self, client: TestClient) -> None:
        """Sessizlik chunk'ları kabul edilmeli."""
        with client.websocket_connect("/ws/translate") as ws:
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

    def test_mixed_audio_and_json(self, client: TestClient) -> None:
        """Audio chunk'lar arası JSON mesajı gönderilebilmeli."""
        with client.websocket_connect("/ws/translate") as ws:
            config = {
                "type": "config",
                "source_lang": "auto",
                "target_langs": ["en"],
            }
            ws.send_json(config)

            ws.send_bytes(self._make_sine_chunk())
            ws.send_json({"type": "config", "target_langs": ["th"]})
            ws.send_bytes(self._make_sine_chunk())
