"""
Comprehensive Tests for Hook System Coverage
Tests HookManager, CircuitBreakerState, and HookExecutionContext
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import pytest
import time

from ollama_chatbot.plugins.hooks import (
    HookManager,
    HookExecutionContext,
    CircuitBreakerState,
)
from ollama_chatbot.plugins.types import (
    HookType,
    HookPriority,
    HookContext,
    PluginResult,
)


class TestCircuitBreakerState:
    """Tests for CircuitBreakerState"""

    def test_circuit_breaker_state_initialization(self):
        """Test circuit breaker state initialization"""
        cb = CircuitBreakerState(failure_threshold=3, timeout_seconds=60)

        assert cb.failure_count == 0
        assert cb.state == "closed"
        assert cb.failure_threshold == 3
        assert cb.timeout_seconds == 60
        assert cb.last_failure_time is None

    def test_record_success_resets_state(self):
        """Test that recording success resets failure count"""
        cb = CircuitBreakerState(failure_threshold=3, timeout_seconds=60)

        # Simulate some failures
        cb.failure_count = 2
        cb.state = "half_open"

        cb.record_success()

        assert cb.failure_count == 0
        assert cb.state == "closed"

    def test_record_failure_increments_count(self):
        """Test that recording failure increments count"""
        cb = CircuitBreakerState(failure_threshold=3, timeout_seconds=60)

        cb.record_failure()

        assert cb.failure_count == 1
        assert cb.last_failure_time is not None
        assert cb.state == "closed"  # Not open yet

    def test_record_failure_opens_circuit(self):
        """Test that reaching threshold opens circuit"""
        cb = CircuitBreakerState(failure_threshold=3, timeout_seconds=60)

        # Record failures until threshold
        cb.record_failure()
        cb.record_failure()
        assert cb.state == "closed"

        cb.record_failure()
        assert cb.state == "open"
        assert cb.failure_count == 3

    def test_can_execute_when_closed(self):
        """Test can_execute returns True when closed"""
        cb = CircuitBreakerState(failure_threshold=3, timeout_seconds=60)

        assert cb.can_execute() is True

    def test_can_execute_when_open_no_timeout(self):
        """Test can_execute returns False when open and timeout not elapsed"""
        cb = CircuitBreakerState(failure_threshold=1, timeout_seconds=60)

        # Open the circuit
        cb.record_failure()
        assert cb.state == "open"

        # Should not be able to execute
        assert cb.can_execute() is False

    def test_can_execute_when_open_after_timeout(self):
        """Test can_execute returns True after timeout and transitions to half_open"""
        cb = CircuitBreakerState(failure_threshold=1, timeout_seconds=1)

        # Open the circuit
        cb.record_failure()
        assert cb.state == "open"

        # Manually set last_failure_time to past
        cb.last_failure_time = datetime.utcnow() - timedelta(seconds=2)

        # Should transition to half_open
        result = cb.can_execute()
        assert result is True
        assert cb.state == "half_open"

    def test_can_execute_when_half_open(self):
        """Test can_execute returns True when half_open"""
        cb = CircuitBreakerState()
        cb.state = "half_open"

        assert cb.can_execute() is True


class TestHookExecutionContext:
    """Tests for HookExecutionContext"""

    @pytest.mark.asyncio
    async def test_hook_execution_context_basic(self):
        """Test basic hook execution context"""
        ctx = HookExecutionContext(HookType.ON_REQUEST_START, timeout=30.0)

        assert ctx.hook_type == HookType.ON_REQUEST_START
        assert ctx.timeout == 30.0
        assert ctx.start_time is None
        assert ctx.cancelled is False

    @pytest.mark.asyncio
    async def test_hook_execution_context_manager(self):
        """Test hook execution context as context manager"""
        ctx = HookExecutionContext(HookType.ON_REQUEST_START, timeout=30.0)

        async with ctx:
            assert ctx.start_time is not None
            start = ctx.start_time
            await asyncio.sleep(0.01)

        # After exiting, start_time should still be set
        assert ctx.start_time == start

    @pytest.mark.asyncio
    async def test_hook_execution_context_elapsed_ms(self):
        """Test elapsed time calculation"""
        ctx = HookExecutionContext(HookType.ON_REQUEST_START, timeout=30.0)

        async with ctx:
            await asyncio.sleep(0.01)
            elapsed = ctx.elapsed_ms()
            assert elapsed > 0
            assert elapsed >= 10  # At least 10ms

    @pytest.mark.asyncio
    async def test_hook_execution_context_elapsed_before_start(self):
        """Test elapsed_ms returns 0 before starting"""
        ctx = HookExecutionContext(HookType.ON_REQUEST_START, timeout=30.0)

        assert ctx.elapsed_ms() == 0.0

    @pytest.mark.asyncio
    async def test_hook_execution_context_timeout_handling(self):
        """Test timeout error handling in context manager"""
        ctx = HookExecutionContext(HookType.ON_REQUEST_START, timeout=0.01)

        # Simulate timeout by raising asyncio.TimeoutError
        try:
            async with ctx:
                raise asyncio.TimeoutError()
        except asyncio.TimeoutError:
            pass  # Expected


class TestHookManagerBasics:
    """Tests for HookManager basic functionality"""

    def test_hook_manager_initialization(self):
        """Test hook manager initialization"""
        manager = HookManager(enable_circuit_breaker=True, default_timeout=30.0, max_concurrent_hooks=10)

        assert manager.enable_circuit_breaker is True
        assert manager.default_timeout == 30.0
        assert manager.max_concurrent_hooks == 10
        assert len(manager._hooks) == 0
        assert len(manager._circuit_breakers) == 0
        assert len(manager._metrics) == 0

    def test_hook_manager_initialization_defaults(self):
        """Test hook manager with default parameters"""
        manager = HookManager()

        assert manager.enable_circuit_breaker is True
        assert manager.default_timeout == 30.0
        assert manager.max_concurrent_hooks == 10


class TestHookRegistration:
    """Tests for hook registration"""

    @pytest.mark.asyncio
    async def test_register_hook_basic(self):
        """Test basic hook registration"""
        manager = HookManager(enable_circuit_breaker=False)

        async def test_hook(context: HookContext) -> HookContext:
            return context

        await manager.register_hook(
            hook_type=HookType.ON_REQUEST_START,
            callback=test_hook,
            priority=HookPriority.NORMAL,
            plugin_name="test-plugin",
        )

        hooks = manager._hooks[HookType.ON_REQUEST_START]
        assert len(hooks) > 0
        assert hooks[0].plugin_name == "test-plugin"
        assert hooks[0].priority == HookPriority.NORMAL

    @pytest.mark.asyncio
    async def test_register_multiple_hooks_sorted_by_priority(self):
        """Test that hooks are sorted by priority"""
        manager = HookManager(enable_circuit_breaker=False)

        async def hook1(context: HookContext) -> HookContext:
            return context

        async def hook2(context: HookContext) -> HookContext:
            return context

        async def hook3(context: HookContext) -> HookContext:
            return context

        # Register in random priority order
        await manager.register_hook(HookType.ON_REQUEST_START, hook2, HookPriority.NORMAL, "plugin2")
        await manager.register_hook(HookType.ON_REQUEST_START, hook1, HookPriority.HIGH, "plugin1")
        await manager.register_hook(HookType.ON_REQUEST_START, hook3, HookPriority.LOW, "plugin3")

        hooks = manager._hooks[HookType.ON_REQUEST_START]

        # Should be sorted: HIGH, NORMAL, LOW
        assert hooks[0].priority == HookPriority.HIGH
        assert hooks[1].priority == HookPriority.NORMAL
        assert hooks[2].priority == HookPriority.LOW

    @pytest.mark.asyncio
    async def test_register_hook_with_circuit_breaker(self):
        """Test hook registration creates circuit breaker"""
        manager = HookManager(enable_circuit_breaker=True)

        async def test_hook(context: HookContext) -> HookContext:
            return context

        await manager.register_hook(hook_type=HookType.ON_REQUEST_START, callback=test_hook, plugin_name="test-plugin")

        # Circuit breaker should be created
        breaker_key = manager._get_breaker_key("test-plugin", HookType.ON_REQUEST_START)
        assert breaker_key in manager._circuit_breakers

    @pytest.mark.asyncio
    async def test_register_hook_initializes_metrics(self):
        """Test hook registration initializes metrics"""
        manager = HookManager(enable_circuit_breaker=False)

        async def test_hook(context: HookContext) -> HookContext:
            return context

        await manager.register_hook(hook_type=HookType.ON_REQUEST_START, callback=test_hook, plugin_name="test-plugin")

        assert "test-plugin" in manager._metrics

    @pytest.mark.asyncio
    async def test_unregister_hook(self):
        """Test hook unregistration"""
        manager = HookManager(enable_circuit_breaker=False)

        async def test_hook(context: HookContext) -> HookContext:
            return context

        await manager.register_hook(hook_type=HookType.ON_REQUEST_START, callback=test_hook, plugin_name="test-plugin")

        initial_count = len(manager._hooks[HookType.ON_REQUEST_START])

        await manager.unregister_hook(HookType.ON_REQUEST_START, "test-plugin")

        final_count = len(manager._hooks[HookType.ON_REQUEST_START])
        assert final_count < initial_count


class TestHookExecution:
    """Tests for hook execution"""

    @pytest.mark.asyncio
    async def test_execute_hooks_empty(self):
        """Test executing hooks when none are registered"""
        manager = HookManager(enable_circuit_breaker=False)

        context = HookContext(hook_type=HookType.ON_REQUEST_START, data={"test": "data"})

        results = await manager.execute_hooks(HookType.ON_REQUEST_START, context)

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_execute_single_hook_success(self):
        """Test executing a single successful hook"""
        manager = HookManager(enable_circuit_breaker=False)

        async def test_hook(context: HookContext) -> HookContext:
            context.data["processed"] = True
            return context

        await manager.register_hook(HookType.ON_REQUEST_START, test_hook, plugin_name="test-plugin")

        context = HookContext(hook_type=HookType.ON_REQUEST_START, data={})

        results = await manager.execute_hooks(HookType.ON_REQUEST_START, context)

        assert len(results) == 1
        assert results[0].success is True

    @pytest.mark.asyncio
    async def test_execute_hooks_in_priority_order(self):
        """Test hooks execute in priority order"""
        manager = HookManager(enable_circuit_breaker=False)
        execution_order = []

        async def high_hook(context: HookContext) -> HookContext:
            execution_order.append("high")
            return context

        async def normal_hook(context: HookContext) -> HookContext:
            execution_order.append("normal")
            return context

        async def low_hook(context: HookContext) -> HookContext:
            execution_order.append("low")
            return context

        # Register in random order
        await manager.register_hook(HookType.ON_REQUEST_START, normal_hook, HookPriority.NORMAL, "normal")
        await manager.register_hook(HookType.ON_REQUEST_START, high_hook, HookPriority.HIGH, "high")
        await manager.register_hook(HookType.ON_REQUEST_START, low_hook, HookPriority.LOW, "low")

        context = HookContext(hook_type=HookType.ON_REQUEST_START, data={})
        await manager.execute_hooks(HookType.ON_REQUEST_START, context)

        assert execution_order == ["high", "normal", "low"]

    @pytest.mark.asyncio
    async def test_execute_hook_with_exception(self):
        """Test hook execution with exception"""
        manager = HookManager(enable_circuit_breaker=False)

        async def failing_hook(context: HookContext) -> HookContext:
            raise ValueError("Test error")

        await manager.register_hook(HookType.ON_REQUEST_START, failing_hook, plugin_name="failing-plugin")

        context = HookContext(hook_type=HookType.ON_REQUEST_START, data={})
        results = await manager.execute_hooks(HookType.ON_REQUEST_START, context)

        assert len(results) == 1
        assert results[0].success is False
        assert "Test error" in results[0].error

    @pytest.mark.asyncio
    async def test_execute_hook_with_timeout(self):
        """Test hook execution timeout"""
        manager = HookManager(enable_circuit_breaker=False, default_timeout=0.1)

        async def slow_hook(context: HookContext) -> HookContext:
            await asyncio.sleep(1.0)  # Longer than timeout
            return context

        await manager.register_hook(HookType.ON_REQUEST_START, slow_hook, plugin_name="slow-plugin")

        context = HookContext(hook_type=HookType.ON_REQUEST_START, data={})
        results = await manager.execute_hooks(HookType.ON_REQUEST_START, context)

        assert len(results) == 1
        assert results[0].success is False
        assert "timeout" in results[0].error.lower()

    @pytest.mark.asyncio
    async def test_execute_hook_disabled(self):
        """Test disabled hooks are not executed"""
        manager = HookManager(enable_circuit_breaker=False)

        async def test_hook(context: HookContext) -> HookContext:
            context.data["executed"] = True
            return context

        await manager.register_hook(HookType.ON_REQUEST_START, test_hook, plugin_name="test-plugin", enabled=False)

        context = HookContext(hook_type=HookType.ON_REQUEST_START, data={})
        results = await manager.execute_hooks(HookType.ON_REQUEST_START, context)

        # Hook should not execute
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_execute_hooks_fail_fast(self):
        """Test fail_fast stops execution on first failure"""
        manager = HookManager(enable_circuit_breaker=False)
        execution_count = []

        async def failing_hook(context: HookContext) -> HookContext:
            execution_count.append("fail")
            raise ValueError("Failure")

        async def success_hook(context: HookContext) -> HookContext:
            execution_count.append("success")
            return context

        # Register hooks
        await manager.register_hook(HookType.ON_REQUEST_START, failing_hook, HookPriority.HIGH, "fail")
        await manager.register_hook(HookType.ON_REQUEST_START, success_hook, HookPriority.LOW, "success")

        context = HookContext(hook_type=HookType.ON_REQUEST_START, data={})
        results = await manager.execute_hooks(HookType.ON_REQUEST_START, context, fail_fast=True)

        # Only first hook should execute
        assert len(execution_count) == 1
        assert execution_count[0] == "fail"
        assert len(results) == 1


class TestCircuitBreakerIntegration:
    """Tests for circuit breaker integration with hook execution"""

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures"""
        manager = HookManager(enable_circuit_breaker=True)

        # Set low threshold for testing
        breaker_key = manager._get_breaker_key("failing-plugin", HookType.ON_REQUEST_START)

        async def failing_hook(context: HookContext) -> HookContext:
            raise ValueError("Always fails")

        await manager.register_hook(HookType.ON_REQUEST_START, failing_hook, plugin_name="failing-plugin")

        # Set circuit breaker to low threshold
        manager._circuit_breakers[breaker_key] = CircuitBreakerState(failure_threshold=2, timeout_seconds=60)

        context = HookContext(hook_type=HookType.ON_REQUEST_START, data={})

        # First failure
        await manager.execute_hooks(HookType.ON_REQUEST_START, context)
        assert manager._circuit_breakers[breaker_key].failure_count == 1

        # Second failure - should open circuit
        await manager.execute_hooks(HookType.ON_REQUEST_START, context)
        assert manager._circuit_breakers[breaker_key].state == "open"

    @pytest.mark.asyncio
    async def test_circuit_breaker_blocks_when_open(self):
        """Test circuit breaker blocks execution when open"""
        manager = HookManager(enable_circuit_breaker=True)
        execution_count = []

        async def test_hook(context: HookContext) -> HookContext:
            execution_count.append(1)
            return context

        await manager.register_hook(HookType.ON_REQUEST_START, test_hook, plugin_name="test-plugin")

        # Manually open circuit breaker
        breaker_key = manager._get_breaker_key("test-plugin", HookType.ON_REQUEST_START)
        manager._circuit_breakers[breaker_key].state = "open"
        manager._circuit_breakers[breaker_key].last_failure_time = datetime.utcnow()

        context = HookContext(hook_type=HookType.ON_REQUEST_START, data={})
        results = await manager.execute_hooks(HookType.ON_REQUEST_START, context)

        # Hook should not execute
        assert len(execution_count) == 0
        assert len(results) == 1
        assert results[0].success is False
        assert "Circuit breaker open" in results[0].error

    @pytest.mark.asyncio
    async def test_circuit_breaker_success_resets(self):
        """Test successful execution resets circuit breaker"""
        manager = HookManager(enable_circuit_breaker=True)

        async def test_hook(context: HookContext) -> HookContext:
            return context

        await manager.register_hook(HookType.ON_REQUEST_START, test_hook, plugin_name="test-plugin")

        breaker_key = manager._get_breaker_key("test-plugin", HookType.ON_REQUEST_START)

        # Simulate some failures
        manager._circuit_breakers[breaker_key].failure_count = 2

        context = HookContext(hook_type=HookType.ON_REQUEST_START, data={})
        await manager.execute_hooks(HookType.ON_REQUEST_START, context)

        # Success should reset failure count
        assert manager._circuit_breakers[breaker_key].failure_count == 0


