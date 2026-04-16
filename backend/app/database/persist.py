"""Non-blocking DB persistence — fire-and-forget helpers."""

import asyncio
import logging

from app.database.connection import get_session_factory
from app.database import repository as repo

logger = logging.getLogger(__name__)


async def persist_session_start(
    source_lang: str, target_langs: list[str]
) -> str:
    """Session oluştur, id döndür. Hata → boş string."""
    try:
        factory = get_session_factory()
        async with factory() as db:
            session = await repo.create_session(
                db, source_lang=source_lang, target_langs=target_langs
            )
            return session.id
    except Exception as e:
        logger.warning(f"[DB] Session create failed: {e}")
        return ""


async def persist_session_end(session_id: str, duration_s: float) -> None:
    """Session'ı bitir. Fire-and-forget."""
    if not session_id:
        return
    try:
        factory = get_session_factory()
        async with factory() as db:
            await repo.end_session(db, session_id, duration_s)
    except Exception as e:
        logger.warning(f"[DB] Session end failed: {e}")


async def persist_transcript(
    session_id: str,
    speaker_id: int,
    text: str,
    lang: str,
    confidence: float,
    translations: dict[str, str] | None = None,
) -> None:
    """Transcript + translations kaydet. Fire-and-forget."""
    if not session_id or not text:
        return
    try:
        factory = get_session_factory()
        async with factory() as db:
            transcript = await repo.add_transcript(
                db, session_id, speaker_id, text, lang, confidence
            )
            if translations:
                for t_lang, t_text in translations.items():
                    await repo.add_translation(
                        db, transcript.id, t_lang, t_text
                    )
    except Exception as e:
        logger.warning(f"[DB] Transcript persist failed: {e}")


def fire_and_forget(coro) -> None:
    """Coroutine'i background task olarak çalıştır."""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(coro)
    except RuntimeError:
        logger.warning("[DB] No running loop for fire-and-forget")
