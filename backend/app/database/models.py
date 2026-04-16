"""SQLAlchemy ORM modelleri."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


def _uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class Session(Base):
    """WebSocket translation session."""

    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=_uuid)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_s = Column(Float, nullable=True)
    speaker_count = Column(Integer, default=1)
    source_lang = Column(String(5), default="auto")
    target_langs = Column(JSON, default=list)

    transcripts = relationship(
        "Transcript", back_populates="session", cascade="all, delete-orphan"
    )


class Transcript(Base):
    """ASR transcription kaydı."""

    __tablename__ = "transcripts"

    id = Column(String(36), primary_key=True, default=_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    speaker_id = Column(Integer, default=0)
    text = Column(Text)
    lang = Column(String(5))
    confidence = Column(Float)

    session = relationship("Session", back_populates="transcripts")
    translations = relationship(
        "Translation", back_populates="transcript", cascade="all, delete-orphan"
    )


class Translation(Base):
    """Çeviri kaydı."""

    __tablename__ = "translations"

    id = Column(String(36), primary_key=True, default=_uuid)
    transcript_id = Column(String(36), ForeignKey("transcripts.id"))
    lang = Column(String(5))
    text = Column(Text)

    transcript = relationship("Transcript", back_populates="translations")


class GlossaryDomain(Base):
    """Sözlük domain'i."""

    __tablename__ = "glossary_domains"

    id = Column(String(36), primary_key=True, default=_uuid)
    name = Column(String(50), unique=True)
    description = Column(Text, nullable=True)

    terms = relationship(
        "GlossaryTerm", back_populates="domain", cascade="all, delete-orphan"
    )


class GlossaryTerm(Base):
    """Sözlük terimi."""

    __tablename__ = "glossary_terms"

    id = Column(String(36), primary_key=True, default=_uuid)
    domain_id = Column(String(36), ForeignKey("glossary_domains.id"))
    canonical_term = Column(String(255))
    category = Column(String(100), nullable=True)
    context_note = Column(Text, nullable=True)

    domain = relationship("GlossaryDomain", back_populates="terms")
    translations = relationship(
        "GlossaryTranslation", back_populates="term", cascade="all, delete-orphan"
    )


class GlossaryTranslation(Base):
    """Sözlük terim çevirisi."""

    __tablename__ = "glossary_translations"

    id = Column(String(36), primary_key=True, default=_uuid)
    term_id = Column(String(36), ForeignKey("glossary_terms.id"))
    language = Column(String(5))
    translation = Column(String(500))
    aliases = Column(JSON, default=list)

    term = relationship("GlossaryTerm", back_populates="translations")