class TestHookManagerUtilities:
    """Tests for HookManager utility methods"""

    @pytest.mark.asyncio
    async def test_get_metrics_single_plugin(self):
        """Test getting metrics for a single plugin"""
        manager = HookManager(enable_circuit_breaker=False)

        async def test_hook(context: HookContext) -> HookContext:
            return context

        await manager.register_hook(HookType.ON_REQUEST_START, test_hook, plugin_name="test-plugin")

        # Execute hook to generate metrics
        context = HookContext(hook_type=HookType.ON_REQUEST_START, data={})
        await manager.execute_hooks(HookType.ON_REQUEST_START, context)

        metrics = await manager.get_metrics("test-plugin")
        assert metrics is not None
        assert isinstance(metrics, dict)

    @pytest.mark.asyncio
    async def test_get_metrics_all_plugins(self):
        """Test getting metrics for all plugins"""
        manager = HookManager(enable_circuit_breaker=False)

        async def hook1(context: HookContext) -> HookContext:
            return context

        async def hook2(context: HookContext) -> HookContext:
            return context

        await manager.register_hook(HookType.ON_REQUEST_START, hook1, plugin_name="plugin1")
        await manager.register_hook(HookType.ON_REQUEST_START, hook2, plugin_name="plugin2")

        metrics = await manager.get_metrics()
        assert isinstance(metrics, dict)
        assert "plugin1" in metrics or "plugin2" in metrics

    @pytest.mark.asyncio
    async def test_get_hook_info(self):
        """Test getting hook information"""
        manager = HookManager(enable_circuit_breaker=False)

        async def test_hook(context: HookContext) -> HookContext:
            return context

        await manager.register_hook(
            HookType.ON_REQUEST_START, test_hook, priority=HookPriority.HIGH, plugin_name="test-plugin"
        )

        info = await manager.get_hook_info()
        assert isinstance(info, dict)
        assert HookType.ON_REQUEST_START.value in info

    @pytest.mark.asyncio
    async def test_enable_hook(self):
        """Test enabling a disabled hook"""
        manager = HookManager(enable_circuit_breaker=False)

        async def test_hook(context: HookContext) -> HookContext:
            return context

        await manager.register_hook(HookType.ON_REQUEST_START, test_hook, plugin_name="test-plugin", enabled=False)

        # Enable the hook
        await manager.enable_hook("test-plugin", HookType.ON_REQUEST_START)

        # Verify it's enabled
        hooks = manager._hooks[HookType.ON_REQUEST_START]
        for hook in hooks:
            if hook.plugin_name == "test-plugin":
                assert hook.enabled is True

    @pytest.mark.asyncio
    async def test_disable_hook(self):
        """Test disabling an enabled hook"""
        manager = HookManager(enable_circuit_breaker=False)

        async def test_hook(context: HookContext) -> HookContext:
            return context

        await manager.register_hook(HookType.ON_REQUEST_START, test_hook, plugin_name="test-plugin", enabled=True)

        # Disable the hook
        await manager.disable_hook("test-plugin", HookType.ON_REQUEST_START)

        # Verify it's disabled
        hooks = manager._hooks[HookType.ON_REQUEST_START]
        for hook in hooks:
            if hook.plugin_name == "test-plugin":
                assert hook.enabled is False

    @pytest.mark.asyncio
    async def test_reset_circuit_breaker(self):
        """Test manually resetting circuit breaker"""
        manager = HookManager(enable_circuit_breaker=True)

        async def test_hook(context: HookContext) -> HookContext:
            return context

        await manager.register_hook(HookType.ON_REQUEST_START, test_hook, plugin_name="test-plugin")

        breaker_key = manager._get_breaker_key("test-plugin", HookType.ON_REQUEST_START)

        # Simulate failure
        manager._circuit_breakers[breaker_key].failure_count = 5
        manager._circuit_breakers[breaker_key].state = "open"

        # Reset
        await manager.reset_circuit_breaker("test-plugin")

        # Should be reset
        assert manager._circuit_breakers[breaker_key].failure_count == 0
        assert manager._circuit_breakers[breaker_key].state == "closed"

    @pytest.mark.asyncio
    async def test_clear_all_hooks(self):
        """Test clearing all hooks"""
        manager = HookManager(enable_circuit_breaker=False)

        async def test_hook(context: HookContext) -> HookContext:
            return context

        await manager.register_hook(HookType.ON_REQUEST_START, test_hook, plugin_name="plugin1")
        await manager.register_hook(HookType.ON_REQUEST_COMPLETE, test_hook, plugin_name="plugin2")

        assert len(manager._hooks) > 0

        await manager.clear_all_hooks()

        assert len(manager._hooks) == 0
        assert len(manager._circuit_breakers) == 0
        assert len(manager._metrics) == 0


