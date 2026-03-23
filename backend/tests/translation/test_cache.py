"""Translation cache testleri."""

import time

import pytest

from app.translation.cache import TranslationCache


class TestTranslationCache:
    """TranslationCache class testleri."""

    @pytest.fixture
    def cache(self) -> TranslationCache:
        return TranslationCache(ttl_seconds=3600)

    def test_cache_miss(self, cache: TranslationCache) -> None:
        """Olmayan key → None."""
        result = cache.get("hello", "en", "tr")
        assert result is None

    def test_cache_hit(self, cache: TranslationCache) -> None:
        """Set sonrası get → value."""
        cache.set("hello", "en", "tr", "merhaba")
        result = cache.get("hello", "en", "tr")
        assert result == "merhaba"

    def test_different_keys(self, cache: TranslationCache) -> None:
        """Farklı text/lang kombinasyonları farklı entry'ler."""
        cache.set("hello", "en", "tr", "merhaba")
        cache.set("hello", "en", "ru", "привет")
        assert cache.get("hello", "en", "tr") == "merhaba"
        assert cache.get("hello", "en", "ru") == "привет"

    def test_expiry(self) -> None:
        """TTL sonrası entry expire olmalı."""
        cache = TranslationCache(ttl_seconds=0.01)  # 10ms TTL
        cache.set("test", "en", "tr", "test_value")
        time.sleep(0.02)
        assert cache.get("test", "en", "tr") is None

    def test_stats(self, cache: TranslationCache) -> None:
        """Hit/miss istatistikleri doğru tutulmalı."""
        cache.set("a", "en", "tr", "b")
        cache.get("a", "en", "tr")  # hit
        cache.get("x", "en", "tr")  # miss
        assert cache.hits == 1
        assert cache.misses == 1

    def test_size(self, cache: TranslationCache) -> None:
        """Cache boyutu doğru raporlanmalı."""
        assert cache.size == 0
        cache.set("a", "en", "tr", "b")
        cache.set("c", "en", "ru", "d")
        assert cache.size == 2
