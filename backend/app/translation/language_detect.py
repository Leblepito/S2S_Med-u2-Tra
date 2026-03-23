"""Dil tespit stratejisi — Whisper primary, config fallback."""

import logging

logger = logging.getLogger(__name__)


def resolve_source_language(
    whisper_lang: str,
    whisper_confidence: float,
    config_lang: str,
    confidence_threshold: float = 0.5,
) -> str:
    """Kaynak dili belirle: config belirli ise config, değilse Whisper.

    Args:
        whisper_lang: Whisper'ın tespit ettiği dil.
        whisper_confidence: Whisper confidence (0-1).
        config_lang: Client config'inden gelen dil ("auto" veya kod).
        confidence_threshold: Whisper confidence eşiği.

    Returns:
        Belirlenen kaynak dil kodu.
    """
    # Config belirli dil belirtmişse → her zaman config
    if config_lang != "auto":
        logger.info(f"[LANG] Config override: {config_lang}")
        return config_lang

    # Auto mode → Whisper sonucunu kullan
    logger.info(
        f"[LANG] Whisper: {whisper_lang} "
        f"({whisper_confidence:.2f})"
    )
    return whisper_lang
