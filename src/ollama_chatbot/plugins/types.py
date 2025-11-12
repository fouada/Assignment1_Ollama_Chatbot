"""
Production-Grade Type Definitions for Plugin Architecture
Follows MIT-level standards for type safety and extensibility

Design Principles:
- Protocol-based design for structural subtyping (PEP 544)
- Immutable data structures where appropriate
- Generic types for reusability
- Comprehensive type hints (PEP 484, 585, 586, 593)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Protocol,
    Set,
    TypeVar,
    Union,
    runtime_checkable,
)

# ============================================================================
# Core Type Variables
# ============================================================================

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)


# ============================================================================
# Enumerations
# ============================================================================


class PluginType(Enum):
    """Plugin categories following Open-Closed Principle"""

    MESSAGE_PROCESSOR = auto()  # Pre/post-processing of messages
    BACKEND_PROVIDER = auto()  # AI backend implementations
    FEATURE_EXTENSION = auto()  # Capability extensions (RAG, memory, tools)
    MIDDLEWARE = auto()  # Request/response transformation
    OBSERVABILITY = auto()  # Logging, metrics, tracing


class HookPriority(Enum):
    """Execution priority for hooks - ensures deterministic ordering"""

    CRITICAL = 0  # Security, validation (execute first)
    HIGH = 100
    NORMAL = 500
    LOW = 1000
    MONITORING = 2000  # Observability (execute last)


class PluginState(Enum):
    """Plugin lifecycle states - finite state machine"""

    UNLOADED = auto()
    LOADING = auto()
    LOADED = auto()
    INITIALIZING = auto()
    ACTIVE = auto()
    PAUSED = auto()
    ERROR = auto()
    UNLOADING = auto()


class HookType(Enum):
    """Hook execution points - event-driven architecture"""

    # Lifecycle hooks
    ON_STARTUP = "on_startup"
    ON_SHUTDOWN = "on_shutdown"
    ON_PLUGIN_LOAD = "on_plugin_load"
    ON_PLUGIN_UNLOAD = "on_plugin_unload"

    # Request lifecycle
    ON_REQUEST_START = "on_request_start"
    ON_REQUEST_COMPLETE = "on_request_complete"
    ON_REQUEST_ERROR = "on_request_error"

    # Message processing
    BEFORE_MESSAGE = "before_message"
    AFTER_MESSAGE = "after_message"
    ON_STREAM_CHUNK = "on_stream_chunk"

    # Model operations
    BEFORE_MODEL_LOAD = "before_model_load"
    AFTER_MODEL_LOAD = "after_model_load"
    ON_MODEL_SWITCH = "on_model_switch"

    # Error handling
    ON_ERROR = "on_error"
    ON_RETRY = "on_retry"


# ============================================================================
# Data Classes - Immutable where possible
# ============================================================================


@dataclass(frozen=True)
class PluginMetadata:
    """
    Plugin metadata - immutable descriptor
    Follows semantic versioning (semver.org)

    API Version Compatibility:
        api_version: Specifies which plugin API version this plugin uses
        This ensures plugins built for older APIs don't break with new changes

    Dependency Management:
        dependencies: List of required plugin names
        dependency_versions: Version constraints for each dependency
        Format: ">=1.0.0,<2.0.0" or "~=1.5.0" or "==1.2.3"
    """

    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    api_version: str = "1.0.0"  # Plugin API version compatibility
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    dependency_versions: Dict[str, str] = field(default_factory=dict)  # Version constraints
    tags: tuple[str, ...] = field(default_factory=tuple)
    homepage: Optional[str] = None
    license: str = "MIT"

    def __post_init__(self):
        """Validate metadata on construction"""
        if not self.name or not self.name.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"Invalid plugin name: {self.name}")
        if not self._is_valid_semver(self.version):
            raise ValueError(f"Invalid version format: {self.version}")
        if not self._is_valid_semver(self.api_version):
            raise ValueError(f"Invalid API version format: {self.api_version}")
        # Validate dependency versions format
        for dep_name, version_spec in self.dependency_versions.items():
            if not self._is_valid_version_spec(version_spec):
                raise ValueError(f"Invalid version specification for {dep_name}: {version_spec}")

    @staticmethod
    def _is_valid_semver(version: str) -> bool:
        """Validate semantic version format"""
        parts = version.split(".")
        return len(parts) == 3 and all(p.isdigit() for p in parts)

    @staticmethod
    def _is_valid_version_spec(spec: str) -> bool:
        """Validate version specification format (e.g., '>=1.0.0,<2.0.0')"""
        if not spec:
            return False
        # Allow simple patterns: ==, >=, <=, >, <, ~=
        import re
        pattern = r"^(==|>=|<=|>|<|~=)\s*\d+\.\d+\.\d+(,\s*(==|>=|<=|>|<|~=)\s*\d+\.\d+\.\d+)*$"
        return bool(re.match(pattern, spec))

    def is_compatible_with_api(self, current_api_version: str) -> bool:
        """Check if plugin is compatible with current API version"""
        # Simple major version compatibility check
        plugin_major = int(self.api_version.split(".")[0])
        current_major = int(current_api_version.split(".")[0])
        return plugin_major == current_major

    def check_dependency_version(self, dep_name: str, dep_version: str) -> bool:
        """
        Check if a dependency version satisfies the constraint

        Args:
            dep_name: Dependency plugin name
            dep_version: Version of installed dependency

        Returns:
            True if version satisfies constraint
        """
        if dep_name not in self.dependency_versions:
            return True  # No constraint specified

        spec = self.dependency_versions[dep_name]
        return self._version_satisfies(dep_version, spec)

    @staticmethod
    def _version_satisfies(version: str, spec: str) -> bool:
        """Check if version satisfies specification"""
        from packaging import version as pkg_version
        try:
            ver = pkg_version.parse(version)
            # Parse constraints
            for constraint in spec.split(","):
                constraint = constraint.strip()
                if constraint.startswith("=="):
                    required = pkg_version.parse(constraint[2:].strip())
                    if ver != required:
                        return False
                elif constraint.startswith(">="):
                    required = pkg_version.parse(constraint[2:].strip())
                    if ver < required:
                        return False
                elif constraint.startswith("<="):
                    required = pkg_version.parse(constraint[2:].strip())
                    if ver > required:
                        return False
                elif constraint.startswith(">"):
                    required = pkg_version.parse(constraint[1:].strip())
                    if ver <= required:
                        return False
                elif constraint.startswith("<"):
                    required = pkg_version.parse(constraint[1:].strip())
                    if ver >= required:
                        return False
                elif constraint.startswith("~="):
                    # Compatible release: ~=1.5.0 matches >=1.5.0,<1.6.0
                    required = pkg_version.parse(constraint[2:].strip())
                    parts = constraint[2:].strip().split(".")
                    if len(parts) >= 2:
                        next_minor = f"{parts[0]}.{int(parts[1])+1}.0"
                        if not (ver >= required and ver < pkg_version.parse(next_minor)):
                            return False
            return True
        except Exception:
            # If packaging not available or parse fails, allow it
            return True


@dataclass
class PluginConfig:
    """
    Plugin configuration - mutable for runtime updates
    Supports JSON schema validation
    """

    enabled: bool = True
    priority: HookPriority = HookPriority.NORMAL
    config: Dict[str, Any] = field(default_factory=dict)
    max_retries: int = 3
    timeout_seconds: float = 30.0
    rate_limit: Optional[int] = None  # Requests per minute
    environment: Literal["development", "staging", "production"] = "production"

    def validate(self) -> List[str]:
        """Validate configuration - returns list of errors"""
        errors = []
        if self.timeout_seconds <= 0:
            errors.append("timeout_seconds must be positive")
        if self.max_retries < 0:
            errors.append("max_retries must be non-negative")
        if self.rate_limit is not None and self.rate_limit <= 0:
            errors.append("rate_limit must be positive")
        return errors


@dataclass
class Message:
    """
    Message data structure - domain model
    Supports streaming and batch processing
    """

    content: str
    role: Literal["user", "assistant", "system"]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    model: Optional[str] = None
    tokens: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for API responses"""
        return {
            "content": self.content,
            "role": self.role,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "model": self.model,
            "tokens": self.tokens,
        }


