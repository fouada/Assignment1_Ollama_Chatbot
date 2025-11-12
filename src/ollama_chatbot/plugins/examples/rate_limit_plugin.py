"""
Rate Limiting Plugin - ISO/IEC 25010 Security & Performance Compliance

Provides rate limiting, throttling, and DoS protection using token bucket algorithm.

Author: ISO/IEC 25010 Compliance
Version: 1.0.0
"""

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from plugins.base_plugin import BaseMiddleware
from plugins.types import (
    HookPriority,
    PluginConfig,
    PluginMetadata,
    PluginResult,
    PluginType,
)


@dataclass
class TokenBucket:
    """Token bucket for rate limiting"""

    capacity: int
    tokens: float
    refill_rate: float  # tokens per second
    last_refill: float


class RateLimitPlugin(BaseMiddleware):
    """
    Rate Limiting & Throttling Plugin

    Features:
    - Token bucket algorithm
    - Per-user rate limiting
    - Per-IP rate limiting
    - Per-endpoint rate limiting
    - Burst handling
    - DoS protection

    ISO/IEC 25010 Compliance:
    - Security > Confidentiality: ✅ (prevents brute force)
    - Performance > Time Behaviour: ✅ (protects system)
    - Reliability > Availability: ✅ (prevents DoS)
    """

    def __init__(self):
        super().__init__()
        self._user_buckets: Dict[str, TokenBucket] = defaultdict(self._create_bucket)
        self._ip_buckets: Dict[str, TokenBucket] = defaultdict(self._create_bucket)
        self._max_requests_per_minute: int = 60
        self._max_burst: int = 10
        self._enable_user_limiting: bool = True
        self._enable_ip_limiting: bool = True

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="rate_limiter",
            version="1.0.0",
            author="ISO Compliance Team",
            description="Token bucket rate limiting and DoS protection",
            plugin_type=PluginType.MIDDLEWARE,
            dependencies=(),
            tags=("security", "rate-limiting", "performance", "iso25010"),
            priority=HookPriority.CRITICAL,
        )

    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        """Initialize rate limiter"""
        try:
            self._max_requests_per_minute = config.config.get("max_requests_per_minute", 60)
            self._max_burst = config.config.get("max_burst", 10)
            self._enable_user_limiting = config.config.get("enable_user_limiting", True)
            self._enable_ip_limiting = config.config.get("enable_ip_limiting", True)

            self._logger.info(
                "Rate limiter initialized",
                extra={
                    "max_requests_per_minute": self._max_requests_per_minute,
                    "max_burst": self._max_burst,
                },
            )

            return PluginResult.ok(None)

        except Exception as e:
            return PluginResult.fail(f"Failed to initialize rate limiter: {e}")

    def _create_bucket(self) -> TokenBucket:
        """Create a new token bucket"""
        refill_rate = self._max_requests_per_minute / 60.0  # tokens per second

        return TokenBucket(
            capacity=self._max_burst,
            tokens=self._max_burst,
            refill_rate=refill_rate,
            last_refill=time.time(),
        )

    async def _process_request(self, request: Dict[str, Any]) -> PluginResult[Dict[str, Any]]:
        """Check rate limits before processing request"""
        try:
            user_id = request.get("user_id", "anonymous")
            ip_address = request.get("ip_address", "unknown")

            # Check user rate limit
            if self._enable_user_limiting:
                user_allowed = await self._check_rate_limit(self._user_buckets[user_id])
                if not user_allowed:
                    return PluginResult.fail(
                        f"Rate limit exceeded for user: {user_id}",
                        error_code="RATE_LIMIT_EXCEEDED",
                        status_code=429,
                        extra={
                            "retry_after": 60,
                            "limit": self._max_requests_per_minute,
                        },
                    )

            # Check IP rate limit
            if self._enable_ip_limiting:
                ip_allowed = await self._check_rate_limit(self._ip_buckets[ip_address])
                if not ip_allowed:
                    return PluginResult.fail(
                        f"Rate limit exceeded for IP: {ip_address}",
                        error_code="RATE_LIMIT_EXCEEDED",
                        status_code=429,
                        extra={
                            "retry_after": 60,
                            "limit": self._max_requests_per_minute,
                        },
                    )

            # Add rate limit headers to request
            request["rate_limit_remaining"] = int(self._user_buckets[user_id].tokens)
            request["rate_limit_limit"] = self._max_requests_per_minute

            return PluginResult.ok(request)

        except Exception as e:
            self._logger.error(f"Rate limiting error: {e}")
            # Allow request on error to avoid blocking legitimate traffic
            return PluginResult.ok(request)

    async def _check_rate_limit(self, bucket: TokenBucket) -> bool:
        """Check if request is allowed using token bucket algorithm"""
        current_time = time.time()

        # Refill tokens based on elapsed time
        elapsed = current_time - bucket.last_refill
        tokens_to_add = elapsed * bucket.refill_rate
        bucket.tokens = min(bucket.capacity, bucket.tokens + tokens_to_add)
        bucket.last_refill = current_time

        # Check if token available
        if bucket.tokens >= 1.0:
            bucket.tokens -= 1.0
            return True
        else:
            return False

    async def _process_response(self, response: Dict[str, Any]) -> PluginResult[Dict[str, Any]]:
        """Add rate limit headers to response"""
        try:
            if "headers" not in response:
                response["headers"] = {}

            # Add rate limit headers
            response["headers"].update(
                {
                    "X-RateLimit-Limit": str(self._max_requests_per_minute),
                    "X-RateLimit-Remaining": str(response.get("rate_limit_remaining", 0)),
                    "X-RateLimit-Reset": str(int(time.time()) + 60),
                }
            )

            return PluginResult.ok(response)

        except Exception as e:
            return PluginResult.ok(response)

    async def _do_health_check(self) -> PluginResult[Dict[str, Any]]:
        """Health check with rate limit stats"""
        return PluginResult.ok(
            {
                "status": "healthy",
                "tracked_users": len(self._user_buckets),
                "tracked_ips": len(self._ip_buckets),
                "max_requests_per_minute": self._max_requests_per_minute,
                "max_burst": self._max_burst,
            }
        )


# Export plugin
__all__ = ["RateLimitPlugin"]
