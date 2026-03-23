"""Mock TTS — Azure Speech SDK olmadan geliştirme/test için."""

import logging
import struct
from typing import Protocol, runtime_checkable

from app.constants import TTS_SAMPLE_RATE

logger = logging.getLogger(__name__)

# 1 karakter ≈ 50ms audio
_MS_PER_CHAR = 50
_SAMPLES_PER_MS = TTS_SAMPLE_RATE // 1000  # 24


@runtime_checkable
class TTSEngine(Protocol):
    """TTS engine arayüzü."""

    async def synthesize(self, text: str, lang: str) -> bytes: ...


class MockTTS:
    """Mock TTS — sessiz PCM16 audio üretir (24kHz)."""

    async def synthesize(self, text: str, lang: str) -> bytes:
        """Mock TTS sentez — sessiz audio döndür.

        Args:
            text: Sentezlenecek metin.
            lang: Dil kodu.

        Returns:
            PCM16 LE bytes (24kHz, mono).
        """
        if not text:
            return b""

        duration_ms = len(text) * _MS_PER_CHAR
        num_samples = duration_ms * _SAMPLES_PER_MS
        audio = struct.pack(f"<{num_samples}h", *([0] * num_samples))

        logger.info(
            f"[MOCK_TTS] {lang}: {duration_ms}ms, "
            f"{len(audio)} bytes"
        )
        return audio


class AzureTTSEngine:
    """Azure Cognitive Services TTS — Speech SDK wrapper."""

    def __init__(self, api_key: str, region: str = "southeastasia") -> None:
        self._api_key = api_key
        self._region = region

    async def synthesize(self, text: str, lang: str) -> bytes:
        """Azure TTS sentez.

        Args:
            text: Sentezlenecek metin.
            lang: Dil kodu.

        Returns:
            PCM16 LE bytes (24kHz, mono).
        """
        if not text:
            return b""

        import asyncio

        from app.tts.voice_map import get_voice

        voice = get_voice(lang)
        ssml = self._build_ssml(text, voice.name, voice.lang_code)
        return await asyncio.to_thread(self._synthesize_sync, ssml)

    def _build_ssml(
        self, text: str, voice_name: str, lang_code: str
    ) -> str:
        """SSML template oluştur."""
        return (
            '<speak version="1.0" '
            f'xml:lang="{lang_code}">'
            f'<voice name="{voice_name}">{text}</voice>'
            "</speak>"
        )

    def _synthesize_sync(self, ssml: str) -> bytes:
        """Sync Azure SDK call (thread'de çalışır)."""
        import azure.cognitiveservices.speech as speechsdk

        config = speechsdk.SpeechConfig(
            subscription=self._api_key, region=self._region
        )
        config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Raw24Khz16BitMonoPcm
        )
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=config, audio_config=None
        )
        result = synthesizer.speak_ssml(ssml)
        return result.audio_data


def create_tts(
    use_mocks: bool = True,
    azure_key: str = "",
    azure_region: str = "southeastasia",
) -> TTSEngine:
    """TTS engine factory.

    Args:
        use_mocks: True → MockTTS, False → AzureTTSEngine.
        azure_key: Azure Speech subscription key.
        azure_region: Azure bölgesi.

    Returns:
        TTSEngine instance.
    """
    if use_mocks:
        logger.info("[TTS] Mock mode")
        return MockTTS()
    return AzureTTSEngine(api_key=azure_key, region=azure_region)