class TestHookManagerEdgeCases:
    """Tests for edge cases and error conditions"""

    @pytest.mark.asyncio
    async def test_hook_returning_none(self):
        """Test hook that returns None"""
        manager = HookManager(enable_circuit_breaker=False)

        async def none_hook(context: HookContext):
            # Returns None instead of context
            pass

        await manager.register_hook(HookType.ON_REQUEST_START, none_hook, plugin_name="none-plugin")

        context = HookContext(hook_type=HookType.ON_REQUEST_START, data={})
        results = await manager.execute_hooks(HookType.ON_REQUEST_START, context)

        # Should handle None return
        assert len(results) == 1
        assert results[0].success is True

    @pytest.mark.asyncio
    async def test_hook_returning_non_plugin_result(self):
        """Test hook that returns non-PluginResult value"""
        manager = HookManager(enable_circuit_breaker=False)

        async def simple_hook(context: HookContext):
            return {"custom": "data"}

        await manager.register_hook(HookType.ON_REQUEST_START, simple_hook, plugin_name="simple-plugin")

        context = HookContext(hook_type=HookType.ON_REQUEST_START, data={})
        results = await manager.execute_hooks(HookType.ON_REQUEST_START, context)

        # Should wrap in PluginResult
        assert len(results) == 1
        assert results[0].success is True

    @pytest.mark.asyncio
    async def test_concurrent_hook_execution(self):
        """Test concurrent hook execution with semaphore"""
        manager = HookManager(enable_circuit_breaker=False, max_concurrent_hooks=2)

        execution_times = []

        async def slow_hook(context: HookContext) -> HookContext:
            start = time.time()
            await asyncio.sleep(0.1)
            execution_times.append(time.time() - start)
            return context

        # Register 3 hooks
        for i in range(3):
            await manager.register_hook(HookType.ON_REQUEST_START, slow_hook, plugin_name=f"plugin{i}")

        context = HookContext(hook_type=HookType.ON_REQUEST_START, data={})
        await manager.execute_hooks(HookType.ON_REQUEST_START, context)

        # All hooks should execute
        assert len(execution_times) == 3

    def test_get_breaker_key(self):
        """Test circuit breaker key generation"""
        manager = HookManager()

        key = manager._get_breaker_key("my-plugin", HookType.ON_REQUEST_START)

        assert "my-plugin" in key
        assert HookType.ON_REQUEST_START.value in key
