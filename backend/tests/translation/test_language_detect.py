"""Language detection testleri."""

import pytest

from app.translation.language_detect import resolve_source_language


class TestResolveSourceLanguage:
    """resolve_source_language fonksiyonu testleri."""

    def test_whisper_high_confidence(self) -> None:
        """Yüksek confidence → Whisper dili kullan."""
        result = resolve_source_language(
            whisper_lang="tr", whisper_confidence=0.9, config_lang="auto"
        )
        assert result == "tr"

    def test_whisper_low_confidence_config_set(self) -> None:
        """Düşük confidence + config belirli → config dili kullan."""
        result = resolve_source_language(
            whisper_lang="en", whisper_confidence=0.3, config_lang="tr"
        )
        assert result == "tr"

    def test_whisper_low_confidence_config_auto(self) -> None:
        """Düşük confidence + config auto → yine Whisper dili kullan."""
        result = resolve_source_language(
            whisper_lang="ru", whisper_confidence=0.3, config_lang="auto"
        )
        assert result == "ru"

    def test_config_overrides_auto(self) -> None:
        """Config belirli dil → her zaman config."""
        result = resolve_source_language(
            whisper_lang="en", whisper_confidence=0.95, config_lang="tr"
        )
        assert result == "tr"

    def test_default_threshold(self) -> None:
        """Default threshold 0.5."""
        # 0.5 üstü → whisper
        assert resolve_source_language("tr", 0.6, "auto") == "tr"
        # 0.5 altı, auto → yine whisper (fallback yok)
        assert resolve_source_language("tr", 0.4, "auto") == "tr"
