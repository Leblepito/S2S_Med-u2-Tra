"""Azure Translator testleri (mock httpx responses)."""

import json

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.translation.azure_translator import AzureTranslator


class TestAzureTranslator:
    """AzureTranslator class testleri."""

    @pytest.fixture
    def translator(self) -> AzureTranslator:
        return AzureTranslator(api_key="test-key", region="westeurope")

    def _mock_response(self, translations: list[dict]) -> MagicMock:
        """Azure API response mock oluştur."""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = [{"translations": translations}]
        response.raise_for_status = MagicMock()
        return response

    @pytest.mark.asyncio
    async def test_single_target(self, translator: AzureTranslator) -> None:
        """Tek hedef dile çeviri."""
        mock_resp = self._mock_response(
            [{"text": "Hello", "to": "en"}]
        )
        with patch.object(
            translator._client, "post", return_value=mock_resp
        ):
            result = await translator.translate("Merhaba", "tr", ["en"])
        assert result == {"en": "Hello"}

    @pytest.mark.asyncio
    async def test_batch_multiple_targets(
        self, translator: AzureTranslator
    ) -> None:
        """Birden fazla hedef dil tek API call'da."""
        mock_resp = self._mock_response([
            {"text": "Hello", "to": "en"},
            {"text": "Привет", "to": "ru"},
            {"text": "สวัสดี", "to": "th"},
        ])
        with patch.object(
            translator._client, "post", return_value=mock_resp
        ):
            result = await translator.translate(
                "Merhaba", "tr", ["en", "ru", "th"]
            )
        assert len(result) == 3
        assert result["en"] == "Hello"
        assert result["ru"] == "Привет"

    @pytest.mark.asyncio
    async def test_api_called_with_correct_params(
        self, translator: AzureTranslator
    ) -> None:
        """API doğru parametrelerle çağrılmalı."""
        mock_resp = self._mock_response(
            [{"text": "Hello", "to": "en"}]
        )
        mock_post = AsyncMock(return_value=mock_resp)
        with patch.object(translator._client, "post", mock_post):
            await translator.translate("test", "tr", ["en"])

        _, kwargs = mock_post.call_args
        params = kwargs.get("params", {})
        assert params.get("from") == "tr"
        assert "en" in params.get("to", [])

    @pytest.mark.asyncio
    async def test_empty_text(self, translator: AzureTranslator) -> None:
        """Boş text → API çağrılmadan boş dict."""
        result = await translator.translate("", "en", ["tr"])
        assert result == {"tr": ""}

    @pytest.mark.asyncio
    async def test_retry_on_429(self, translator: AzureTranslator) -> None:
        """429 rate limit → retry."""
        error_resp = MagicMock()
        error_resp.status_code = 429

        ok_resp = self._mock_response([{"text": "Hello", "to": "en"}])

        mock_post = AsyncMock(side_effect=[error_resp, ok_resp])
        with patch.object(translator._client, "post", mock_post):
            with patch("app.translation.azure_translator.asyncio.sleep", new_callable=AsyncMock):
                result = await translator.translate("test", "tr", ["en"])
        assert result["en"] == "Hello"
        assert mock_post.call_count == 2

    @pytest.mark.asyncio
    async def test_headers_contain_key(
        self, translator: AzureTranslator
    ) -> None:
        """Request header'larında API key olmalı."""
        assert translator._headers["Ocp-Apim-Subscription-Key"] == "test-key"
        assert translator._headers["Ocp-Apim-Subscription-Region"] == "westeurope"
