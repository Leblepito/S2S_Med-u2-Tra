"""Audio capture modülü testleri."""

import math
import struct

import numpy as np
import pytest

from app.audio.capture import AudioBuffer, bytes_to_samples, validate_chunk
from app.constants import CHUNK_BYTES
from app.exceptions import AudioFormatError


class TestValidateChunk:
    """validate_chunk fonksiyonu testleri."""

    def test_valid_chunk(self) -> None:
        """960 byte chunk kabul edilmeli."""
        validate_chunk(bytes(CHUNK_BYTES))

    def test_short_chunk(self) -> None:
        """960'dan kısa chunk → AudioFormatError."""
        with pytest.raises(AudioFormatError, match="960"):
            validate_chunk(bytes(100))

    def test_long_chunk(self) -> None:
        """960'dan uzun chunk → AudioFormatError."""
        with pytest.raises(AudioFormatError, match="960"):
            validate_chunk(bytes(1920))

    def test_empty_chunk(self) -> None:
        """Boş chunk → AudioFormatError."""
        with pytest.raises(AudioFormatError):
            validate_chunk(b"")


class TestBytesToSamples:
    """bytes_to_samples fonksiyonu testleri."""

    def test_known_values(self) -> None:
        """Bilinen PCM16 değerler doğru dönüşmeli."""
        # 3 sample: 0, 1000, -1000
        data = struct.pack("<3h", 0, 1000, -1000)
        samples = bytes_to_samples(data)
        assert samples.dtype == np.int16
        assert len(samples) == 3
        assert samples[0] == 0
        assert samples[1] == 1000
        assert samples[2] == -1000

    def test_output_dtype(self) -> None:
        """Output dtype int16 olmalı."""
        data = bytes(CHUNK_BYTES)
        samples = bytes_to_samples(data)
        assert samples.dtype == np.int16

    def test_sample_count(self) -> None:
        """960 byte → 480 sample."""
        data = bytes(CHUNK_BYTES)
        samples = bytes_to_samples(data)
        assert len(samples) == 480


class TestAudioBuffer:
    """AudioBuffer class testleri."""

    def test_accumulation(self) -> None:
        """Chunk'lar biriktirilmeli, threshold'a kadar None dönmeli."""
        buf = AudioBuffer(threshold_samples=960)  # 2 chunk = 960 sample
        chunk = bytes(CHUNK_BYTES)  # 480 sample

        result = buf.add_chunk(chunk)
        assert result is None  # 480 < 960

    def test_threshold_reached(self) -> None:
        """Threshold'a ulaşınca segment dönmeli."""
        buf = AudioBuffer(threshold_samples=480)  # 1 chunk yeter
        chunk = bytes(CHUNK_BYTES)

        result = buf.add_chunk(chunk)
        assert result is not None
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.int16
        assert len(result) >= 480

    def test_buffer_reset_after_segment(self) -> None:
        """Segment verildikten sonra buffer sıfırlanmalı."""
        buf = AudioBuffer(threshold_samples=480)
        chunk = bytes(CHUNK_BYTES)

        buf.add_chunk(chunk)  # segment döner
        result = buf.add_chunk(chunk)  # yeni segment
        assert result is not None

    def test_multiple_chunks_accumulate(self) -> None:
        """Birden fazla chunk biriktirip tek segment olarak vermeli."""
        buf = AudioBuffer(threshold_samples=16000)  # 1 saniye
        chunk = bytes(CHUNK_BYTES)

        # 16000 / 480 ≈ 34 chunk gerekli
        for _ in range(33):
            result = buf.add_chunk(chunk)
            assert result is None

        result = buf.add_chunk(chunk)
        assert result is not None
        assert len(result) >= 16000

    def test_default_threshold(self) -> None:
        """Default threshold 16000 sample (1 saniye) olmalı."""
        buf = AudioBuffer()
        assert buf.threshold_samples == 16000
