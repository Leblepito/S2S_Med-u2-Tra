"""Speaker embedding cache — cosine similarity ile konuşmacı eşleme."""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class SpeakerEmbeddingCache:
    """In-memory speaker embedding cache.

    Args:
        threshold: Cosine similarity eşiği (0-1). Altında → yeni speaker.
    """

    def __init__(self, threshold: float = 0.7) -> None:
        self.threshold = threshold
        self._embeddings: dict[int, np.ndarray] = {}

    @property
    def size(self) -> int:
        """Cache'teki speaker sayısı."""
        return len(self._embeddings)

    def add_embedding(self, speaker_id: int, embedding: np.ndarray) -> None:
        """Speaker embedding'i cache'e ekle.

        Args:
            speaker_id: Speaker ID.
            embedding: Normalized embedding vektörü.
        """
        self._embeddings[speaker_id] = embedding.copy()

    def find_closest(self, embedding: np.ndarray) -> Optional[int]:
        """En yakın speaker'ı bul.

        Args:
            embedding: Sorgu embedding vektörü.

        Returns:
            speaker_id veya None (threshold altındaysa).
        """
        if not self._embeddings:
            return None

        best_id: Optional[int] = None
        best_sim: float = -1.0

        for sid, cached in self._embeddings.items():
            sim = self._cosine_similarity(embedding, cached)
            if sim > best_sim:
                best_sim = sim
                best_id = sid

        if best_sim >= self.threshold:
            return best_id
        return None

    def _cosine_similarity(
        self, a: np.ndarray, b: np.ndarray
    ) -> float:
        """Cosine similarity hesapla."""
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))
