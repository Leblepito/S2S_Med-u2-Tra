"""Health endpoint testi."""


class TestHealth:
    """Health endpoint testleri."""

    def test_health_returns_ok(self, client) -> None:
        """GET /health 200 ve doğru JSON dönmeli."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "babelflow"
