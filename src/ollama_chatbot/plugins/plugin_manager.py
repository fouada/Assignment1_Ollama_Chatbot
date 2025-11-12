"""
Production-Grade Plugin Manager - Inversion of Control Container
Implements dependency injection, lifecycle management, and hot-reload

Design Patterns:
- Singleton pattern for global plugin registry
- Factory pattern for plugin instantiation
- Dependency Injection for plugin dependencies
- Observer pattern via hook system integration
- Strategy pattern for loading mechanisms

Architecture Principles:
- SOLID: Single responsibility, Open/Closed, Liskov substitution,
  Interface segregation, Dependency inversion
- Clean Architecture: Dependencies flow inward
- Domain-Driven Design: Plugin as aggregate root
"""

from __future__ import annotations

import asyncio
import importlib
import importlib.util
import inspect
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union, cast

from .hooks import HookManager
from .types import (
    BackendProvider,
    FeatureExtension,
    HookContext,
    HookPriority,
    HookType,
    Message,
    MessageProcessor,
    Middleware,
    Pluggable,
    PluginConfig,
    PluginConfigError,
    PluginDependencyError,
    PluginError,
    PluginLoadError,
    PluginMetadata,
    PluginResult,
    PluginState,
    PluginType,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Pluggable)


# ============================================================================
# Plugin Registry - Dependency Container
# ============================================================================


class PluginRegistry:
    """
    Thread-safe plugin registry with dependency injection

    Responsibilities:
    - Plugin instance storage
    - Type-based lookup
    - Dependency graph management
    - Lifecycle state tracking
    """

    def __init__(self):
        self._plugins: Dict[str, Pluggable] = {}
        self._plugin_states: Dict[str, PluginState] = {}
        self._plugin_configs: Dict[str, PluginConfig] = {}
        self._lock = asyncio.Lock()

        # Type-based indices for fast lookup
        self._by_type: Dict[PluginType, List[str]] = {ptype: [] for ptype in PluginType}

        # Dependency graph (plugin_name -> list of dependencies)
        self._dependencies: Dict[str, List[str]] = {}

    async def register(self, name: str, plugin: Pluggable, config: PluginConfig) -> None:
        """Register plugin instance"""
        async with self._lock:
            if name in self._plugins:
                raise PluginError(f"Plugin '{name}' already registered")

            self._plugins[name] = plugin
            self._plugin_configs[name] = config
            self._plugin_states[name] = PluginState.LOADED

            # Update type index
            plugin_type = plugin.metadata.plugin_type
            self._by_type[plugin_type].append(name)

            # Store dependencies
            self._dependencies[name] = list(plugin.metadata.dependencies)

            logger.info(f"Registered plugin: {name} (type={plugin_type.name})")

    async def unregister(self, name: str) -> None:
        """Unregister plugin"""
        async with self._lock:
            if name not in self._plugins:
                return

            plugin = self._plugins[name]
            plugin_type = plugin.metadata.plugin_type

            # Remove from indices
            del self._plugins[name]
            del self._plugin_states[name]
            del self._plugin_configs[name]
            self._by_type[plugin_type].remove(name)
            del self._dependencies[name]

            logger.info(f"Unregistered plugin: {name}")

    async def get(self, name: str) -> Optional[Pluggable]:
        """Get plugin by name"""
        return self._plugins.get(name)

    async def get_by_type(self, plugin_type: PluginType) -> List[Pluggable]:
        """Get all plugins of a specific type"""
        names = self._by_type.get(plugin_type, [])
        return [self._plugins[name] for name in names if name in self._plugins]

    async def get_state(self, name: str) -> Optional[PluginState]:
        """Get plugin state"""
        return self._plugin_states.get(name)

    async def set_state(self, name: str, state: PluginState) -> None:
        """Update plugin state"""
        async with self._lock:
            if name in self._plugin_states:
                self._plugin_states[name] = state

    async def get_config(self, name: str) -> Optional[PluginConfig]:
        """Get plugin configuration"""
        return self._plugin_configs.get(name)

    async def list_plugins(self) -> List[str]:
        """List all registered plugin names"""
        return list(self._plugins.keys())

    async def get_dependencies(self, name: str) -> List[str]:
        """Get plugin dependencies"""
        return self._dependencies.get(name, [])


# ============================================================================
# Plugin Loader - Factory and Discovery
# ============================================================================


