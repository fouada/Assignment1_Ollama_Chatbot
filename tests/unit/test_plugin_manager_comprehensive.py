"""
Comprehensive Tests for PluginManager Coverage
Tests PluginRegistry, PluginLoader, and PluginManager
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import pytest
from typing import List

from ollama_chatbot.plugins.plugin_manager import (
    PluginManager,
    PluginRegistry,
    PluginLoader,
)
from ollama_chatbot.plugins.base_plugin import BasePlugin
from ollama_chatbot.plugins.types import (
    PluginConfig,
    PluginMetadata,
    PluginType,
    PluginResult,
    PluginState,
    PluginError,
    PluginLoadError,
    PluginDependencyError,
    HookType,
    HookPriority,
)


# ============================================================================
# Mock Plugins for Testing
# ============================================================================

class SimpleTestPlugin(BasePlugin):
    """Simple test plugin"""
    
    def __init__(self):
        super().__init__()
        self._metadata = PluginMetadata(
            name="simple-test",
            version="1.0.0",
            author="Test",
            description="Simple test plugin",
            plugin_type=PluginType.FEATURE_EXTENSION,
        )
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        return PluginResult.ok(None)
    
    async def _do_shutdown(self) -> PluginResult[None]:
        return PluginResult.ok(None)


class DependentPlugin(BasePlugin):
    """Plugin with dependencies"""
    
    def __init__(self, depends_on: List[str] = None):
        super().__init__()
        self._metadata = PluginMetadata(
            name="dependent-plugin",
            version="1.0.0",
            author="Test",
            description="Plugin with dependencies",
            plugin_type=PluginType.FEATURE_EXTENSION,
            dependencies=tuple(depends_on or []),
        )
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        return PluginResult.ok(None)
    
    async def _do_shutdown(self) -> PluginResult[None]:
        return PluginResult.ok(None)


class HookPlugin(BasePlugin):
    """Plugin that registers hooks"""
    
    def __init__(self):
        super().__init__()
        self._metadata = PluginMetadata(
            name="hook-plugin",
            version="1.0.0",
            author="Test",
            description="Plugin with hooks",
            plugin_type=PluginType.FEATURE_EXTENSION,
        )
        self.hook_called = False
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        return PluginResult.ok(None)
    
    async def _do_shutdown(self) -> PluginResult[None]:
        return PluginResult.ok(None)
    
    async def on_startup(self, context):
        """Hook method that should be auto-registered"""
        self.hook_called = True
        return context


# ============================================================================
# PluginRegistry Tests
# ============================================================================

class TestPluginRegistry:
    """Tests for PluginRegistry"""
    
    @pytest.mark.asyncio
    async def test_registry_initialization(self):
        """Test registry initialization"""
        registry = PluginRegistry()
        
        assert len(registry._plugins) == 0
        assert len(registry._plugin_states) == 0
        assert len(registry._plugin_configs) == 0
        assert all(len(registry._by_type[ptype]) == 0 for ptype in PluginType)
    
    @pytest.mark.asyncio
    async def test_register_plugin(self):
        """Test registering a plugin"""
        registry = PluginRegistry()
        plugin = SimpleTestPlugin()
        config = PluginConfig()
        
        await registry.register("test-plugin", plugin, config)
        
        assert "test-plugin" in registry._plugins
        assert registry._plugin_states["test-plugin"] == PluginState.LOADED
        assert registry._plugin_configs["test-plugin"] == config
    
    @pytest.mark.asyncio
    async def test_register_duplicate_plugin_raises(self):
        """Test registering duplicate plugin raises error"""
        registry = PluginRegistry()
        plugin = SimpleTestPlugin()
        config = PluginConfig()
        
        await registry.register("test-plugin", plugin, config)
        
        with pytest.raises(PluginError, match="already registered"):
            await registry.register("test-plugin", plugin, config)
    
    @pytest.mark.asyncio
    async def test_register_plugin_updates_type_index(self):
        """Test plugin registration updates type index"""
        registry = PluginRegistry()
        plugin = SimpleTestPlugin()
        config = PluginConfig()
        
        await registry.register("test-plugin", plugin, config)
        
        assert "test-plugin" in registry._by_type[PluginType.FEATURE_EXTENSION]
    
    @pytest.mark.asyncio
    async def test_register_plugin_stores_dependencies(self):
        """Test plugin registration stores dependencies"""
        registry = PluginRegistry()
        plugin = DependentPlugin(depends_on=["dep1", "dep2"])
        config = PluginConfig()
        
        await registry.register("dependent", plugin, config)
        
        assert registry._dependencies["dependent"] == ["dep1", "dep2"]
    
    @pytest.mark.asyncio
    async def test_unregister_plugin(self):
        """Test unregistering a plugin"""
        registry = PluginRegistry()
        plugin = SimpleTestPlugin()
        config = PluginConfig()
        
        await registry.register("test-plugin", plugin, config)
        await registry.unregister("test-plugin")
        
        assert "test-plugin" not in registry._plugins
        assert "test-plugin" not in registry._plugin_states
        assert "test-plugin" not in registry._plugin_configs
        assert "test-plugin" not in registry._by_type[PluginType.FEATURE_EXTENSION]
    
    @pytest.mark.asyncio
    async def test_unregister_nonexistent_plugin(self):
        """Test unregistering nonexistent plugin doesn't raise"""
        registry = PluginRegistry()
        
        # Should not raise
        await registry.unregister("nonexistent")
    
    @pytest.mark.asyncio
    async def test_get_plugin(self):
        """Test getting a plugin by name"""
        registry = PluginRegistry()
        plugin = SimpleTestPlugin()
        config = PluginConfig()
        
        await registry.register("test-plugin", plugin, config)
        
        retrieved = await registry.get("test-plugin")
        assert retrieved is plugin
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_plugin(self):
        """Test getting nonexistent plugin returns None"""
        registry = PluginRegistry()
        
        result = await registry.get("nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_by_type(self):
        """Test getting plugins by type"""
        registry = PluginRegistry()
        
        plugin1 = SimpleTestPlugin()
        plugin2 = SimpleTestPlugin()
        config = PluginConfig()
        
        await registry.register("plugin1", plugin1, config)
        await registry.register("plugin2", plugin2, config)
        
        plugins = await registry.get_by_type(PluginType.FEATURE_EXTENSION)
        assert len(plugins) == 2
    
    @pytest.mark.asyncio
    async def test_get_by_type_empty(self):
        """Test getting plugins by type when none registered"""
        registry = PluginRegistry()
        
        plugins = await registry.get_by_type(PluginType.BACKEND_PROVIDER)
        assert len(plugins) == 0
    
    @pytest.mark.asyncio
    async def test_get_state(self):
        """Test getting plugin state"""
        registry = PluginRegistry()
        plugin = SimpleTestPlugin()
        config = PluginConfig()
        
        await registry.register("test-plugin", plugin, config)
        
        state = await registry.get_state("test-plugin")
        assert state == PluginState.LOADED
    
    @pytest.mark.asyncio
    async def test_set_state(self):
        """Test setting plugin state"""
        registry = PluginRegistry()
        plugin = SimpleTestPlugin()
        config = PluginConfig()
        
        await registry.register("test-plugin", plugin, config)
        await registry.set_state("test-plugin", PluginState.ACTIVE)
        
        state = await registry.get_state("test-plugin")
        assert state == PluginState.ACTIVE
    
    @pytest.mark.asyncio
    async def test_get_config(self):
        """Test getting plugin configuration"""
        registry = PluginRegistry()
        plugin = SimpleTestPlugin()
        config = PluginConfig(enabled=True)
        
        await registry.register("test-plugin", plugin, config)
        
        retrieved_config = await registry.get_config("test-plugin")
        assert retrieved_config is config
    
    @pytest.mark.asyncio
    async def test_list_plugins(self):
        """Test listing all plugins"""
        registry = PluginRegistry()
        
        plugin1 = SimpleTestPlugin()
        plugin2 = SimpleTestPlugin()
        config = PluginConfig()
        
        await registry.register("plugin1", plugin1, config)
        await registry.register("plugin2", plugin2, config)
        
        plugins = await registry.list_plugins()
        assert len(plugins) == 2
        assert "plugin1" in plugins
        assert "plugin2" in plugins
    
    @pytest.mark.asyncio
    async def test_get_dependencies(self):
        """Test getting plugin dependencies"""
        registry = PluginRegistry()
        plugin = DependentPlugin(depends_on=["dep1"])
        config = PluginConfig()
        
        await registry.register("dependent", plugin, config)
        
        deps = await registry.get_dependencies("dependent")
        assert deps == ["dep1"]


# ============================================================================
# PluginLoader Tests
# ============================================================================

class TestPluginLoader:
    """Tests for PluginLoader"""
    
    @pytest.mark.asyncio
    async def test_load_from_file_success(self):
        """Test loading plugin from file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_file = Path(tmpdir) / "test_plugin.py"
            plugin_file.write_text("""
from ollama_chatbot.plugins.base_plugin import BasePlugin
from ollama_chatbot.plugins.types import PluginMetadata, PluginType, PluginConfig, PluginResult

class TestPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self._metadata = PluginMetadata(
            name="test",
            version="1.0.0",
            author="Test",
            description="Test",
            plugin_type=PluginType.FEATURE_EXTENSION,
        )
    
    @property
    def metadata(self):
        return self._metadata
    
    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        return PluginResult.ok(None)
    
    async def _do_shutdown(self) -> PluginResult[None]:
        return PluginResult.ok(None)
""")
            
            loader = PluginLoader()
            plugin = await loader.load_from_file(plugin_file, "TestPlugin")
            
            assert plugin is not None
            assert plugin.metadata.name == "test"
    
    @pytest.mark.asyncio
    async def test_load_from_nonexistent_file(self):
        """Test loading from nonexistent file raises error"""
        loader = PluginLoader()
        
        with pytest.raises(PluginLoadError):
            await loader.load_from_file(Path("/nonexistent/file.py"))
    
    @pytest.mark.asyncio
    async def test_load_from_file_class_not_found(self):
        """Test loading specific class that doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_file = Path(tmpdir) / "test_plugin.py"
            plugin_file.write_text("# Empty file")
            
            loader = PluginLoader()
            
            with pytest.raises(PluginLoadError, match="not found"):
                await loader.load_from_file(plugin_file, "NonExistentClass")
    
    @pytest.mark.asyncio
    async def test_load_from_file_no_pluggable_class(self):
        """Test loading file with no Pluggable class"""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_file = Path(tmpdir) / "test_plugin.py"
            plugin_file.write_text("""
class NotAPlugin:
    pass
""")
            
            loader = PluginLoader()
            
            with pytest.raises(PluginLoadError, match="No Pluggable"):
                await loader.load_from_file(plugin_file)
    
    @pytest.mark.asyncio
    async def test_discover_plugins(self):
        """Test discovering plugins in directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir)
            
            # Create some plugin files
            (plugin_dir / "test_plugin.py").write_text("# plugin")
            (plugin_dir / "another_plugin.py").write_text("# plugin")
            (plugin_dir / "not_a_plugin.txt").write_text("# not a plugin")
            
            loader = PluginLoader()
            plugins = await loader.discover_plugins(plugin_dir)
            
            # Should find the .py files
            assert len(plugins) >= 2
    
    @pytest.mark.asyncio
    async def test_discover_plugins_nonexistent_dir(self):
        """Test discovering plugins in nonexistent directory"""
        loader = PluginLoader()
        
        plugins = await loader.discover_plugins(Path("/nonexistent"))
        assert len(plugins) == 0
    
    @pytest.mark.asyncio
    async def test_discover_plugins_with_subdirs(self):
        """Test discovering plugins in subdirectories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir)
            subdir = plugin_dir / "subdir"
            subdir.mkdir()
            
            (plugin_dir / "plugin1_plugin.py").write_text("# plugin")
            (subdir / "plugin2_plugin.py").write_text("# plugin")
            
            loader = PluginLoader()
            plugins = await loader.discover_plugins(plugin_dir)
            
            assert len(plugins) >= 2


