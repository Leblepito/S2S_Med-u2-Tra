import pytest
import httpx
import websockets

S2S_WS_URL = "ws://localhost:8000/ws/device/test-device"

@pytest.mark.asyncio
async def test_s2s_ws_device_auth_required():
    """S2S WebSocket device connection should require a valid JWT token."""
    try:
        async with websockets.connect(S2S_WS_URL) as websocket:
            pytest.fail("WebSocket connected without JWT token")
    except websockets.exceptions.InvalidStatusCode as e:
        assert e.status_code in [4003, 4403, 403, 401]
