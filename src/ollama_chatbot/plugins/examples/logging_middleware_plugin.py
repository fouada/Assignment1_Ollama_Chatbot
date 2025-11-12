"""
Logging Middleware Plugin - Example Middleware
Demonstrates request/response logging with structured output

Features:
- Structured JSON logging
- Performance metrics
- Request/response sanitization
- Log levels configuration
"""

import json
import time
from datetime import datetime
from typing import Any, Dict

from ..base_plugin import BaseMiddleware
from ..types import PluginConfig, PluginMetadata, PluginResult, PluginType


class LoggingMiddlewarePlugin(BaseMiddleware):
    """
    Logging middleware for requests and responses

    Configuration:
        - log_requests: Log incoming requests (default: True)
        - log_responses: Log outgoing responses (default: True)
        - log_performance: Log timing metrics (default: True)
        - sanitize_fields: Fields to sanitize (list)
        - max_content_length: Max content to log (default: 1000)
    """

    def __init__(self):
        super().__init__()
        self._log_requests = True
        self._log_responses = True
        self._log_performance = True
        self._sanitize_fields = set()
        self._max_content_length = 1000

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="logging_middleware",
            version="1.0.0",
            author="System",
            description="Structured logging for requests and responses",
            plugin_type=PluginType.MIDDLEWARE,
            tags=("logging", "middleware", "monitoring", "observability"),
        )

    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        """Initialize logging middleware"""
        try:
            self._log_requests = config.config.get("log_requests", True)
            self._log_responses = config.config.get("log_responses", True)
            self._log_performance = config.config.get("log_performance", True)
            self._max_content_length = config.config.get("max_content_length", 1000)

            # Fields to sanitize (e.g., passwords, tokens)
            sanitize_fields = config.config.get("sanitize_fields", ["password", "token", "api_key"])
            self._sanitize_fields = set(sanitize_fields)

            self._logger.info("Logging middleware initialized")

            return PluginResult.ok(None)

        except Exception as e:
            return PluginResult.fail(f"Initialization error: {e}")

    async def _do_shutdown(self) -> PluginResult[None]:
        """Cleanup"""
        self._logger.info("Logging middleware shutdown")
        return PluginResult.ok(None)

    async def _process_request(self, request: Dict[str, Any]) -> PluginResult[Dict[str, Any]]:
        """
        Log and process incoming request

        Adds:
        - Timestamp
        - Request ID
        - Performance tracking start time
        """
        try:
            if not self._log_requests:
                return PluginResult.ok(request)

            # Add metadata
            request_with_meta = request.copy()
            request_with_meta["_middleware"] = {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": self._generate_request_id(),
                "start_time": time.perf_counter(),
            }

            # Log request (sanitized)
            sanitized_request = self._sanitize_data(request)
            self._logger.info(
                "Request",
                extra={
                    "request_id": request_with_meta["_middleware"]["request_id"],
                    "request": self._truncate_content(sanitized_request),
                },
            )

            return PluginResult.ok(request_with_meta)

        except Exception as e:
            self._logger.exception("Request processing failed")
            return PluginResult.fail(f"Request processing error: {e}")

    async def _process_response(self, response: Dict[str, Any]) -> PluginResult[Dict[str, Any]]:
        """
        Log and process outgoing response

        Adds:
        - Response timestamp
        - Performance metrics
        """
        try:
            if not self._log_responses:
                return PluginResult.ok(response)

            # Calculate performance if start time present
            if "_middleware" in response and "start_time" in response["_middleware"]:
                start_time = response["_middleware"]["start_time"]
                duration_ms = (time.perf_counter() - start_time) * 1000

                if self._log_performance:
                    self._logger.info(
                        "Performance",
                        extra={
                            "request_id": response["_middleware"].get("request_id"),
                            "duration_ms": round(duration_ms, 2),
                        },
                    )

                # Add duration to response metadata
                response["_middleware"]["duration_ms"] = round(duration_ms, 2)

            # Log response (sanitized)
            sanitized_response = self._sanitize_data(response)
            self._logger.info(
                "Response",
                extra={
                    "request_id": response.get("_middleware", {}).get("request_id"),
                    "response": self._truncate_content(sanitized_response),
                },
            )

            return PluginResult.ok(response)

        except Exception as e:
            self._logger.exception("Response processing failed")
            return PluginResult.fail(f"Response processing error: {e}")

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize sensitive fields

        Replaces values of sensitive fields with [REDACTED]
        """
        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            if key.lower() in self._sanitize_fields:
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            elif isinstance(value, list):
                sanitized[key] = [self._sanitize_data(item) if isinstance(item, dict) else item for item in value]
            else:
                sanitized[key] = value

        return sanitized

    def _truncate_content(self, data: Any) -> Any:
        """
        Truncate long content for logging

        Prevents excessive log sizes
        """
        if isinstance(data, str):
            if len(data) > self._max_content_length:
                return data[: self._max_content_length] + "... [truncated]"
            return data

        if isinstance(data, dict):
            return {key: self._truncate_content(value) for key, value in data.items()}

        if isinstance(data, list):
            return [self._truncate_content(item) for item in data]

        return data

    def _generate_request_id(self) -> str:
        """
        Generate unique request ID

        Format: timestamp-based ID for tracing
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        return f"req-{timestamp}"
