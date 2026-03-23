"""Voice map testleri."""

import pytest

from app.tts.voice_map import VoiceConfig, get_voice


class TestGetVoice:
    """get_voice fonksiyonu testleri."""

    @pytest.mark.parametrize(
        "lang,expected_name",
        [
            ("tr", "tr-TR-AhmetNeural"),
            ("ru", "ru-RU-DmitryNeural"),
            ("en", "en-US-JennyNeural"),
            ("th", "th-TH-PremwadeeNeural"),
            ("vi", "vi-VN-HoaiMyNeural"),
            ("zh", "zh-CN-XiaoxiaoNeural"),
            ("id", "id-ID-ArdiNeural"),
        ],
    )
    def test_all_7_langs(self, lang: str, expected_name: str) -> None:
        """7 dil için doğru voice dönmeli."""
        voice = get_voice(lang)
        assert isinstance(voice, VoiceConfig)
        assert voice.name == expected_name

    def test_unknown_lang_fallback(self) -> None:
        """Bilinmeyen dil → en fallback."""
        voice = get_voice("xx")
        assert voice.name == "en-US-JennyNeural"

    def test_voice_has_lang_code(self) -> None:
        """VoiceConfig lang_code içermeli."""
        voice = get_voice("tr")
        assert voice.lang_code == "tr-TR"
