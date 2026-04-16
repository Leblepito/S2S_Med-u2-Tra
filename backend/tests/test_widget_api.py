"""Tests for widget config API."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_widget_config_returns_defaults():
    """GET /api/widget/config should return supported languages and defaults."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/widget/config")
        assert resp.status_code == 200
        data = resp.json()
        assert "supported_languages" in data
        assert len(data["supported_languages"]) == 7
        assert data["default_language"] == "en"
        assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_widget_config_has_features():
    """Config should include feature flags."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/widget/config")
        data = resp.json()
        assert "features" in data
        assert data["features"]["voice_translation"] is True
        assert data["features"]["text_display"] is True
        assert data["features"]["audio_playback"] is True


@pytest.mark.asyncio
async def test_widget_config_languages_have_required_fields():
    """Each language should have code, name, and flag."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/widget/config")
        data = resp.json()
        for lang in data["supported_languages"]:
            assert "code" in lang
            assert "name" in lang
            assert "flag" in lang


@pytest.mark.asyncio
async def test_widget_config_cors_allows_leblepito():
    """Config endpoint should allow leblepito.com CORS."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/widget/config",
            headers={"Origin": "https://leblepito.com"},
        )
        assert resp.status_code == 200
