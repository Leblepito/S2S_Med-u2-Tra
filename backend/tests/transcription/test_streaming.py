"""Streaming transcription testleri."""

import math
import struct

import pytest

from app.constants import CHUNK_BYTES
from app.schemas import PartialTranscript
from app.transcription.streaming import StreamingTranscriber


@pytest.fixture
def transcriber() -> StreamingTranscriber:
    """Mock modda streaming transcriber."""
    return StreamingTranscriber(use_mocks=True)


@pytest.fixture
def silence_chunk() -> bytes:
    return bytes(CHUNK_BYTES)


@pytest.fixture
def speech_chunk() -> bytes:
    samples = [
        int(math.sin(2 * math.pi * 440 * i / 16000) * 16000)
        for i in range(480)
    ]
    return struct.pack(f"<{len(samples)}h", *samples)


class TestStreamingTranscriber:
    """StreamingTranscriber testleri."""

    def test_silence_no_output(
        self, transcriber: StreamingTranscriber, silence_chunk: bytes
    ) -> None:
        """Sessizlikte transcript üretilmemeli."""
        for _ in range(50):
            result = transcriber.process_chunk(silence_chunk)
            assert result is None

    def test_speech_produces_transcript(
        self, transcriber: StreamingTranscriber,
        speech_chunk: bytes,
        silence_chunk: bytes,
    ) -> None:
        """Yeterli konuşma + sessizlik → PartialTranscript üretmeli."""
        # 10 chunk konuşma = 300ms (> 250ms min)
        for _ in range(10):
            transcriber.process_chunk(speech_chunk)
        # 12 chunk sessizlik = 360ms (> 300ms min_silence)
        result = None
        for _ in range(12):
            r = transcriber.process_chunk(silence_chunk)
            if r is not None:
                result = r
        assert result is not None
        assert isinstance(result, PartialTranscript)

    def test_transcript_has_fields(
        self, transcriber: StreamingTranscriber,
        speech_chunk: bytes,
        silence_chunk: bytes,
    ) -> None:
        """Transcript doğru alanları içermeli."""
        for _ in range(10):
            transcriber.process_chunk(speech_chunk)
        result = None
        for _ in range(12):
            r = transcriber.process_chunk(silence_chunk)
            if r is not None:
                result = r
        assert result is not None
        assert result.type == "partial_transcript"
        assert isinstance(result.text, str)
        assert result.lang in {"tr", "ru", "en", "th", "vi", "zh", "id"}
        assert 0.0 <= result.confidence <= 1.0
        assert result.speaker_id == 0

    def test_latency_tracked(
        self, transcriber: StreamingTranscriber,
        speech_chunk: bytes,
        silence_chunk: bytes,
    ) -> None:
        """Transcription latency takip edilmeli."""
        for _ in range(10):
            transcriber.process_chunk(speech_chunk)
        for _ in range(12):
            transcriber.process_chunk(silence_chunk)
        assert transcriber.last_latency_ms is not None
        assert transcriber.last_latency_ms >= 0
