"""Translation cache — in-memory, TTL destekli."""

import hashlib
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class TranslationCache:
    """In-memory translation cache (Redis sonra değiştirilecek).

    Args:
        ttl_seconds: Cache entry yaşam süresi (saniye).
    """

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, tuple[str, float]] = {}
        self.hits: int = 0
        self.misses: int = 0

    @property
    def size(self) -> int:
        """Cache'teki entry sayısı."""
        return len(self._store)

    def get(
        self, text: str, source_lang: str, target_lang: str
    ) -> Optional[str]:
        """Cache'ten çeviri al.

        Args:
            text: Kaynak metin.
            source_lang: Kaynak dil.
            target_lang: Hedef dil.

        Returns:
            Çeviri string veya None (miss/expired).
        """
        key = self._make_key(text, source_lang, target_lang)
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
        """Cache'e çeviri yaz.

        Args:
            text: Kaynak metin.
            source_lang: Kaynak dil.
            target_lang: Hedef dil.
            translation: Çeviri metni.
        """
        key = self._make_key(text, source_lang, target_lang)
        expires_at = time.monotonic() + self.ttl_seconds
        self._store[key] = (translation, expires_at)

    def _make_key(
        self, text: str, source_lang: str, target_lang: str
    ) -> str:
        """Cache key oluştur: hash(text + source + target)."""
        raw = f"{text}|{source_lang}|{target_lang}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
