"""
Base Plugin Classes - Abstract Base Classes for Plugin Development
Provides common functionality and template method pattern

Design Patterns:
- Template Method: Base class defines skeleton, subclasses implement specifics
- Strategy: Plugins are interchangeable strategies
- Null Object: Default implementations prevent errors
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from .types import (
    BackendProvider,
    ChatContext,
    FeatureExtension,
    Message,
    MessageProcessor,
    Middleware,
    PluginConfig,
    PluginMetadata,
    PluginResult,
    PluginType,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Base Plugin - Common Functionality
# ============================================================================


class BasePlugin(ABC):
    """
    Abstract base class for all plugins

    Provides:
    - Common initialization logic
    - Default health check implementation
    - Configuration management
    - Logging setup

    Subclasses must implement:
    - metadata property
    - _do_initialize() method
    - _do_shutdown() method
    """

    def __init__(self):
        self._config: Optional[PluginConfig] = None
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._initialized = False

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Plugin metadata - must be implemented by subclass"""
        pass

    async def initialize(self, config: PluginConfig) -> PluginResult[None]:
        """
        Initialize plugin with configuration

        Template method pattern - calls _do_initialize() for custom logic

        Args:
            config: Plugin configuration

        Returns:
            Result indicating success/failure
        """
        if self._initialized:
            return PluginResult.ok(None)

        try:
            # Store config
            self._config = config

            # Validate config
            errors = config.validate()
            if errors:
                return PluginResult.fail(f"Configuration errors: {', '.join(errors)}")

            # Call subclass initialization
            result = await self._do_initialize(config)

            if result.success:
                self._initialized = True
                self._logger.info(f"Plugin initialized: {self.metadata.name}")

            return result

        except Exception as e:
            self._logger.exception("Initialization failed")
            return PluginResult.fail(f"Initialization error: {e}")

    async def shutdown(self) -> PluginResult[None]:
        """
        Shutdown plugin gracefully

        Template method pattern - calls _do_shutdown() for custom logic

        Returns:
            Result indicating success/failure
        """
        if not self._initialized:
            return PluginResult.ok(None)

        try:
            result = await self._do_shutdown()

            if result.success:
                self._initialized = False
                self._logger.info(f"Plugin shutdown: {self.metadata.name}")

            return result

        except Exception as e:
            self._logger.exception("Shutdown failed")
            return PluginResult.fail(f"Shutdown error: {e}")

    async def health_check(self) -> PluginResult[Dict[str, Any]]:
        """
        Default health check implementation

        Subclasses can override for custom health checks

        Returns:
            Health status dictionary
        """
        health_data = {
            "plugin": self.metadata.name,
            "version": self.metadata.version,
            "initialized": self._initialized,
            "status": "healthy" if self._initialized else "not_initialized",
        }

        return PluginResult.ok(health_data)

    @abstractmethod
    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        """
        Custom initialization logic - implemented by subclass

        Args:
            config: Plugin configuration

        Returns:
            Result indicating success/failure
        """
        pass

    @abstractmethod
    async def _do_shutdown(self) -> PluginResult[None]:
        """
        Custom shutdown logic - implemented by subclass

        Returns:
            Result indicating success/failure
        """
        pass


# ============================================================================
# Message Processor Base
# ============================================================================


