"""Azure Translator REST API wrapper."""

import asyncio
import logging
import uuid

import httpx

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.cognitive.microsofttranslator.com/translate"
_API_VERSION = "3.0"
_MAX_RETRIES = 3
_RETRY_DELAY = 0.5


class AzureTranslator:
    """Azure Translator API client.

    Args:
        api_key: Azure Translator subscription key.
        region: Azure bölgesi.
    """

    def __init__(self, api_key: str, region: str = "southeastasia") -> None:
        self._client = httpx.AsyncClient(timeout=10.0)
        self._headers = {
            "Ocp-Apim-Subscription-Key": api_key,
            "Ocp-Apim-Subscription-Region": region,
            "Content-Type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }

    async def translate(
        self, text: str, source_lang: str, target_langs: list[str]
    ) -> dict[str, str]:
        """Metni hedef dillere çevir (batch: tek API call).

        Args:
            text: Kaynak metin.
            source_lang: Kaynak dil kodu.
            target_langs: Hedef dil kodları.

        Returns:
            {lang: çeviri} dict.
        """
        if not text:
            return {lang: "" for lang in target_langs}

        params = self._build_params(source_lang, target_langs)
        body = [{"text": text}]

        data = await self._call_with_retry(params, body)
        return self._parse_response(data, target_langs)

    def _build_params(
        self, source_lang: str, target_langs: list[str]
    ) -> dict:
        """API query parametreleri oluştur."""
        params: dict = {"api-version": _API_VERSION, "from": source_lang}
        for lang in target_langs:
            params.setdefault("to", [])
            if isinstance(params["to"], list):
                params["to"].append(lang)
            else:
                params["to"] = [params["to"], lang]
        return params

    async def _call_with_retry(
        self, params: dict, body: list[dict]
    ) -> list:
        """API call + retry on 429."""
        for attempt in range(_MAX_RETRIES):
            try:
                resp = await self._client.post(
                    _BASE_URL,
                    headers=self._headers,
                    params=params,
                    json=body,
                )
                if resp.status_code == 429:
                    raise Exception("429 Too Many Requests")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                if attempt < _MAX_RETRIES - 1:
                    delay = _RETRY_DELAY * (2 ** attempt)
                    logger.warning(
                        f"[AZURE] Retry {attempt + 1}: {e} "
                        f"(bekleniyor {delay:.1f}s)"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"[AZURE] {_MAX_RETRIES} deneme başarısız")
                    raise
        return []  # unreachable

    def _parse_response(
        self, data: list, target_langs: list[str]
    ) -> dict[str, str]:
        """API response'unu {lang: text} dict'e çevir."""
        result: dict[str, str] = {}
        if data and "translations" in data[0]:
            for t in data[0]["translations"]:
                result[t["to"]] = t["text"]
        # Eksik diller için boş string
        for lang in target_langs:
            result.setdefault(lang, "")
        return result
