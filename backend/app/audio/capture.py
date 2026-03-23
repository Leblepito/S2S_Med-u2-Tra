"""Audio capture — chunk validation, format conversion, buffering."""

import logging
from typing import Optional

import numpy as np

from app.constants import CHUNK_BYTES
from app.exceptions import AudioFormatError

logger = logging.getLogger(__name__)


def validate_chunk(data: bytes) -> None:
    """Audio chunk boyutunu doğrula.

    Args:
        data: PCM16 audio chunk.

    Raises:
        AudioFormatError: Chunk boyutu CHUNK_BYTES (960) değilse.
    """
    if len(data) != CHUNK_BYTES:
        msg = f"Chunk boyutu {len(data)} bytes, beklenen {CHUNK_BYTES}"
        raise AudioFormatError(msg)


def bytes_to_samples(data: bytes) -> np.ndarray:
    """PCM16 Little-Endian bytes'ı int16 numpy array'e çevir.

    Args:
        data: PCM16 LE audio bytes.

    Returns:
        int16 numpy array.
    """
    return np.frombuffer(data, dtype=np.int16).copy()


class AudioBuffer:
    """Audio chunk'ları biriktirip threshold'da segment veren buffer.

    Args:
        threshold_samples: Segment vermek için gereken minimum sample sayısı.
    """

    def __init__(self, threshold_samples: int = 16000) -> None:
        self.threshold_samples = threshold_samples
        self._chunks: list[np.ndarray] = []
        self._total_samples: int = 0

    def add_chunk(self, data: bytes) -> Optional[np.ndarray]:
        """Chunk ekle, threshold'a ulaşınca segment döndür.

        Args:
            data: PCM16 audio chunk bytes.

        Returns:
            Threshold'a ulaşıldıysa int16 numpy array, yoksa None.
        """
        samples = bytes_to_samples(data)
        self._chunks.append(samples)
        self._total_samples += len(samples)

        if self._total_samples >= self.threshold_samples:
            segment = np.concatenate(self._chunks)
            self._chunks.clear()
            self._total_samples = 0
            return segment
        return None
