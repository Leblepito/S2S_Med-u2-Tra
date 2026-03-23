"""Speaker diarization — konuşmacı ayrımı."""

import logging
from typing import Protocol, runtime_checkable

import numpy as np

logger = logging.getLogger(__name__)


@runtime_checkable
class SpeakerDiarizer(Protocol):
    """Speaker diarizer arayüzü."""

    def identify(self, audio: np.ndarray) -> int: ...


class MockDiarizer:
    """Energy-based mock diarizer — RMS bucket'a göre speaker_id atar."""

    def __init__(self, num_buckets: int = 4) -> None:
        self._num_buckets = num_buckets

    def identify(self, audio: np.ndarray) -> int:
        """Audio segment'inden speaker_id belirle.

        Args:
            audio: int16 numpy array.

        Returns:
            speaker_id (0-based).
        """
        if len(audio) == 0:
            return 0

        rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
        # RMS'e göre bucket: 0-4000 → 0, 4000-8000 → 1, ...
        bucket = int(rms / 4000)
        speaker_id = min(bucket, self._num_buckets - 1)
        logger.info(f"[DIARIZE] RMS={rms:.0f} → speaker {speaker_id}")
        return speaker_id


class RealDiarizer:
    """pyannote.audio ile speaker diarization."""

    def __init__(self) -> None:
        logger.info("[DIARIZE] pyannote model yükleniyor...")
        from pyannote.audio import Inference  # noqa: lazy

        self._inference = Inference(
            "pyannote/embedding", window="whole"
        )
        logger.info("[DIARIZE] Model hazır")

    def identify(self, audio: np.ndarray) -> int:
        """pyannote embedding ile speaker_id belirle."""
        if len(audio) == 0:
            return 0
        audio_f32 = audio.astype(np.float32) / 32768.0
        embedding = self._inference(
            {"waveform": audio_f32.reshape(1, -1), "sample_rate": 16000}
        )
        # Embedding cache ile en yakın speaker'ı bul
        # (speaker_cache.py ile entegre edilecek)
        return 0


def create_diarizer(use_mocks: bool = True) -> SpeakerDiarizer:
    """Diarizer factory.

    Args:
        use_mocks: True → MockDiarizer, False → RealDiarizer.

    Returns:
        SpeakerDiarizer instance.
    """
    if use_mocks:
        logger.info("[DIARIZE] Mock mode")
        return MockDiarizer()
    return RealDiarizer()
