"""
Production-Grade Plugin System for Ollama Chatbot

MIT-Level Features:
- Type-safe protocol-based plugins
- Event-driven hook system
- Dependency injection
- Hot-reload support
- Circuit breakers for fault tolerance
- Comprehensive metrics and observability

Example Usage:
    >>> from plugins import PluginManager
    >>> from pathlib import Path
    >>>
    >>> # Initialize plugin manager
    >>> manager = PluginManager(plugin_directory=Path("plugins"))
    >>> await manager.initialize()
    >>>
    >>> # Load plugins
    >>> await manager.load_plugins_from_directory()
    >>>
    >>> # Get backend
    >>> backend = await manager.get_backend_provider("ollama")
    >>> result = await backend.chat(context)
"""

from .base_plugin import (
    BaseBackendProvider,
    BaseFeatureExtension,
    BaseMessageProcessor,
    BaseMiddleware,
    BasePlugin,
)
from .hooks import HookManager, create_hook_decorator
from .plugin_manager import PluginManager, PluginRegistry
from .types import (
    BackendProvider,
    ChatContext,
    FeatureExtension,
    HookContext,
    HookPriority,
    HookType,
    Message,
    MessageProcessor,
    Middleware,
    PluginConfig,
    PluginError,
    PluginMetadata,
    PluginMetrics,
    PluginResult,
    PluginState,
    PluginType,
    Pluggable,
)

__version__ = "1.0.0"

__all__ = [
    # Core Manager
    "PluginManager",
    "PluginRegistry",
    "HookManager",
    # Base Classes
    "BasePlugin",
    "BaseMessageProcessor",
    "BaseBackendProvider",
    "BaseFeatureExtension",
    "BaseMiddleware",
    # Protocols
    "Pluggable",
    "MessageProcessor",
    "BackendProvider",
    "FeatureExtension",
    "Middleware",
    # Types
    "PluginType",
    "PluginState",
    "PluginMetadata",
    "PluginConfig",
    "PluginResult",
    "PluginMetrics",
    "PluginError",
    # Hook System
    "HookType",
    "HookPriority",
    "HookContext",
    "create_hook_decorator",
    # Domain Models
    "Message",
    "ChatContext",
]
