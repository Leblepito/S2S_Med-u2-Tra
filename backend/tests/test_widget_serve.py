"""Tests for widget static file serving."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_widget_js_endpoint_returns_javascript():
    """GET /widget/babelflow.js should return JS with BabelFlow global."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/widget/babelflow.js")
        assert resp.status_code == 200
        assert "javascript" in resp.headers.get("content-type", "")
        assert "BabelFlow" in resp.text


@pytest.mark.asyncio
async def test_widget_js_contains_init_method():
    """babelflow.js must expose BabelFlow.init function."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/widget/babelflow.js")
        assert resp.status_code == 200
        assert "init" in resp.text


@pytest.mark.asyncio
async def test_widget_cors_allows_leblepito():
    """CORS should allow leblepito.com origin."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/widget/babelflow.js",
            headers={"Origin": "https://leblepito.com"},
        )
        assert resp.status_code == 200
        allow_origin = resp.headers.get("access-control-allow-origin", "")
        assert "leblepito.com" in allow_origin