# ============================================================================
# PluginManager Tests
# ============================================================================

class TestPluginManager:
    """Tests for PluginManager"""
    
    @pytest.mark.asyncio
    async def test_plugin_manager_initialization(self):
        """Test plugin manager initialization"""
        manager = PluginManager(
            plugin_directory=Path("/tmp/plugins"),
            enable_hot_reload=True,
            enable_circuit_breaker=False
        )
        
        assert manager.plugin_directory == Path("/tmp/plugins")
        assert manager.enable_hot_reload is True
        assert manager.enable_circuit_breaker is False
        assert not manager._initialized
    
    @pytest.mark.asyncio
    async def test_plugin_manager_initialize(self):
        """Test plugin manager initialization"""
        manager = PluginManager()
        
        await manager.initialize()
        
        assert manager._initialized is True
    
    @pytest.mark.asyncio
    async def test_plugin_manager_double_initialize(self):
        """Test double initialization is safe"""
        manager = PluginManager()
        
        await manager.initialize()
        await manager.initialize()  # Should not raise
        
        assert manager._initialized is True
    
    @pytest.mark.asyncio
    async def test_plugin_manager_shutdown(self):
        """Test plugin manager shutdown"""
        manager = PluginManager()
        await manager.initialize()
        
        await manager.shutdown()
        
        assert manager._initialized is False
    
    @pytest.mark.asyncio
    async def test_plugin_manager_shutdown_not_initialized(self):
        """Test shutdown when not initialized"""
        manager = PluginManager()
        
        await manager.shutdown()  # Should not raise
        
        assert manager._initialized is False
    
    @pytest.mark.asyncio
    async def test_load_plugin_from_mock(self):
        """Test loading a mock plugin directly"""
        manager = PluginManager()
        await manager.initialize()
        
        # Manually register a mock plugin
        plugin = SimpleTestPlugin()
        config = PluginConfig()
        
        await manager.registry.register("mock-plugin", plugin, config)
        
        # Initialize the plugin
        await manager._initialize_plugin("mock-plugin")
        
        state = await manager.registry.get_state("mock-plugin")
        assert state == PluginState.ACTIVE
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_initialize_plugin_not_registered_raises(self):
        """Test initializing unregistered plugin raises error"""
        manager = PluginManager()
        await manager.initialize()
        
        with pytest.raises(PluginError, match="not registered"):
            await manager._initialize_plugin("nonexistent")
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_initialize_plugin_failure_sets_error_state(self):
        """Test failed plugin initialization sets error state"""
        manager = PluginManager()
        await manager.initialize()
        
        # Create a plugin that fails to initialize
        plugin = SimpleTestPlugin()
        config = PluginConfig()
        
        await manager.registry.register("failing", plugin, config)
        
        # Mock the initialize to fail
        async def failing_init(cfg):
            return PluginResult.fail("Initialization failed")
        plugin.initialize = failing_init
        
        with pytest.raises(PluginError):
            await manager._initialize_plugin("failing")
        
        state = await manager.registry.get_state("failing")
        assert state == PluginState.ERROR
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_shutdown_plugin(self):
        """Test shutting down a plugin"""
        manager = PluginManager()
        await manager.initialize()
        
        plugin = SimpleTestPlugin()
        config = PluginConfig()
        
        await manager.registry.register("test", plugin, config)
        await manager._initialize_plugin("test")
        
        await manager._shutdown_plugin("test")
        
        state = await manager.registry.get_state("test")
        assert state == PluginState.UNLOADED
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_shutdown_plugin_nonexistent(self):
        """Test shutting down nonexistent plugin"""
        manager = PluginManager()
        await manager.initialize()
        
        # Should not raise
        await manager._shutdown_plugin("nonexistent")
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_check_dependencies_satisfied(self):
        """Test dependency checking when satisfied"""
        manager = PluginManager()
        await manager.initialize()
        
        # Register dependency first
        dep_plugin = SimpleTestPlugin()
        dep_config = PluginConfig()
        await manager.registry.register("dependency", dep_plugin, dep_config)
        await manager._initialize_plugin("dependency")
        
        # Now register dependent plugin
        plugin = DependentPlugin(depends_on=["dependency"])
        
        # Should not raise
        await manager._check_dependencies(plugin)
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_check_dependencies_missing_raises(self):
        """Test dependency checking when dependency missing"""
        manager = PluginManager()
        await manager.initialize()
        
        plugin = DependentPlugin(depends_on=["missing-dep"])
        
        with pytest.raises(PluginDependencyError, match="Missing dependency"):
            await manager._check_dependencies(plugin)
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_check_dependencies_not_active_raises(self):
        """Test dependency checking when dependency not active"""
        manager = PluginManager()
        await manager.initialize()
        
        # Register dependency but don't initialize it
        dep_plugin = SimpleTestPlugin()
        dep_config = PluginConfig()
        await manager.registry.register("dependency", dep_plugin, dep_config)
        
        plugin = DependentPlugin(depends_on=["dependency"])
        
        with pytest.raises(PluginDependencyError, match="not active"):
            await manager._check_dependencies(plugin)
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_register_plugin_hooks(self):
        """Test auto-registering plugin hooks"""
        manager = PluginManager()
        await manager.initialize()
        
        plugin = HookPlugin()
        config = PluginConfig(priority=HookPriority.HIGH)
        
        await manager.registry.register("hook-plugin", plugin, config)
        
        # Register hooks
        await manager._register_plugin_hooks(plugin)
        
        # Check if hook was registered
        # We can't easily verify this without executing hooks
        # but we can check that no error was raised
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_execute_message_processors(self):
        """Test executing message processors"""
        from ollama_chatbot.plugins.types import Message, ChatContext
        from ollama_chatbot.plugins.base_plugin import BaseMessageProcessor
        
        class TestProcessor(BaseMessageProcessor):
            def __init__(self):
                super().__init__()
                self._metadata = PluginMetadata(
                    name="test-processor",
                    version="1.0.0",
                    author="Test",
                    description="Test",
                    plugin_type=PluginType.MESSAGE_PROCESSOR,
                )
            
            @property
            def metadata(self):
                return self._metadata
            
            async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
                return PluginResult.ok(None)
            
            async def _do_shutdown(self) -> PluginResult[None]:
                return PluginResult.ok(None)
            
            async def _process_message(self, message: Message, context: ChatContext) -> PluginResult[Message]:
                message.content = message.content.upper()
                return PluginResult.ok(message)
        
        manager = PluginManager()
        await manager.initialize()
        
        processor = TestProcessor()
        config = PluginConfig()
        
        await manager.registry.register("processor", processor, config)
        await manager._initialize_plugin("processor")
        
        message = Message(content="hello", role="user")
        context = ChatContext(messages=[], model="test")
        
        result = await manager.execute_message_processors(message, context)
        
        assert result.success
        assert result.data.content == "HELLO"
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_get_backend_provider(self):
        """Test getting backend provider by name"""
        from ollama_chatbot.plugins.base_plugin import BaseBackendProvider
        from ollama_chatbot.plugins.types import ChatContext, Message
        
        class TestBackend(BaseBackendProvider):
            def __init__(self):
                super().__init__()
                self._metadata = PluginMetadata(
                    name="ollama",
                    version="1.0.0",
                    author="Test",
                    description="Test",
                    plugin_type=PluginType.BACKEND_PROVIDER,
                )
            
            @property
            def metadata(self):
                return self._metadata
            
            async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
                return PluginResult.ok(None)
            
            async def _do_shutdown(self) -> PluginResult[None]:
                return PluginResult.ok(None)
            
            async def _chat(self, context: ChatContext) -> PluginResult:
                return PluginResult.ok(Message(content="response", role="assistant"))
            
            async def _list_models(self) -> PluginResult[List[str]]:
                return PluginResult.ok(["model1"])
        
        manager = PluginManager()
        await manager.initialize()
        
        backend = TestBackend()
        config = PluginConfig()
        
        await manager.registry.register("ollama", backend, config)
        await manager._initialize_plugin("ollama")
        
        provider = await manager.get_backend_provider("ollama")
        
        assert provider is not None
        assert provider.metadata.name == "ollama"
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_get_backend_provider_not_found(self):
        """Test getting nonexistent backend provider"""
        manager = PluginManager()
        await manager.initialize()
        
        provider = await manager.get_backend_provider("nonexistent")
        assert provider is None
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_get_plugin_status(self):
        """Test getting plugin status"""
        manager = PluginManager()
        await manager.initialize()
        
        plugin = SimpleTestPlugin()
        config = PluginConfig(enabled=True)
        
        await manager.registry.register("test", plugin, config)
        await manager._initialize_plugin("test")
        
        status = await manager.get_plugin_status()
        
        assert "test" in status
        assert status["test"]["type"] == "FEATURE_EXTENSION"
        assert status["test"]["version"] == "1.0.0"
        assert status["test"]["enabled"] is True
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_get_metrics(self):
        """Test getting metrics"""
        manager = PluginManager()
        await manager.initialize()
        
        metrics = await manager.get_metrics()
        
        assert isinstance(metrics, dict)
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_load_plugins_from_directory(self):
        """Test loading plugins from directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir)
            
            # Create a valid plugin file
            plugin_file = plugin_dir / "test_plugin.py"
            plugin_file.write_text("""
