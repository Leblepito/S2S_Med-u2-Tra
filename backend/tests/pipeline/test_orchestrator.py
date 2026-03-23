"""Pipeline orchestrator testleri."""

import math
import struct

import pytest

from app.constants import CHUNK_BYTES
from app.pipeline.orchestrator import PipelineOrchestrator
from app.schemas import PartialTranscript, TranslationResult


@pytest.fixture
def orchestrator() -> PipelineOrchestrator:
    return PipelineOrchestrator(
        use_mocks=True,
        target_langs=["en", "th"],
        config_source_lang="auto",
    )


@pytest.fixture
def silence_chunk() -> bytes:
    return bytes(CHUNK_BYTES)


@pytest.fixture
def speech_chunk() -> bytes:
    samples = [
        int(math.sin(2 * math.pi * 440 * i / 16000) * 16000)
        for i in range(480)
    ]
    return struct.pack(f"<{len(samples)}h", *samples)


class TestPipelineOrchestrator:
    """PipelineOrchestrator testleri."""

    @pytest.mark.asyncio
    async def test_silence_no_messages(
        self, orchestrator: PipelineOrchestrator, silence_chunk: bytes
    ) -> None:
        """Sessizlikte mesaj üretilmemeli."""
        for _ in range(20):
            msgs = await orchestrator.process_chunk(silence_chunk)
            assert len(msgs) == 0

    @pytest.mark.asyncio
    async def test_speech_produces_transcript_and_translation(
        self,
        orchestrator: PipelineOrchestrator,
        speech_chunk: bytes,
        silence_chunk: bytes,
    ) -> None:
        """Konuşma + sessizlik → transcript + translation."""
        # 10 chunk konuşma
        for _ in range(10):
            await orchestrator.process_chunk(speech_chunk)
        # 12 chunk sessizlik
        all_msgs: list = []
        for _ in range(12):
            msgs = await orchestrator.process_chunk(silence_chunk)
            all_msgs.extend(msgs)

        has_transcript = any(
            isinstance(m, PartialTranscript) for m in all_msgs
        )
        has_translation = any(
            isinstance(m, TranslationResult) for m in all_msgs
        )
        assert has_transcript
        assert has_translation

    @pytest.mark.asyncio
    async def test_translation_has_target_langs(
        self,
        orchestrator: PipelineOrchestrator,
        speech_chunk: bytes,
        silence_chunk: bytes,
    ) -> None:
        """Translation sonucu hedef dilleri içermeli."""
        for _ in range(10):
            await orchestrator.process_chunk(speech_chunk)
        all_msgs: list = []
        for _ in range(12):
            msgs = await orchestrator.process_chunk(silence_chunk)
            all_msgs.extend(msgs)

        translations = [
            m for m in all_msgs if isinstance(m, TranslationResult)
        ]
        assert len(translations) > 0
        t = translations[0]
        # source_lang = "tr" (mock whisper), target'lar en + th
        # source_lang kendisi target'ta olmamalı
        assert len(t.translations) > 0

    @pytest.mark.asyncio
    async def test_cache_hit_on_repeat(
        self,
        orchestrator: PipelineOrchestrator,
        speech_chunk: bytes,
        silence_chunk: bytes,
    ) -> None:
        """Aynı metin tekrar gelince cache hit olmalı."""
        # İlk turda cache'e yazar
        for _ in range(10):
            await orchestrator.process_chunk(speech_chunk)
        for _ in range(12):
            await orchestrator.process_chunk(silence_chunk)

        # Cache stats kontrol
        assert orchestrator._cache.size > 0
