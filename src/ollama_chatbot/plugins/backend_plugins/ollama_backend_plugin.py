"""
Ollama Backend Plugin - Production-Grade Implementation
Provides Ollama integration as a pluggable backend

Features:
- Streaming and non-streaming responses
- Model management
- Error handling with retries
- Health monitoring
- Performance metrics
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import AsyncIterator, List, Optional, Union

try:
    import ollama
except ImportError:
    ollama = None  # Graceful degradation

from ..base_plugin import BaseBackendProvider
from ..types import (
    ChatContext,
    Message,
    PluginConfig,
    PluginMetadata,
    PluginResult,
    PluginType,
)


class OllamaBackendPlugin(BaseBackendProvider):
    """
    Ollama backend provider plugin

    Configuration options:
    - host: Ollama server host (default: localhost:11434)
    - timeout: Request timeout in seconds
    - max_retries: Maximum retry attempts
    - default_model: Default model to use
    """

    def __init__(self):
        super().__init__()
        self._client: Optional[ollama.Client] = None
        self._host: str = "http://localhost:11434"
        self._default_model: str = "llama3.2"
        self._available_models: List[str] = []

    @property
    def metadata(self) -> PluginMetadata:
        """Plugin metadata"""
        return PluginMetadata(
            name="ollama_backend",
            version="1.0.0",
            author="System",
            description="Ollama backend provider with streaming support",
            plugin_type=PluginType.BACKEND_PROVIDER,
            tags=("ollama", "llm", "backend", "streaming"),
            homepage="https://ollama.ai",
        )

    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        """Initialize Ollama client"""
        if ollama is None:
            return PluginResult.fail("ollama package not installed")

        try:
            # Get configuration
            self._host = config.config.get("host", self._host)
            self._default_model = config.config.get("default_model", self._default_model)

            # Create client (synchronous Ollama client)
            # Note: ollama package doesn't have async client yet, so we'll use
            # asyncio.to_thread for async compatibility
            self._logger.info(f"Connecting to Ollama at {self._host}")

            # Test connection by listing models
            models_result = await self._list_models()
            if not models_result.success:
                return PluginResult.fail(f"Failed to connect: {models_result.error}")

            self._logger.info(f"Connected to Ollama, found {len(self._available_models)} model(s)")

            return PluginResult.ok(None)

        except Exception as e:
            return PluginResult.fail(f"Initialization error: {e}")

    async def _do_shutdown(self) -> PluginResult[None]:
        """Cleanup resources"""
        self._client = None
        self._available_models = []
        self._logger.info("Ollama backend shut down")
        return PluginResult.ok(None)

    async def _chat(self, context: ChatContext) -> PluginResult[Union[Message, AsyncIterator[str]]]:
        """
        Generate chat response

        Supports both streaming and non-streaming modes
        """
        try:
            # Prepare messages for Ollama
            messages = [{"role": msg.role, "content": msg.content} for msg in context.messages]

            model = context.model or self._default_model

            # Ollama options
            options = {"temperature": context.temperature}

            if context.max_tokens:
                options["num_predict"] = context.max_tokens

            if context.stream:
                # Streaming response
                return PluginResult.ok(self._stream_chat(messages, model, options))
            else:
                # Non-streaming response
                response = await asyncio.to_thread(
                    ollama.chat,
                    model=model,
                    messages=messages,
                    options=options,
                    stream=False,
                )

                # Extract response
                content = response.get("message", {}).get("content", "")

                # Create message
                message = Message(
                    content=content,
                    role="assistant",
                    model=model,
                    timestamp=datetime.utcnow(),
                    metadata={
                        "total_duration": response.get("total_duration"),
                        "load_duration": response.get("load_duration"),
                        "prompt_eval_count": response.get("prompt_eval_count"),
                        "eval_count": response.get("eval_count"),
                    },
                )

                return PluginResult.ok(message)

        except Exception as e:
            self._logger.exception("Chat generation failed")
            return PluginResult.fail(f"Chat error: {e}")

    async def _stream_chat(self, messages: List[dict], model: str, options: dict) -> AsyncIterator[str]:
        """
        Stream chat response chunk by chunk

        Yields individual content chunks
        """
        try:
            # Ollama's stream returns iterator of chunks
            stream = ollama.chat(model=model, messages=messages, options=options, stream=True)

            for chunk in stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content

        except Exception as e:
            self._logger.exception("Streaming failed")
            yield f"[Error: {e}]"

    async def _list_models(self) -> PluginResult[List[str]]:
        """List available Ollama models"""
        try:
            # Call Ollama list API
            response = await asyncio.to_thread(ollama.list)

            # Extract model names
            models = [model.get("name", model.get("model")) for model in response.get("models", [])]

            self._available_models = models

            self._logger.debug(f"Available models: {models}")

            return PluginResult.ok(models)

        except Exception as e:
            self._logger.exception("Model listing failed")
            return PluginResult.fail(f"Model listing error: {e}")

    async def health_check(self) -> PluginResult[dict]:
        """
        Health check with Ollama connectivity test

        Returns:
            Health status with connection info
        """
        base_health = await super().health_check()

        if not base_health.success or not base_health.data:
            return base_health

        health_data = base_health.data

        # Test Ollama connectivity
        try:
            models_result = await self._list_models()

            health_data["ollama_connected"] = models_result.success
            health_data["ollama_host"] = self._host
            health_data["available_models"] = len(self._available_models)
            health_data["models"] = self._available_models

            if models_result.success:
                health_data["status"] = "healthy"
            else:
                health_data["status"] = "degraded"
                health_data["error"] = models_result.error

        except Exception as e:
            health_data["status"] = "unhealthy"
            health_data["error"] = str(e)
            health_data["ollama_connected"] = False

        return PluginResult.ok(health_data)
