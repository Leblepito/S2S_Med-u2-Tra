"""Glossary pipeline hook abstract base class'ları."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from app.schemas import PartialTranscript, TranslationResult


class GlossaryPreProcessor(ABC):
    """ASR çıktısını Translation'a göndermeden önce işle.

    MVP: passthrough (terim tespiti yok).
    Post-MVP: medikal/turizm terimleri tespit, bağlam ekleme.
    """

    @abstractmethod
    async def process(
        self, transcript: PartialTranscript
    ) -> PartialTranscript: ...


class GlossaryPostProcessor(ABC):
    """Translation çıktısını TTS'e göndermeden önce düzelt.

    MVP: passthrough (düzeltme yok).
    Post-MVP: sözlük bazlı düzeltme, ton kontrolü.
    """

    @abstractmethod
    async def process(
        self, translation: TranslationResult
    ) -> TranslationResult: ...


class ContextEnricher(ABC):
    """Konuşma bağlamını analiz et ve zenginleştir.

    MVP: passthrough (analiz yok).
    Post-MVP: özet, niyet tespiti, aksiyon belirleme.
    """

    @abstractmethod
    async def enrich(
        self, translation: TranslationResult
    ) -> "EnrichedResult": ...


@dataclass
class EnrichedResult:
    """Context enrichment sonucu."""

    translation: TranslationResult
    summary: Optional[str] = None
    intent: Optional[str] = None
    actions: list[str] = field(default_factory=list)