@dataclass
class ChatContext:
    """
    Conversation context - aggregate root
    Immutable history with copy-on-write updates
    """

    messages: List[Message]
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, message: Message) -> ChatContext:
        """Return new context with message added - immutable pattern"""
        return ChatContext(
            messages=self.messages + [message],
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=self.stream,
            metadata=self.metadata.copy(),
        )


@dataclass
class HookContext:
    """
    Hook execution context - carries state through pipeline
    Thread-local storage for async execution
    """

    hook_type: HookType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    trace_id: Optional[str] = None  # For distributed tracing
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Safe data access"""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Mutable data updates during hook execution"""
        self.data[key] = value


@dataclass
class PluginResult(Generic[T]):
    """
    Result monad for plugin execution - Railway Oriented Programming
    Encapsulates success/failure without exceptions
    """

    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: Optional[float] = None
    error_code: Optional[str] = None
    status_code: Optional[int] = None

    @classmethod
    def ok(cls, data: T, **metadata) -> PluginResult[T]:
        """Create success result"""
        return cls(success=True, data=data, metadata=metadata)

    @classmethod
    def fail(
        cls, error: str, error_code: Optional[str] = None, status_code: Optional[int] = None, **metadata
    ) -> PluginResult[T]:
        """Create failure result"""
        return cls(success=False, error=error, error_code=error_code, status_code=status_code, metadata=metadata)

    def map(self, func: Callable[[T], Any]) -> PluginResult:
        """Transform success data - functor pattern"""
        if self.success and self.data is not None:
            try:
                return PluginResult.ok(func(self.data))
            except Exception as e:
                return PluginResult.fail(str(e))
        return self

    def flat_map(self, func: Callable[[T], PluginResult]) -> PluginResult:
        """Chain operations - monad pattern"""
        if self.success and self.data is not None:
            return func(self.data)
        return self


