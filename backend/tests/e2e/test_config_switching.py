"""Config switching testleri — mock/real geçişi."""

import os
from unittest.mock import patch

import pytest

from app.audio.diarization import MockDiarizer, create_diarizer
from app.config import Settings
from app.transcription.whisper_engine import MockWhisperEngine, create_whisper_engine
from app.translation.mock_translator import MockTranslator, create_translator
from app.tts.mock_tts import MockTTS, create_tts


class TestConfigSwitching:
    """USE_MOCKS true/false geçişi testleri."""

    def test_mock_mode_all_factories(self) -> None:
        """USE_MOCKS=true → tüm factory'ler mock döndürmeli."""
        assert isinstance(create_whisper_engine(use_mocks=True), MockWhisperEngine)
        assert isinstance(create_translator(use_mocks=True), MockTranslator)
        assert isinstance(create_tts(use_mocks=True), MockTTS)
        assert isinstance(create_diarizer(use_mocks=True), MockDiarizer)

    def test_settings_default_mock(self) -> None:
        """Default Settings USE_MOCKS=True."""
        settings = Settings()
        assert settings.USE_MOCKS is True

    def test_settings_env_override(self) -> None:
        """USE_MOCKS env'den override edilebilmeli."""
        with patch.dict(os.environ, {"USE_MOCKS": "false"}):
            settings = Settings()
            assert settings.USE_MOCKS is False

    def test_glossary_mode_default(self) -> None:
        """Default GLOSSARY_MODE = passthrough."""
        settings = Settings()
        assert settings.GLOSSARY_MODE == "passthrough"

    def test_all_azure_keys_empty_default(self) -> None:
        """Default'ta tüm Azure key'leri boş."""
        settings = Settings()
        assert settings.AZURE_TRANSLATOR_KEY == ""
        assert settings.AZURE_SPEECH_KEY == ""
