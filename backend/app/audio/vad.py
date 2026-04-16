"""Voice Activity Detection — Silero VAD wrapper + mock mode."""

import logging
from typing import Callable, Optional, Protocol

import numpy as np

from app.audio.capture import bytes_to_samples
from app.constants import CHUNK_SAMPLES, SAMPLE_RATE

logger = logging.getLogger(__name__)

# VAD fonksiyon tipi: bytes → bool
VadFn = Callable[[bytes], bool]

# 30ms chunk süresi
CHUNK_DURATION_MS = (CHUNK_SAMPLES / SAMPLE_RATE) * 1000  # 30ms


def create_vad(
    use_mocks: bool = True,
    threshold: float = 0.5,
) -> VadFn:
    """VAD fonksiyonu oluştur.

    Args:
        use_mocks: True → energy-based mock VAD, False → Silero VAD.
        threshold: Karar eşiği (mock: RMS energy, Silero: probability).

    Returns:
        VadFn: bytes → bool fonksiyonu.
    """
    if use_mocks:
        return _create_mock_vad(threshold)
    return _create_silero_vad(threshold)


def _create_mock_vad(threshold: float) -> VadFn:
    """Energy-based mock VAD — torch gerektirmez."""
    energy_threshold = 500.0  # RMS energy eşiği

    def vad_fn(chunk: bytes) -> bool:
        samples = bytes_to_samples(chunk).astype(np.float32)
        rms = np.sqrt(np.mean(samples ** 2))
        return bool(rms > energy_threshold)

    return vad_fn


def _create_silero_vad(threshold: float) -> VadFn:
    """Silero VAD — torch.hub üzerinden model yükler."""
    import torch  # noqa: lazy import

    model, utils = torch.hub.load(
        "snakers4/silero-vad", "silero_vad", trust_repo=True
    )
    (get_speech_timestamps, _, _, _, _) = utils

    def vad_fn(chunk: bytes) -> bool:
        samples = bytes_to_samples(chunk).astype(np.float32) / 32768.0
        tensor = torch.from_numpy(samples)
        prob = model(tensor, SAMPLE_RATE).item()
        return bool(prob > threshold)

    return vad_fn


class SpeechSegmentDetector:
    """Chunk'lardan speech segment'leri tespit eder.

    VAD ile her chunk'ı değerlendirir, konuşma başlangıç/bitiş
    geçişlerini takip eder, min süre filtrelerini uygular.

    Args:
        vad_fn: VAD fonksiyonu (bytes → bool).
        min_speech_ms: Minimum konuşma süresi (ms).
        min_silence_ms: Segment bitişi için gereken sessizlik süresi (ms).
    """

    def __init__(
        self,
        vad_fn: VadFn,
        min_speech_ms: int = 250,
        min_silence_ms: int = 300,
    ) -> None:
        self.vad_fn = vad_fn
        self.min_speech_ms = min_speech_ms
        self.min_silence_ms = min_silence_ms
        self._speech_chunks: list[np.ndarray] = []
        self._speech_ms: float = 0.0
        self._silence_ms: float = 0.0
        self._in_speech: bool = False

    def process_chunk(self, chunk: bytes) -> Optional[np.ndarray]:
        """Chunk işle, segment tamamlanınca döndür.

        Args:
            chunk: PCM16 audio chunk.

        Returns:
            Tamamlanmış speech segment (int16 array) veya None.
        """
        is_speech = self.vad_fn(chunk)

        if is_speech:
            return self._handle_speech(chunk)
        return self._handle_silence()

    def _handle_speech(self, chunk: bytes) -> None:
        """Konuşma chunk'ı işle."""
        samples = bytes_to_samples(chunk)
        self._speech_chunks.append(samples)
        self._speech_ms += CHUNK_DURATION_MS
        self._silence_ms = 0.0
        self._in_speech = True
        return None

    def _handle_silence(self) -> Optional[np.ndarray]:
        """Sessizlik chunk'ı işle, segment tamamlanmışsa döndür."""
        if not self._in_speech:
            return None

        self._silence_ms += CHUNK_DURATION_MS

        if self._silence_ms >= self.min_silence_ms:
            return self._finalize_segment()
        return None

    def _finalize_segment(self) -> Optional[np.ndarray]:
        """Speech segment'i tamamla ve döndür."""
        segment = None
        if self._speech_ms >= self.min_speech_ms and self._speech_chunks:
            segment = np.concatenate(self._speech_chunks)
            logger.info(
                f"[VAD] Segment: {self._speech_ms:.0f}ms, "
                f"{len(segment)} samples"
            )
        self._reset()
        return segment

    def _reset(self) -> None:
        """State'i sıfırla."""
        self._speech_chunks.clear()
        self._speech_ms = 0.0
        self._silence_ms = 0.0
        self._in_speech = False
