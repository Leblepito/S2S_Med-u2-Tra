"""Admin API endpoint testleri."""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.database.connection import get_db
from app.database.models import Base
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def _override_db():
    """In-memory test DB — admin route'lar için override."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def _get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()
    await engine.dispose()


class TestAdminRoutes:
    """Admin API testleri."""

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(app)

    def test_list_sessions(self, client: TestClient) -> None:
        """GET /api/admin/sessions → 200."""
        resp = client.get("/api/admin/sessions")
        assert resp.status_code == 200
        assert "sessions" in resp.json()

    def test_get_stats(self, client: TestClient) -> None:
        """GET /api/admin/stats → stats dict."""
        resp = client.get("/api/admin/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_sessions" in data

    def test_list_glossary_domains(self, client: TestClient) -> None:
        """GET /api/admin/glossary/domains → 200."""
        resp = client.get("/api/admin/glossary/domains")
        assert resp.status_code == 200
        assert "domains" in resp.json()

    def test_create_glossary_domain(self, client: TestClient) -> None:
        """POST /api/admin/glossary/domains → domain oluşur."""
        resp = client.post(
            "/api/admin/glossary/domains",
            json={"name": "test_medical", "description": "Test domain"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "test_medical"
        assert "id" in data
