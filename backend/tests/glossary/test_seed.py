"""Glossary seed data testleri."""

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.database.models import Base, GlossaryDomain, GlossaryTerm, GlossaryTranslation
from app.glossary.seed import seed_glossary_data


@pytest_asyncio.fixture
async def db() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


class TestSeedGlossary:
    """Glossary seed testleri."""

    @pytest.mark.asyncio
    async def test_seed_creates_domains(self, db: AsyncSession) -> None:
        """2 domain oluşturulmalı."""
        await seed_glossary_data(db)
        result = await db.execute(select(GlossaryDomain))
        domains = list(result.scalars().all())
        assert len(domains) == 2
        names = {d.name for d in domains}
        assert "medical" in names
        assert "tourism" in names

    @pytest.mark.asyncio
    async def test_seed_medical_terms(self, db: AsyncSession) -> None:
        """20 medikal terim oluşturulmalı."""
        await seed_glossary_data(db)
        result = await db.execute(
            select(GlossaryDomain).where(GlossaryDomain.name == "medical")
        )
        domain = result.scalar_one()
        terms = await db.execute(
            select(GlossaryTerm).where(GlossaryTerm.domain_id == domain.id)
        )
        assert len(list(terms.scalars().all())) == 20

    @pytest.mark.asyncio
    async def test_seed_tourism_terms(self, db: AsyncSession) -> None:
        """15 turizm terimi oluşturulmalı."""
        await seed_glossary_data(db)
        result = await db.execute(
            select(GlossaryDomain).where(GlossaryDomain.name == "tourism")
        )
        domain = result.scalar_one()
        terms = await db.execute(
            select(GlossaryTerm).where(GlossaryTerm.domain_id == domain.id)
        )
        assert len(list(terms.scalars().all())) == 15

    @pytest.mark.asyncio
    async def test_seed_translations_7_langs(self, db: AsyncSession) -> None:
        """Her terim 7 dilde çeviri içermeli."""
        await seed_glossary_data(db)
        result = await db.execute(select(GlossaryTerm).limit(1))
        term = result.scalar_one()
        translations = await db.execute(
            select(GlossaryTranslation).where(
                GlossaryTranslation.term_id == term.id
            )
        )
        assert len(list(translations.scalars().all())) == 7

    @pytest.mark.asyncio
    async def test_seed_idempotent(self, db: AsyncSession) -> None:
        """İkinci çalıştırmada duplicate oluşmamalı."""
        await seed_glossary_data(db)
        await seed_glossary_data(db)  # tekrar
        result = await db.execute(select(GlossaryDomain))
        assert len(list(result.scalars().all())) == 2