class PluginLoader:
    """
    Dynamic plugin loading with security sandboxing

    Supports:
    - Python module loading
    - Class-based plugins
    - Plugin validation
    - Dependency checking
    """

    @staticmethod
    async def load_from_file(file_path: Path, class_name: Optional[str] = None) -> Pluggable:
        """
        Load plugin from Python file

        Args:
            file_path: Path to plugin .py file
            class_name: Specific class name to load (auto-detect if None)

        Returns:
            Plugin instance

        Raises:
            PluginLoadError: If loading fails
        """
        try:
            # Dynamic module loading
            module_name = file_path.stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)

            if spec is None or spec.loader is None:
                raise PluginLoadError(f"Could not load module from {file_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find plugin class
            if class_name:
                plugin_class = getattr(module, class_name, None)
                if plugin_class is None:
                    raise PluginLoadError(f"Class '{class_name}' not found in {file_path}")
            else:
                # Auto-detect: find first class implementing Pluggable
                plugin_class = PluginLoader._find_plugin_class(module)

            if plugin_class is None:
                raise PluginLoadError(f"No Pluggable class found in {file_path}")

            # Instantiate plugin
            plugin = plugin_class()

            # Validate plugin
            PluginLoader._validate_plugin(plugin)

            logger.info(f"Loaded plugin from {file_path}: {plugin.metadata.name}")
            return plugin

        except Exception as e:
            raise PluginLoadError(f"Failed to load plugin from {file_path}: {e}")

    @staticmethod
    def _find_plugin_class(module) -> Optional[Type[Pluggable]]:
        """Find first class implementing Pluggable protocol"""
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Skip imported classes
            if obj.__module__ != module.__name__:
                continue

            # Check if implements Pluggable (duck typing via protocol)
            if PluginLoader._implements_pluggable(obj):
                return obj

        return None

    @staticmethod
    def _implements_pluggable(cls: Type) -> bool:
        """Check if class implements Pluggable protocol"""
        required_methods = ["initialize", "shutdown", "health_check"]
        required_properties = ["metadata"]

        for method in required_methods:
            if not hasattr(cls, method):
                return False

        for prop in required_properties:
            if not hasattr(cls, prop):
                return False

        return True

    @staticmethod
    def _validate_plugin(plugin: Pluggable) -> None:
        """
        Validate plugin structure

        Raises:
            PluginLoadError: If validation fails
        """
        # Check metadata
        if not isinstance(plugin.metadata, PluginMetadata):
            raise PluginLoadError("Invalid plugin metadata")

        # Check required methods are callable
        if not callable(getattr(plugin, "initialize", None)):
            raise PluginLoadError("Plugin missing initialize() method")

        if not callable(getattr(plugin, "shutdown", None)):
            raise PluginLoadError("Plugin missing shutdown() method")

        if not callable(getattr(plugin, "health_check", None)):
            raise PluginLoadError("Plugin missing health_check() method")

    @staticmethod
    async def discover_plugins(directory: Path) -> List[Path]:
        """
        Discover all plugin files in directory

        Convention:
        - Files ending in _plugin.py or _middleware.py
        - Located in specified directory or subdirectories

        Args:
            directory: Root directory to search

        Returns:
            List of plugin file paths
        """
        if not directory.exists() or not directory.is_dir():
            logger.warning(f"Plugin directory not found: {directory}")
            return []

        plugin_files = []

        # Search patterns
        patterns = ["*_plugin.py", "*_middleware.py"]

        for pattern in patterns:
            plugin_files.extend(directory.rglob(pattern))

        logger.info(f"Discovered {len(plugin_files)} plugin file(s) in {directory}")
        return plugin_files


# ============================================================================
# Plugin Manager - Orchestrator
# ============================================================================


class PluginManager:
    """
    Central plugin management system

    Responsibilities:
    - Plugin lifecycle (load, initialize, activate, shutdown)
    - Dependency resolution and injection
    - Hook system integration
    - Hot-reload support
    - Health monitoring
    - Metrics aggregation

    Example:
        >>> manager = PluginManager()
        >>> await manager.initialize()
        >>> await manager.load_plugins_from_directory(Path("plugins"))
        >>> result = await manager.execute_message_processors(message, context)
    """

    def __init__(
        self,
        plugin_directory: Optional[Path] = None,
        enable_hot_reload: bool = False,
        enable_circuit_breaker: bool = True,
    ):
        """
        Initialize plugin manager

        Args:
            plugin_directory: Directory containing plugins
            enable_hot_reload: Enable plugin hot-reloading
            enable_circuit_breaker: Enable fault protection
        """
        self.plugin_directory = plugin_directory or Path("plugins")
        self.enable_hot_reload = enable_hot_reload
        self.enable_circuit_breaker = enable_circuit_breaker

        # Core components
        self.registry = PluginRegistry()
        self.hook_manager = HookManager(enable_circuit_breaker=enable_circuit_breaker)
        self.loader = PluginLoader()

        # State
        self._initialized = False
        self._lock = asyncio.Lock()

        logger.info(f"PluginManager created (directory={plugin_directory}, " f"hot_reload={enable_hot_reload})")

    async def initialize(self) -> None:
        """
        Initialize plugin manager

        Lifecycle:
        1. Discover plugins
        2. Load plugins
        3. Resolve dependencies
        4. Initialize plugins
        5. Register hooks
        """
        if self._initialized:
            logger.warning("PluginManager already initialized")
            return

        async with self._lock:
            logger.info("Initializing PluginManager...")

            # Trigger startup hooks
            await self.hook_manager.execute_hooks(
                HookType.ON_STARTUP, HookContext(hook_type=HookType.ON_STARTUP, data={})
            )

            self._initialized = True
            logger.info("PluginManager initialized successfully")

    async def shutdown(self) -> None:
        """
        Shutdown plugin manager gracefully

        Lifecycle:
        1. Trigger shutdown hooks
        2. Deactivate plugins
        3. Shutdown plugins
        4. Unload plugins
        5. Cleanup resources
        """
        if not self._initialized:
            return

        async with self._lock:
            logger.info("Shutting down PluginManager...")

            # Trigger shutdown hooks
            await self.hook_manager.execute_hooks(
                HookType.ON_SHUTDOWN,
                HookContext(hook_type=HookType.ON_SHUTDOWN, data={}),
            )

            # Shutdown all plugins
            plugin_names = await self.registry.list_plugins()
            for name in plugin_names:
                await self.unload_plugin(name)

            self._initialized = False
            logger.info("PluginManager shutdown complete")

    async def load_plugin(self, file_path: Path, config: Optional[PluginConfig] = None) -> str:
        """
        Load and initialize a single plugin

        Args:
            file_path: Path to plugin file
            config: Plugin configuration (uses defaults if None)

        Returns:
            Plugin name

        Raises:
            PluginLoadError: If loading fails
        """
        # Load plugin class
        plugin = await self.loader.load_from_file(file_path)
        plugin_name = plugin.metadata.name

        # Use provided config or create default
        if config is None:
            config = PluginConfig()

        # Validate config
        errors = config.validate()
        if errors:
            raise PluginConfigError(f"Invalid config for {plugin_name}: {errors}")

        # Check dependencies
        await self._check_dependencies(plugin)

        # Register plugin
        await self.registry.register(plugin_name, plugin, config)

        # Initialize plugin
        await self._initialize_plugin(plugin_name)

        # Register hooks if plugin defines them
        await self._register_plugin_hooks(plugin)

        # Trigger plugin load hook
        await self.hook_manager.execute_hooks(
            HookType.ON_PLUGIN_LOAD,
            HookContext(hook_type=HookType.ON_PLUGIN_LOAD, data={"plugin_name": plugin_name}),
        )

        logger.info(f"Plugin loaded successfully: {plugin_name}")
        return plugin_name

    async def unload_plugin(self, plugin_name: str) -> None:
        """
        Unload and cleanup a plugin

        Args:
            plugin_name: Name of plugin to unload
        """
        plugin = await self.registry.get(plugin_name)
        if plugin is None:
            logger.warning(f"Plugin not found: {plugin_name}")
            return

        # Shutdown plugin
        await self._shutdown_plugin(plugin_name)

        # Unregister hooks
        for hook_type in HookType:
            await self.hook_manager.unregister_hook(hook_type, plugin_name)

        # Trigger unload hook
        await self.hook_manager.execute_hooks(
            HookType.ON_PLUGIN_UNLOAD,
            HookContext(hook_type=HookType.ON_PLUGIN_UNLOAD, data={"plugin_name": plugin_name}),
        )

        # Unregister from registry
        await self.registry.unregister(plugin_name)

        logger.info(f"Plugin unloaded: {plugin_name}")

    async def load_plugins_from_directory(self, directory: Optional[Path] = None) -> List[str]:
        """
        Discover and load all plugins from directory

        Args:
            directory: Plugin directory (uses default if None)

        Returns:
            List of loaded plugin names
        """
        plugin_dir = directory or self.plugin_directory

        # Discover plugins
        plugin_files = await self.loader.discover_plugins(plugin_dir)

        loaded_plugins = []
        for file_path in plugin_files:
            try:
                plugin_name = await self.load_plugin(file_path)
                loaded_plugins.append(plugin_name)
            except PluginLoadError as e:
                logger.error(f"Failed to load plugin from {file_path}: {e}")
                continue

        logger.info(f"Loaded {len(loaded_plugins)} plugin(s) from {plugin_dir}")
        return loaded_plugins

    async def _initialize_plugin(self, plugin_name: str) -> None:
        """Initialize plugin with configuration"""
        plugin = await self.registry.get(plugin_name)
        config = await self.registry.get_config(plugin_name)

        if plugin is None or config is None:
            raise PluginError(f"Plugin not registered: {plugin_name}")

        await self.registry.set_state(plugin_name, PluginState.INITIALIZING)

        try:
            result = await plugin.initialize(config)
            if not result.success:
                raise PluginError(f"Initialization failed: {result.error}")

            await self.registry.set_state(plugin_name, PluginState.ACTIVE)
            logger.info(f"Plugin initialized: {plugin_name}")

        except Exception as e:
            await self.registry.set_state(plugin_name, PluginState.ERROR)
            raise PluginError(f"Plugin initialization error: {e}")

    async def _shutdown_plugin(self, plugin_name: str) -> None:
        """Shutdown plugin gracefully"""
        plugin = await self.registry.get(plugin_name)
        if plugin is None:
            return

        await self.registry.set_state(plugin_name, PluginState.UNLOADING)

        try:
            result = await plugin.shutdown()
            if not result.success:
                logger.warning(f"Plugin shutdown reported error: {result.error}")

            await self.registry.set_state(plugin_name, PluginState.UNLOADED)
            logger.info(f"Plugin shutdown: {plugin_name}")

        except Exception as e:
            logger.error(f"Error during plugin shutdown: {e}")
            await self.registry.set_state(plugin_name, PluginState.ERROR)

    async def _check_dependencies(self, plugin: Pluggable) -> None:
        """
        Check if plugin dependencies are satisfied

        Raises:
            PluginDependencyError: If dependencies missing
        """
        for dep_name in plugin.metadata.dependencies:
            dep_plugin = await self.registry.get(dep_name)
            if dep_plugin is None:
                raise PluginDependencyError(f"Missing dependency '{dep_name}' for plugin " f"'{plugin.metadata.name}'")

            dep_state = await self.registry.get_state(dep_name)
            if dep_state != PluginState.ACTIVE:
                raise PluginDependencyError(f"Dependency '{dep_name}' not active (state={dep_state})")

    async def _register_plugin_hooks(self, plugin: Pluggable) -> None:
        """
        Auto-register plugin methods as hooks

        Convention:
        - Methods starting with 'on_' are hook handlers
        - Method name maps to hook type (e.g., on_startup -> ON_STARTUP)
        """
        plugin_name = plugin.metadata.name

        # Get plugin config for priority
        config = await self.registry.get_config(plugin_name)
        priority = config.priority if config else HookPriority.NORMAL

        # Find hook methods
        for attr_name in dir(plugin):
            if not attr_name.startswith("on_"):
                continue

            method = getattr(plugin, attr_name)
            if not callable(method):
                continue

            # Map method name to hook type
            hook_type_name = attr_name.upper()
            try:
                hook_type = HookType(attr_name)  # Try value match first
            except ValueError:
                # Try name match
                hook_type = next((ht for ht in HookType if ht.name == hook_type_name), None)

            if hook_type:
                await self.hook_manager.register_hook(
                    hook_type=hook_type,
                    callback=method,
                    priority=priority,
                    plugin_name=plugin_name,
                )

    # ========================================================================
    # Plugin Execution Methods
    # ========================================================================

    async def execute_message_processors(self, message: Message, context: Any) -> PluginResult[Message]:
        """
        Execute all message processing plugins

        Args:
            message: Message to process
            context: Chat context

        Returns:
            Processed message (or original if processing fails)
        """
        processors = await self.registry.get_by_type(PluginType.MESSAGE_PROCESSOR)

        current_message = message

        for processor in processors:
            if not isinstance(processor, MessageProcessor):
                continue

            result = await processor.process_message(current_message, context)

            if result.success and result.data:
                current_message = result.data
            else:
                logger.warning(f"Message processor failed: {processor.metadata.name} - {result.error}")

        return PluginResult.ok(current_message)

    async def get_backend_provider(self, name: str = "ollama") -> Optional[BackendProvider]:
        """Get backend provider by name"""
        plugins = await self.registry.get_by_type(PluginType.BACKEND_PROVIDER)

        for plugin in plugins:
            if plugin.metadata.name == name:
                return cast(BackendProvider, plugin)

        return None

    async def get_plugin_status(self) -> Dict[str, Any]:
        """Get status of all plugins"""
        plugin_names = await self.registry.list_plugins()

        status = {}
        for name in plugin_names:
            plugin = await self.registry.get(name)
            state = await self.registry.get_state(name)
            config = await self.registry.get_config(name)

            if plugin:
                health = await plugin.health_check()
                status[name] = {
                    "type": plugin.metadata.plugin_type.name,
                    "version": plugin.metadata.version,
                    "state": state.name if state else "UNKNOWN",
                    "enabled": config.enabled if config else False,
                    "health": health.to_dict() if hasattr(health, "to_dict") else {},
                }

        return status

    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics"""
        return await self.hook_manager.get_metrics()
