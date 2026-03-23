"""Async CRUD repository — Session, Transcript, Translation."""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import (
    GlossaryDomain,
    GlossaryTerm,
    Session,
    Transcript,
    Translation,
)

logger = logging.getLogger(__name__)


async def create_session(
    db: AsyncSession,
    source_lang: str = "auto",
    target_langs: list[str] | None = None,
) -> Session:
    """Yeni session oluştur."""
    session = Session(
        source_lang=source_lang,
        target_langs=target_langs or [],
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def end_session(
    db: AsyncSession, session_id: str, duration_s: float
) -> None:
    """Session'ı bitir."""
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    if session:
        session.ended_at = datetime.utcnow()
        session.duration_s = duration_s
        await db.commit()


async def add_transcript(
    db: AsyncSession,
    session_id: str,
    speaker_id: int,
    text: str,
    lang: str,
    confidence: float,
) -> Transcript:
    """Transcript kaydet."""
    transcript = Transcript(
        session_id=session_id,
        speaker_id=speaker_id,
        text=text,
        lang=lang,
        confidence=confidence,
    )
    db.add(transcript)
    await db.commit()
    await db.refresh(transcript)
    return transcript


async def add_translation(
    db: AsyncSession,
    transcript_id: str,
    lang: str,
    text: str,
) -> Translation:
    """Translation kaydet."""
    translation = Translation(
        transcript_id=transcript_id,
        lang=lang,
        text=text,
    )
    db.add(translation)
    await db.commit()
    return translation


async def get_sessions(
    db: AsyncSession, offset: int = 0, limit: int = 20
) -> list[Session]:
    """Session listesi (pagination)."""
    result = await db.execute(
        select(Session)
        .order_by(Session.started_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_session_detail(
    db: AsyncSession, session_id: str
) -> Optional[Session]:
    """Session detay (transcripts + translations dahil)."""
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id)
        .options(
            selectinload(Session.transcripts).selectinload(
                Transcript.translations
            )
        )
    )
    return result.scalar_one_or_none()


async def delete_session(db: AsyncSession, session_id: str) -> bool:
    """Session sil (cascade: transcripts + translations)."""
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    if session:
        await db.delete(session)
        await db.commit()
        return True
    return False


async def get_stats(db: AsyncSession) -> dict:
    """Toplam istatistikler."""
    session_count = await db.scalar(select(func.count(Session.id)))
    transcript_count = await db.scalar(select(func.count(Transcript.id)))
    avg_duration = await db.scalar(select(func.avg(Session.duration_s)))
    return {
        "total_sessions": session_count or 0,
        "total_transcripts": transcript_count or 0,
        "avg_duration_s": round(avg_duration or 0, 2),
    }


async def get_glossary_domains(db: AsyncSession) -> list[GlossaryDomain]:
    """Glossary domain listesi."""
    result = await db.execute(select(GlossaryDomain))
    return list(result.scalars().all())


async def create_glossary_domain(
    db: AsyncSession, name: str, description: str = ""
) -> GlossaryDomain:
    """Yeni glossary domain oluştur."""
    domain = GlossaryDomain(name=name, description=description)
    db.add(domain)
    await db.commit()
    await db.refresh(domain)
    return domain


async def get_glossary_terms(
    db: AsyncSession, domain_id: str
) -> list[GlossaryTerm]:
    """Domain'e ait terimler."""
    result = await db.execute(
        select(GlossaryTerm).where(GlossaryTerm.domain_id == domain_id)
    )
    return list(result.scalars().all())


async def create_glossary_term(
    db: AsyncSession,
    domain_id: str,
    canonical_term: str,
    category: str = "",
    context_note: str = "",
) -> GlossaryTerm:
    """Yeni glossary terimi oluştur."""
    term = GlossaryTerm(
        domain_id=domain_id,
        canonical_term=canonical_term,
        category=category,
        context_note=context_note,
    )
    db.add(term)
    await db.commit()
    await db.refresh(term)
    return term
