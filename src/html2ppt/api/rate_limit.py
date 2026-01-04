"""Rate limiting middleware for API endpoints."""

import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from html2ppt.config.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10  # Maximum burst of requests allowed


class TokenBucket:
    """Token bucket rate limiter implementation."""

    def __init__(self, rate: float, capacity: int) -> None:
        """Initialize token bucket.

        Args:
            rate: Tokens added per second
            capacity: Maximum tokens in bucket
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from the bucket.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were available and consumed
        """
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now

        # Add tokens based on elapsed time
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    @property
    def retry_after(self) -> float:
        """Calculate seconds until tokens are available."""
        if self.tokens >= 1:
            return 0
        return (1 - self.tokens) / self.rate


class RateLimiter:
    """In-memory rate limiter using token bucket algorithm."""

    def __init__(self, config: RateLimitConfig | None = None) -> None:
        """Initialize rate limiter.

        Args:
            config: Rate limiting configuration
        """
        self.config = config or RateLimitConfig()
        # Store token buckets per client (keyed by IP)
        self._buckets: dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(
                rate=self.config.requests_per_minute / 60.0,
                capacity=self.config.burst_size,
            )
        )
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = time.time()

    def is_allowed(self, client_id: str) -> tuple[bool, float]:
        """Check if request is allowed for the given client.

        Args:
            client_id: Client identifier (usually IP address)

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        self._maybe_cleanup()
        bucket = self._buckets[client_id]
        allowed = bucket.consume()
        return allowed, bucket.retry_after

    def _maybe_cleanup(self) -> None:
        """Remove stale entries from the bucket store."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return

        self._last_cleanup = now
        # Remove buckets that are at capacity (idle clients)
        stale_keys = [
            key for key, bucket in self._buckets.items() if bucket.tokens >= bucket.capacity
        ]
        for key in stale_keys:
            del self._buckets[key]

        if stale_keys:
            logger.debug("Rate limiter cleanup", removed_count=len(stale_keys))


# Global rate limiter instance
_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies."""
    # Check X-Forwarded-For header (set by reverse proxies)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # Take the first IP in the chain (original client)
        return forwarded_for.split(",")[0].strip()

    # Check X-Real-IP header
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip

    # Fall back to direct client IP
    if request.client:
        return request.client.host

    return "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware that applies rate limiting to requests."""

    def __init__(
        self,
        app,
        config: RateLimitConfig | None = None,
        exclude_paths: list[str] | None = None,
    ) -> None:
        """Initialize rate limit middleware.

        Args:
            app: ASGI application
            config: Rate limiting configuration
            exclude_paths: Paths to exclude from rate limiting
        """
        super().__init__(app)
        self.rate_limiter = RateLimiter(config)
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/redoc", "/openapi.json"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and apply rate limiting."""
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        client_ip = get_client_ip(request)
        allowed, retry_after = self.rate_limiter.is_allowed(client_ip)

        if not allowed:
            logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                path=request.url.path,
                retry_after=retry_after,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please slow down.",
                    "retry_after": round(retry_after, 1),
                },
                headers={"Retry-After": str(int(retry_after) + 1)},
            )

        return await call_next(request)
