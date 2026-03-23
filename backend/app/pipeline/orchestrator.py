"""Pipeline orchestrator — ASR → Translation akışı."""

import logging
import time
from typing import Optional, Union

from app.schemas import PartialTranscript, TranslationResult
from app.transcription.streaming import StreamingTranscriber
from app.translation.cache import TranslationCache
from app.translation.language_detect import resolve_source_language
from app.translation.mock_translator import Translator, create_translator

logger = logging.getLogger(__name__)

PipelineMessage = Union[PartialTranscript, TranslationResult]


class PipelineOrchestrator:
    """ASR → Translation pipeline.

    Args:
        use_mocks: Mock mode.
        target_langs: Hedef diller.
        config_source_lang: Client config kaynak dili.
    """

    def __init__(
        self,
        use_mocks: bool = True,
        target_langs: list[str] | None = None,
        config_source_lang: str = "auto",
        azure_key: str = "",
        azure_region: str = "southeastasia",
    ) -> None:
        self._transcriber = StreamingTranscriber(use_mocks=use_mocks)
        self._translator: Translator = create_translator(
            use_mocks=use_mocks,
            azure_key=azure_key,
            azure_region=azure_region,
        )
        self._cache = TranslationCache()
        self._target_langs = target_langs or ["en"]
        self._config_source_lang = config_source_lang

    async def process_chunk(
        self, chunk: bytes
    ) -> list[PipelineMessage]:
        """Chunk işle, transcript + translation mesajları döndür.

        Args:
            chunk: PCM16 audio chunk.

        Returns:
            Mesaj listesi (0, 1 veya 2 mesaj).
        """
        messages: list[PipelineMessage] = []

        transcript = self._transcriber.process_chunk(chunk)
        if transcript is None:
            return messages

        messages.append(transcript)

        if not transcript.text:
            return messages

        source_lang = resolve_source_language(
            whisper_lang=transcript.lang,
            whisper_confidence=transcript.confidence,
            config_lang=self._config_source_lang,
        )

        translation = await self._translate_with_cache(
            transcript.text, source_lang
        )
        if translation:
            messages.append(translation)

        return messages

    async def _translate_with_cache(
        self, text: str, source_lang: str
    ) -> Optional[TranslationResult]:
        """Cache kontrollü çeviri."""
        translations: dict[str, str] = {}
        uncached_langs: list[str] = []

        for lang in self._target_langs:
            if lang == source_lang:
                continue
            cached = self._cache.get(text, source_lang, lang)
            if cached is not None:
                translations[lang] = cached
            else:
                uncached_langs.append(lang)

        if uncached_langs:
            start = time.perf_counter()
            fresh = await self._translator.translate(
                text, source_lang, uncached_langs
            )
            duration = (time.perf_counter() - start) * 1000
            logger.info(f"[PIPELINE] Translation: {duration:.1f}ms")

            for lang, translated in fresh.items():
                translations[lang] = translated
                self._cache.set(text, source_lang, lang, translated)

        if not translations:
            return None

        return TranslationResult(
            source_text=text,
            source_lang=source_lang,
            translations=translations,
            speaker_id=0,
        )
