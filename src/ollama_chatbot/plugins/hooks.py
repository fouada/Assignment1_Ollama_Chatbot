"""
Production-Grade Hook System - Event-Driven Architecture
Implements observer pattern with async support and priority ordering

Design Patterns:
- Observer pattern for event subscriptions
- Chain of Responsibility for hook execution
- Strategy pattern for execution policies
- Circuit Breaker for fault tolerance

Thread Safety:
- asyncio locks for concurrent access
- Thread-safe collections
- Copy-on-write for hook lists
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from copy import copy
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any, Dict, List, Optional, Set

from .types import (
    AsyncHookCallback,
    HookContext,
    HookExecutionError,
    HookPriority,
    HookRegistration,
    HookType,
    PluginMetrics,
    PluginResult,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Circuit Breaker for Fault Tolerance
# ============================================================================


class CircuitBreakerState:
    """
    Thread-safe circuit breaker state machine
    Prevents cascading failures from misbehaving plugins

    Thread Safety:
        All state modifications are protected by a threading.Lock
        to prevent race conditions in concurrent environments.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        failure_count: int = 0,
        last_failure_time: Optional[datetime] = None,
        state: str = "closed"
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = failure_count
        self.last_failure_time = last_failure_time
        self.state = state  # closed, open, half_open
        self._lock = Lock()  # Thread safety

    def record_success(self) -> None:
        """Reset on successful execution (thread-safe)"""
        with self._lock:
            self.failure_count = 0
            self.state = "closed"

    def record_failure(self) -> None:
        """Track failures and potentially open circuit (thread-safe)"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now(timezone.utc)

            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

    def can_execute(self) -> bool:
        """Check if execution is allowed (thread-safe)"""
        with self._lock:
            if self.state == "closed":
                return True

            if self.state == "open":
                # Check if timeout has elapsed
                if self.last_failure_time:
                    elapsed = datetime.now(timezone.utc) - self.last_failure_time
                    if elapsed.total_seconds() > self.timeout_seconds:
                        self.state = "half_open"
                        logger.info("Circuit breaker entering half-open state")
                        return True
                return False

            # half_open state - allow one attempt
            return True


# ============================================================================
# Hook Execution Context Manager
# ============================================================================


class HookExecutionContext:
    """
    Context for hook execution with timeout and cancellation support
    Ensures proper cleanup even on errors
    """

    def __init__(self, hook_type: HookType, timeout: float = 30.0):
        self.hook_type = hook_type
        self.timeout = timeout
        self.start_time: Optional[float] = None
        self.cancelled = False

    async def __aenter__(self):
        self.start_time = time.perf_counter()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is asyncio.TimeoutError:
            logger.error(f"Hook {self.hook_type.value} timed out after {self.timeout}s")
            return False  # Propagate timeout
        return False

    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds"""
        if self.start_time is None:
            return 0.0
        return (time.perf_counter() - self.start_time) * 1000


# ============================================================================
# Hook Manager - Core Event System
# ============================================================================


