"""WebSocket audio handler testleri."""

import json

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestWebSocketAudioHandler:
    """WebSocket /ws/translate endpoint testleri."""

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(app)

    def test_connect_with_config(self, client: TestClient) -> None:
        """Config mesajıyla bağlantı kabul edilmeli."""
        with client.websocket_connect("/ws/translate") as ws:
            config = {
                "type": "config",
                "source_lang": "auto",
                "target_langs": ["en", "th"],
                "enable_diarization": False,
            }
            ws.send_json(config)
            # Bağlantı açık kalmalı, hata mesajı gelmemeli

    def test_config_required_first(self, client: TestClient) -> None:
        """İlk mesaj config olmalı, değilse error + close."""
        with client.websocket_connect("/ws/translate") as ws:
            ws.send_bytes(bytes(960))  # binary gönder, config değil
            response = ws.receive_json()
            assert response["type"] == "error"

    def test_invalid_config_rejected(self, client: TestClient) -> None:
        """Geçersiz config → error mesajı."""
        with client.websocket_connect("/ws/translate") as ws:
            ws.send_json({"type": "config", "target_langs": []})
            response = ws.receive_json()
            assert response["type"] == "error"

    def test_binary_after_config(self, client: TestClient) -> None:
        """Config sonrası binary chunk kabul edilmeli."""
        with client.websocket_connect("/ws/translate") as ws:
            config = {
                "type": "config",
                "source_lang": "auto",
                "target_langs": ["en"],
            }
            ws.send_json(config)
            ws.send_bytes(bytes(960))  # valid chunk — hata gelmemeli

    def test_invalid_json_after_config(self, client: TestClient) -> None:
        """Config sonrası geçersiz JSON → error mesajı (bağlantı kapanmaz)."""
        with client.websocket_connect("/ws/translate") as ws:
            config = {
                "type": "config",
                "source_lang": "auto",
                "target_langs": ["en"],
            }
            ws.send_json(config)
            ws.send_text("invalid json{{{")
            response = ws.receive_json()
            assert response["type"] == "error"
