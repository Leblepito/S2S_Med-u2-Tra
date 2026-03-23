"""Request logging + CORS preflight cache middleware."""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

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
