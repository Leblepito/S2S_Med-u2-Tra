"""Translation cache testleri (in-memory + Redis mock)."""

import time
from unittest.mock import MagicMock, patch

import pytest

from app.translation.cache import TranslationCache


class TestTranslationCache:
    """In-memory cache testleri."""

    @pytest.fixture
    def cache(self) -> TranslationCache:
        return TranslationCache(ttl_seconds=3600)

    def test_cache_miss(self, cache: TranslationCache) -> None:
        result = cache.get("hello", "en", "tr")
        assert result is None

    def test_cache_hit(self, cache: TranslationCache) -> None:
        cache.set("hello", "en", "tr", "merhaba")
        result = cache.get("hello", "en", "tr")
        assert result == "merhaba"

    def test_different_keys(self, cache: TranslationCache) -> None:
        cache.set("hello", "en", "tr", "merhaba")
        cache.set("hello", "en", "ru", "привет")
        assert cache.get("hello", "en", "tr") == "merhaba"
        assert cache.get("hello", "en", "ru") == "привет"

    def test_expiry(self) -> None:
        cache = TranslationCache(ttl_seconds=0.01)
        cache.set("test", "en", "tr", "test_value")
        time.sleep(0.02)
        assert cache.get("test", "en", "tr") is None

    def test_stats(self, cache: TranslationCache) -> None:
        cache.set("a", "en", "tr", "b")
        cache.get("a", "en", "tr")  # hit
        cache.get("x", "en", "tr")  # miss
        assert cache.hits == 1
        assert cache.misses == 1

    def test_size(self, cache: TranslationCache) -> None:
        assert cache.size == 0
        cache.set("a", "en", "tr", "b")
        cache.set("c", "en", "ru", "d")
        assert cache.size == 2

    def test_using_redis_false(self, cache: TranslationCache) -> None:
        assert cache.using_redis is False


class TestRedisCacheFallback:
    """Redis connection failure → in-memory fallback."""

    def test_invalid_url_falls_back(self) -> None:
        """Geçersiz Redis URL → in-memory fallback, hata fırlatmaz."""
        cache = TranslationCache(redis_url="redis://invalid:9999")
        assert cache.using_redis is False
        cache.set("a", "en", "tr", "b")
        assert cache.get("a", "en", "tr") == "b"

    def test_no_url_in_memory_only(self) -> None:
        """redis_url=None → in-memory only."""
        cache = TranslationCache(redis_url=None)
        assert cache.using_redis is False


class TestRedisCacheMock:
    """Mock Redis ile cache testleri."""

    def _make_cache_with_mock_redis(
        self, mock_redis: MagicMock, ttl: int = 3600
    ) -> TranslationCache:
        """Redis mock'lu cache oluştur."""
        cache = TranslationCache(ttl_seconds=ttl)
        cache._redis = mock_redis
        return cache

    def test_redis_get_hit(self) -> None:
        """Redis get hit → value döner."""
        mock_redis = MagicMock()
        mock_redis.get.return_value = "merhaba"
        cache = self._make_cache_with_mock_redis(mock_redis)

        assert cache.using_redis is True
        result = cache.get("hello", "en", "tr")
        assert result == "merhaba"
        assert cache.hits == 1

    def test_redis_get_miss(self) -> None:
        """Redis get miss → None."""
        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        cache = self._make_cache_with_mock_redis(mock_redis)

        result = cache.get("hello", "en", "tr")
        assert result is None
        assert cache.misses == 1

    def test_redis_set_calls_setex(self) -> None:
        """Redis set → SETEX ile TTL."""
        mock_redis = MagicMock()
        cache = self._make_cache_with_mock_redis(mock_redis, ttl=600)

        cache.set("hello", "en", "tr", "merhaba")
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        assert args[1] == 600
        assert args[2] == "merhaba"

    def test_redis_error_falls_back(self) -> None:
        """Redis get hatası → in-memory fallback."""
        mock_redis = MagicMock()
        mock_redis.get.side_effect = Exception("Redis down")
        cache = self._make_cache_with_mock_redis(mock_redis)

        cache.set("hello", "en", "tr", "merhaba")
        result = cache.get("hello", "en", "tr")
        assert result == "merhaba"
