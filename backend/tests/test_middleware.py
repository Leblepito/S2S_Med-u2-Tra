"""Middleware testleri."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestMiddleware:
    """Middleware entegrasyon testleri."""

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(app)

    def test_x_response_time_header(self, client: TestClient) -> None:
        """Response X-Response-Time header içermeli."""
        resp = client.get("/health")
        assert "X-Response-Time" in resp.headers

    def test_rate_limit_remaining_header(self, client: TestClient) -> None:
        """Response X-RateLimit-Remaining header içermeli."""
        resp = client.get("/health")
        assert "X-RateLimit-Remaining" in resp.headers

    def test_rate_limit_not_hit_normal(self, client: TestClient) -> None:
        """Normal kullanımda 429 dönmemeli."""
        for _ in range(5):
            resp = client.get("/health")
            assert resp.status_code == 200
