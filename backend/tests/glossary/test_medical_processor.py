"""Medical/Tourism PreProcessor + PostProcessor testleri."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.database.models import Base
from app.glossary.factory import create_post_processor, create_pre_processor
from app.glossary.medical import DomainPreProcessor, MedicalPreProcessor, TourismPreProcessor
from app.glossary.post_processor import MedicalPostProcessor
from app.glossary.seed import seed_glossary_data
from app.schemas import PartialTranscript, TranslationResult


@pytest_asyncio.fixture
async def db() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        await seed_glossary_data(session)
        yield session
    await engine.dispose()


class TestMedicalPreProcessor:
    """MedicalPreProcessor testleri."""

    @pytest.mark.asyncio
    async def test_detect_botox(self, db: AsyncSession) -> None:
        """'botox' kelimesi tespit edilmeli."""
        pre = MedicalPreProcessor()
        await pre.load_terms(db)
        transcript = PartialTranscript(
            text="I want botox injection", lang="en", speaker_id=0, confidence=0.9
        )
        result = await pre.process(transcript)
        assert "botox" in result.detected_terms

    @pytest.mark.asyncio
    async def test_detect_turkish_term(self, db: AsyncSession) -> None:
        """Türkçe terim (burun estetiği) tespit edilmeli."""
        pre = MedicalPreProcessor()
        await pre.load_terms(db)
        transcript = PartialTranscript(
            text="Burun estetiği yaptırmak istiyorum", lang="tr", speaker_id=0, confidence=0.9
        )
        result = await pre.process(transcript)
        assert "rhinoplasty" in result.detected_terms

    @pytest.mark.asyncio
    async def test_no_detection_in_unrelated(self, db: AsyncSession) -> None:
        """İlgisiz metinde terim tespit edilmemeli."""
        pre = MedicalPreProcessor()
        await pre.load_terms(db)
        transcript = PartialTranscript(
            text="What is the weather today", lang="en", speaker_id=0, confidence=0.9
        )
        result = await pre.process(transcript)
        assert result.detected_terms == []

    @pytest.mark.asyncio
    async def test_case_insensitive(self, db: AsyncSession) -> None:
        """Büyük/küçük harf duyarsız arama."""
        pre = MedicalPreProcessor()
        await pre.load_terms(db)
        transcript = PartialTranscript(
            text="BOTOX please", lang="en", speaker_id=0, confidence=0.9
        )
        result = await pre.process(transcript)
        assert "botox" in result.detected_terms

    @pytest.mark.asyncio
    async def test_multiple_terms(self, db: AsyncSession) -> None:
        """Birden fazla terim tespit edilmeli."""
        pre = MedicalPreProcessor()
        await pre.load_terms(db)
        transcript = PartialTranscript(
            text="I have pain and swelling after botox", lang="en", speaker_id=0, confidence=0.9
        )
        result = await pre.process(transcript)
        assert "botox" in result.detected_terms
        assert "pain" in result.detected_terms
        assert "swelling" in result.detected_terms


class TestTourismPreProcessor:
    """TourismPreProcessor testleri."""

    @pytest.mark.asyncio
    async def test_detect_checkin(self, db: AsyncSession) -> None:
        """'check-in' tespit edilmeli."""
        pre = TourismPreProcessor()
        await pre.load_terms(db)
        transcript = PartialTranscript(
            text="I want to check-in please", lang="en", speaker_id=0, confidence=0.9
        )
        result = await pre.process(transcript)
        assert "check-in" in result.detected_terms

    @pytest.mark.asyncio
    async def test_detect_turkish_tourism(self, db: AsyncSession) -> None:
        """Türkçe turizm terimi tespit edilmeli."""
        pre = TourismPreProcessor()
        await pre.load_terms(db)
        transcript = PartialTranscript(
            text="Hesap lütfen", lang="tr", speaker_id=0, confidence=0.9
        )
        result = await pre.process(transcript)
        assert "bill" in result.detected_terms


class TestPostProcessor:
    """GlossaryPostProcessor testleri."""

    @pytest.mark.asyncio
    async def test_adds_glossary_note(self, db: AsyncSession) -> None:
        """Yanlış çeviri → glossary note eklenmeli."""
        post = MedicalPostProcessor()
        await post.load_terms(db)
        translation = TranslationResult(
            source_text="I need botox",
            source_lang="en",
            translations={"tr": "I need injection"},  # yanlış çeviri
            speaker_id=0,
        )
        result = await post.process(translation)
        assert len(result.glossary_notes) > 0
        assert any("botoks" in n for n in result.glossary_notes)


class TestFactory:
    """Factory mode switching testleri."""

    def test_medical_pre(self) -> None:
        pre = create_pre_processor("medical")
        assert isinstance(pre, MedicalPreProcessor)

    def test_tourism_pre(self) -> None:
        pre = create_pre_processor("tourism")
        assert isinstance(pre, TourismPreProcessor)

    def test_medical_post(self) -> None:
        post = create_post_processor("medical")
        assert isinstance(post, MedicalPostProcessor)

    def test_tourism_post(self) -> None:
        from app.glossary.post_processor import TourismPostProcessor
        post = create_post_processor("tourism")
        assert isinstance(post, TourismPostProcessor)

    def test_passthrough_still_works(self) -> None:
        from app.glossary.passthrough import PassthroughPreProcessor
        pre = create_pre_processor("passthrough")
        assert isinstance(pre, PassthroughPreProcessor)
