"""Mock translator testleri."""

import pytest

from app.translation.mock_translator import (
    MockTranslator,
    Translator,
    create_translator,
)


class TestMockTranslator:
    """MockTranslator class testleri."""

    @pytest.fixture
    def translator(self) -> MockTranslator:
        return MockTranslator()

    @pytest.mark.asyncio
    async def test_single_target(self, translator: MockTranslator) -> None:
        """Tek hedef dile çeviri."""
        result = await translator.translate("merhaba", "tr", ["en"])
        assert "en" in result
        assert "merhaba" in result["en"]

    @pytest.mark.asyncio
    async def test_multiple_targets(self, translator: MockTranslator) -> None:
        """Birden fazla hedef dile çeviri."""
        result = await translator.translate(
            "hello", "en", ["tr", "th", "ru"]
        )
        assert len(result) == 3
        assert "tr" in result
        assert "th" in result
        assert "ru" in result

    @pytest.mark.asyncio
    async def test_format_contains_arrow(
        self, translator: MockTranslator
    ) -> None:
        """Mock format: '[XX→YY] text'."""
        result = await translator.translate("test", "en", ["tr"])
        assert "EN→TR" in result["tr"] or "en→tr" in result["tr"].lower()

    @pytest.mark.asyncio
    async def test_all_7_langs(self, translator: MockTranslator) -> None:
        """7 dil çiftinin tümü çalışmalı."""
        langs = ["tr", "ru", "en", "th", "vi", "zh", "id"]
        for source in langs:
            targets = [l for l in langs if l != source]
            result = await translator.translate("test", source, targets)
            assert len(result) == 6

    @pytest.mark.asyncio
    async def test_empty_text(self, translator: MockTranslator) -> None:
        """Boş text → boş çeviri."""
        result = await translator.translate("", "en", ["tr"])
        assert result["tr"] == ""


class TestCreateTranslator:
    """create_translator factory testleri."""

    def test_mock_mode(self) -> None:
        """use_mocks=True → MockTranslator."""
        t = create_translator(use_mocks=True)
        assert isinstance(t, MockTranslator)

    def test_returns_translator_protocol(self) -> None:
        """Factory Translator protocol'üne uygun instance dönmeli."""
        t = create_translator(use_mocks=True)
        assert isinstance(t, Translator)