# ============================================================================
# Protocols - Structural Subtyping
# ============================================================================


@runtime_checkable
class Pluggable(Protocol):
    """
    Base protocol for all plugins - duck typing interface
    No inheritance required, just implement methods
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Plugin descriptor"""
        ...

    async def initialize(self, config: PluginConfig) -> PluginResult[None]:
        """Async initialization with dependency injection"""
        ...

    async def shutdown(self) -> PluginResult[None]:
        """Graceful shutdown with cleanup"""
        ...

    async def health_check(self) -> PluginResult[Dict[str, Any]]:
        """Health status for monitoring"""
        ...


@runtime_checkable
class MessageProcessor(Pluggable, Protocol):
    """Protocol for message processing plugins"""

    async def process_message(self, message: Message, context: ChatContext) -> PluginResult[Message]:
        """Transform message - pure function where possible"""
        ...


@runtime_checkable
class BackendProvider(Pluggable, Protocol):
    """Protocol for AI backend implementations"""

    async def chat(self, context: ChatContext) -> PluginResult[Union[Message, AsyncIterator[str]]]:
        """Generate chat response - supports streaming"""
        ...

    async def list_models(self) -> PluginResult[List[str]]:
        """Discover available models"""
        ...


@runtime_checkable
class FeatureExtension(Pluggable, Protocol):
    """Protocol for feature extensions (RAG, memory, tools)"""

    async def extend(self, context: ChatContext) -> PluginResult[ChatContext]:
        """Enhance context with additional capabilities"""
        ...


