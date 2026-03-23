"""BabelFlow WebSocket protokol mesaj şemaları — Pydantic V2."""

import json
import logging
from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator

from app.constants import SUPPORTED_LANGS

logger = logging.getLogger(__name__)

_VALID_SOURCE_LANGS = SUPPORTED_LANGS | {"auto"}


class ConfigMessage(BaseModel):
    """Client → Server: Oturum konfigürasyonu."""

    type: str = Field(default="config", frozen=True)
    source_lang: str = "auto"
    target_langs: list[str]
    enable_diarization: bool = False

    @field_validator("source_lang")
    @classmethod
    def validate_source_lang(cls, v: str) -> str:
        """Kaynak dil desteklenen diller veya 'auto' olmalı."""
        if v not in _VALID_SOURCE_LANGS:
            msg = f"Desteklenmeyen kaynak dil: {v}"
            raise ValueError(msg)
        return v

    @field_validator("target_langs")
    @classmethod
    def validate_target_langs(cls, v: list[str]) -> list[str]:
        """Hedef diller boş olmamalı ve desteklenmeli."""
        if not v:
            msg = "En az bir hedef dil gerekli"
            raise ValueError(msg)
        invalid = set(v) - SUPPORTED_LANGS
        if invalid:
            msg = f"Desteklenmeyen hedef dil(ler): {invalid}"
            raise ValueError(msg)
        return v


class PartialTranscript(BaseModel):
    """Server → Client: Kısmi transcription sonucu."""

    type: str = Field(default="partial_transcript", frozen=True)
    text: str
    lang: str
    speaker_id: int
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("lang")
    @classmethod
    def validate_lang(cls, v: str) -> str:
        """Dil desteklenen diller arasında olmalı."""
        if v not in SUPPORTED_LANGS:
            msg = f"Desteklenmeyen dil: {v}"
            raise ValueError(msg)
        return v


class FinalTranscript(BaseModel):
    """Server → Client: Final transcription sonucu."""

    type: str = Field(default="final_transcript", frozen=True)
    text: str
    lang: str
    speaker_id: int
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("lang")
    @classmethod
    def validate_lang(cls, v: str) -> str:
        """Dil desteklenen diller arasında olmalı."""
        if v not in SUPPORTED_LANGS:
            msg = f"Desteklenmeyen dil: {v}"
            raise ValueError(msg)
        return v


class TranslationResult(BaseModel):
    """Server → Client: Çeviri sonucu."""

    type: str = Field(default="translation", frozen=True)
    source_text: str
    source_lang: str
    translations: dict[str, str]
    speaker_id: int

    @field_validator("source_lang")
    @classmethod
    def validate_source_lang(cls, v: str) -> str:
        """Kaynak dil desteklenen diller arasında olmalı."""
        if v not in SUPPORTED_LANGS:
            msg = f"Desteklenmeyen kaynak dil: {v}"
            raise ValueError(msg)
        return v


class TTSHeader(BaseModel):
    """Binary TTS audio frame'inin JSON header'ı."""

    type: str = Field(default="tts_audio", frozen=True)
    lang: str
    chunk_index: int = Field(ge=0)


class ErrorResponse(BaseModel):
    """Server → Client: Hata mesajı."""

    type: str = Field(default="error", frozen=True)
    message: str
    code: Optional[str] = None


# Tüm server→client mesaj tipleri
ServerMessage = Union[
    PartialTranscript,
    FinalTranscript,
    TranslationResult,
    ErrorResponse,
]


def parse_client_message(data: str) -> ConfigMessage:
    """JSON string'i ConfigMessage'a parse et.

    Args:
        data: JSON string.

    Returns:
        ConfigMessage instance.

    Raises:
        ValueError: Geçersiz JSON, eksik/bilinmeyen type.
    """
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        msg = f"Geçersiz JSON: {e}"
        raise ValueError(msg) from e

    if not isinstance(parsed, dict) or "type" not in parsed:
        msg = "Mesajda 'type' alanı eksik"
        raise ValueError(msg)

    if parsed["type"] != "config":
        msg = f"Bilinmeyen mesaj type: {parsed['type']}"
        raise ValueError(msg)

    return ConfigMessage(**parsed)


def serialize_server_message(msg: ServerMessage) -> str:
    """Server mesajını JSON string'e serialize et.

    Args:
        msg: Server mesaj instance'ı.

    Returns:
        JSON string.
    """
    return msg.model_dump_json()