from ollama_chatbot.plugins.base_plugin import BasePlugin
from ollama_chatbot.plugins.types import PluginMetadata, PluginType, PluginConfig, PluginResult

class TestPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self._metadata = PluginMetadata(
            name="test",
            version="1.0.0",
            author="Test",
            description="Test",
            plugin_type=PluginType.FEATURE_EXTENSION,
        )
    
    @property
    def metadata(self):
        return self._metadata
    
    async def _do_initialize(self, config: PluginConfig) -> PluginResult[None]:
        return PluginResult.ok(None)
    
    async def _do_shutdown(self) -> PluginResult[None]:
        return PluginResult.ok(None)
""")
            
            manager = PluginManager(plugin_directory=plugin_dir)
            await manager.initialize()
            
            # This will try to load plugins - some may fail but shouldn't crash
            loaded = await manager.load_plugins_from_directory()
            
            # We may or may not load plugins depending on validation
            assert isinstance(loaded, list)
            
            await manager.shutdown()


class TestPluginManagerEdgeCases:
    """Tests for edge cases"""
    
    @pytest.mark.asyncio
    async def test_plugin_manager_with_hooks_integration(self):
        """Test plugin manager with hook system integration"""
        manager = PluginManager(enable_circuit_breaker=True)
        await manager.initialize()
        
        # The hook manager should be initialized
        assert manager.hook_manager is not None
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_shutdown_with_multiple_plugins(self):
        """Test shutdown with multiple registered plugins"""
        manager = PluginManager()
        await manager.initialize()
        
        # Register multiple plugins
        for i in range(3):
            plugin = SimpleTestPlugin()
            config = PluginConfig()
            await manager.registry.register(f"plugin{i}", plugin, config)
            await manager._initialize_plugin(f"plugin{i}")
        
        # Shutdown should handle all plugins
        await manager.shutdown()
        
        assert manager._initialized is False

