"""Passthrough glossary — MVP'de hiçbir şey yapmaz, girdiyi aynen döner."""

from app.glossary.base import (
    ContextEnricher,
    EnrichedResult,
    GlossaryPostProcessor,
    GlossaryPreProcessor,
)
from app.schemas import PartialTranscript, TranslationResult


class PassthroughPreProcessor(GlossaryPreProcessor):
    """MVP: sözlük yok, transcript direkt geçer."""

    async def process(
        self, transcript: PartialTranscript
    ) -> PartialTranscript:
        return transcript


class PassthroughPostProcessor(GlossaryPostProcessor):
    """MVP: düzeltme yok, translation direkt geçer."""

    async def process(
        self, translation: TranslationResult
    ) -> TranslationResult:
        return translation


class PassthroughEnricher(ContextEnricher):
    """MVP: zenginleştirme yok, boş EnrichedResult döner."""

    async def enrich(
        self, translation: TranslationResult
    ) -> EnrichedResult:
        return EnrichedResult(translation=translation)
