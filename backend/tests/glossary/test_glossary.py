"""Glossary hook noktaları testleri."""

import time

import pytest

from app.glossary.base import (
    ContextEnricher,
    EnrichedResult,
    GlossaryPostProcessor,
    GlossaryPreProcessor,
)
from app.glossary.factory import (
    create_enricher,
    create_post_processor,
    create_pre_processor,
)
from app.glossary.passthrough import (
    PassthroughEnricher,
    PassthroughPostProcessor,
    PassthroughPreProcessor,
)
from app.schemas import PartialTranscript, TranslationResult


@pytest.fixture
def transcript() -> PartialTranscript:
    return PartialTranscript(
        text="Merhaba nasılsınız",
        lang="tr",
        speaker_id=0,
        confidence=0.95,
    )


@pytest.fixture
def translation() -> TranslationResult:
    return TranslationResult(
        source_text="Merhaba nasılsınız",
        source_lang="tr",
        translations={"en": "Hello how are you", "th": "สวัสดีครับ"},
        speaker_id=0,
    )


class TestABCEnforcement:
    """ABC class'lar instantiate edilememeli."""

    def test_pre_processor_abc(self) -> None:
        """GlossaryPreProcessor direkt instantiate → TypeError."""
        with pytest.raises(TypeError):
            GlossaryPreProcessor()  # type: ignore

    def test_post_processor_abc(self) -> None:
        """GlossaryPostProcessor direkt instantiate → TypeError."""
        with pytest.raises(TypeError):
            GlossaryPostProcessor()  # type: ignore

    def test_enricher_abc(self) -> None:
        """ContextEnricher direkt instantiate → TypeError."""
        with pytest.raises(TypeError):
            ContextEnricher()  # type: ignore


class TestPassthroughPreProcessor:
    """PassthroughPreProcessor testleri."""

    @pytest.mark.asyncio
    async def test_returns_same_transcript(
        self, transcript: PartialTranscript
    ) -> None:
        """Transcript aynen dönmeli."""
        pre = PassthroughPreProcessor()
        result = await pre.process(transcript)
        assert result is transcript

    @pytest.mark.asyncio
    async def test_latency_under_1ms(
        self, transcript: PartialTranscript
    ) -> None:
        """Passthrough latency <1ms."""
        pre = PassthroughPreProcessor()
        start = time.perf_counter()
        await pre.process(transcript)
        duration_ms = (time.perf_counter() - start) * 1000
        assert duration_ms < 1.0


class TestPassthroughPostProcessor:
    """PassthroughPostProcessor testleri."""

    @pytest.mark.asyncio
    async def test_returns_same_translation(
        self, translation: TranslationResult
    ) -> None:
        """Translation aynen dönmeli."""
        post = PassthroughPostProcessor()
        result = await post.process(translation)
        assert result is translation

    @pytest.mark.asyncio
    async def test_latency_under_1ms(
        self, translation: TranslationResult
    ) -> None:
        """Passthrough latency <1ms."""
        post = PassthroughPostProcessor()
        start = time.perf_counter()
        await post.process(translation)
        duration_ms = (time.perf_counter() - start) * 1000
        assert duration_ms < 1.0


class TestPassthroughEnricher:
    """PassthroughEnricher testleri."""

    @pytest.mark.asyncio
    async def test_returns_enriched_result(
        self, translation: TranslationResult
    ) -> None:
        """EnrichedResult dönmeli."""
        enricher = PassthroughEnricher()
        result = await enricher.enrich(translation)
        assert isinstance(result, EnrichedResult)
        assert result.translation is translation
        assert result.summary is None
        assert result.intent is None
        assert result.actions == []

    @pytest.mark.asyncio
    async def test_latency_under_1ms(
        self, translation: TranslationResult
    ) -> None:
        """Passthrough latency <1ms."""
        enricher = PassthroughEnricher()
        start = time.perf_counter()
        await enricher.enrich(translation)
        duration_ms = (time.perf_counter() - start) * 1000
        assert duration_ms < 1.0


class TestFactory:
    """Factory fonksiyon testleri."""

    def test_create_pre_processor_passthrough(self) -> None:
        """mode='passthrough' → PassthroughPreProcessor."""
        pre = create_pre_processor(mode="passthrough")
        assert isinstance(pre, PassthroughPreProcessor)
        assert isinstance(pre, GlossaryPreProcessor)

    def test_create_post_processor_passthrough(self) -> None:
        """mode='passthrough' → PassthroughPostProcessor."""
        post = create_post_processor(mode="passthrough")
        assert isinstance(post, PassthroughPostProcessor)
        assert isinstance(post, GlossaryPostProcessor)

    def test_create_enricher_passthrough(self) -> None:
        """mode='passthrough' → PassthroughEnricher."""
        enricher = create_enricher(mode="passthrough")
        assert isinstance(enricher, PassthroughEnricher)
        assert isinstance(enricher, ContextEnricher)

    def test_unknown_mode_raises(self) -> None:
        """Bilinmeyen mode → ValueError."""
        with pytest.raises(ValueError, match="Unknown"):
            create_pre_processor(mode="nonexistent")
        with pytest.raises(ValueError, match="Unknown"):
            create_post_processor(mode="nonexistent")
        with pytest.raises(ValueError, match="Unknown"):
            create_enricher(mode="nonexistent")