class BaseMessageProcessor(BasePlugin, MessageProcessor):
    """
    Base class for message processing plugins

    Use cases:
    - Content filtering (profanity, PII)
    - Translation
    - Formatting (markdown, code highlighting)
    - Sentiment analysis
    - Token counting

    Example Implementation:
        ```python
        from ollama_chatbot.plugins import BaseMessageProcessor
        from ollama_chatbot.plugins.types import (
            Message, ChatContext, PluginMetadata,
            PluginConfig, PluginResult, PluginType
        )

        class ProfanityFilterPlugin(BaseMessageProcessor):
            '''Filter profanity from messages'''

            def __init__(self):
                super().__init__()
                self._bad_words = set()

            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="profanity-filter",
                    version="1.0.0",
                    author="YourName",
                    description="Filters profanity from messages",
                    plugin_type=PluginType.MESSAGE_PROCESSOR,
                )

            async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
                # Load bad words list
                self._bad_words = set(config.config.get("bad_words", []))
                return PluginResult.ok(None)

            async def _do_shutdown(self) -> PluginResult[None]:
                self._bad_words.clear()
                return PluginResult.ok(None)

            async def _process_message(
                self, message: Message, context: ChatContext
            ) -> PluginResult[Message]:
                # Filter profanity
                content = message.content
                for word in self._bad_words:
                    content = content.replace(word, "*" * len(word))

                return PluginResult.ok(Message(
                    content=content,
                    role=message.role,
                    metadata=message.metadata
                ))
        ```

    Usage:
        ```python
        # In your application
        from plugins import PluginManager

        manager = PluginManager()
        await manager.initialize()

        # Load your plugin
        await manager.load_plugin(Path("profanity_filter_plugin.py"))

        # Process messages
        user_message = Message(content="Hello world", role="user")
        context = ChatContext(messages=[user_message], model="llama3.2")

        result = await manager.execute_message_processors(user_message, context)
        if result.success:
            filtered_message = result.data
        ```
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Default metadata - override in subclass"""
        return PluginMetadata(
            name="base_message_processor",
            version="1.0.0",
            author="System",
            description="Base message processor",
            plugin_type=PluginType.MESSAGE_PROCESSOR,
        )

    async def process_message(self, message: Message, context: ChatContext) -> PluginResult[Message]:
        """
        Process message - implements MessageProcessor protocol

        Args:
            message: Message to process
            context: Chat context

        Returns:
            Processed message
        """
        if not self._initialized:
            return PluginResult.fail("Plugin not initialized")

        try:
            return await self._process_message(message, context)
        except Exception as e:
            self._logger.exception("Message processing failed")
            return PluginResult.fail(f"Processing error: {e}")

    @abstractmethod
    async def _process_message(self, message: Message, context: ChatContext) -> PluginResult[Message]:
        """
        Custom message processing logic

        Args:
            message: Message to process
            context: Chat context

        Returns:
            Processed message
        """
        pass

    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        """Default initialization - can be overridden"""
        return PluginResult.ok(None)

    async def _do_shutdown(self) -> PluginResult[None]:
        """Default shutdown - can be overridden"""
        return PluginResult.ok(None)


# ============================================================================
# Backend Provider Base
# ============================================================================


class BaseBackendProvider(BasePlugin, BackendProvider):
    """
    Base class for AI backend providers

    Use cases:
    - Ollama integration
    - OpenAI API
    - Anthropic Claude
    - HuggingFace models
    - Custom local models
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Default metadata - override in subclass"""
        return PluginMetadata(
            name="base_backend",
            version="1.0.0",
            author="System",
            description="Base backend provider",
            plugin_type=PluginType.BACKEND_PROVIDER,
        )

    async def chat(self, context: ChatContext) -> PluginResult[Union[Message, AsyncIterator[str]]]:
        """
        Generate chat response - implements BackendProvider protocol

        Args:
            context: Chat context with messages and parameters

        Returns:
            Message or streaming response
        """
        if not self._initialized:
            return PluginResult.fail("Plugin not initialized")

        try:
            return await self._chat(context)
        except Exception as e:
            self._logger.exception("Chat generation failed")
            return PluginResult.fail(f"Chat error: {e}")

    async def list_models(self) -> PluginResult[List[str]]:
        """
        List available models - implements BackendProvider protocol

        Returns:
            List of model names
        """
        if not self._initialized:
            return PluginResult.fail("Plugin not initialized")

        try:
            return await self._list_models()
        except Exception as e:
            self._logger.exception("Model listing failed")
            return PluginResult.fail(f"Model listing error: {e}")

    @abstractmethod
    async def _chat(self, context: ChatContext) -> PluginResult[Union[Message, AsyncIterator[str]]]:
        """
        Custom chat logic

        Args:
            context: Chat context

        Returns:
            Generated message or stream
        """
        pass

    @abstractmethod
    async def _list_models(self) -> PluginResult[List[str]]:
        """
        Custom model listing logic

        Returns:
            List of available models
        """
        pass

    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        """Default initialization - can be overridden"""
        return PluginResult.ok(None)

    async def _do_shutdown(self) -> PluginResult[None]:
        """Default shutdown - can be overridden"""
        return PluginResult.ok(None)


