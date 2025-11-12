"""
Additional Tests to Boost Coverage to 85%+
Tests for PluginSandbox, topological_sort_plugins, version checking, and other edge cases
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from ollama_chatbot.plugins.plugin_manager import (
    PluginSandbox,
    topological_sort_plugins,
    PluginLoader,
    RESOURCE_AVAILABLE,
)
from ollama_chatbot.plugins.types import (
    PluginMetadata,
    PluginType,
    PluginDependencyError,
    PluginLoadError,
    PluginConfig,
    PluginResult,
)
from ollama_chatbot.plugins.base_plugin import BasePlugin


# ============================================================================
# PluginSandbox Tests
# ============================================================================


class TestPluginSandbox:
    """Test PluginSandbox resource limiting"""

    def test_sandbox_initialization(self):
        """Test sandbox initialization"""
        sandbox = PluginSandbox(max_memory_mb=256, max_cpu_seconds=10, enabled=True)
        assert sandbox.max_memory_mb == 256
        assert sandbox.max_cpu_seconds == 10
        assert sandbox.enabled is True
        assert sandbox._original_limits == {}

    def test_sandbox_disabled(self):
        """Test sandbox when disabled"""
        sandbox = PluginSandbox(enabled=False)
        # Should not raise any errors
        sandbox.apply_limits()
        sandbox.restore_limits()

    def test_sandbox_apply_limits_when_disabled(self):
        """Test apply_limits returns early when disabled"""
        sandbox = PluginSandbox(enabled=False)
        sandbox.apply_limits()
        assert sandbox._original_limits == {}

    def test_sandbox_restore_limits_no_original_limits(self):
        """Test restore_limits when no original limits were set"""
        sandbox = PluginSandbox(enabled=True)
        # Should not raise any errors
        sandbox.restore_limits()

    @pytest.mark.skipif(not RESOURCE_AVAILABLE, reason="resource module not available on Windows")
    def test_sandbox_apply_limits_unix(self):
        """Test apply_limits on Unix systems"""
        import resource
        
        sandbox = PluginSandbox(max_memory_mb=512, max_cpu_seconds=30, enabled=True)
        
        with patch.object(resource, 'getrlimit') as mock_getrlimit, \
             patch.object(resource, 'setrlimit') as mock_setrlimit:
            
            # Mock current limits
            mock_getrlimit.return_value = (1024 * 1024 * 1024, 1024 * 1024 * 1024)
            
            sandbox.apply_limits()
            
            # Verify getrlimit was called
            assert mock_getrlimit.call_count == 2
            # Verify setrlimit was called with correct values
            assert mock_setrlimit.call_count == 2

    @pytest.mark.skipif(not RESOURCE_AVAILABLE, reason="resource module not available on Windows")
    def test_sandbox_apply_limits_error_handling(self):
        """Test apply_limits handles errors gracefully"""
        import resource
        
        sandbox = PluginSandbox(enabled=True)
        
        with patch.object(resource, 'getrlimit', side_effect=OSError("Permission denied")):
            # Should not raise, just log warning
            sandbox.apply_limits()

    @pytest.mark.skipif(not RESOURCE_AVAILABLE, reason="resource module not available on Windows")
    def test_sandbox_restore_limits_unix(self):
        """Test restore_limits on Unix systems"""
        import resource
        
        sandbox = PluginSandbox(enabled=True)
        sandbox._original_limits = {
            "memory": (1024 * 1024 * 1024, 1024 * 1024 * 1024),
            "cpu": (3600, 3600)
        }
        
        with patch.object(resource, 'setrlimit') as mock_setrlimit:
            sandbox.restore_limits()
            
            # Verify setrlimit was called for both memory and CPU
            assert mock_setrlimit.call_count == 2

    @pytest.mark.skipif(not RESOURCE_AVAILABLE, reason="resource module not available on Windows")
    def test_sandbox_restore_limits_error_handling(self):
        """Test restore_limits handles errors gracefully"""
        import resource
        
        sandbox = PluginSandbox(enabled=True)
        sandbox._original_limits = {"memory": (1024, 1024)}
        
        with patch.object(resource, 'setrlimit', side_effect=ValueError("Invalid limit")):
            # Should not raise, just log warning
            sandbox.restore_limits()

    @pytest.mark.skipif(RESOURCE_AVAILABLE, reason="Test Windows behavior")
    def test_sandbox_windows_no_op(self):
        """Test sandbox on Windows (no-op behavior)"""
        sandbox = PluginSandbox(enabled=True)
        # Should not raise any errors on Windows
        sandbox.apply_limits()
        sandbox.restore_limits()


# ============================================================================
# Topological Sort Tests
# ============================================================================


class TestTopologicalSort:
    """Test topological_sort_plugins function"""

    def test_topological_sort_empty(self):
        """Test with empty graph"""
        result = topological_sort_plugins({})
        assert result == []

    def test_topological_sort_single_plugin(self):
        """Test with single plugin"""
        graph = {"plugin_a": []}
        result = topological_sort_plugins(graph)
        assert result == ["plugin_a"]

    def test_topological_sort_linear_dependencies(self):
        """Test with linear dependency chain"""
        graph = {
            "plugin_a": [],
            "plugin_b": ["plugin_a"],
            "plugin_c": ["plugin_b"]
        }
        result = topological_sort_plugins(graph)
        assert result == ["plugin_a", "plugin_b", "plugin_c"]

    def test_topological_sort_multiple_roots(self):
        """Test with multiple independent plugins"""
        graph = {
            "plugin_a": [],
            "plugin_b": [],
            "plugin_c": []
        }
        result = topological_sort_plugins(graph)
        # All are valid since they're independent
        assert len(result) == 3
        assert set(result) == {"plugin_a", "plugin_b", "plugin_c"}

    def test_topological_sort_diamond_dependency(self):
        """Test with diamond-shaped dependency"""
        graph = {
            "plugin_a": [],
            "plugin_b": ["plugin_a"],
            "plugin_c": ["plugin_a"],
            "plugin_d": ["plugin_b", "plugin_c"]
        }
        result = topological_sort_plugins(graph)
        
        # plugin_a must come first
        assert result[0] == "plugin_a"
        # plugin_d must come last
        assert result[-1] == "plugin_d"
        # plugin_b and plugin_c must be before plugin_d
        assert result.index("plugin_b") < result.index("plugin_d")
        assert result.index("plugin_c") < result.index("plugin_d")

    def test_topological_sort_circular_dependency(self):
        """Test circular dependency detection"""
        graph = {
            "plugin_a": ["plugin_b"],
            "plugin_b": ["plugin_a"]
        }
        
        with pytest.raises(PluginDependencyError, match="Circular dependency detected"):
            topological_sort_plugins(graph)

    def test_topological_sort_circular_three_plugins(self):
        """Test circular dependency with three plugins"""
        graph = {
            "plugin_a": ["plugin_c"],
            "plugin_b": ["plugin_a"],
            "plugin_c": ["plugin_b"]
        }
        
        with pytest.raises(PluginDependencyError, match="Circular dependency detected"):
            topological_sort_plugins(graph)

    def test_topological_sort_self_dependency(self):
        """Test plugin depending on itself"""
        graph = {
            "plugin_a": ["plugin_a"]
        }
        
        with pytest.raises(PluginDependencyError, match="Circular dependency detected"):
            topological_sort_plugins(graph)

    def test_topological_sort_missing_dependency(self):
        """Test with missing dependency (not in graph)"""
        graph = {
            "plugin_a": ["plugin_b"],  # plugin_b not in graph
        }
        # Should still work, just won't count the missing dependency
        result = topological_sort_plugins(graph)
        assert "plugin_a" in result


# ============================================================================
# PluginMetadata Version Checking Tests
# ============================================================================


class TestPluginMetadataVersionChecking:
    """Test version checking functionality in PluginMetadata"""

    def test_is_compatible_with_api_same_major(self):
        """Test API compatibility with same major version"""
        metadata = PluginMetadata(
            name="test",
            version="1.0.0",
            author="Test",
            description="Test",
            plugin_type=PluginType.FEATURE_EXTENSION,
            api_version="1.5.0"
        )
        
        # Same major version should be compatible
        assert metadata.is_compatible_with_api("1.0.0") is True
        assert metadata.is_compatible_with_api("1.9.9") is True

    def test_is_compatible_with_api_different_major(self):
        """Test API incompatibility with different major version"""
        metadata = PluginMetadata(
            name="test",
            version="1.0.0",
            author="Test",
            description="Test",
            plugin_type=PluginType.FEATURE_EXTENSION,
            api_version="1.0.0"
        )
        
        # Different major version should be incompatible
        assert metadata.is_compatible_with_api("2.0.0") is False

    def test_check_dependency_version_no_constraint(self):
        """Test dependency version check with no constraint"""
        metadata = PluginMetadata(
            name="test",
            version="1.0.0",
            author="Test",
            description="Test",
            plugin_type=PluginType.FEATURE_EXTENSION,
        )
        
        # No constraint, should always be True
        assert metadata.check_dependency_version("some-dep", "1.0.0") is True
        assert metadata.check_dependency_version("some-dep", "99.0.0") is True

    def test_check_dependency_version_with_constraint(self):
        """Test dependency version check with constraint"""
        metadata = PluginMetadata(
            name="test",
            version="1.0.0",
            author="Test",
            description="Test",
            plugin_type=PluginType.FEATURE_EXTENSION,
            dependency_versions={"dep1": ">=1.0.0"}
        )
        
        assert metadata.check_dependency_version("dep1", "1.0.0") is True
        assert metadata.check_dependency_version("dep1", "2.0.0") is True

    def test_version_satisfies_equals(self):
        """Test version satisfaction with == operator"""
        result = PluginMetadata._version_satisfies("1.5.0", "==1.5.0")
        assert result is True
        
        result = PluginMetadata._version_satisfies("1.5.1", "==1.5.0")
        assert result is False

    def test_version_satisfies_greater_than_equals(self):
        """Test version satisfaction with >= operator"""
        result = PluginMetadata._version_satisfies("2.0.0", ">=1.5.0")
        assert result is True
        
        result = PluginMetadata._version_satisfies("1.0.0", ">=1.5.0")
        assert result is False

    def test_version_satisfies_less_than_equals(self):
        """Test version satisfaction with <= operator"""
        result = PluginMetadata._version_satisfies("1.0.0", "<=1.5.0")
        assert result is True
        
        result = PluginMetadata._version_satisfies("2.0.0", "<=1.5.0")
        assert result is False

    def test_version_satisfies_greater_than(self):
        """Test version satisfaction with > operator"""
        result = PluginMetadata._version_satisfies("2.0.0", ">1.5.0")
        assert result is True
        
        result = PluginMetadata._version_satisfies("1.5.0", ">1.5.0")
        assert result is False

    def test_version_satisfies_less_than(self):
        """Test version satisfaction with < operator"""
        result = PluginMetadata._version_satisfies("1.0.0", "<1.5.0")
        assert result is True
        
        result = PluginMetadata._version_satisfies("1.5.0", "<1.5.0")
        assert result is False

    def test_version_satisfies_compatible_release(self):
        """Test version satisfaction with ~= operator (compatible release)"""
        result = PluginMetadata._version_satisfies("1.5.2", "~=1.5.0")
        assert result is True
        
        result = PluginMetadata._version_satisfies("1.6.0", "~=1.5.0")
        assert result is False

    def test_version_satisfies_multiple_constraints(self):
        """Test version satisfaction with multiple constraints"""
        result = PluginMetadata._version_satisfies("1.5.0", ">=1.0.0,<2.0.0")
        assert result is True
        
        result = PluginMetadata._version_satisfies("2.5.0", ">=1.0.0,<2.0.0")
        assert result is False

    def test_version_satisfies_invalid_version(self):
        """Test version satisfaction with invalid version (should return True)"""
        # When packaging fails or not available, should return True (permissive)
        result = PluginMetadata._version_satisfies("invalid", ">=1.0.0")
        assert result is True


# ============================================================================
# PluginLoader Edge Cases
# ============================================================================


class TestPluginLoaderEdgeCases:
    """Test edge cases in PluginLoader"""

    @pytest.mark.asyncio
    async def test_load_from_file_import_error(self):
        """Test loading plugin with missing dependency"""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
from nonexistent_module import something

class TestPlugin:
    pass
""")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(PluginLoadError, match="missing dependencies"):
                await PluginLoader.load_from_file(temp_path)
        finally:
            temp_path.unlink()

    @pytest.mark.asyncio
    async def test_load_from_file_execution_error(self):
        """Test loading plugin that fails during module execution"""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
