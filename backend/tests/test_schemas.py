"""Pydantic V2 schema modelleri testleri."""

import json

import pytest
from pydantic import ValidationError

from app.schemas import (
    ConfigMessage,
    ErrorResponse,
    FinalTranscript,
    PartialTranscript,
    TranslationResult,
    TTSHeader,
    parse_client_message,
    serialize_server_message,
)


class TestConfigMessage:
    """ConfigMessage modeli testleri."""

    def test_valid_config(self) -> None:
        """Geçerli config mesajı oluşturulabilmeli."""
        msg = ConfigMessage(
            source_lang="auto",
            target_langs=["en", "th"],
            enable_diarization=True,
        )
        assert msg.type == "config"
        assert msg.source_lang == "auto"
        assert msg.target_langs == ["en", "th"]
        assert msg.enable_diarization is True

    def test_default_values(self) -> None:
        """Default değerler doğru olmalı."""
        msg = ConfigMessage(target_langs=["en"])
        assert msg.source_lang == "auto"
        assert msg.enable_diarization is False

    def test_invalid_target_lang(self) -> None:
        """Desteklenmeyen hedef dil reddedilmeli."""
        with pytest.raises(ValidationError):
            ConfigMessage(target_langs=["xx"])

    def test_empty_target_langs(self) -> None:
        """Boş hedef dil listesi reddedilmeli."""
        with pytest.raises(ValidationError):
            ConfigMessage(target_langs=[])

    def test_invalid_source_lang(self) -> None:
        """Desteklenmeyen kaynak dil reddedilmeli (auto hariç)."""
        with pytest.raises(ValidationError):
            ConfigMessage(source_lang="xx", target_langs=["en"])

    def test_serialize(self) -> None:
        """JSON serialize doğru çalışmalı."""
        msg = ConfigMessage(target_langs=["en", "th"])
        data = json.loads(msg.model_dump_json())
        assert data["type"] == "config"
        assert data["target_langs"] == ["en", "th"]


class TestPartialTranscript:
    """PartialTranscript modeli testleri."""

    def test_valid_partial(self) -> None:
        """Geçerli partial transcript oluşturulabilmeli."""
        msg = PartialTranscript(
            text="Merhaba nasıl...",
            lang="tr",
            speaker_id=0,
            confidence=0.92,
        )
        assert msg.type == "partial_transcript"
        assert msg.text == "Merhaba nasıl..."
        assert msg.lang == "tr"
        assert msg.speaker_id == 0
        assert msg.confidence == 0.92

    def test_confidence_range(self) -> None:
        """Confidence 0-1 arasında olmalı."""
        with pytest.raises(ValidationError):
            PartialTranscript(
                text="test", lang="en", speaker_id=0, confidence=1.5
            )
        with pytest.raises(ValidationError):
            PartialTranscript(
                text="test", lang="en", speaker_id=0, confidence=-0.1
            )

    def test_invalid_lang(self) -> None:
        """Desteklenmeyen dil reddedilmeli."""
        with pytest.raises(ValidationError):
            PartialTranscript(
                text="test", lang="xx", speaker_id=0, confidence=0.9
            )


class TestFinalTranscript:
    """FinalTranscript modeli testleri."""

    def test_type_field(self) -> None:
        """Type alanı 'final_transcript' olmalı."""
        msg = FinalTranscript(
            text="Merhaba nasılsınız",
            lang="tr",
            speaker_id=0,
            confidence=0.95,
        )
        assert msg.type == "final_transcript"


class TestTranslationResult:
    """TranslationResult modeli testleri."""

    def test_valid_translation(self) -> None:
        """Geçerli translation result oluşturulabilmeli."""
        msg = TranslationResult(
            source_text="Merhaba nasılsınız",
            source_lang="tr",
            translations={"en": "Hello how are you", "th": "สวัสดีครับ"},
            speaker_id=0,
        )
        assert msg.type == "translation"
        assert msg.translations["en"] == "Hello how are you"

    def test_invalid_source_lang(self) -> None:
        """Desteklenmeyen kaynak dil reddedilmeli."""
        with pytest.raises(ValidationError):
            TranslationResult(
                source_text="test",
                source_lang="xx",
                translations={"en": "test"},
                speaker_id=0,
            )


class TestTTSHeader:
    """TTSHeader modeli testleri."""

    def test_valid_header(self) -> None:
        """Geçerli TTS header oluşturulabilmeli."""
        header = TTSHeader(lang="en", chunk_index=0)
        assert header.type == "tts_audio"
        assert header.lang == "en"
        assert header.chunk_index == 0

    def test_negative_chunk_index(self) -> None:
        """Negatif chunk_index reddedilmeli."""
        with pytest.raises(ValidationError):
            TTSHeader(lang="en", chunk_index=-1)


class TestErrorResponse:
    """ErrorResponse modeli testleri."""

    def test_error_with_code(self) -> None:
        """Error response code ile oluşturulabilmeli."""
        msg = ErrorResponse(message="Invalid config", code="INVALID_CONFIG")
        assert msg.type == "error"
        assert msg.code == "INVALID_CONFIG"

    def test_error_without_code(self) -> None:
        """Error response code olmadan oluşturulabilmeli."""
        msg = ErrorResponse(message="Something went wrong")
        assert msg.code is None


class TestParseClientMessage:
    """parse_client_message fonksiyonu testleri."""

    def test_valid_config_json(self) -> None:
        """Geçerli config JSON'ı parse edilmeli."""
        data = json.dumps({
            "type": "config",
            "source_lang": "auto",
            "target_langs": ["en", "th"],
            "enable_diarization": True,
        })
        msg = parse_client_message(data)
        assert isinstance(msg, ConfigMessage)
        assert msg.target_langs == ["en", "th"]

    def test_invalid_json(self) -> None:
        """Geçersiz JSON ValueError fırlatmalı."""
        with pytest.raises(ValueError, match="JSON"):
            parse_client_message("not json{{{")

    def test_unknown_type(self) -> None:
        """Bilinmeyen type ValueError fırlatmalı."""
        data = json.dumps({"type": "unknown", "data": 123})
        with pytest.raises(ValueError, match="type"):
            parse_client_message(data)

    def test_missing_type(self) -> None:
        """Type alanı eksik → ValueError."""
        data = json.dumps({"source_lang": "auto", "target_langs": ["en"]})
        with pytest.raises(ValueError, match="type"):
            parse_client_message(data)


class TestSerializeServerMessage:
    """serialize_server_message fonksiyonu testleri."""

    def test_round_trip(self) -> None:
        """Serialize → parse round-trip doğru çalışmalı."""
        original = PartialTranscript(
            text="hello", lang="en", speaker_id=0, confidence=0.9
        )
        json_str = serialize_server_message(original)
        data = json.loads(json_str)
        assert data["type"] == "partial_transcript"
        assert data["text"] == "hello"

    def test_translation_serialize(self) -> None:
        """TranslationResult serialize doğru çalışmalı."""
        msg = TranslationResult(
            source_text="test",
            source_lang="en",
            translations={"tr": "test"},
            speaker_id=0,
        )
        json_str = serialize_server_message(msg)
        data = json.loads(json_str)
        assert data["translations"]["tr"] == "test"
