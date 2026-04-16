"""API endpoint testleri."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestAPIEndpoints:
    """REST API endpoint testleri."""

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(app)

    def test_health(self, client: TestClient) -> None:
        """GET /health → 200."""
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_config_summary(self, client: TestClient) -> None:
        """GET /api/config → mock mode bilgisi."""
        resp = client.get("/api/config")
        assert resp.status_code == 200
        data = resp.json()
        assert data["mock_mode"] is True
        assert "supported_langs" in data
        assert len(data["supported_langs"]) == 7

    def test_pipeline_status(self, client: TestClient) -> None:
        """GET /api/pipeline/status → stage listesi."""
        resp = client.get("/api/pipeline/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        stages = data["stages"]
        assert "vad" in stages
        assert "asr" in stages
        assert "translation" in stages
        assert "tts" in stages
        assert "glossary" in stages
        assert "diarization" in stages

    def test_latency(self, client: TestClient) -> None:
        """GET /api/latency → stats dict."""
        resp = client.get("/api/latency")
        assert resp.status_code == 200
        assert "stats" in resp.json()
