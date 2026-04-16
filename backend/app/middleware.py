"""Request logging, CORS preflight cache, rate limiting middleware."""

import logging
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

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
    """IP-based rate limiting.

    Args:
        max_requests_per_minute: HTTP request limiti per IP.
    """

    def __init__(self, app: object, max_requests_per_minute: int = 120) -> None:
        super().__init__(app)
        self._max_rpm = max_requests_per_minute
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Rate limit kontrolü."""
        client_ip = self._get_client_ip(request)
        now = time.monotonic()

        # Eski kayıtları temizle (son 60s)
        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if now - t < 60
        ]

        if len(self._requests[client_ip]) >= self._max_rpm:
            logger.warning(f"[RATE_LIMIT] {client_ip}: {self._max_rpm}/min exceeded")
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests", "retry_after": 60},
            )

        self._requests[client_ip].append(now)
        response = await call_next(request)
        remaining = self._max_rpm - len(self._requests[client_ip])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """Client IP'sini al (proxy arkasında X-Forwarded-For)."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
