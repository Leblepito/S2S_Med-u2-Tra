"""Translation cache — Redis primary, in-memory fallback."""

import hashlib
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class TranslationCache:
    """Translation cache with Redis support and in-memory fallback.

    Args:
        ttl_seconds: Cache entry yaşam süresi (saniye).
        redis_url: Redis bağlantı URL'i. None → sadece in-memory.
    """

    def __init__(
        self,
        ttl_seconds: int = 3600,
        redis_url: Optional[str] = None,
    ) -> None:
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, tuple[str, float]] = {}
        self._redis = self._connect_redis(redis_url)
        self.hits: int = 0
        self.misses: int = 0

    def _connect_redis(self, redis_url: Optional[str]) -> Optional[object]:
        """Redis bağlantısı kur. Hata → None (in-memory fallback)."""
        if not redis_url:
            return None
        try:
            import redis as redis_lib
            client = redis_lib.from_url(redis_url, decode_responses=True)
            client.ping()
            logger.info(f"[CACHE] Redis connected: {redis_url}")
            return client
        except Exception as e:
            logger.warning(f"[CACHE] Redis bağlantı hatası: {e} → in-memory fallback")
            return None

    @property
    def size(self) -> int:
        """Cache'teki entry sayısı (in-memory)."""
        return len(self._store)

    @property
    def using_redis(self) -> bool:
        """Redis aktif mi?"""
        return self._redis is not None

    def get(
        self, text: str, source_lang: str, target_lang: str
    ) -> Optional[str]:
        """Cache'ten çeviri al. Redis → in-memory fallback."""
        key = self._make_key(text, source_lang, target_lang)

        # Redis'ten dene
        if self._redis is not None:
            try:
                value = self._redis.get(f"tr:{key}")
                if value is not None:
                    self.hits += 1
                    return value
                self.misses += 1
                return None
            except Exception as e:
                logger.warning(f"[CACHE] Redis get hatası: {e}")

        # In-memory fallback
        entry = self._store.get(key)
        if entry is None:
            self.misses += 1
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            self.misses += 1
            return None
        self.hits += 1
        return value

    def set(
        self, text: str, source_lang: str, target_lang: str, translation: str
    ) -> None:
        """Cache'e çeviri yaz. Redis + in-memory."""
        key = self._make_key(text, source_lang, target_lang)

        # Redis'e yaz
        if self._redis is not None:
            try:
                self._redis.setex(f"tr:{key}", self.ttl_seconds, translation)
            except Exception as e:
                logger.warning(f"[CACHE] Redis set hatası: {e}")

        # In-memory'ye de yaz (fallback)
        expires_at = time.monotonic() + self.ttl_seconds
        self._store[key] = (translation, expires_at)

    def _make_key(
        self, text: str, source_lang: str, target_lang: str
    ) -> str:
        """Cache key oluştur."""
        raw = f"{text}|{source_lang}|{target_lang}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
