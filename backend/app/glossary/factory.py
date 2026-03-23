"""Glossary processor factory — config'e göre doğru class döndürür."""

import logging

from app.glossary.base import (
    ContextEnricher,
    GlossaryPostProcessor,
    GlossaryPreProcessor,
)
from app.glossary.medical import MedicalPreProcessor, TourismPreProcessor
from app.glossary.passthrough import (
    PassthroughEnricher,
    PassthroughPostProcessor,
    PassthroughPreProcessor,
)
from app.glossary.post_processor import (
    MedicalPostProcessor,
    TourismPostProcessor,
)

logger = logging.getLogger(__name__)


def create_pre_processor(mode: str = "passthrough") -> GlossaryPreProcessor:
    """GlossaryPreProcessor factory.

    Args:
        mode: "passthrough", "medical", "tourism".
    """
    if mode == "passthrough":
        return PassthroughPreProcessor()
    if mode == "medical":
        return MedicalPreProcessor()
    if mode == "tourism":
        return TourismPreProcessor()
    msg = f"Unknown pre_processor mode: {mode}"
    raise ValueError(msg)


def create_post_processor(
    mode: str = "passthrough",
) -> GlossaryPostProcessor:
    """GlossaryPostProcessor factory.

    Args:
        mode: "passthrough", "medical", "tourism".
    """
    if mode == "passthrough":
        return PassthroughPostProcessor()
    if mode == "medical":
        return MedicalPostProcessor()
    if mode == "tourism":
        return TourismPostProcessor()
    msg = f"Unknown post_processor mode: {mode}"
    raise ValueError(msg)


def create_enricher(mode: str = "passthrough") -> ContextEnricher:
    """ContextEnricher factory."""
    if mode in {"passthrough", "medical", "tourism"}:
        return PassthroughEnricher()
    msg = f"Unknown enricher mode: {mode}"
    raise ValueError(msg)
