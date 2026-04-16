"""Pipeline latency monitoring — stage bazlı süre takibi + structured log."""

import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class LatencyMonitor:
    """Pipeline stage'lerinin latency'sini ölçer ve raporlar."""

    def __init__(self) -> None:
        self._starts: dict[str, float] = {}
        self._durations: dict[str, list[float]] = {}
        self._pipeline_start: float = 0.0
        self._last_stage_durations: dict[str, float] = {}

    def start_pipeline(self) -> None:
        """Pipeline ölçümünü başlat."""
        self._pipeline_start = time.perf_counter()
        self._last_stage_durations.clear()

    def start_stage(self, name: str) -> None:
        """Stage ölçümünü başlat."""
        self._starts[name] = time.perf_counter()

    def end_stage(self, name: str) -> float:
        """Stage ölçümünü bitir, duration_ms döndür."""
        start = self._starts.pop(name, None)
        if start is None:
            return 0.0
        duration_ms = (time.perf_counter() - start) * 1000
        self._durations.setdefault(name, []).append(duration_ms)
        self._last_stage_durations[name] = round(duration_ms, 2)
        return duration_ms

    def end_pipeline(self) -> float:
        """Pipeline ölçümünü bitir, structured log yaz."""
        if self._pipeline_start == 0.0:
            return 0.0
        total_ms = (time.perf_counter() - self._pipeline_start) * 1000
        self._log_structured(total_ms)
        self._pipeline_start = 0.0
        return total_ms

    def _log_structured(self, total_ms: float) -> None:
        """JSON structured log yaz."""
        log_data = {
            "event": "pipeline_complete",
            "total_ms": round(total_ms, 2),
            "stages": self._last_stage_durations.copy(),
        }
        logger.info(json.dumps(log_data))

    def get_stats(self) -> dict[str, dict[str, Any]]:
        """Tüm stage'lerin istatistiklerini döndür."""
        stats: dict[str, dict[str, Any]] = {}
        for name, durations in self._durations.items():
            sorted_d = sorted(durations)
            n = len(sorted_d)
            stats[name] = {
                "count": n,
                "p50": round(sorted_d[n // 2], 2) if n else 0,
                "p95": round(sorted_d[int(n * 0.95)], 2) if n else 0,
                "p99": round(sorted_d[int(n * 0.99)], 2) if n else 0,
            }
        return stats

    def reset(self) -> None:
        """Tüm ölçümleri sıfırla."""
        self._starts.clear()
        self._durations.clear()
        self._last_stage_durations.clear()
        self._pipeline_start = 0.0
