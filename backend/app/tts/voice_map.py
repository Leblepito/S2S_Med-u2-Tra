"""Dil → Azure TTS ses eşlemesi."""

import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class VoiceConfig(BaseModel):
    """TTS ses konfigürasyonu."""

    name: str
    lang_code: str


_VOICE_MAP: dict[str, VoiceConfig] = {
    "tr": VoiceConfig(name="tr-TR-AhmetNeural", lang_code="tr-TR"),
    "ru": VoiceConfig(name="ru-RU-DmitryNeural", lang_code="ru-RU"),
    "en": VoiceConfig(name="en-US-JennyNeural", lang_code="en-US"),
    "th": VoiceConfig(name="th-TH-PremwadeeNeural", lang_code="th-TH"),
    "vi": VoiceConfig(name="vi-VN-HoaiMyNeural", lang_code="vi-VN"),
    "zh": VoiceConfig(name="zh-CN-XiaoxiaoNeural", lang_code="zh-CN"),
    "id": VoiceConfig(name="id-ID-ArdiNeural", lang_code="id-ID"),
}

_FALLBACK = _VOICE_MAP["en"]


def get_voice(lang: str) -> VoiceConfig:
    """Dil kodu için TTS ses konfigürasyonu döndür.

    Args:
        lang: 2 harfli dil kodu.

    Returns:
        VoiceConfig. Bilinmeyen dil → en fallback.
    """
    voice = _VOICE_MAP.get(lang, _FALLBACK)
    if lang not in _VOICE_MAP:
        logger.warning(f"[VOICE] Bilinmeyen dil '{lang}', fallback: en")
    return voice
