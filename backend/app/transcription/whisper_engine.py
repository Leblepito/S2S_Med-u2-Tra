"""Faster Whisper ASR engine wrapper + mock mode."""

import logging
import time
from typing import Protocol, runtime_checkable

import numpy as np
from pydantic import BaseModel, Field

from app.constants import SAMPLE_RATE

logger = logging.getLogger(__name__)


class TranscriptionResult(BaseModel):
    """ASR transcription sonucu."""

    text: str
    language: str
    confidence: float = Field(ge=0.0, le=1.0)
    duration_ms: float = Field(ge=0.0)


@runtime_checkable
class WhisperEngine(Protocol):
    """Whisper engine arayüzü."""

    def transcribe(self, audio: np.ndarray) -> TranscriptionResult: ...


class MockWhisperEngine:
    """Mock Whisper engine — torch/faster_whisper gerektirmez."""

    def transcribe(self, audio: np.ndarray) -> TranscriptionResult:
        """Mock transcription — energy'ye göre basit sonuç döndür.

        Args:
            audio: int16 numpy array.

        Returns:
            TranscriptionResult.
        """
        start = time.perf_counter()

        if len(audio) == 0:
            return TranscriptionResult(
                text="", language="en", confidence=0.0, duration_ms=0.0
            )

        rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
        duration_ms = (time.perf_counter() - start) * 1000

        if rms < 100:
            return TranscriptionResult(
                text="", language="en", confidence=0.1,
                duration_ms=duration_ms,
            )

        return TranscriptionResult(
            text="[mock transcription]",
            language="tr",
            confidence=0.85,
            duration_ms=duration_ms,
        )


class RealWhisperEngine:
    """Faster Whisper engine — CTranslate2 backend."""

    def __init__(self, model_size: str = "large-v3", device: str = "cuda") -> None:
        from faster_whisper import WhisperModel  # noqa: lazy import

        logger.info(f"[WHISPER] Yükleniyor: {model_size} ({device})")
        self._model = WhisperModel(model_size, device=device)
        logger.info("[WHISPER] Model hazır")

    def transcribe(self, audio: np.ndarray) -> TranscriptionResult:
        """Audio'yu transcribe et.

        Args:
            audio: int16 numpy array.

        Returns:
            TranscriptionResult.
        """
        if len(audio) == 0:
            return TranscriptionResult(
                text="", language="en", confidence=0.0, duration_ms=0.0
            )

        start = time.perf_counter()
        audio_f32 = audio.astype(np.float32) / 32768.0

        segments, info = self._model.transcribe(
            audio_f32,
            language=None,
            beam_size=5,
            vad_filter=False,
        )
        text = " ".join(s.text.strip() for s in segments)
        duration_ms = (time.perf_counter() - start) * 1000

        result = TranscriptionResult(
            text=text,
            language=info.language,
            confidence=info.language_probability,
            duration_ms=duration_ms,
        )
        logger.info(
            f"[WHISPER] {result.language} ({result.confidence:.2f}) "
            f"{duration_ms:.1f}ms: {text[:50]}"
        )
        return result


def create_whisper_engine(
    use_mocks: bool = True,
    model_size: str = "large-v3",
    device: str = "cuda",
) -> WhisperEngine:
    """Whisper engine factory.

    Args:
        use_mocks: True → MockWhisperEngine, False → RealWhisperEngine.
        model_size: Whisper model boyutu.
        device: cuda veya cpu.

    Returns:
        WhisperEngine instance.
    """
    if use_mocks:
        logger.info("[WHISPER] Mock mode")
        return MockWhisperEngine()
    return RealWhisperEngine(model_size=model_size, device=device)
