"""Glossary post-processor — çeviri düzeltme + glossary notes."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import GlossaryDomain, GlossaryTerm, GlossaryTranslation
from app.glossary.base import GlossaryPostProcessor
from app.schemas import TranslationResult

logger = logging.getLogger(__name__)


class _TranslationEntry:
    """Cache'lenmiş terim çevirisi."""

    def __init__(self, canonical: str, lang: str, correct: str) -> None:
        self.canonical = canonical
        self.lang = lang
        self.correct = correct


class DomainPostProcessor(GlossaryPostProcessor):
    """Domain-based glossary post-processor — yanlış çeviri düzeltme.

    Args:
        domain_name: Glossary domain adı.
    """

    def __init__(self, domain_name: str) -> None:
        self._domain_name = domain_name
        self._corrections: dict[str, list[_TranslationEntry]] = {}
        self._loaded: bool = False

    async def load_terms(self, db: AsyncSession) -> None:
        """DB'den terim çevirilerini yükle."""
        result = await db.execute(
            select(GlossaryDomain).where(
                GlossaryDomain.name == self._domain_name
            )
        )
        domain = result.scalar_one_or_none()
        if not domain:
            self._loaded = True
            return

        terms_result = await db.execute(
            select(GlossaryTerm).where(GlossaryTerm.domain_id == domain.id)
        )
        for term in terms_result.scalars().all():
            trans_result = await db.execute(
                select(GlossaryTranslation).where(
                    GlossaryTranslation.term_id == term.id
                )
            )
            entries = []
            for tr in trans_result.scalars().all():
                entries.append(_TranslationEntry(
                    canonical=term.canonical_term,
                    lang=tr.language,
                    correct=tr.translation,
                ))
            self._corrections[term.canonical_term.lower()] = entries

        self._loaded = True
        logger.info(
            f"[GLOSSARY_POST] {self._domain_name}: "
            f"{len(self._corrections)} terim yüklendi"
        )

    async def process(
        self, translation: TranslationResult
    ) -> TranslationResult:
        """Çevirilerden glossary ile uyumsuz olanları düzelt."""
        if not self._loaded:
            return translation

        notes: list[str] = list(translation.glossary_notes)
        updated_translations = dict(translation.translations)
        source_lower = translation.source_text.lower()

        for canonical, entries in self._corrections.items():
            if canonical not in source_lower:
                continue
            for entry in entries:
                if entry.lang not in updated_translations:
                    continue
                current = updated_translations[entry.lang]
                if entry.correct.lower() not in current.lower():
                    notes.append(
                        f"Glossary [{entry.lang}]: {canonical} → {entry.correct}"
                    )

        if notes != list(translation.glossary_notes):
            translation = translation.model_copy(
                update={
                    "glossary_notes": notes,
                    "translations": updated_translations,
                }
            )

        return translation


class MedicalPostProcessor(DomainPostProcessor):
    """Medikal çeviri düzeltme."""

    def __init__(self) -> None:
        super().__init__("medical")


class TourismPostProcessor(DomainPostProcessor):
    """Turizm çeviri düzeltme."""

    def __init__(self) -> None:
        super().__init__("tourism")
