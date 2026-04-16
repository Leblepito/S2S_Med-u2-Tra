"""Azure TTS SSML generation testleri."""

import pytest

from app.tts.mock_tts import AzureTTSEngine


class TestAzureTTSSSML:
    """AzureTTSEngine SSML generation testleri."""

    @pytest.fixture
    def engine(self) -> AzureTTSEngine:
        return AzureTTSEngine(api_key="test-key", region="westeurope")

    def test_ssml_contains_voice_name(self, engine: AzureTTSEngine) -> None:
        """SSML doğru voice name içermeli."""
        ssml = engine._build_ssml("hello", "en-US-JennyNeural", "en-US")
        assert 'name="en-US-JennyNeural"' in ssml

    def test_ssml_contains_text(self, engine: AzureTTSEngine) -> None:
        """SSML metin içermeli."""
        ssml = engine._build_ssml("Merhaba", "tr-TR-AhmetNeural", "tr-TR")
        assert "Merhaba" in ssml

    def test_ssml_contains_lang(self, engine: AzureTTSEngine) -> None:
        """SSML xml:lang içermeli."""
        ssml = engine._build_ssml("test", "en-US-JennyNeural", "en-US")
        assert 'xml:lang="en-US"' in ssml

    def test_ssml_valid_xml_structure(self, engine: AzureTTSEngine) -> None:
        """SSML <speak> ve <voice> tag'leri içermeli."""
        ssml = engine._build_ssml("test", "en-US-JennyNeural", "en-US")
        assert ssml.startswith('<speak version="1.0"')
        assert "<voice " in ssml
        assert "</voice>" in ssml
        assert "</speak>" in ssml

    @pytest.mark.asyncio
    async def test_empty_text_returns_empty(
        self, engine: AzureTTSEngine
    ) -> None:
        """Boş text → boş bytes (API çağrılmaz)."""
        result = await engine.synthesize("", "en")
        assert result == b""
