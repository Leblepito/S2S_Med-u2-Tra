"""Admin API routes — session, stats, glossary yönetimi."""

import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database import repository as repo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


class DomainCreate(BaseModel):
    name: str
    description: str = ""


class TermCreate(BaseModel):
    domain_id: str
    canonical_term: str
    category: str = ""
    context_note: str = ""


@router.get("/sessions")
async def list_sessions(
    offset: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)
) -> dict:
    """Session listesi (pagination)."""
    sessions = await repo.get_sessions(db, offset=offset, limit=limit)
    return {
        "sessions": [
            {
                "id": s.id,
                "started_at": s.started_at.isoformat(),
                "duration_s": s.duration_s,
                "source_lang": s.source_lang,
                "target_langs": s.target_langs,
            }
            for s in sessions
        ]
    }


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str, db: AsyncSession = Depends(get_db)
) -> dict:
    """Session detay (transcripts + translations)."""
    session = await repo.get_session_detail(db, session_id)
    if not session:
        return {"error": "Session not found"}
    return {
        "id": session.id,
        "started_at": session.started_at.isoformat(),
        "duration_s": session.duration_s,
        "source_lang": session.source_lang,
        "target_langs": session.target_langs,
        "transcripts": [
            {
                "id": t.id,
                "speaker_id": t.speaker_id,
                "text": t.text,
                "lang": t.lang,
                "confidence": t.confidence,
                "translations": [
                    {"lang": tr.lang, "text": tr.text}
                    for tr in t.translations
                ],
            }
            for t in session.transcripts
        ],
    }


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str, db: AsyncSession = Depends(get_db)
) -> dict:
    """Session sil."""
    deleted = await repo.delete_session(db, session_id)
    return {"deleted": deleted}


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)) -> dict:
    """Toplam istatistikler."""
    return await repo.get_stats(db)


@router.get("/glossary/domains")
async def list_domains(db: AsyncSession = Depends(get_db)) -> dict:
    """Glossary domain listesi."""
    domains = await repo.get_glossary_domains(db)
    return {
        "domains": [
            {"id": d.id, "name": d.name, "description": d.description}
            for d in domains
        ]
    }


@router.post("/glossary/domains")
async def create_domain(
    body: DomainCreate, db: AsyncSession = Depends(get_db)
) -> dict:
    """Yeni glossary domain oluştur."""
    domain = await repo.create_glossary_domain(
        db, name=body.name, description=body.description
    )
    return {"id": domain.id, "name": domain.name}


@router.get("/glossary/terms")
async def list_terms(
    domain_id: str, db: AsyncSession = Depends(get_db)
) -> dict:
    """Domain'e ait terimler."""
    terms = await repo.get_glossary_terms(db, domain_id)
    return {
        "terms": [
            {
                "id": t.id,
                "canonical_term": t.canonical_term,
                "category": t.category,
            }
            for t in terms
        ]
    }


@router.post("/glossary/terms")
async def create_term(
    body: TermCreate, db: AsyncSession = Depends(get_db)
) -> dict:
    """Yeni glossary terimi oluştur."""
    term = await repo.create_glossary_term(
        db,
        domain_id=body.domain_id,
        canonical_term=body.canonical_term,
        category=body.category,
        context_note=body.context_note,
    )
    return {"id": term.id, "canonical_term": term.canonical_term}


@router.get("/glossary/export")
async def export_glossary(db: AsyncSession = Depends(get_db)) -> dict:
    """Tüm glossary'yi JSON olarak export et."""
    domains = await repo.get_glossary_domains(db)
    result = []
    for d in domains:
        terms = await repo.get_glossary_terms(db, d.id)
        term_list = []
        for t in terms:
            translations = await repo.get_glossary_term_translations(db, t.id)
            trans_dict = {tr.language: tr.translation for tr in translations}
            term_list.append({
                "canonical_term": t.canonical_term,
                "category": t.category or "",
                "translations": trans_dict,
            })
        result.append({
            "name": d.name,
            "description": d.description or "",
            "terms": term_list,
        })
    return {"domains": result}
