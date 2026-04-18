"""Request logging, CORS preflight cache, rate limiting middleware."""

import logging
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.rate_limit_backend import InMemoryBackend, RateLimitBackend

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """HTTP request logging — method, path, status, duration."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Request/response loglama."""
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            f"{request.method} {request.url.path} "
            f"→ {response.status_code} ({duration_ms:.1f}ms)"
        )
        response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"
        return response


class CORSPreflightCacheMiddleware(BaseHTTPMiddleware):
    """CORS preflight response'a max-age header ekler."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Preflight cache header ekle."""
        response = await call_next(request)
        if request.method == "OPTIONS":
            response.headers["Access-Control-Max-Age"] = "3600"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """IP-based rate limiting with a pluggable backend.

    The original behavior (per-process in-memory counter) is preserved
    when no backend is supplied: this is the right default for local
    dev and single-worker deploys. Provide an explicit backend
    (`InMemoryBackend()` or `RedisBackend(url)`, or anything matching
    the `RateLimitBackend` Protocol) to share counters across uvicorn
    workers — see `app.rate_limit_backend.make_backend`.

    Args:
        max_requests_per_minute: HTTP request limiti per IP.
        backend: rate-limit counter store. Defaults to InMemoryBackend.
    """

    def __init__(
        self,
        app: object,
        max_requests_per_minute: int = 120,
        backend: RateLimitBackend | None = None,
    ) -> None:
        super().__init__(app)
        self._max_rpm = max_requests_per_minute
        self._backend: RateLimitBackend = backend or InMemoryBackend()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Rate limit kontrolü."""
        client_ip = self._get_client_ip(request)
        allowed, remaining = await self._backend.hit(
            key=f"rl:{client_ip}", limit=self._max_rpm, window_seconds=60
        )

        if not allowed:
            logger.warning(f"[RATE_LIMIT] {client_ip}: {self._max_rpm}/min exceeded")
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests", "retry_after": 60},
                headers={"Retry-After": "60"},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """Client IP'sini al (proxy arkasında X-Forwarded-For)."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
