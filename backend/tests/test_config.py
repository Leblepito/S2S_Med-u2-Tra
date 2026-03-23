"""Config, constants ve exceptions modülü testleri."""

import os
from unittest.mock import patch

import pytest

from app.config import Settings, get_settings
from app.constants import (
    CHANNELS,
    CHUNK_BYTES,
    CHUNK_SAMPLES,
    SAMPLE_RATE,
    SUPPORTED_LANGS,
    TTS_SAMPLE_RATE,
)
from app.exceptions import (
    AudioFormatError,
    BabelFlowError,
    TranscriptionError,
    TranslationError,
    TTSError,
    WebSocketError,
)


class TestSettings:
    """Pydantic Settings testleri."""

    def test_default_values(self) -> None:
        """Default değerler doğru yüklenmeli."""
        settings = Settings()
        assert settings.WHISPER_MODEL_SIZE == "large-v3"
        assert settings.WHISPER_DEVICE == "cuda"
        assert settings.AZURE_TRANSLATOR_REGION == "southeastasia"
        assert settings.AZURE_SPEECH_REGION == "southeastasia"
        assert settings.REDIS_URL == "redis://localhost:6379"
        assert settings.USE_MOCKS is True
        assert settings.LOG_LEVEL == "INFO"

    def test_azure_keys_default_empty(self) -> None:
        """Azure key'leri default olarak boş string olmalı."""
        settings = Settings()
        assert settings.AZURE_TRANSLATOR_KEY == ""
        assert settings.AZURE_SPEECH_KEY == ""

    def test_env_override(self) -> None:
        """Env variable'lar Settings'i override etmeli."""
        env = {
            "WHISPER_MODEL_SIZE": "small",
            "WHISPER_DEVICE": "cpu",
            "USE_MOCKS": "false",
            "LOG_LEVEL": "DEBUG",
            "AZURE_TRANSLATOR_KEY": "test-key-123",
        }
        with patch.dict(os.environ, env, clear=False):
            settings = Settings()
            assert settings.WHISPER_MODEL_SIZE == "small"
            assert settings.WHISPER_DEVICE == "cpu"
            assert settings.USE_MOCKS is False
            assert settings.LOG_LEVEL == "DEBUG"
            assert settings.AZURE_TRANSLATOR_KEY == "test-key-123"

    def test_get_settings_returns_settings(self) -> None:
        """get_settings fonksiyonu Settings instance dönmeli."""
        settings = get_settings()
        assert isinstance(settings, Settings)


class TestConstants:
    """Audio sabitleri testleri."""

    def test_supported_langs_count(self) -> None:
        """7 dil desteklenmeli."""
        assert len(SUPPORTED_LANGS) == 7

    def test_supported_langs_content(self) -> None:
        """Tüm 7 dil mevcut olmalı."""
        expected = {"tr", "ru", "en", "th", "vi", "zh", "id"}
        assert SUPPORTED_LANGS == expected

    def test_supported_langs_immutable(self) -> None:
        """SUPPORTED_LANGS frozenset olmalı (değiştirilemez)."""
        assert isinstance(SUPPORTED_LANGS, frozenset)

    def test_sample_rate(self) -> None:
        """Input sample rate 16kHz olmalı."""
        assert SAMPLE_RATE == 16000

    def test_channels(self) -> None:
        """Mono kanal olmalı."""
        assert CHANNELS == 1

    def test_chunk_samples(self) -> None:
        """30ms @ 16kHz = 480 sample."""
        assert CHUNK_SAMPLES == 480

    def test_chunk_bytes(self) -> None:
        """PCM16 = 2 byte/sample → 480 * 2 = 960 bytes."""
        assert CHUNK_BYTES == CHUNK_SAMPLES * 2
        assert CHUNK_BYTES == 960

    def test_tts_sample_rate(self) -> None:
        """TTS output 24kHz olmalı."""
        assert TTS_SAMPLE_RATE == 24000


class TestExceptions:
    """Custom exception hiyerarşisi testleri."""

    def test_base_error_is_exception(self) -> None:
        """BabelFlowError Exception'dan türemeli."""
        assert issubclass(BabelFlowError, Exception)

    def test_audio_format_error_hierarchy(self) -> None:
        """AudioFormatError BabelFlowError'dan türemeli."""
        assert issubclass(AudioFormatError, BabelFlowError)
        err = AudioFormatError("bad format")
        assert str(err) == "bad format"

    def test_transcription_error_hierarchy(self) -> None:
        """TranscriptionError BabelFlowError'dan türemeli."""
        assert issubclass(TranscriptionError, BabelFlowError)

    def test_translation_error_hierarchy(self) -> None:
        """TranslationError BabelFlowError'dan türemeli."""
        assert issubclass(TranslationError, BabelFlowError)

    def test_tts_error_hierarchy(self) -> None:
        """TTSError BabelFlowError'dan türemeli."""
        assert issubclass(TTSError, BabelFlowError)

    def test_websocket_error_hierarchy(self) -> None:
        """WebSocketError BabelFlowError'dan türemeli."""
        assert issubclass(WebSocketError, BabelFlowError)

    def test_catch_all_with_base(self) -> None:
        """BabelFlowError catch tüm alt hataları yakalamalı."""
        with pytest.raises(BabelFlowError):
            raise AudioFormatError("test")
        with pytest.raises(BabelFlowError):
            raise TranslationError("test")
        with pytest.raises(BabelFlowError):
            raise WebSocketError("test")
