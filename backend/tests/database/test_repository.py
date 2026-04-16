"""Database repository CRUD testleri."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.database.models import Base
from app.database import repository as repo


@pytest_asyncio.fixture
async def db() -> AsyncSession:
    """In-memory SQLite test database."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


class TestSessionCRUD:
    """Session CRUD testleri."""

    @pytest.mark.asyncio
    async def test_create_session(self, db: AsyncSession) -> None:
        session = await repo.create_session(db, source_lang="tr", target_langs=["en"])
        assert session.id is not None
        assert session.source_lang == "tr"

    @pytest.mark.asyncio
    async def test_end_session(self, db: AsyncSession) -> None:
        session = await repo.create_session(db)
        await repo.end_session(db, session.id, duration_s=45.5)
        detail = await repo.get_session_detail(db, session.id)
        assert detail is not None
        assert detail.duration_s == 45.5

    @pytest.mark.asyncio
    async def test_get_sessions_pagination(self, db: AsyncSession) -> None:
        for _ in range(5):
            await repo.create_session(db)
        sessions = await repo.get_sessions(db, offset=0, limit=3)
        assert len(sessions) == 3

    @pytest.mark.asyncio
    async def test_delete_session(self, db: AsyncSession) -> None:
        session = await repo.create_session(db)
        deleted = await repo.delete_session(db, session.id)
        assert deleted is True

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, db: AsyncSession) -> None:
        deleted = await repo.delete_session(db, "nonexistent")
        assert deleted is False


class TestTranscriptCRUD:
    """Transcript CRUD testleri."""

    @pytest.mark.asyncio
    async def test_add_transcript(self, db: AsyncSession) -> None:
        session = await repo.create_session(db)
        transcript = await repo.add_transcript(
            db, session.id, speaker_id=0, text="Merhaba", lang="tr", confidence=0.9
        )
        assert transcript.id is not None
        assert transcript.text == "Merhaba"

    @pytest.mark.asyncio
    async def test_add_translation(self, db: AsyncSession) -> None:
        session = await repo.create_session(db)
        transcript = await repo.add_transcript(db, session.id, 0, "Hello", "en", 0.95)
        translation = await repo.add_translation(db, transcript.id, "tr", "Merhaba")
        assert translation.lang == "tr"

    @pytest.mark.asyncio
    async def test_session_detail_includes_transcripts(self, db: AsyncSession) -> None:
        session = await repo.create_session(db)
        transcript = await repo.add_transcript(db, session.id, 0, "Hello", "en", 0.9)
        await repo.add_translation(db, transcript.id, "tr", "Merhaba")
        detail = await repo.get_session_detail(db, session.id)
        assert len(detail.transcripts) == 1
        assert len(detail.transcripts[0].translations) == 1


class TestStats:
    """Stats testleri."""

    @pytest.mark.asyncio
    async def test_stats_empty(self, db: AsyncSession) -> None:
        stats = await repo.get_stats(db)
        assert stats["total_sessions"] == 0

    @pytest.mark.asyncio
    async def test_stats_with_data(self, db: AsyncSession) -> None:
        s = await repo.create_session(db)
        await repo.end_session(db, s.id, duration_s=30.0)
        await repo.add_transcript(db, s.id, 0, "test", "en", 0.9)
        stats = await repo.get_stats(db)
        assert stats["total_sessions"] == 1
        assert stats["total_transcripts"] == 1


class TestGlossary:
    """Glossary CRUD testleri."""

    @pytest.mark.asyncio
    async def test_create_domain(self, db: AsyncSession) -> None:
        domain = await repo.create_glossary_domain(db, "medical", "Medikal terimler")
        assert domain.name == "medical"

    @pytest.mark.asyncio
    async def test_create_term(self, db: AsyncSession) -> None:
        domain = await repo.create_glossary_domain(db, "travel")
        term = await repo.create_glossary_term(db, domain.id, "check-in", "hotel", "Otel giriş")
        assert term.canonical_term == "check-in"

    @pytest.mark.asyncio
    async def test_get_terms(self, db: AsyncSession) -> None:
        domain = await repo.create_glossary_domain(db, "medical")
        await repo.create_glossary_term(db, domain.id, "botox")
        await repo.create_glossary_term(db, domain.id, "rhinoplasty")
        terms = await repo.get_glossary_terms(db, domain.id)
        assert len(terms) == 2
