"""Tests for ESP32 device WebSocket handler."""

import json

import pytest
from starlette.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_device_ws_rejects_without_token():
    """Device WS should close with 4003 if no token provided."""
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/device/test-device-1"):
            pass


def test_device_ws_rejects_empty_token():
    """Device WS should close with 4003 if token is empty."""
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/device/test-device-1?token="):
            pass


def test_device_ws_accepts_with_token():
    """Device WS should accept connection when valid token provided."""
    with client.websocket_connect("/ws/device/test-device-1?token=test-secret") as ws:
        # Send config
        ws.send_text(json.dumps({
            "type": "config",
            "target_language": "tr",
        }))
        # Connection should stay open — close from client side
        ws.close()


def test_device_ws_heartbeat_ack():
    """Device WS should respond to heartbeat with heartbeat_ack."""
    with client.websocket_connect("/ws/device/test-device-2?token=abc123") as ws:
        ws.send_text(json.dumps({"type": "heartbeat"}))
        resp = ws.receive_text()
        data = json.loads(resp)
        assert data["type"] == "heartbeat_ack"
        ws.close()


def test_device_ws_accepts_binary_audio():
    """Device WS should accept 8kHz PCM16 binary audio without error."""
    import numpy as np

    with client.websocket_connect("/ws/device/test-device-3?token=xyz") as ws:
        # Send config first
        ws.send_text(json.dumps({
            "type": "config",
            "target_language": "en",
        }))
        # Send 8kHz audio chunk (240 samples = 30ms @ 8kHz)
        audio = np.zeros(240, dtype=np.int16)
        ws.send_bytes(audio.tobytes())
        ws.close()
