"""Mock translator — Azure olmadan geliştirme/test için."""

import logging
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class Translator(Protocol):
    """Translator arayüzü."""

    async def translate(
        self, text: str, source_lang: str, target_langs: list[str]
    ) -> dict[str, str]: ...


class MockTranslator:
    """Mock translator — '[XX→YY] text' formatında sahte çeviri döndürür."""

    async def translate(
        self, text: str, source_lang: str, target_langs: list[str]
    ) -> dict[str, str]:
        """Mock çeviri.

        Args:
            text: Kaynak metin.
            source_lang: Kaynak dil kodu.
            target_langs: Hedef dil kodları.

        Returns:
            {lang: çeviri} dict.
        """
        if not text:
            return {lang: "" for lang in target_langs}

        src = source_lang.upper()
        result = {
            lang: f"[{src}→{lang.upper()}] {text}"
            for lang in target_langs
        }
        logger.info(
            f"[MOCK_TRANSLATE] {source_lang}→{target_langs}: "
            f"'{text[:30]}'"
        )
        return result


def create_translator(
    use_mocks: bool = True,
    azure_key: str = "",
    azure_region: str = "southeastasia",
) -> Translator:
    """Translator factory.

    Args:
        use_mocks: True → MockTranslator, False → AzureTranslator.
        azure_key: Azure Translator API key.
        azure_region: Azure bölgesi.

    Returns:
        Translator instance.
    """
    if use_mocks:
        logger.info("[TRANSLATOR] Mock mode")
        return MockTranslator()

    from app.translation.azure_translator import AzureTranslator

    return AzureTranslator(api_key=azure_key, region=azure_region)
