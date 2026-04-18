"""Pluggable rate-limit backends for the BabelFlow middleware.

Why
---
The original `RateLimitMiddleware` kept hits in a per-process
`defaultdict`. With multi-worker uvicorn each worker had its own
counter, so a 120 req/min limit became 120 × workers in the worst
case. This module factors the hit-counter behind a small interface
so the in-memory default can be swapped for a shared Redis backend
without touching the middleware.

Backends
--------
- `InMemoryBackend`   — original behavior, single-process. Default.
- `RedisBackend`      — `redis-py` async client; lazy-imported so the
                         dependency is only required when configured.

Choose via `Settings.RATE_LIMIT_BACKEND` ("memory" | "redis").
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Protocol


class RateLimitBackend(Protocol):
    """Sliding-window per-key hit counter."""

    async def hit(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        """Record one hit for `key`.

        Returns
        -------
        (allowed, remaining)
            allowed   — True if the request is within the limit
            remaining — slots still available in the current window
                        after this hit (0 when the request was blocked).
        """
        ...


class InMemoryBackend:
    """Single-process sliding window.

    Suitable for local dev and single-worker deployments. Each worker
    has independent state, so the effective fleet limit is
    `limit × num_workers` — switch to RedisBackend when that matters.
    """

    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def hit(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        now = time.monotonic()
        bucket = self._hits[key]
        bucket[:] = [t for t in bucket if now - t < window_seconds]
        if len(bucket) >= limit:
            return False, 0
        bucket.append(now)
        return True, max(0, limit - len(bucket))


class RedisBackend:
    """Shared sliding window via Redis sorted-set.

    Requires the `redis` package (>=5). The backend lazy-imports it
    so the dep is optional unless this backend is explicitly selected.
    """

    def __init__(self, url: str) -> None:
        try:
            from redis import asyncio as redis_asyncio
        except ImportError as exc:  # pragma: no cover - exercised by ops, not unit tests
            raise RuntimeError(
                "RATE_LIMIT_BACKEND=redis requires the `redis` package "
                "(pip install redis>=5)."
            ) from exc
        self._redis = redis_asyncio.from_url(url, decode_responses=False)

    async def hit(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        now = time.time()
        cutoff = now - window_seconds
        # Atomic pipeline: drop stale, add this hit, count, set TTL.
        async with self._redis.pipeline(transaction=True) as p:
            p.zremrangebyscore(key, 0, cutoff)
            p.zadd(key, {f"{now}".encode(): now})
            p.zcard(key)
            p.expire(key, window_seconds + 1)
            _, _, count, _ = await p.execute()

        if count > limit:
            # Roll back the hit we just inserted so the window measures
            # only allowed requests; otherwise rejected hits would
            # poison the next window.
            await self._redis.zremrangebyscore(key, now - 0.001, now + 0.001)
            return False, 0
        return True, max(0, limit - count)


def make_backend(name: str, redis_url: str | None = None) -> RateLimitBackend:
    """Factory: `"memory"` (default) or `"redis"` (requires REDIS_URL)."""
    n = (name or "memory").strip().lower()
    if n == "memory":
        return InMemoryBackend()
    if n == "redis":
        if not redis_url:
            raise RuntimeError("RATE_LIMIT_BACKEND=redis requires REDIS_URL")
        return RedisBackend(redis_url)
    raise RuntimeError(f"Unknown RATE_LIMIT_BACKEND: {name!r}")
