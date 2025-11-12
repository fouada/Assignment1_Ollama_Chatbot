"""
Comprehensive Tests for Base Plugin Coverage
These tests cover error paths and edge cases to increase coverage to 95%
"""

import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import pytest
from typing import List

from ollama_chatbot.plugins.base_plugin import (
    BasePlugin,
    BaseBackendProvider,
    BaseMessageProcessor,
    BaseFeatureExtension,
    BaseMiddleware,
)
from ollama_chatbot.plugins.types import (
    PluginConfig,
    PluginMetadata,
    PluginType,
    PluginResult,
    Message,
    ChatContext,
)


# ============================================================================
# Test Plugin Implementations
# ============================================================================

class MinimalTestPlugin(BasePlugin):
    """Minimal plugin for testing abstract base class"""
    
    def __init__(self):
        super().__init__()
        self._metadata = PluginMetadata(
            name="minimal-test",
            version="1.0.0",
            author="Test",
            description="Test plugin",
            plugin_type=PluginType.FEATURE_EXTENSION,
        )
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        return PluginResult.ok(None)
    
    async def _do_shutdown(self) -> PluginResult[None]:
        return PluginResult.ok(None)


class FailingInitPlugin(BasePlugin):
    """Plugin that fails initialization"""
    
    def __init__(self):
        super().__init__()
        self._metadata = PluginMetadata(
            name="failing-init",
            version="1.0.0",
            author="Test",
            description="Failing plugin",
            plugin_type=PluginType.FEATURE_EXTENSION,
        )
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        raise ValueError("Initialization failed intentionally")
    
    async def _do_shutdown(self) -> PluginResult[None]:
        return PluginResult.ok(None)


class FailingShutdownPlugin(BasePlugin):
    """Plugin that fails shutdown"""
    
    def __init__(self):
        super().__init__()
        self._metadata = PluginMetadata(
            name="failing-shutdown",
            version="1.0.0",
            author="Test",
            description="Failing shutdown plugin",
            plugin_type=PluginType.FEATURE_EXTENSION,
        )
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        return PluginResult.ok(None)
    
    async def _do_shutdown(self) -> PluginResult[None]:
        raise RuntimeError("Shutdown failed intentionally")


class ConfigValidationPlugin(BasePlugin):
    """Plugin that tests config validation"""
    
    def __init__(self):
        super().__init__()
        self._metadata = PluginMetadata(
            name="config-validation",
            version="1.0.0",
            author="Test",
            description="Config validation plugin",
            plugin_type=PluginType.FEATURE_EXTENSION,
        )
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        return PluginResult.fail("Config validation failed")
    
    async def _do_shutdown(self) -> PluginResult[None]:
        return PluginResult.ok(None)


class MockBackendProvider(BaseBackendProvider):
    """Mock backend provider implementation for testing"""
    
    def __init__(self):
        super().__init__()
        self._metadata = PluginMetadata(
            name="test-backend",
            version="1.0.0",
            author="Test",
            description="Test backend",
            plugin_type=PluginType.BACKEND_PROVIDER,
        )
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        return PluginResult.ok(None)
    
    async def _do_shutdown(self) -> PluginResult[None]:
        return PluginResult.ok(None)
    
    async def _chat(self, context: ChatContext) -> PluginResult:
        return PluginResult.ok(Message(content="Test response", role="assistant"))
    
    async def _list_models(self) -> PluginResult[List[str]]:
        return PluginResult.ok(["model1", "model2"])


class MockMessageProcessor(BaseMessageProcessor):
    """Mock message processor implementation for testing"""
    
    def __init__(self, should_modify: bool = True):
        super().__init__()
        self._metadata = PluginMetadata(
            name="test-processor",
            version="1.0.0",
            author="Test",
            description="Test processor",
            plugin_type=PluginType.MESSAGE_PROCESSOR,
        )
        self.should_modify = should_modify
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        return PluginResult.ok(None)
    
    async def _do_shutdown(self) -> PluginResult[None]:
        return PluginResult.ok(None)
    
    async def _process_message(self, message: Message, context: ChatContext) -> PluginResult[Message]:
        if self.should_modify:
            modified = Message(
                content=message.content.upper(),
                role=message.role,
                timestamp=message.timestamp,
            )
            return PluginResult.ok(modified)
        return PluginResult.ok(message)


class MockFeatureExtension(BaseFeatureExtension):
    """Mock feature extension implementation for testing"""
    
    def __init__(self):
        super().__init__()
        self._metadata = PluginMetadata(
            name="test-feature",
            version="1.0.0",
            author="Test",
            description="Test feature",
            plugin_type=PluginType.FEATURE_EXTENSION,
        )
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        return PluginResult.ok(None)
    
    async def _do_shutdown(self) -> PluginResult[None]:
        return PluginResult.ok(None)
    
    async def _extend(self, context: ChatContext) -> PluginResult[ChatContext]:
        context.metadata["extended"] = True
        return PluginResult.ok(context)


