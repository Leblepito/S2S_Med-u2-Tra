"""§1.3/S4 — pluggable rate-limit backends."""

import pytest

from app.rate_limit_backend import InMemoryBackend, make_backend


@pytest.mark.asyncio
async def test_in_memory_allows_up_to_limit():
    b = InMemoryBackend()
    for i in range(5):
        allowed, remaining = await b.hit("k", limit=5, window_seconds=60)
        assert allowed is True
        assert remaining == 4 - i


@pytest.mark.asyncio
async def test_in_memory_blocks_over_limit():
    b = InMemoryBackend()
    for _ in range(3):
        await b.hit("k", limit=3, window_seconds=60)
    allowed, remaining = await b.hit("k", limit=3, window_seconds=60)
    assert allowed is False
    assert remaining == 0


@pytest.mark.asyncio
async def test_in_memory_isolates_keys():
    b = InMemoryBackend()
    await b.hit("a", limit=1, window_seconds=60)
    blocked, _ = await b.hit("a", limit=1, window_seconds=60)
    assert blocked is False
    allowed, _ = await b.hit("b", limit=1, window_seconds=60)
    assert allowed is True


@pytest.mark.asyncio
async def test_in_memory_window_expiry(monkeypatch):
    """Old hits drop out so a slot frees up after the window."""
    b = InMemoryBackend()
    # fake monotonic clock
    fake_now = {"t": 1000.0}

    import app.rate_limit_backend as mod
    monkeypatch.setattr(mod.time, "monotonic", lambda: fake_now["t"])

    await b.hit("k", limit=1, window_seconds=60)
    blocked, _ = await b.hit("k", limit=1, window_seconds=60)
    assert blocked is False

    fake_now["t"] += 61.0
    allowed, _ = await b.hit("k", limit=1, window_seconds=60)
    assert allowed is True


def test_factory_unknown_backend_raises():
    with pytest.raises(RuntimeError, match="Unknown RATE_LIMIT_BACKEND"):
        make_backend("nope")


def test_factory_redis_requires_url():
    with pytest.raises(RuntimeError, match="REDIS_URL"):
        make_backend("redis", redis_url=None)


def test_factory_memory_default():
    assert isinstance(make_backend("memory"), InMemoryBackend)
    # Empty / None falls through to memory too
    assert isinstance(make_backend(""), InMemoryBackend)
