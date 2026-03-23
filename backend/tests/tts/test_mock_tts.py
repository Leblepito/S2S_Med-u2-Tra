"""Mock TTS testleri."""

import pytest

from app.constants import TTS_SAMPLE_RATE
from app.tts.mock_tts import MockTTS, TTSEngine, create_tts


class TestMockTTS:
    """MockTTS class testleri."""

    @pytest.fixture
    def tts(self) -> MockTTS:
        return MockTTS()

    @pytest.mark.asyncio
    async def test_returns_bytes(self, tts: MockTTS) -> None:
        """synthesize bytes dönmeli."""
        audio = await tts.synthesize("hello", "en")
        assert isinstance(audio, bytes)

    @pytest.mark.asyncio
    async def test_pcm16_format(self, tts: MockTTS) -> None:
        """Output PCM16 formatında olmalı (çift sayıda byte)."""
        audio = await tts.synthesize("test", "en")
        assert len(audio) % 2 == 0

    @pytest.mark.asyncio
    async def test_proportional_duration(self, tts: MockTTS) -> None:
        """Uzun text → daha fazla audio byte."""
        short = await tts.synthesize("hi", "en")
        long = await tts.synthesize("this is a much longer sentence", "en")
        assert len(long) > len(short)

    @pytest.mark.asyncio
    async def test_empty_text(self, tts: MockTTS) -> None:
        """Boş text → boş bytes."""
        audio = await tts.synthesize("", "en")
        assert audio == b""

    @pytest.mark.asyncio
    async def test_24khz_sample_rate(self, tts: MockTTS) -> None:
        """Output 24kHz olmalı. 1 char ≈ 50ms → samples = chars * 1200."""
        audio = await tts.synthesize("hello", "en")
        samples = len(audio) // 2  # PCM16
        expected_min = 5 * TTS_SAMPLE_RATE * 50 // 1000  # 5 chars * 50ms
        assert samples >= expected_min * 0.8  # %20 tolerans


class TestCreateTTS:
    """create_tts factory testleri."""

    def test_mock_mode(self) -> None:
        """use_mocks=True → MockTTS."""
        t = create_tts(use_mocks=True)
        assert isinstance(t, MockTTS)

    def test_protocol(self) -> None:
        """Factory TTSEngine protocol'üne uygun dönmeli."""
        t = create_tts(use_mocks=True)
        assert isinstance(t, TTSEngine)
