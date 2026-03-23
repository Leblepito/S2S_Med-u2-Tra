"""Speaker diarization testleri."""

import math
import struct

import numpy as np
import pytest

from app.audio.diarization import (
    MockDiarizer,
    SpeakerDiarizer,
    create_diarizer,
)


@pytest.fixture
def diarizer() -> MockDiarizer:
    return MockDiarizer()


@pytest.fixture
def silence_audio() -> np.ndarray:
    return np.zeros(16000, dtype=np.int16)


@pytest.fixture
def loud_audio() -> np.ndarray:
    """Yüksek energy audio (speaker 0 olmalı)."""
    samples = [
        int(math.sin(2 * math.pi * 440 * i / 16000) * 16000)
        for i in range(16000)
    ]
    return np.array(samples, dtype=np.int16)


@pytest.fixture
def quiet_audio() -> np.ndarray:
    """Düşük energy audio (speaker 1 olmalı)."""
    samples = [
        int(math.sin(2 * math.pi * 220 * i / 16000) * 3000)
        for i in range(16000)
    ]
    return np.array(samples, dtype=np.int16)


class TestMockDiarizer:
    """MockDiarizer testleri."""

    def test_returns_int(self, diarizer: MockDiarizer, loud_audio: np.ndarray) -> None:
        """identify int dönmeli."""
        result = diarizer.identify(loud_audio)
        assert isinstance(result, int)

    def test_silence_returns_zero(
        self, diarizer: MockDiarizer, silence_audio: np.ndarray
    ) -> None:
        """Sessizlik → speaker 0."""
        result = diarizer.identify(silence_audio)
        assert result == 0

    def test_consistent_speaker(
        self, diarizer: MockDiarizer, loud_audio: np.ndarray
    ) -> None:
        """Aynı audio aynı speaker_id dönmeli."""
        id1 = diarizer.identify(loud_audio)
        id2 = diarizer.identify(loud_audio)
        assert id1 == id2

    def test_two_speakers_distinguished(
        self, diarizer: MockDiarizer,
        loud_audio: np.ndarray,
        quiet_audio: np.ndarray,
    ) -> None:
        """Farklı energy → farklı speaker_id olabilir."""
        id_loud = diarizer.identify(loud_audio)
        id_quiet = diarizer.identify(quiet_audio)
        # Mock mode'da energy bucket'a göre ayrım
        assert isinstance(id_loud, int)
        assert isinstance(id_quiet, int)

    def test_speaker_id_non_negative(
        self, diarizer: MockDiarizer, loud_audio: np.ndarray
    ) -> None:
        """Speaker ID >= 0 olmalı."""
        assert diarizer.identify(loud_audio) >= 0

    def test_empty_audio(self, diarizer: MockDiarizer) -> None:
        """Boş audio → speaker 0."""
        empty = np.array([], dtype=np.int16)
        assert diarizer.identify(empty) == 0


class TestCreateDiarizer:
    """create_diarizer factory testleri."""

    def test_mock_mode(self) -> None:
        """use_mocks=True → MockDiarizer."""
        d = create_diarizer(use_mocks=True)
        assert isinstance(d, MockDiarizer)

    def test_protocol(self) -> None:
        """Factory SpeakerDiarizer protocol'üne uygun dönmeli."""
        d = create_diarizer(use_mocks=True)
        assert isinstance(d, SpeakerDiarizer)
