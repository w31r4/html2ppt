"""Tests for rate limiting functionality."""

import time

import pytest

from html2ppt.api.rate_limit import (
    RateLimitConfig,
    RateLimiter,
    TokenBucket,
    get_client_ip,
)


class TestTokenBucket:
    """Tests for TokenBucket class."""

    def test_initial_capacity(self):
        """Bucket starts at full capacity."""
        bucket = TokenBucket(rate=1.0, capacity=10)
        assert bucket.tokens == 10

    def test_consume_tokens(self):
        """Consuming tokens reduces available tokens."""
        bucket = TokenBucket(rate=1.0, capacity=10)
        assert bucket.consume(1) is True
        assert bucket.tokens == 9

    def test_consume_multiple_tokens(self):
        """Can consume multiple tokens at once."""
        bucket = TokenBucket(rate=1.0, capacity=10)
        assert bucket.consume(5) is True
        assert bucket.tokens == 5

    def test_consume_all_tokens(self):
        """Can consume all available tokens."""
        bucket = TokenBucket(rate=1.0, capacity=10)
        assert bucket.consume(10) is True
        assert bucket.tokens == 0

    def test_cannot_consume_more_than_available(self):
        """Cannot consume more tokens than available."""
        bucket = TokenBucket(rate=1.0, capacity=5)
        assert bucket.consume(6) is False
        assert bucket.tokens == 5  # Unchanged

    def test_tokens_refill_over_time(self):
        """Tokens refill based on rate and elapsed time."""
        bucket = TokenBucket(rate=100.0, capacity=10)  # 100 tokens/second
        bucket.tokens = 5
        bucket.last_update = time.time() - 0.05  # 50ms ago

        # Force refill by consuming
        bucket.consume(1)

        # Should have added ~5 tokens (100 * 0.05), then consumed 1
        assert bucket.tokens >= 8

    def test_tokens_dont_exceed_capacity(self):
        """Tokens don't refill beyond capacity."""
        bucket = TokenBucket(rate=100.0, capacity=10)
        bucket.last_update = time.time() - 1.0  # 1 second ago

        # Force refill
        bucket.consume(0)

        assert bucket.tokens == 10  # Capped at capacity

    def test_retry_after_calculation(self):
        """Retry after is calculated correctly."""
        bucket = TokenBucket(rate=2.0, capacity=10)  # 2 tokens/second
        bucket.tokens = 0

        # Should take 0.5 seconds to get 1 token
        assert bucket.retry_after == pytest.approx(0.5, rel=0.1)

    def test_retry_after_zero_when_tokens_available(self):
        """Retry after is 0 when tokens are available."""
        bucket = TokenBucket(rate=1.0, capacity=10)
        assert bucket.retry_after == 0


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_allows_requests_within_limit(self):
        """Allows requests within the rate limit."""
        config = RateLimitConfig(requests_per_minute=60, burst_size=10)
        limiter = RateLimiter(config)

        # First burst should be allowed
        for _ in range(10):
            allowed, _ = limiter.is_allowed("client1")
            assert allowed is True

    def test_blocks_requests_over_burst(self):
        """Blocks requests that exceed burst size."""
        config = RateLimitConfig(requests_per_minute=60, burst_size=5)
        limiter = RateLimiter(config)

        # Exhaust burst
        for _ in range(5):
            limiter.is_allowed("client1")

        # Next request should be blocked
        allowed, retry_after = limiter.is_allowed("client1")
        assert allowed is False
        assert retry_after > 0

    def test_separate_limits_per_client(self):
        """Each client has separate rate limits."""
        config = RateLimitConfig(requests_per_minute=60, burst_size=5)
        limiter = RateLimiter(config)

        # Exhaust client1's burst
        for _ in range(5):
            limiter.is_allowed("client1")

        # client1 is blocked
        allowed1, _ = limiter.is_allowed("client1")
        assert allowed1 is False

        # client2 still has tokens
        allowed2, _ = limiter.is_allowed("client2")
        assert allowed2 is True

    def test_tokens_refill_over_time(self):
        """Tokens refill allowing new requests."""
        config = RateLimitConfig(
            requests_per_minute=6000,  # 100/second for faster test
            burst_size=2,
        )
        limiter = RateLimiter(config)

        # Exhaust burst
        limiter.is_allowed("client1")
        limiter.is_allowed("client1")

        # Wait for refill (10ms should give ~1 token at 100/s)
        time.sleep(0.02)

        allowed, _ = limiter.is_allowed("client1")
        assert allowed is True


class TestGetClientIp:
    """Tests for get_client_ip function."""

    def test_extracts_from_x_forwarded_for(self):
        """Extracts IP from X-Forwarded-For header."""

        class MockRequest:
            headers = {"x-forwarded-for": "192.168.1.1, 10.0.0.1"}
            client = None

        result = get_client_ip(MockRequest())
        assert result == "192.168.1.1"

    def test_extracts_from_x_real_ip(self):
        """Extracts IP from X-Real-IP header."""

        class MockRequest:
            headers = {"x-real-ip": "192.168.1.2"}
            client = None

        result = get_client_ip(MockRequest())
        assert result == "192.168.1.2"

    def test_falls_back_to_client_host(self):
        """Falls back to client.host when no proxy headers."""

        class MockClient:
            host = "192.168.1.3"

        class MockRequest:
            headers = {}
            client = MockClient()

        result = get_client_ip(MockRequest())
        assert result == "192.168.1.3"

    def test_returns_unknown_when_no_ip(self):
        """Returns 'unknown' when no IP can be determined."""

        class MockRequest:
            headers = {}
            client = None

        result = get_client_ip(MockRequest())
        assert result == "unknown"

    def test_x_forwarded_for_takes_precedence(self):
        """X-Forwarded-For takes precedence over X-Real-IP."""

        class MockRequest:
            headers = {
                "x-forwarded-for": "192.168.1.1",
                "x-real-ip": "192.168.1.2",
            }
            client = None

        result = get_client_ip(MockRequest())
        assert result == "192.168.1.1"


class TestRateLimitConfig:
    """Tests for RateLimitConfig class."""

    def test_default_values(self):
        """Config has sensible defaults."""
        config = RateLimitConfig()
        assert config.requests_per_minute == 60
        assert config.requests_per_hour == 1000
        assert config.burst_size == 10

    def test_custom_values(self):
        """Config accepts custom values."""
        config = RateLimitConfig(
            requests_per_minute=120,
            requests_per_hour=2000,
            burst_size=20,
        )
        assert config.requests_per_minute == 120
        assert config.requests_per_hour == 2000
        assert config.burst_size == 20