# ============================================================================
# Feature Extension Base
# ============================================================================


class BaseFeatureExtension(BasePlugin, FeatureExtension):
    """
    Base class for feature extension plugins

    Use cases:
    - RAG (Retrieval Augmented Generation)
    - Conversation memory
    - Function/tool calling
    - Search integration
    - Database query
    - Code execution
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Default metadata - override in subclass"""
        return PluginMetadata(
            name="base_feature",
            version="1.0.0",
            author="System",
            description="Base feature extension",
            plugin_type=PluginType.FEATURE_EXTENSION,
        )

    async def extend(self, context: ChatContext) -> PluginResult[ChatContext]:
        """
        Extend context with additional capabilities

        Args:
            context: Original chat context

        Returns:
            Enhanced chat context
        """
        if not self._initialized:
            return PluginResult.fail("Plugin not initialized")

        try:
            return await self._extend(context)
        except Exception as e:
            self._logger.exception("Context extension failed")
            return PluginResult.fail(f"Extension error: {e}")

    @abstractmethod
    async def _extend(self, context: ChatContext) -> PluginResult[ChatContext]:
        """
        Custom extension logic

        Args:
            context: Original context

        Returns:
            Enhanced context
        """
        pass

    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        """Default initialization - can be overridden"""
        return PluginResult.ok(None)

    async def _do_shutdown(self) -> PluginResult[None]:
        """Default shutdown - can be overridden"""
        return PluginResult.ok(None)


# ============================================================================
# Middleware Base
# ============================================================================


class BaseMiddleware(BasePlugin, Middleware):
    """
    Base class for middleware plugins

    Use cases:
    - Request validation
    - Response transformation
    - Logging and metrics
    - Rate limiting
    - Authentication
    - Caching
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Default metadata - override in subclass"""
        return PluginMetadata(
            name="base_middleware",
            version="1.0.0",
            author="System",
            description="Base middleware",
            plugin_type=PluginType.MIDDLEWARE,
        )

    async def process_request(self, request: Dict[str, Any]) -> PluginResult[Dict[str, Any]]:
        """
        Process incoming request

        Args:
            request: Request data

        Returns:
            Processed request
        """
        if not self._initialized:
            return PluginResult.fail("Plugin not initialized")

        try:
            return await self._process_request(request)
        except Exception as e:
            self._logger.exception("Request processing failed")
            return PluginResult.fail(f"Request processing error: {e}")

    async def process_response(self, response: Dict[str, Any]) -> PluginResult[Dict[str, Any]]:
        """
        Process outgoing response

        Args:
            response: Response data

        Returns:
            Processed response
        """
        if not self._initialized:
            return PluginResult.fail("Plugin not initialized")

        try:
            return await self._process_response(response)
        except Exception as e:
            self._logger.exception("Response processing failed")
            return PluginResult.fail(f"Response processing error: {e}")

    @abstractmethod
    async def _process_request(self, request: Dict[str, Any]) -> PluginResult[Dict[str, Any]]:
        """
        Custom request processing logic

        Args:
            request: Request data

        Returns:
            Processed request
        """
        pass

    @abstractmethod
    async def _process_response(self, response: Dict[str, Any]) -> PluginResult[Dict[str, Any]]:
        """
        Custom response processing logic

        Args:
            response: Response data

        Returns:
            Processed response
        """
        pass

    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        """Default initialization - can be overridden"""
        return PluginResult.ok(None)

    async def _do_shutdown(self) -> PluginResult[None]:
        """Default shutdown - can be overridden"""
        return PluginResult.ok(None)
