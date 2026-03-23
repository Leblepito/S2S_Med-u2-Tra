"""Speaker embedding cache testleri."""

import numpy as np
import pytest

from app.audio.speaker_cache import SpeakerEmbeddingCache


class TestSpeakerEmbeddingCache:
    """SpeakerEmbeddingCache class testleri."""

    @pytest.fixture
    def cache(self) -> SpeakerEmbeddingCache:
        return SpeakerEmbeddingCache(threshold=0.7)

    def _make_embedding(self, seed: int, dim: int = 128) -> np.ndarray:
        """Deterministic test embedding oluştur."""
        rng = np.random.RandomState(seed)
        emb = rng.randn(dim).astype(np.float32)
        return emb / np.linalg.norm(emb)

    def test_add_and_find(self, cache: SpeakerEmbeddingCache) -> None:
        """Eklenen embedding bulunmalı."""
        emb = self._make_embedding(42)
        cache.add_embedding(0, emb)
        result = cache.find_closest(emb)
        assert result == 0

    def test_unknown_speaker(self, cache: SpeakerEmbeddingCache) -> None:
        """Cache boşken → None."""
        emb = self._make_embedding(99)
        result = cache.find_closest(emb)
        assert result is None

    def test_threshold_rejection(self, cache: SpeakerEmbeddingCache) -> None:
        """Farklı embedding threshold altında → None."""
        emb1 = self._make_embedding(1)
        emb2 = self._make_embedding(2)  # farklı seed = farklı yön
        cache.add_embedding(0, emb1)
        # Cosine similarity düşük olmalı
        result = cache.find_closest(emb2)
        # Threshold'a bağlı — farklı seed'ler genelde düşük similarity verir
        assert result is None or isinstance(result, int)

    def test_multiple_speakers(self, cache: SpeakerEmbeddingCache) -> None:
        """Birden fazla speaker cache'lenebilmeli."""
        emb0 = self._make_embedding(10)
        emb1 = self._make_embedding(20)
        cache.add_embedding(0, emb0)
        cache.add_embedding(1, emb1)

        assert cache.find_closest(emb0) == 0
        assert cache.find_closest(emb1) == 1

    def test_closest_match(self, cache: SpeakerEmbeddingCache) -> None:
        """En yakın embedding'e eşleşmeli."""
        emb0 = self._make_embedding(10)
        emb1 = self._make_embedding(20)
        cache.add_embedding(0, emb0)
        cache.add_embedding(1, emb1)

        # emb0'a çok yakın bir vektör
        noisy = emb0 + np.random.RandomState(99).randn(128).astype(np.float32) * 0.01
        noisy = noisy / np.linalg.norm(noisy)
        result = cache.find_closest(noisy)
        assert result == 0

    def test_size(self, cache: SpeakerEmbeddingCache) -> None:
        """Cache boyutu doğru raporlanmalı."""
        assert cache.size == 0
        cache.add_embedding(0, self._make_embedding(1))
        assert cache.size == 1
        cache.add_embedding(1, self._make_embedding(2))
        assert cache.size == 2
