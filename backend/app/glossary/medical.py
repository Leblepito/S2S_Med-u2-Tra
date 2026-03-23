"""Medikal glossary pre-processor — terim tespiti + bağlam ekleme."""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import GlossaryDomain, GlossaryTerm, GlossaryTranslation
from app.glossary.base import GlossaryPreProcessor
from app.schemas import PartialTranscript

logger = logging.getLogger(__name__)


class _TermEntry:
    """Cache'lenmiş terim bilgisi."""

    def __init__(
        self, canonical: str, category: str, aliases: list[str]
    ) -> None:
        self.canonical = canonical
        self.category = category
        self.search_terms = [canonical.lower()] + [a.lower() for a in aliases]


class DomainPreProcessor(GlossaryPreProcessor):
    """Domain-based glossary pre-processor. Lazy DB load + cache.

    Args:
        domain_name: Glossary domain adı ("medical", "tourism").
    """

    def __init__(self, domain_name: str) -> None:
        self._domain_name = domain_name
        self._terms: list[_TermEntry] = []
        self._loaded: bool = False

    async def load_terms(self, db: AsyncSession) -> None:
        """DB'den terimleri yükle ve cache'le."""
        result = await db.execute(
            select(GlossaryDomain).where(
                GlossaryDomain.name == self._domain_name
            )
        )
        domain = result.scalar_one_or_none()
        if not domain:
            logger.warning(f"[GLOSSARY] Domain '{self._domain_name}' not found")
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
            aliases = []
            for tr in trans_result.scalars().all():
                aliases.append(tr.translation)
                if tr.aliases:
                    aliases.extend(tr.aliases)

            self._terms.append(_TermEntry(
                canonical=term.canonical_term,
                category=term.category or "",
                aliases=aliases,
            ))

        self._loaded = True
        logger.info(
            f"[GLOSSARY] {self._domain_name}: {len(self._terms)} terim yüklendi"
        )

    async def process(
        self, transcript: PartialTranscript
    ) -> PartialTranscript:
        """Transcript'te terim ara, detected_terms'e ekle."""
        if not self._loaded or not transcript.text:
            return transcript

        text_lower = transcript.text.lower()
        detected: list[str] = []

        for entry in self._terms:
            for search in entry.search_terms:
                if search in text_lower:
                    detected.append(entry.canonical)
                    break

        if detected:
            transcript = transcript.model_copy(
                update={"detected_terms": detected}
            )
            logger.info(
                f"[GLOSSARY] Detected: {detected} in '{transcript.text[:40]}'"
            )

        return transcript


class MedicalPreProcessor(DomainPreProcessor):
    """Medikal terim tespiti."""

    def __init__(self) -> None:
        super().__init__("medical")


class TourismPreProcessor(DomainPreProcessor):
    """Turizm terim tespiti."""

    def __init__(self) -> None:
        super().__init__("tourism")
