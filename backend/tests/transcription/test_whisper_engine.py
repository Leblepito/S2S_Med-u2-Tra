"""Faster Whisper engine testleri."""

import numpy as np
import pytest

from app.transcription.whisper_engine import (
    TranscriptionResult,
    WhisperEngine,
    create_whisper_engine,
)


class TestTranscriptionResult:
    """TranscriptionResult model testleri."""

    def test_valid_result(self) -> None:
        """Geçerli sonuç oluşturulabilmeli."""
        result = TranscriptionResult(
            text="Merhaba nasılsınız",
            language="tr",
            confidence=0.95,
            duration_ms=150.0,
        )
        assert result.text == "Merhaba nasılsınız"
        assert result.language == "tr"

    def test_empty_text(self) -> None:
        """Boş text geçerli olmalı (sessizlik)."""
        result = TranscriptionResult(
            text="", language="en", confidence=0.0, duration_ms=10.0
        )
        assert result.text == ""


class TestWhisperEngine:
    """WhisperEngine class testleri."""

    @pytest.fixture
    def engine(self) -> WhisperEngine:
        return create_whisper_engine(use_mocks=True)

    def test_create_returns_engine(self) -> None:
        """create_whisper_engine WhisperEngine dönmeli."""
        engine = create_whisper_engine(use_mocks=True)
        assert isinstance(engine, WhisperEngine)

    def test_transcribe_returns_result(self, engine: WhisperEngine) -> None:
        """transcribe TranscriptionResult dönmeli."""
        audio = np.zeros(16000, dtype=np.int16)  # 1 saniye sessizlik
        result = engine.transcribe(audio)
        assert isinstance(result, TranscriptionResult)

    def test_transcribe_has_text(self, engine: WhisperEngine) -> None:
        """Mock engine text dönmeli."""
        audio = np.ones(16000, dtype=np.int16) * 1000
        result = engine.transcribe(audio)
        assert isinstance(result.text, str)

    def test_transcribe_has_language(self, engine: WhisperEngine) -> None:
        """Mock engine dil bilgisi dönmeli."""
        audio = np.ones(16000, dtype=np.int16) * 1000
        result = engine.transcribe(audio)
        assert result.language in {"tr", "ru", "en", "th", "vi", "zh", "id"}

    def test_transcribe_has_duration(self, engine: WhisperEngine) -> None:
        """transcribe süre bilgisi dönmeli."""
        audio = np.zeros(16000, dtype=np.int16)
        result = engine.transcribe(audio)
        assert result.duration_ms >= 0

    def test_transcribe_confidence_range(self, engine: WhisperEngine) -> None:
        """Confidence 0-1 arasında olmalı."""
        audio = np.zeros(16000, dtype=np.int16)
        result = engine.transcribe(audio)
        assert 0.0 <= result.confidence <= 1.0

    def test_empty_audio(self, engine: WhisperEngine) -> None:
        """Boş audio → boş text."""
        audio = np.array([], dtype=np.int16)
        result = engine.transcribe(audio)
        assert result.text == ""