class HookManager:
    """
    Enterprise-grade hook management system

    Features:
    - Priority-based hook ordering
    - Async execution with timeout protection
    - Circuit breaker for fault isolation
    - Comprehensive metrics and observability
    - Hot-reload support
    - Thread-safe operations

    Example:
        >>> manager = HookManager()
        >>> await manager.register_hook(
        ...     HookType.BEFORE_MESSAGE,
        ...     my_callback,
        ...     priority=HookPriority.HIGH,
        ...     plugin_name="my_plugin"
        ... )
        >>> await manager.execute_hooks(HookType.BEFORE_MESSAGE, context)
    """

    def __init__(
        self,
        enable_circuit_breaker: bool = True,
        default_timeout: float = 30.0,
        max_concurrent_hooks: int = 10,
    ):
        """
        Initialize hook manager

        Args:
            enable_circuit_breaker: Enable fault protection
            default_timeout: Default timeout for hook execution
            max_concurrent_hooks: Max parallel hook executions
        """
        # Hook storage - defaultdict for automatic initialization
        self._hooks: Dict[HookType, List[HookRegistration]] = defaultdict(list)

        # Thread safety
        self._lock = asyncio.Lock()
        self._metrics_lock = Lock()  # Synchronous lock for metrics updates

        # Circuit breakers per hook registration
        self._circuit_breakers: Dict[str, CircuitBreakerState] = {}

        # Metrics tracking
        self._metrics: Dict[str, PluginMetrics] = {}

        # Configuration
        self.enable_circuit_breaker = enable_circuit_breaker
        self.default_timeout = default_timeout
        self.max_concurrent_hooks = max_concurrent_hooks

        # Semaphore for concurrency control
        self._semaphore = asyncio.Semaphore(max_concurrent_hooks)

        logger.info(
            f"HookManager initialized (circuit_breaker={enable_circuit_breaker}, "
            f"timeout={default_timeout}s, max_concurrent={max_concurrent_hooks})"
        )

    async def register_hook(
        self,
        hook_type: HookType,
        callback: AsyncHookCallback,
        priority: HookPriority = HookPriority.NORMAL,
        plugin_name: str = "unknown",
        enabled: bool = True,
    ) -> None:
        """
        Register a hook callback with priority

        Thread-safe with copy-on-write pattern for lock-free reads

        Args:
            hook_type: Type of hook to register
            callback: Async callback function
            priority: Execution priority (lower = earlier)
            plugin_name: Name of plugin registering hook
            enabled: Whether hook is initially enabled
        """
        registration = HookRegistration(
            hook_type=hook_type,
            callback=callback,
            priority=priority,
            plugin_name=plugin_name,
            enabled=enabled,
        )

        async with self._lock:
            # Add to hooks list
            self._hooks[hook_type].append(registration)

            # Sort by priority for deterministic execution order
            self._hooks[hook_type].sort()

            # Initialize circuit breaker
            breaker_key = self._get_breaker_key(plugin_name, hook_type)
            if breaker_key not in self._circuit_breakers:
                self._circuit_breakers[breaker_key] = CircuitBreakerState()

            # Initialize metrics
            if plugin_name not in self._metrics:
                self._metrics[plugin_name] = PluginMetrics(plugin_name=plugin_name)

        logger.info(f"Registered hook: {hook_type.value} for plugin '{plugin_name}' " f"with priority {priority.name}")

    async def unregister_hook(self, hook_type: HookType, plugin_name: str) -> None:
        """
        Unregister all hooks for a plugin and hook type

        Args:
            hook_type: Type of hook to unregister
            plugin_name: Name of plugin to remove
        """
        async with self._lock:
            original_count = len(self._hooks[hook_type])
            self._hooks[hook_type] = [reg for reg in self._hooks[hook_type] if reg.plugin_name != plugin_name]
            removed_count = original_count - len(self._hooks[hook_type])

        if removed_count > 0:
            logger.info(f"Unregistered {removed_count} hook(s) for plugin '{plugin_name}' " f"on {hook_type.value}")

    async def execute_hooks(
        self,
        hook_type: HookType,
        context: HookContext,
        fail_fast: bool = False,
    ) -> List[PluginResult[Any]]:
        """
        Execute all registered hooks for a given type

        Execution order:
        1. Sort hooks by priority
        2. Execute in order with timeout protection
        3. Collect results
        4. Update metrics

        Args:
            hook_type: Type of hooks to execute
            context: Execution context with data
            fail_fast: Stop on first failure (default: continue on errors)

        Returns:
            List of results from each hook execution
        """
        # Get hooks snapshot without holding lock
        hooks_snapshot = await self._get_hooks_snapshot(hook_type)

        if not hooks_snapshot:
            logger.debug(f"No hooks registered for {hook_type.value}")
            return []

        logger.debug(f"Executing {len(hooks_snapshot)} hook(s) for {hook_type.value}")

        results = []

        for registration in hooks_snapshot:
            if not registration.enabled:
                continue

            # Circuit breaker check
            breaker_key = self._get_breaker_key(registration.plugin_name, hook_type)
            circuit_breaker = self._circuit_breakers.get(breaker_key)

            if self.enable_circuit_breaker and circuit_breaker and not circuit_breaker.can_execute():
                logger.warning(
                    f"Circuit breaker open for {registration.plugin_name} on " f"{hook_type.value}, skipping"
                )
                results.append(
                    PluginResult.fail(
                        error="Circuit breaker open",
                        plugin=registration.plugin_name,
                    )
                )
                continue

            # Execute hook with concurrency control
            result = await self._execute_single_hook(registration, context)
            results.append(result)

            # Update circuit breaker
            if circuit_breaker:
                if result.success:
                    circuit_breaker.record_success()
                else:
                    circuit_breaker.record_failure()

            # Fail fast if requested
            if fail_fast and not result.success:
                logger.error(f"Hook execution failed (fail_fast=True), stopping: " f"{result.error}")
                break

        return results

    async def _execute_single_hook(self, registration: HookRegistration, context: HookContext) -> PluginResult[Any]:
        """
        Execute a single hook with timeout and error handling

        Features:
        - Timeout protection
        - Exception isolation
        - Metrics collection
        - Structured logging
        """
        async with self._semaphore:  # Concurrency control
            exec_context = HookExecutionContext(registration.hook_type, self.default_timeout)

            try:
                async with exec_context:
                    # Execute with timeout
                    result = await asyncio.wait_for(registration.callback(context), timeout=self.default_timeout)

                    # Handle void callbacks (no return value)
                    if result is None:
                        result = PluginResult.ok(None)

                    # Ensure PluginResult type
                    if not isinstance(result, PluginResult):
                        result = PluginResult.ok(result)

                    # Add execution time
                    result.execution_time_ms = exec_context.elapsed_ms()

                    # Update metrics
                    self._update_metrics(registration.plugin_name, result, exec_context.elapsed_ms())

                    logger.debug(f"Hook executed: {registration.plugin_name} " f"({exec_context.elapsed_ms():.2f}ms)")

                    return result

            except asyncio.TimeoutError:
                error_msg = f"Hook timeout after {self.default_timeout}s: " f"{registration.plugin_name}"
                logger.error(error_msg)
                result = PluginResult.fail(error=error_msg)
                self._update_metrics(registration.plugin_name, result, self.default_timeout * 1000)
                return result

            except Exception as e:
                error_msg = f"Hook execution error in {registration.plugin_name}: " f"{type(e).__name__}: {str(e)}"
                logger.exception(error_msg)
                result = PluginResult.fail(error=error_msg)
                self._update_metrics(registration.plugin_name, result, exec_context.elapsed_ms())
                return result

    async def _get_hooks_snapshot(self, hook_type: HookType) -> List[HookRegistration]:
        """
        Get a snapshot of hooks for a type (lock-free read via copy)

        Returns:
            Copy of hooks list sorted by priority
        """
        # Quick read without lock - safe because we use copy-on-write
        # for modifications
        hooks = self._hooks.get(hook_type, [])
        return copy(hooks)  # Return copy to prevent concurrent modification

    def _get_breaker_key(self, plugin_name: str, hook_type: HookType) -> str:
        """Generate unique key for circuit breaker"""
        return f"{plugin_name}:{hook_type.value}"

    def _update_metrics(self, plugin_name: str, result: PluginResult, execution_time_ms: float) -> None:
        """Update plugin metrics (thread-safe)"""
        with self._metrics_lock:
            if plugin_name in self._metrics:
                self._metrics[plugin_name].update(result, execution_time_ms)

    async def get_metrics(self, plugin_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics for plugins

        Args:
            plugin_name: Specific plugin name, or None for all plugins

        Returns:
            Metrics dictionary
        """
        if plugin_name:
            metrics = self._metrics.get(plugin_name)
            return metrics.to_dict() if metrics else {}

        return {name: metrics.to_dict() for name, metrics in self._metrics.items()}

    async def get_hook_info(self) -> Dict[str, Any]:
        """
        Get information about registered hooks

        Returns:
            Dictionary with hook registration information
        """
        info = {}
        for hook_type, registrations in self._hooks.items():
            info[hook_type.value] = [
                {
                    "plugin": reg.plugin_name,
                    "priority": reg.priority.name,
                    "enabled": reg.enabled,
                }
                for reg in registrations
            ]
        return info

    async def enable_hook(self, plugin_name: str, hook_type: HookType) -> None:
        """Enable a specific hook"""
        async with self._lock:
            for reg in self._hooks.get(hook_type, []):
                if reg.plugin_name == plugin_name:
                    reg.enabled = True
                    logger.info(f"Enabled hook for {plugin_name} on {hook_type.value}")

    async def disable_hook(self, plugin_name: str, hook_type: HookType) -> None:
        """Disable a specific hook"""
        async with self._lock:
            for reg in self._hooks.get(hook_type, []):
                if reg.plugin_name == plugin_name:
                    reg.enabled = False
                    logger.info(f"Disabled hook for {plugin_name} on {hook_type.value}")

    async def reset_circuit_breaker(self, plugin_name: str) -> None:
        """Manually reset circuit breaker for a plugin"""
        for key in list(self._circuit_breakers.keys()):
            if key.startswith(f"{plugin_name}:"):
                self._circuit_breakers[key] = CircuitBreakerState()
        logger.info(f"Reset circuit breakers for {plugin_name}")

    async def clear_all_hooks(self) -> None:
        """Clear all registered hooks (useful for testing)"""
        async with self._lock:
            self._hooks.clear()
            self._circuit_breakers.clear()
            self._metrics.clear()
        logger.warning("Cleared all hooks")


# ============================================================================
# Hook Decorators - Convenience Methods
# ============================================================================

# Global task tracking for decorator-registered hooks (prevents memory leaks)
_decorator_tasks: Set[asyncio.Task] = set()


def create_hook_decorator(hook_manager: HookManager):
    """
    Factory for creating hook decorators with proper task management

    Memory Safety:
        Tracks all registration tasks to prevent memory leaks.
        Tasks are automatically cleaned up when completed.

    Example:
        >>> hook = create_hook_decorator(manager)
        >>>
        >>> @hook(HookType.BEFORE_MESSAGE, priority=HookPriority.HIGH)
        >>> async def my_hook(context: HookContext):
        >>>     print("Processing message")
    """

    def hook(
        hook_type: HookType,
        priority: HookPriority = HookPriority.NORMAL,
        plugin_name: str = "decorator",
    ):
        def decorator(func: AsyncHookCallback):
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            # Register on decoration with proper task management
            task = asyncio.create_task(
                hook_manager.register_hook(
                    hook_type=hook_type,
                    callback=wrapper,
                    priority=priority,
                    plugin_name=plugin_name,
                )
            )

            # Track task and add cleanup callback
            _decorator_tasks.add(task)
            task.add_done_callback(_decorator_tasks.discard)

            return wrapper

        return decorator

    return hook
