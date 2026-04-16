"""Latency monitor testleri."""

import time

import pytest

from app.pipeline.latency_monitor import LatencyMonitor


class TestLatencyMonitor:
    """LatencyMonitor class testleri."""

    @pytest.fixture
    def monitor(self) -> LatencyMonitor:
        return LatencyMonitor()

    def test_start_end_returns_duration(
        self, monitor: LatencyMonitor
    ) -> None:
        """start + end → pozitif duration_ms."""
        monitor.start_stage("test")
        time.sleep(0.01)
        duration = monitor.end_stage("test")
        assert duration >= 5  # en az ~10ms ama toleranslı

    def test_get_stats_empty(self, monitor: LatencyMonitor) -> None:
        """Ölçüm yokken boş stats."""
        stats = monitor.get_stats()
        assert stats == {}

    def test_get_stats_with_data(self, monitor: LatencyMonitor) -> None:
        """Ölçüm sonrası stats doğru."""
        for _ in range(5):
            monitor.start_stage("asr")
            monitor.end_stage("asr")
        stats = monitor.get_stats()
        assert "asr" in stats
        assert stats["asr"]["count"] == 5
        assert stats["asr"]["p50"] >= 0
        assert stats["asr"]["p95"] >= 0

    def test_multiple_stages(self, monitor: LatencyMonitor) -> None:
        """Birden fazla stage takip edilebilmeli."""
        monitor.start_stage("vad")
        monitor.end_stage("vad")
        monitor.start_stage("asr")
        monitor.end_stage("asr")
        stats = monitor.get_stats()
        assert "vad" in stats
        assert "asr" in stats

    def test_reset(self, monitor: LatencyMonitor) -> None:
        """Reset sonrası stats boş."""
        monitor.start_stage("test")
        monitor.end_stage("test")
        monitor.reset()
        assert monitor.get_stats() == {}

    def test_end_without_start(self, monitor: LatencyMonitor) -> None:
        """Start olmadan end → 0 döner."""
        duration = monitor.end_stage("nonexistent")
        assert duration == 0.0
