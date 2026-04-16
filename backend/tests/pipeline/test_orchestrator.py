"""Pipeline orchestrator testleri."""

import math
import struct

import pytest

from app.constants import CHUNK_BYTES
from app.pipeline.orchestrator import PipelineOrchestrator, TTSResult
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
            msgs, tts = await orchestrator.process_chunk(silence_chunk)
            assert len(msgs) == 0
            assert len(tts) == 0

    @pytest.mark.asyncio
    async def test_speech_produces_all_outputs(
        self,
        orchestrator: PipelineOrchestrator,
        speech_chunk: bytes,
        silence_chunk: bytes,
    ) -> None:
        """Konuşma → transcript + translation + TTS."""
        for _ in range(10):
            await orchestrator.process_chunk(speech_chunk)
        all_msgs: list = []
        all_tts: list = []
        for _ in range(12):
            msgs, tts = await orchestrator.process_chunk(silence_chunk)
            all_msgs.extend(msgs)
            all_tts.extend(tts)

        has_transcript = any(
            isinstance(m, PartialTranscript) for m in all_msgs
        )
        has_translation = any(
            isinstance(m, TranslationResult) for m in all_msgs
        )
        assert has_transcript
        assert has_translation
        assert len(all_tts) > 0
        assert all(isinstance(t, TTSResult) for t in all_tts)

    @pytest.mark.asyncio
    async def test_tts_has_audio_bytes(
        self,
        orchestrator: PipelineOrchestrator,
        speech_chunk: bytes,
        silence_chunk: bytes,
    ) -> None:
        """TTS sonucu audio bytes içermeli."""
        for _ in range(10):
            await orchestrator.process_chunk(speech_chunk)
        all_tts: list = []
        for _ in range(12):
            _, tts = await orchestrator.process_chunk(silence_chunk)
            all_tts.extend(tts)

        for t in all_tts:
            assert isinstance(t.audio, bytes)
            assert len(t.audio) > 0
            assert t.lang in {"en", "th"}

    @pytest.mark.asyncio
    async def test_latency_stats_populated(
        self,
        orchestrator: PipelineOrchestrator,
        speech_chunk: bytes,
        silence_chunk: bytes,
    ) -> None:
        """Pipeline çalıştıktan sonra latency stats dolu olmalı."""
        for _ in range(10):
            await orchestrator.process_chunk(speech_chunk)
        for _ in range(12):
            await orchestrator.process_chunk(silence_chunk)

        stats = orchestrator.latency_stats
        assert "asr" in stats
        assert stats["asr"]["count"] > 0

    @pytest.mark.asyncio
    async def test_tts_disabled(
        self, speech_chunk: bytes, silence_chunk: bytes
    ) -> None:
        """enable_tts=False → TTS üretilmemeli."""
        orch = PipelineOrchestrator(
            use_mocks=True,
            target_langs=["en"],
            enable_tts=False,
        )
        for _ in range(10):
            await orch.process_chunk(speech_chunk)
        all_tts: list = []
        for _ in range(12):
            _, tts = await orch.process_chunk(silence_chunk)
            all_tts.extend(tts)
        assert len(all_tts) == 0