class MockMiddleware(BaseMiddleware):
    """Mock middleware implementation for testing"""
    
    def __init__(self):
        super().__init__()
        self._metadata = PluginMetadata(
            name="test-middleware",
            version="1.0.0",
            author="Test",
            description="Test middleware",
            plugin_type=PluginType.MIDDLEWARE,
        )
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        return PluginResult.ok(None)
    
    async def _do_shutdown(self) -> PluginResult[None]:
        return PluginResult.ok(None)
    
    async def _process_request(self, request: dict) -> PluginResult[dict]:
        request["processed"] = True
        return PluginResult.ok(request)
    
    async def _process_response(self, response: dict) -> PluginResult[dict]:
        response["processed"] = True
        return PluginResult.ok(response)


# ============================================================================
# Test Classes
# ============================================================================

class TestBasePluginCoverage:
    """Tests to cover missing paths in BasePlugin"""
    
    @pytest.mark.asyncio
    async def test_double_initialization_idempotent(self):
        """Test that calling initialize twice is safe"""
        plugin = MinimalTestPlugin()
        config = PluginConfig()
        
        result1 = await plugin.initialize(config)
        assert result1.success
        
        # Second initialization should return success without reinitializing
        result2 = await plugin.initialize(config)
        assert result2.success
        assert plugin._initialized
    
    @pytest.mark.asyncio
    async def test_initialization_with_invalid_config(self):
        """Test initialization with configuration validation errors"""
        plugin = MinimalTestPlugin()
        config = PluginConfig()
        
        # Mock validate to return errors
        with patch.object(config, 'validate', return_value=["Error 1", "Error 2"]):
            result = await plugin.initialize(config)
            assert not result.success
            assert "Configuration errors" in result.error
    
    @pytest.mark.asyncio
    async def test_initialization_exception_handling(self):
        """Test that initialization exceptions are caught and returned as failures"""
        plugin = FailingInitPlugin()
        config = PluginConfig()
        
        result = await plugin.initialize(config)
        assert not result.success
        assert "Initialization error" in result.error or "Initialization failed" in result.error
    
    @pytest.mark.asyncio
    async def test_shutdown_not_initialized(self):
        """Test shutdown when plugin was never initialized"""
        plugin = MinimalTestPlugin()
        
        result = await plugin.shutdown()
        assert result.success
        assert not plugin._initialized
    
    @pytest.mark.asyncio
    async def test_shutdown_exception_handling(self):
        """Test that shutdown exceptions are caught"""
        plugin = FailingShutdownPlugin()
        config = PluginConfig()
        
        # Initialize first
        await plugin.initialize(config)
        assert plugin._initialized
        
        # Now shutdown should catch exception
        result = await plugin.shutdown()
        assert not result.success
        assert "Shutdown error" in result.error or "Shutdown failed" in result.error
    
    @pytest.mark.asyncio
    async def test_health_check_not_initialized(self):
        """Test health check when plugin not initialized"""
        plugin = MinimalTestPlugin()
        
        result = await plugin.health_check()
        assert result.success
        assert result.data["status"] == "not_initialized"
        assert result.data["initialized"] is False
    
    @pytest.mark.asyncio
    async def test_health_check_initialized(self):
        """Test health check when plugin is initialized"""
        plugin = MinimalTestPlugin()
        config = PluginConfig()
        
        await plugin.initialize(config)
        
        result = await plugin.health_check()
        assert result.success
        assert result.data["status"] == "healthy"
        assert result.data["initialized"] is True
        assert result.data["plugin"] == "minimal-test"
        assert result.data["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_successful_init_sets_metadata(self):
        """Test successful initialization sets initialized flag"""
        plugin = MinimalTestPlugin()
        config = PluginConfig()
        
        assert not plugin._initialized
        
        result = await plugin.initialize(config)
        assert result.success
        assert plugin._initialized
        assert plugin._config == config
    
    @pytest.mark.asyncio
    async def test_initialization_result_propagation(self):
        """Test that failed _do_initialize result is propagated"""
        plugin = ConfigValidationPlugin()
        config = PluginConfig()
        
        result = await plugin.initialize(config)
        assert not result.success
        assert not plugin._initialized


class TestBackendProviderCoverage:
    """Tests for BaseBackendProvider"""
    
    @pytest.mark.asyncio
    async def test_backend_provider_initialization(self):
        """Test backend provider can be initialized"""
        provider = MockBackendProvider()
        config = PluginConfig()
        
        result = await provider.initialize(config)
        assert result.success
        assert provider._initialized
        
        await provider.shutdown()
    
    @pytest.mark.asyncio
    async def test_backend_provider_chat_not_initialized(self):
        """Test chat fails when provider not initialized"""
        provider = MockBackendProvider()
        
        context = ChatContext(
            messages=[Message(content="Hello", role="user")],
            model="test-model",
        )
        
        result = await provider.chat(context)
        assert not result.success
        assert "not initialized" in result.error
    
    @pytest.mark.asyncio
    async def test_backend_provider_chat_success(self):
        """Test successful chat generation"""
        provider = MockBackendProvider()
        config = PluginConfig()
        await provider.initialize(config)
        
        context = ChatContext(
            messages=[Message(content="Hello", role="user")],
            model="test-model",
        )
        
        result = await provider.chat(context)
        assert result.success
        assert result.data.content == "Test response"
        
        await provider.shutdown()
    
    @pytest.mark.asyncio
    async def test_backend_provider_list_models_not_initialized(self):
        """Test list_models fails when not initialized"""
        provider = MockBackendProvider()
        
        result = await provider.list_models()
        assert not result.success
        assert "not initialized" in result.error
    
    @pytest.mark.asyncio
    async def test_backend_provider_list_models_success(self):
        """Test successful model listing"""
        provider = MockBackendProvider()
        config = PluginConfig()
        await provider.initialize(config)
        
        result = await provider.list_models()
        assert result.success
        assert len(result.data) == 2
        assert "model1" in result.data
        
        await provider.shutdown()
    
    @pytest.mark.asyncio
    async def test_backend_provider_chat_exception_handling(self):
        """Test chat exception handling"""
        provider = MockBackendProvider()
        config = PluginConfig()
        await provider.initialize(config)
        
        # Mock _chat to raise exception
        async def failing_chat(context):
            raise ValueError("Chat error")
        provider._chat = failing_chat
        
        context = ChatContext(
            messages=[Message(content="Hello", role="user")],
            model="test-model",
        )
        
        result = await provider.chat(context)
        assert not result.success
        assert "Chat error" in result.error
        
        await provider.shutdown()
    
    @pytest.mark.asyncio
    async def test_backend_provider_list_models_exception_handling(self):
        """Test list_models exception handling"""
        provider = MockBackendProvider()
        config = PluginConfig()
        await provider.initialize(config)
        
        # Mock _list_models to raise exception
        async def failing_list_models():
            raise ValueError("Model listing error")
        provider._list_models = failing_list_models
        
        result = await provider.list_models()
        assert not result.success
        assert "Model listing error" in result.error
        
        await provider.shutdown()


class TestMessageProcessorCoverage:
    """Tests for BaseMessageProcessor"""
    
    @pytest.mark.asyncio
    async def test_message_processor_not_initialized(self):
        """Test message processing fails when not initialized"""
        processor = MockMessageProcessor()
        
        message = Message(content="hello", role="user")
        context = ChatContext(messages=[], model="test")
        
        result = await processor.process_message(message, context)
        assert not result.success
        assert "not initialized" in result.error
    
    @pytest.mark.asyncio
    async def test_message_processor_modifies_message(self):
        """Test message processor can modify messages"""
        processor = MockMessageProcessor(should_modify=True)
        config = PluginConfig()
        await processor.initialize(config)
        
        message = Message(content="hello world", role="user")
        context = ChatContext(messages=[], model="test")
        
        result = await processor.process_message(message, context)
        assert result.success
        assert result.data.content == "HELLO WORLD"
        
        await processor.shutdown()
    
    @pytest.mark.asyncio
    async def test_message_processor_passthrough(self):
        """Test message processor can pass through unchanged"""
        processor = MockMessageProcessor(should_modify=False)
        config = PluginConfig()
        await processor.initialize(config)
        
        message = Message(content="hello world", role="user")
        context = ChatContext(messages=[], model="test")
        
        result = await processor.process_message(message, context)
        assert result.success
        assert result.data.content == "hello world"
        
        await processor.shutdown()
    
    @pytest.mark.asyncio
    async def test_message_processor_exception_handling(self):
        """Test message processor exception handling"""
        processor = MockMessageProcessor()
        config = PluginConfig()
        await processor.initialize(config)
        
        # Mock _process_message to raise exception
        async def failing_process(message, context):
            raise ValueError("Processing error")
        processor._process_message = failing_process
        
        message = Message(content="hello", role="user")
        context = ChatContext(messages=[], model="test")
        
        result = await processor.process_message(message, context)
        assert not result.success
        assert "Processing error" in result.error
        
        await processor.shutdown()


class TestFeatureExtensionCoverage:
    """Tests for BaseFeatureExtension"""
    
    @pytest.mark.asyncio
    async def test_feature_extension_not_initialized(self):
        """Test feature extension fails when not initialized"""
        feature = MockFeatureExtension()
        
        context = ChatContext(messages=[], model="test")
        
        result = await feature.extend(context)
        assert not result.success
        assert "not initialized" in result.error
    
    @pytest.mark.asyncio
    async def test_feature_extension_success(self):
        """Test feature extension can extend context"""
        feature = MockFeatureExtension()
        config = PluginConfig()
        await feature.initialize(config)
        
        context = ChatContext(messages=[], model="test")
        
        result = await feature.extend(context)
        assert result.success
        assert result.data.metadata.get("extended") is True
        
        await feature.shutdown()
    
    @pytest.mark.asyncio
    async def test_feature_extension_exception_handling(self):
        """Test feature extension exception handling"""
        feature = MockFeatureExtension()
        config = PluginConfig()
        await feature.initialize(config)
        
        # Mock _extend to raise exception
        async def failing_extend(context):
            raise ValueError("Extension error")
        feature._extend = failing_extend
        
        context = ChatContext(messages=[], model="test")
        
        result = await feature.extend(context)
        assert not result.success
        assert "Extension error" in result.error
        
        await feature.shutdown()


class TestMiddlewareCoverage:
    """Tests for BaseMiddleware"""
    
    @pytest.mark.asyncio
    async def test_middleware_process_request_not_initialized(self):
        """Test process_request fails when not initialized"""
        middleware = MockMiddleware()
        
        result = await middleware.process_request({"test": "data"})
        assert not result.success
        assert "not initialized" in result.error
    
    @pytest.mark.asyncio
    async def test_middleware_process_response_not_initialized(self):
        """Test process_response fails when not initialized"""
        middleware = MockMiddleware()
        
        result = await middleware.process_response({"test": "data"})
        assert not result.success
        assert "not initialized" in result.error
    
    @pytest.mark.asyncio
    async def test_middleware_process_request_success(self):
        """Test successful request processing"""
        middleware = MockMiddleware()
        config = PluginConfig()
        await middleware.initialize(config)
        
        result = await middleware.process_request({"test": "data"})
        assert result.success
        assert result.data["processed"] is True
        
        await middleware.shutdown()
    
    @pytest.mark.asyncio
    async def test_middleware_process_response_success(self):
        """Test successful response processing"""
        middleware = MockMiddleware()
        config = PluginConfig()
        await middleware.initialize(config)
        
        result = await middleware.process_response({"test": "data"})
        assert result.success
        assert result.data["processed"] is True
        
        await middleware.shutdown()
    
    @pytest.mark.asyncio
    async def test_middleware_process_request_exception_handling(self):
        """Test request processing exception handling"""
        middleware = MockMiddleware()
        config = PluginConfig()
        await middleware.initialize(config)
        
        # Mock _process_request to raise exception
        async def failing_process(request):
            raise ValueError("Request processing error")
        middleware._process_request = failing_process
        
        result = await middleware.process_request({"test": "data"})
        assert not result.success
        assert "Request processing error" in result.error
        
        await middleware.shutdown()
    
    @pytest.mark.asyncio
    async def test_middleware_process_response_exception_handling(self):
        """Test response processing exception handling"""
        middleware = MockMiddleware()
        config = PluginConfig()
        await middleware.initialize(config)
        
        # Mock _process_response to raise exception
        async def failing_process(response):
            raise ValueError("Response processing error")
        middleware._process_response = failing_process
        
        result = await middleware.process_response({"test": "data"})
        assert not result.success
        assert "Response processing error" in result.error
        
        await middleware.shutdown()


class TestPluginLifecycle:
    """Tests for complete plugin lifecycle"""
    
    @pytest.mark.asyncio
    async def test_plugin_lifecycle_complete(self):
        """Test complete plugin lifecycle"""
        plugin = MinimalTestPlugin()
        config = PluginConfig()
        
        # Not initialized
        assert not plugin._initialized
        
        # Initialize
        result = await plugin.initialize(config)
        assert result.success
        assert plugin._initialized
        
        # Health check
        health_result = await plugin.health_check()
        assert health_result.success
        
        # Shutdown
        shutdown_result = await plugin.shutdown()
        assert shutdown_result.success
        assert not plugin._initialized
    
    @pytest.mark.asyncio
    async def test_plugin_config_access(self):
        """Test plugin can access its configuration"""
        plugin = MinimalTestPlugin()
        config = PluginConfig(
            enabled=True,
            config={"key": "value"}
        )
        
        await plugin.initialize(config)
        
        # Plugin should have access to config via _config attribute
        assert plugin._config == config
        assert plugin._config.config["key"] == "value"
        
        await plugin.shutdown()