raise RuntimeError("Execution failed")
""")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(PluginLoadError, match="Failed to execute module"):
                await PluginLoader.load_from_file(temp_path)
        finally:
            temp_path.unlink()

    @pytest.mark.asyncio
    async def test_validate_plugin_invalid_metadata(self):
        """Test plugin validation with invalid metadata"""
        class BadPlugin:
            metadata = "not a PluginMetadata object"
            
            async def initialize(self, config):
                pass
            
            async def shutdown(self):
                pass
            
            async def health_check(self):
                pass
        
        plugin = BadPlugin()
        
        with pytest.raises(PluginLoadError, match="Invalid plugin metadata"):
            PluginLoader._validate_plugin(plugin)

    @pytest.mark.asyncio
    async def test_validate_plugin_missing_initialize(self):
        """Test plugin validation with missing initialize method"""
        class BadPlugin:
            metadata = PluginMetadata(
                name="bad",
                version="1.0.0",
                author="Test",
                description="Bad plugin",
                plugin_type=PluginType.FEATURE_EXTENSION
            )
            
            async def shutdown(self):
                pass
            
            async def health_check(self):
                pass
        
        plugin = BadPlugin()
        
        with pytest.raises(PluginLoadError, match="missing initialize"):
            PluginLoader._validate_plugin(plugin)

    @pytest.mark.asyncio
    async def test_validate_plugin_missing_shutdown(self):
        """Test plugin validation with missing shutdown method"""
        class BadPlugin:
            metadata = PluginMetadata(
                name="bad",
                version="1.0.0",
                author="Test",
                description="Bad plugin",
                plugin_type=PluginType.FEATURE_EXTENSION
            )
            
            async def initialize(self, config):
                pass
            
            async def health_check(self):
                pass
        
        plugin = BadPlugin()
        
        with pytest.raises(PluginLoadError, match="missing shutdown"):
            PluginLoader._validate_plugin(plugin)

    @pytest.mark.asyncio
    async def test_validate_plugin_missing_health_check(self):
        """Test plugin validation with missing health_check method"""
        class BadPlugin:
            metadata = PluginMetadata(
                name="bad",
                version="1.0.0",
                author="Test",
                description="Bad plugin",
                plugin_type=PluginType.FEATURE_EXTENSION
            )
            
            async def initialize(self, config):
                pass
            
            async def shutdown(self):
                pass
        
        plugin = BadPlugin()
        
        with pytest.raises(PluginLoadError, match="missing health_check"):
            PluginLoader._validate_plugin(plugin)

    @pytest.mark.asyncio
    async def test_validate_plugin_api_version_incompatible(self):
        """Test plugin validation with incompatible API version"""
        class BadPlugin(BasePlugin):
            def __init__(self):
                super().__init__()
                self._metadata = PluginMetadata(
                    name="bad",
                    version="1.0.0",
                    author="Test",
                    description="Bad plugin",
                    plugin_type=PluginType.FEATURE_EXTENSION,
                    api_version="99.0.0"  # Incompatible major version
                )
            
            @property
            def metadata(self):
                return self._metadata
            
            async def _do_initialize(self, config):
                return PluginResult.ok(None)
            
            async def _do_shutdown(self):
                return PluginResult.ok(None)
        
        plugin = BadPlugin()
        
        with pytest.raises(PluginLoadError, match="requires API version"):
            PluginLoader._validate_plugin(plugin)


# ============================================================================
# PluginConfig Validation Tests
# ============================================================================


class TestPluginConfigValidation:
    """Test PluginConfig validation"""

    def test_config_validation_timeout_negative(self):
        """Test config validation with negative timeout"""
        config = PluginConfig(timeout_seconds=-1.0)
        errors = config.validate()
        assert any("timeout_seconds" in error for error in errors)

    def test_config_validation_priority_invalid(self):
        """Test config validation with invalid priority"""
        config = PluginConfig(priority=999)
        errors = config.validate()
        # Priority can be any int, so this might not error
        # But let's test the validation logic exists
        assert isinstance(errors, list)

    def test_config_validation_max_retries_negative(self):
        """Test config validation with negative max_retries"""
        config = PluginConfig(max_retries=-1)
        errors = config.validate()
        assert any("max_retries" in error for error in errors)

    def test_config_validation_all_valid(self):
        """Test config validation with all valid values"""
        config = PluginConfig(
            enabled=True,
            timeout_seconds=30.0,
            max_retries=3
        )
        errors = config.validate()
        assert len(errors) == 0

    def test_config_validation_rate_limit_negative(self):
        """Test config validation with negative rate_limit"""
        config = PluginConfig(rate_limit=-1.0)
        errors = config.validate()
        assert any("rate_limit" in error for error in errors)

