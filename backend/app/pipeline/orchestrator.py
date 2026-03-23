"""Pipeline orchestrator — ASR → Diarize → Glossary → Translation → TTS."""

import logging
from typing import Any, Optional, Union

from app.audio.diarization import SpeakerDiarizer, create_diarizer
from app.glossary.base import (
    ContextEnricher,
    EnrichedResult,
    GlossaryPostProcessor,
    GlossaryPreProcessor,
)
from app.glossary.factory import (
    create_enricher,
    create_post_processor,
    create_pre_processor,
)
from app.pipeline.latency_monitor import LatencyMonitor
from app.schemas import PartialTranscript, TTSHeader, TranslationResult
from app.transcription.streaming import StreamingTranscriber
from app.translation.cache import TranslationCache
from app.translation.language_detect import resolve_source_language
from app.translation.mock_translator import Translator, create_translator
from app.tts.mock_tts import TTSEngine, create_tts

logger = logging.getLogger(__name__)

PipelineMessage = Union[PartialTranscript, TranslationResult]


class TTSResult:
    """TTS sentez sonucu — lang + audio bytes."""

    def __init__(self, lang: str, audio: bytes) -> None:
        self.lang = lang
        self.audio = audio


class PipelineOrchestrator:
    """ASR → Glossary Pre → Translation → Glossary Post → Enrich → TTS.

    Args:
        use_mocks: Mock mode.
        target_langs: Hedef diller.
        config_source_lang: Client config kaynak dili.
        glossary_mode: Glossary processor modu.
    """

    def __init__(
        self,
        use_mocks: bool = True,
        target_langs: list[str] | None = None,
        config_source_lang: str = "auto",
        azure_key: str = "",
        azure_region: str = "southeastasia",
        azure_speech_key: str = "",
        azure_speech_region: str = "southeastasia",
        enable_tts: bool = True,
        enable_diarization: bool = False,
        glossary_mode: str = "passthrough",
    ) -> None:
        self._transcriber = StreamingTranscriber(use_mocks=use_mocks)
        self._diarizer: SpeakerDiarizer = create_diarizer(use_mocks=use_mocks)
        self._enable_diarization = enable_diarization
        self._speaker_langs: dict[int, str] = {}  # per-speaker dil takibi
        self._translator: Translator = create_translator(
            use_mocks=use_mocks,
            azure_key=azure_key,
            azure_region=azure_region,
        )
        self._tts: TTSEngine = create_tts(
            use_mocks=use_mocks,
            azure_key=azure_speech_key,
            azure_region=azure_speech_region,
        )
        self._pre: GlossaryPreProcessor = create_pre_processor(glossary_mode)
        self._post: GlossaryPostProcessor = create_post_processor(glossary_mode)
        self._enricher: ContextEnricher = create_enricher(glossary_mode)
        self._cache = TranslationCache()
        self._monitor = LatencyMonitor()
        self._target_langs = target_langs or ["en"]
        self._config_source_lang = config_source_lang
        self._enable_tts = enable_tts
        self._last_enriched: Optional[EnrichedResult] = None

    @property
    def latency_stats(self) -> dict[str, Any]:
        """Latency istatistikleri."""
        return self._monitor.get_stats()

    @property
    def last_enriched(self) -> Optional[EnrichedResult]:
        """Son enrichment sonucu."""
        return self._last_enriched

    async def process_chunk(
        self, chunk: bytes
    ) -> tuple[list[PipelineMessage], list[TTSResult]]:
        """Chunk → ASR → Diarize → Glossary → Translation → TTS.

        Returns:
            (mesajlar, tts_results) tuple.
        """
        messages: list[PipelineMessage] = []
        tts_results: list[TTSResult] = []

        self._monitor.start_stage("asr")
        stream_result = self._transcriber.process_chunk_with_segment(chunk)
        self._monitor.end_stage("asr")

        if stream_result is None:
            return messages, tts_results

        transcript = stream_result.transcript

        # Speaker diarization
        if self._enable_diarization:
            self._monitor.start_stage("diarize")
            speaker_id = self._diarizer.identify(stream_result.segment)
            self._monitor.end_stage("diarize")
            transcript = PartialTranscript(
                text=transcript.text,
                lang=transcript.lang,
                speaker_id=speaker_id,
                confidence=transcript.confidence,
            )
            self._speaker_langs[speaker_id] = transcript.lang

        # Glossary pre-process
        self._monitor.start_stage("glossary_pre")
        transcript = await self._pre.process(transcript)
        self._monitor.end_stage("glossary_pre")

        messages.append(transcript)
        if not transcript.text:
            return messages, tts_results

        source_lang = resolve_source_language(
            whisper_lang=transcript.lang,
            whisper_confidence=transcript.confidence,
            config_lang=self._config_source_lang,
        )

        self._monitor.start_stage("translate")
        translation = await self._translate_with_cache(
            transcript.text, source_lang, transcript.speaker_id
        )
        self._monitor.end_stage("translate")

        if translation:
            # Glossary post-process
            self._monitor.start_stage("glossary_post")
            translation = await self._post.process(translation)
            self._monitor.end_stage("glossary_post")

            # Context enrichment
            self._monitor.start_stage("enrich")
            self._last_enriched = await self._enricher.enrich(translation)
            self._monitor.end_stage("enrich")

            messages.append(translation)

            if self._enable_tts:
                tts_results = await self._synthesize_all(
                    translation.translations
                )

        return messages, tts_results

    async def _translate_with_cache(
        self, text: str, source_lang: str, speaker_id: int = 0
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
            fresh = await self._translator.translate(
                text, source_lang, uncached_langs
            )
            for lang, translated in fresh.items():
                translations[lang] = translated
                self._cache.set(text, source_lang, lang, translated)

        if not translations:
            return None

        return TranslationResult(
            source_text=text,
            source_lang=source_lang,
            translations=translations,
            speaker_id=speaker_id,
        )

    async def _synthesize_all(
        self, translations: dict[str, str]
    ) -> list[TTSResult]:
        """Tüm çeviriler için TTS sentez."""
        results: list[TTSResult] = []
        for lang, text in translations.items():
            if not text:
                continue
            self._monitor.start_stage("tts")
            audio = await self._tts.synthesize(text, lang)
            self._monitor.end_stage("tts")
            if audio:
                results.append(TTSResult(lang=lang, audio=audio))
        return results
