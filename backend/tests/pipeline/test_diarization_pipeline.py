"""Pipeline diarization entegrasyon testleri."""

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


class TestDiarizationPipeline:
    """Pipeline + diarization testleri."""

    @pytest.mark.asyncio
    async def test_diarization_enabled_sets_speaker_id(
        self, speech_chunk: bytes, silence_chunk: bytes
    ) -> None:
        """Diarization açıkken speaker_id 0'dan farklı olabilir."""
        orch = PipelineOrchestrator(
            use_mocks=True,
            target_langs=["en"],
            enable_diarization=True,
        )
        for _ in range(10):
            await orch.process_chunk(speech_chunk)
        all_msgs: list = []
        for _ in range(12):
            msgs, _ = await orch.process_chunk(silence_chunk)
            all_msgs.extend(msgs)

        transcripts = [
            m for m in all_msgs if isinstance(m, PartialTranscript)
        ]
        assert len(transcripts) > 0
        # speaker_id int olmalı
        assert isinstance(transcripts[0].speaker_id, int)
        assert transcripts[0].speaker_id >= 0

    @pytest.mark.asyncio
    async def test_diarization_disabled_speaker_zero(
        self, speech_chunk: bytes, silence_chunk: bytes
    ) -> None:
        """Diarization kapalıyken speaker_id = 0."""
        orch = PipelineOrchestrator(
            use_mocks=True,
            target_langs=["en"],
            enable_diarization=False,
        )
        for _ in range(10):
            await orch.process_chunk(speech_chunk)
        all_msgs: list = []
        for _ in range(12):
            msgs, _ = await orch.process_chunk(silence_chunk)
            all_msgs.extend(msgs)

        transcripts = [
            m for m in all_msgs if isinstance(m, PartialTranscript)
        ]
        assert len(transcripts) > 0
        assert transcripts[0].speaker_id == 0

    @pytest.mark.asyncio
    async def test_translation_has_matching_speaker_id(
        self, speech_chunk: bytes, silence_chunk: bytes
    ) -> None:
        """Translation speaker_id = transcript speaker_id."""
        orch = PipelineOrchestrator(
            use_mocks=True,
            target_langs=["en"],
            enable_diarization=True,
        )
        for _ in range(10):
            await orch.process_chunk(speech_chunk)
        all_msgs: list = []
        for _ in range(12):
            msgs, _ = await orch.process_chunk(silence_chunk)
            all_msgs.extend(msgs)

        transcripts = [
            m for m in all_msgs if isinstance(m, PartialTranscript)
        ]
        translations = [
            m for m in all_msgs if isinstance(m, TranslationResult)
        ]
        if transcripts and translations:
            assert transcripts[0].speaker_id == translations[0].speaker_id

    @pytest.mark.asyncio
    async def test_diarize_stage_in_latency(
        self, speech_chunk: bytes, silence_chunk: bytes
    ) -> None:
        """Diarization stage latency stats'ta olmalı."""
        orch = PipelineOrchestrator(
            use_mocks=True,
            target_langs=["en"],
            enable_diarization=True,
        )
        for _ in range(10):
            await orch.process_chunk(speech_chunk)
        for _ in range(12):
            await orch.process_chunk(silence_chunk)

        stats = orch.latency_stats
        assert "diarize" in stats
