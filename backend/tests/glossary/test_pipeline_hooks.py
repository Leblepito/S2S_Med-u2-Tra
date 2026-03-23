"""Pipeline glossary hook entegrasyon testleri."""

import math
import struct

import pytest

from app.constants import CHUNK_BYTES
from app.pipeline.orchestrator import PipelineOrchestrator
from app.schemas import PartialTranscript, TranslationResult


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


class TestPipelineWithHooks:
    """Pipeline glossary hook entegrasyonu testleri."""

    @pytest.mark.asyncio
    async def test_passthrough_same_result_as_default(
        self, speech_chunk: bytes, silence_chunk: bytes
    ) -> None:
        """Passthrough hook'lu pipeline = hook'suz pipeline."""
        orch = PipelineOrchestrator(
            use_mocks=True,
            target_langs=["en"],
            glossary_mode="passthrough",
        )
        for _ in range(10):
            await orch.process_chunk(speech_chunk)
        all_msgs: list = []
        for _ in range(12):
            msgs, _ = await orch.process_chunk(silence_chunk)
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
    async def test_glossary_stages_in_latency_stats(
        self, speech_chunk: bytes, silence_chunk: bytes
    ) -> None:
        """Glossary stage'leri latency stats'ta görünmeli."""
        orch = PipelineOrchestrator(
            use_mocks=True,
            target_langs=["en"],
            glossary_mode="passthrough",
        )
        for _ in range(10):
            await orch.process_chunk(speech_chunk)
        for _ in range(12):
            await orch.process_chunk(silence_chunk)

        stats = orch.latency_stats
        assert "glossary_pre" in stats
        assert "glossary_post" in stats
        assert "enrich" in stats

    @pytest.mark.asyncio
    async def test_glossary_latency_under_1ms(
        self, speech_chunk: bytes, silence_chunk: bytes
    ) -> None:
        """Passthrough hook'lar <1ms ek latency eklemeli."""
        orch = PipelineOrchestrator(
            use_mocks=True,
            target_langs=["en"],
            glossary_mode="passthrough",
        )
        for _ in range(10):
            await orch.process_chunk(speech_chunk)
        for _ in range(12):
            await orch.process_chunk(silence_chunk)

        stats = orch.latency_stats
        for stage in ["glossary_pre", "glossary_post", "enrich"]:
            if stage in stats:
                assert stats[stage]["p50"] < 1.0, f"{stage} p50 >= 1ms"

    @pytest.mark.asyncio
    async def test_enriched_result_available(
        self, speech_chunk: bytes, silence_chunk: bytes
    ) -> None:
        """Pipeline çalıştıktan sonra last_enriched dolu olmalı."""
        orch = PipelineOrchestrator(
            use_mocks=True,
            target_langs=["en"],
            glossary_mode="passthrough",
        )
        for _ in range(10):
            await orch.process_chunk(speech_chunk)
        for _ in range(12):
            await orch.process_chunk(silence_chunk)

        enriched = orch.last_enriched
        assert enriched is not None
        assert enriched.summary is None  # passthrough
        assert enriched.actions == []
