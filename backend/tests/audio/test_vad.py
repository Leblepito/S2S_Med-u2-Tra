"""Silero VAD wrapper testleri."""

import math
import struct

import pytest

from app.audio.vad import SpeechSegmentDetector, create_vad
from app.constants import CHUNK_BYTES


@pytest.fixture
def silence_chunk() -> bytes:
    """30ms sessizlik @ 16kHz PCM16."""
    return bytes(CHUNK_BYTES)


@pytest.fixture
def speech_chunk() -> bytes:
    """30ms yapay konuşma sinyali (440Hz sine)."""
    samples = [
        int(math.sin(2 * math.pi * 440 * i / 16000) * 16000)
        for i in range(480)
    ]
    return struct.pack(f"<{len(samples)}h", *samples)


class TestCreateVad:
    """VAD factory fonksiyonu testleri."""

    def test_create_returns_callable(self) -> None:
        """create_vad bir callable dönmeli."""
        vad = create_vad(use_mocks=True)
        assert callable(vad)

    def test_mock_vad_silence(self, silence_chunk: bytes) -> None:
        """Mock VAD sessizliği reddetmeli."""
        vad = create_vad(use_mocks=True)
        assert vad(silence_chunk) is False

    def test_mock_vad_speech(self, speech_chunk: bytes) -> None:
        """Mock VAD konuşmayı algılamalı."""
        vad = create_vad(use_mocks=True)
        assert vad(speech_chunk) is True


class TestSpeechSegmentDetector:
    """SpeechSegmentDetector class testleri."""

    @pytest.fixture
    def detector(self) -> SpeechSegmentDetector:
        vad = create_vad(use_mocks=True)
        return SpeechSegmentDetector(
            vad_fn=vad,
            min_speech_ms=250,
            min_silence_ms=300,
        )

    def test_silence_no_segment(
        self, detector: SpeechSegmentDetector, silence_chunk: bytes
    ) -> None:
        """Sessizlikte segment üretilmemeli."""
        for _ in range(20):
            result = detector.process_chunk(silence_chunk)
            assert result is None

    def test_short_speech_filtered(
        self, detector: SpeechSegmentDetector, speech_chunk: bytes, silence_chunk: bytes
    ) -> None:
        """250ms altı konuşma filtrelenmeli (30ms * 5 = 150ms < 250ms)."""
        for _ in range(5):
            detector.process_chunk(speech_chunk)
        # Hemen sessizliğe geç — kısa konuşma segment vermemeli
        for _ in range(15):
            result = detector.process_chunk(silence_chunk)
        # 150ms konuşma < 250ms min → segment üretilmemeli
        assert result is None

    def test_speech_then_silence_produces_segment(
        self, detector: SpeechSegmentDetector, speech_chunk: bytes, silence_chunk: bytes
    ) -> None:
        """Yeterli konuşma + sessizlik → segment üretmeli."""
        # 30ms * 10 = 300ms konuşma (>= 250ms min)
        for _ in range(10):
            detector.process_chunk(speech_chunk)
        # 30ms * 12 = 360ms sessizlik (>= 300ms min_silence)
        result = None
        for _ in range(12):
            r = detector.process_chunk(silence_chunk)
            if r is not None:
                result = r
        assert result is not None
        assert len(result) > 0

    def test_continuous_speech_no_premature_segment(
        self, detector: SpeechSegmentDetector, speech_chunk: bytes
    ) -> None:
        """Sürekli konuşmada erken segment üretilmemeli."""
        for _ in range(50):
            result = detector.process_chunk(speech_chunk)
            assert result is None  # sessizlik olmadan segment yok

    def test_configurable_thresholds(self) -> None:
        """min_speech_ms ve min_silence_ms configurable olmalı."""
        vad = create_vad(use_mocks=True)
        det = SpeechSegmentDetector(
            vad_fn=vad, min_speech_ms=100, min_silence_ms=100
        )
        assert det.min_speech_ms == 100
        assert det.min_silence_ms == 100
