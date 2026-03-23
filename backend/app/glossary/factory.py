"""Glossary processor factory — config'e göre doğru class döndürür."""

import logging

from app.glossary.base import (
    ContextEnricher,
    GlossaryPostProcessor,
    GlossaryPreProcessor,
)
from app.glossary.passthrough import (
    PassthroughEnricher,
    PassthroughPostProcessor,
    PassthroughPreProcessor,
)

logger = logging.getLogger(__name__)


def create_pre_processor(mode: str = "passthrough") -> GlossaryPreProcessor:
    """GlossaryPreProcessor factory.

    Args:
        mode: Processor modu ("passthrough", post-MVP: "medical", "travel").

    Returns:
        GlossaryPreProcessor instance.
    """
    if mode == "passthrough":
        return PassthroughPreProcessor()
    msg = f"Unknown pre_processor mode: {mode}"
    raise ValueError(msg)


def create_post_processor(
    mode: str = "passthrough",
) -> GlossaryPostProcessor:
    """GlossaryPostProcessor factory.

    Args:
        mode: Processor modu.

    Returns:
        GlossaryPostProcessor instance.
    """
    if mode == "passthrough":
        return PassthroughPostProcessor()
    msg = f"Unknown post_processor mode: {mode}"
    raise ValueError(msg)


def create_enricher(mode: str = "passthrough") -> ContextEnricher:
    """ContextEnricher factory.

    Args:
        mode: Enricher modu.

    Returns:
        ContextEnricher instance.
    """
    if mode == "passthrough":
        return PassthroughEnricher()
    msg = f"Unknown enricher mode: {mode}"
    raise ValueError(msg)