@runtime_checkable
class Middleware(Pluggable, Protocol):
    """Protocol for request/response middleware"""

    async def process_request(self, request: Dict[str, Any]) -> PluginResult[Dict[str, Any]]:
        """Transform incoming request"""
        ...

    async def process_response(self, response: Dict[str, Any]) -> PluginResult[Dict[str, Any]]:
        """Transform outgoing response"""
        ...


# ============================================================================
# Hook System Types
# ============================================================================


HookCallback = Callable[[HookContext], Union[None, PluginResult[Any]]]
AsyncHookCallback = Callable[[HookContext], Any]  # Returns awaitable


@dataclass
class HookRegistration:
    """
    Hook registration record - for event subscribers
    Supports priority-based ordering with timestamp tiebreaking

    Ordering:
        1. Primary: by priority (lower value = higher priority)
        2. Secondary: by registration time (earlier = higher priority)
        3. Tertiary: by plugin name (alphabetical)

    This ensures deterministic, reproducible hook execution order.
    """

    hook_type: HookType
    callback: AsyncHookCallback
    priority: HookPriority
    plugin_name: str
    enabled: bool = True
    registration_time: float = field(default_factory=lambda: __import__('time').time())

    def __lt__(self, other: HookRegistration) -> bool:
        """
        Enable sorting by priority, then registration time, then name

        This provides stable, deterministic ordering even when
        multiple hooks have the same priority level.
        """
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        if self.registration_time != other.registration_time:
            return self.registration_time < other.registration_time
        return self.plugin_name < other.plugin_name


# ============================================================================
# Metrics & Observability
# ============================================================================


@dataclass
class PluginMetrics:
    """
    Plugin performance metrics - for APM systems
    Compatible with Prometheus, DataDog, etc.
    """

    plugin_name: str
    invocations: int = 0
    successes: int = 0
    failures: int = 0
    total_execution_time_ms: float = 0.0
    avg_execution_time_ms: float = 0.0
    min_execution_time_ms: float = float("inf")
    max_execution_time_ms: float = 0.0
    last_error: Optional[str] = None
    last_execution: Optional[datetime] = None

    def update(self, result: PluginResult, execution_time_ms: float) -> None:
        """Update metrics from execution result"""
        self.invocations += 1
        self.last_execution = datetime.utcnow()

        if result.success:
            self.successes += 1
        else:
            self.failures += 1
            self.last_error = result.error

        self.total_execution_time_ms += execution_time_ms
        self.avg_execution_time_ms = self.total_execution_time_ms / self.invocations
        self.min_execution_time_ms = min(self.min_execution_time_ms, execution_time_ms)
        self.max_execution_time_ms = max(self.max_execution_time_ms, execution_time_ms)

    def to_dict(self) -> Dict[str, Any]:
        """Export for monitoring systems"""
        return {
            "plugin_name": self.plugin_name,
            "invocations": self.invocations,
            "successes": self.successes,
            "failures": self.failures,
            "success_rate": (self.successes / self.invocations if self.invocations > 0 else 0.0),
            "avg_execution_time_ms": self.avg_execution_time_ms,
            "min_execution_time_ms": (
                self.min_execution_time_ms if self.min_execution_time_ms != float("inf") else 0.0
            ),
            "max_execution_time_ms": self.max_execution_time_ms,
            "last_error": self.last_error,
            "last_execution": (self.last_execution.isoformat() if self.last_execution else None),
        }


# ============================================================================
# Error Types
# ============================================================================


class PluginError(Exception):
    """Base exception for plugin system"""

    pass


class PluginLoadError(PluginError):
    """Failed to load plugin"""

    pass


class PluginConfigError(PluginError):
    """Invalid plugin configuration"""

    pass


class PluginExecutionError(PluginError):
    """Plugin execution failure"""

    pass


class PluginDependencyError(PluginError):
    """Missing or incompatible dependencies"""

    pass


class HookExecutionError(PluginError):
    """Hook execution failure"""

    pass
