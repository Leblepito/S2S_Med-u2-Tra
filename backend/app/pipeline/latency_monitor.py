"""Pipeline latency monitoring — stage bazlı süre takibi."""

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class LatencyMonitor:
    """Pipeline stage'lerinin latency'sini ölçer ve raporlar."""

    def __init__(self) -> None:
        self._starts: dict[str, float] = {}
        self._durations: dict[str, list[float]] = {}

    def start_stage(self, name: str) -> None:
        """Stage ölçümünü başlat.

        Args:
            name: Stage adı (vad, asr, translate, tts).
        """
        self._starts[name] = time.perf_counter()

    def end_stage(self, name: str) -> float:
        """Stage ölçümünü bitir, duration_ms döndür.

        Args:
            name: Stage adı.

        Returns:
            Geçen süre (ms). Start yoksa 0.
        """
        start = self._starts.pop(name, None)
        if start is None:
            return 0.0

        duration_ms = (time.perf_counter() - start) * 1000
        self._durations.setdefault(name, []).append(duration_ms)
        return duration_ms

    def get_stats(self) -> dict[str, dict[str, Any]]:
        """Tüm stage'lerin istatistiklerini döndür.

        Returns:
            {stage: {count, p50, p95, p99}} dict.
        """
        stats: dict[str, dict[str, Any]] = {}
        for name, durations in self._durations.items():
            sorted_d = sorted(durations)
            n = len(sorted_d)
            stats[name] = {
                "count": n,
                "p50": sorted_d[n // 2] if n else 0,
                "p95": sorted_d[int(n * 0.95)] if n else 0,
                "p99": sorted_d[int(n * 0.99)] if n else 0,
            }
        return stats

    def reset(self) -> None:
        """Tüm ölçümleri sıfırla."""
        self._starts.clear()
        self._durations.clear()
