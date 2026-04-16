"""Streaming transcription — VAD + Whisper entegrasyonu."""

import logging
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np

from app.audio.vad import SpeechSegmentDetector, create_vad
from app.schemas import PartialTranscript
from app.transcription.whisper_engine import (
    WhisperEngine,
    create_whisper_engine,
)

logger = logging.getLogger(__name__)


@dataclass
class StreamingResult:
    """Streaming transcription sonucu + raw audio segment."""

    transcript: PartialTranscript
    segment: np.ndarray


class StreamingTranscriber:
    """VAD ile speech segment tespit et, Whisper ile transcribe et.

    Args:
        use_mocks: Mock mode (torch/whisper gerektirmez).
        min_speech_ms: Minimum konuşma süresi (ms).
        min_silence_ms: Segment bitişi için gereken sessizlik (ms).
    """

    def __init__(
        self,
        use_mocks: bool = True,
        min_speech_ms: int = 250,
        min_silence_ms: int = 300,
    ) -> None:
        vad_fn = create_vad(use_mocks=use_mocks)
        self._detector = SpeechSegmentDetector(
            vad_fn=vad_fn,
            min_speech_ms=min_speech_ms,
            min_silence_ms=min_silence_ms,
        )
        self._engine: WhisperEngine = create_whisper_engine(
            use_mocks=use_mocks
        )
        self.last_latency_ms: Optional[float] = None

    def process_chunk(
        self, chunk: bytes
    ) -> Optional[PartialTranscript]:
        """Chunk işle, transcript hazırsa döndür.

        Args:
            chunk: PCM16 audio chunk (960 bytes).

        Returns:
            PartialTranscript veya None.
        """
        result = self.process_chunk_with_segment(chunk)
        if result is None:
            return None
        return result.transcript

    def process_chunk_with_segment(
        self, chunk: bytes
    ) -> Optional[StreamingResult]:
        """Chunk işle, transcript + raw segment döndür.

        Args:
            chunk: PCM16 audio chunk.

        Returns:
            StreamingResult veya None.
        """
        segment = self._detector.process_chunk(chunk)
        if segment is None:
            return None

        start = time.perf_counter()
        result = self._engine.transcribe(segment)
        self.last_latency_ms = (time.perf_counter() - start) * 1000

        logger.info(
            f"[STREAM] Transcription: {self.last_latency_ms:.1f}ms "
            f"'{result.text[:50]}'"
        )

        transcript = PartialTranscript(
            text=result.text,
            lang=result.language,
            speaker_id=0,
            confidence=result.confidence,
        )
        return StreamingResult(transcript=transcript, segment=segment)
