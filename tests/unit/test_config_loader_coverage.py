"""
Additional Tests for ConfigLoader Coverage
Covers error paths and edge cases to increase coverage
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import pytest

from ollama_chatbot.plugins.config_loader import ConfigLoader, get_config_loader, reload_config
from ollama_chatbot.plugins.types import PluginConfigError, HookPriority


class TestConfigLoaderCoverage:
    """Tests to cover missing paths in ConfigLoader"""

    def test_config_loader_initialization_default(self):
        """Test config loader initialization with default path"""
        loader = ConfigLoader()
        assert loader.config_path is not None
        assert isinstance(loader.config_path, Path)
        assert not loader._loaded

    def test_config_loader_initialization_custom_path(self):
        """Test config loader initialization with custom path"""
        custom_path = Path("/tmp/custom_config.yaml")
        loader = ConfigLoader(config_path=custom_path)
        assert loader.config_path == custom_path

    def test_load_config_yaml_not_installed(self):
        """Test loading config when PyYAML is not installed"""
        loader = ConfigLoader()

        # Mock yaml as None
        import ollama_chatbot.plugins.config_loader as config_module

        original_yaml = config_module.yaml
        config_module.yaml = None

        try:
            with pytest.raises(PluginConfigError, match="PyYAML not installed"):
                loader.load()
        finally:
            config_module.yaml = original_yaml

    def test_load_config_nonexistent_file(self):
        """Test loading config from non-existent file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            nonexistent_path = Path(tmpdir) / "nonexistent.yaml"
            loader = ConfigLoader(config_path=nonexistent_path)

            config = loader.load()

            # Should return default config
            assert config is not None
            assert "plugin_manager" in config
            assert "backends" in config

    def test_load_config_empty_file(self):
        """Test loading empty config file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "empty.yaml"
            config_file.write_text("")

            loader = ConfigLoader(config_path=config_file)
            config = loader.load()

            # Should return default config
            assert config is not None
            assert "plugin_manager" in config

    def test_load_config_invalid_yaml(self):
        """Test loading config with invalid YAML"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "invalid.yaml"
            config_file.write_text("invalid: yaml: content: [[[")

            loader = ConfigLoader(config_path=config_file)

            with pytest.raises(PluginConfigError, match="Invalid YAML"):
                loader.load()

    def test_load_config_io_error(self):
        """Test loading config with IO error"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_file.write_text("enabled: true")

            loader = ConfigLoader(config_path=config_file)

            # Mock open to raise exception
            with patch("builtins.open", side_effect=Exception("IO Error")):
                with pytest.raises(PluginConfigError, match="Failed to load configuration"):
                    loader.load()

    def test_load_valid_config(self):
        """Test loading valid config file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "valid.yaml"
            config_content = """
plugin_manager:
  enable_hot_reload: true
  plugin_directory: "./plugins"
  max_concurrent_plugins: 20

backends:
  ollama:
    enabled: true
    plugin_file: "ollama_backend.py"
    priority: "HIGH"
    config:
      base_url: "http://localhost:11434"

message_processors:
  profanity_filter:
    enabled: false
    plugin_file: "profanity_filter.py"

features: {}
middleware: {}
"""
            config_file.write_text(config_content)

            loader = ConfigLoader(config_path=config_file)
            config = loader.load()

            assert config is not None
            assert config["plugin_manager"]["enable_hot_reload"] is True
            assert "ollama" in config["backends"]
            assert loader._loaded

    def test_get_plugin_manager_config(self):
        """Test getting plugin manager config"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
plugin_manager:
  enable_hot_reload: false
  plugin_directory: "./plugins"
  default_timeout: 60.0
"""
            config_file.write_text(config_content)

            loader = ConfigLoader(config_path=config_file)
            pm_config = loader.get_plugin_manager_config()

            assert pm_config["enable_hot_reload"] is False
            assert pm_config["default_timeout"] == 60.0

    def test_get_backend_configs(self):
        """Test getting backend configurations"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
plugin_manager:
  plugin_directory: "./plugins"

backends:
  backend1:
    enabled: true
    plugin_file: "backend1.py"
    priority: "HIGH"
    max_retries: 5
    timeout: 45.0
    config:
      api_key: "test123"
  backend2:
    enabled: false
    plugin_file: "backend2.py"
"""
            config_file.write_text(config_content)

            loader = ConfigLoader(config_path=config_file)
            backends = loader.get_backend_configs()

            # backend2 should be filtered out (not enabled)
            assert "backend1" in backends
            assert "backend2" not in backends
            assert backends["backend1"].enabled is True
            assert backends["backend1"].priority == HookPriority.HIGH
            assert backends["backend1"].max_retries == 5
            assert backends["backend1"].timeout_seconds == 45.0

    def test_get_message_processor_configs(self):
        """Test getting message processor configurations"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
plugin_manager:
  plugin_directory: "./plugins"

message_processors:
  processor1:
    enabled: true
    plugin_file: "processor1.py"
    priority: "NORMAL"
  processor2:
    enabled: false
    plugin_file: "processor2.py"
"""
            config_file.write_text(config_content)

            loader = ConfigLoader(config_path=config_file)
            processors = loader.get_message_processor_configs()

            assert "processor1" in processors
            assert "processor2" not in processors
            assert processors["processor1"].priority == HookPriority.NORMAL

    def test_get_feature_configs(self):
        """Test getting feature configurations"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
plugin_manager:
  plugin_directory: "./plugins"

features:
  feature1:
    enabled: true
    plugin_file: "feature1.py"
    priority: "LOW"
  feature2:
    enabled: true
    plugin_file: "feature2.py"
"""
            config_file.write_text(config_content)

            loader = ConfigLoader(config_path=config_file)
            features = loader.get_feature_configs()

            assert "feature1" in features
            assert "feature2" in features
            assert features["feature1"].priority == HookPriority.LOW

    def test_get_middleware_configs(self):
        """Test getting middleware configurations"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
plugin_manager:
  plugin_directory: "./plugins"

middleware:
  auth:
    enabled: true
    plugin_file: "auth.py"
    priority: "CRITICAL"
  logging:
    enabled: false
    plugin_file: "logging.py"
"""
            config_file.write_text(config_content)

            loader = ConfigLoader(config_path=config_file)
            middleware = loader.get_middleware_configs()

            assert "auth" in middleware
            assert "logging" not in middleware
            assert middleware["auth"].priority == HookPriority.CRITICAL

    def test_get_all_plugin_configs(self):
        """Test getting all plugin configurations"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create plugin files
            plugin_dir = Path(tmpdir) / "plugins"
            plugin_dir.mkdir()
            (plugin_dir / "backend1.py").write_text("# backend")
            (plugin_dir / "processor1.py").write_text("# processor")

            config_file = Path(tmpdir) / "test.yaml"
            # Use forward slashes for cross-platform compatibility in YAML
            plugin_dir_str = plugin_dir.as_posix()
            config_content = f"""
plugin_manager:
  plugin_directory: "./plugins"

backends:
  backend1:
    enabled: true
    plugin_file: "{plugin_dir_str}/backend1.py"

message_processors:
  processor1:
    enabled: true
    plugin_file: "{plugin_dir_str}/processor1.py"

features: {{}}
middleware: {{}}
"""
            config_file.write_text(config_content)

            loader = ConfigLoader(config_path=config_file)
            all_configs = loader.get_all_plugin_configs()

            assert len(all_configs) == 2
            names = [name for name, _, _ in all_configs]
            assert "backend1" in names
            assert "processor1" in names

    def test_substitute_env_vars_simple(self):
        """Test environment variable substitution"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
plugin_manager:
  plugin_directory: "./plugins"

backends:
  test:
    enabled: true
    plugin_file: "test.py"
    config:
      api_key: "${TEST_API_KEY}"
"""
            config_file.write_text(config_content)

            os.environ["TEST_API_KEY"] = "secret123"
            try:
                loader = ConfigLoader(config_path=config_file)
                config = loader.load()

                assert config["backends"]["test"]["config"]["api_key"] == "secret123"
            finally:
                del os.environ["TEST_API_KEY"]

    def test_substitute_env_vars_with_default(self):
        """Test environment variable substitution with default value"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
plugin_manager:
  plugin_directory: "./plugins"

backends:
  test:
    enabled: true
    plugin_file: "test.py"
    config:
      port: "${PORT:8080}"
"""
            config_file.write_text(config_content)

            # Make sure PORT is not set
            if "PORT" in os.environ:
                del os.environ["PORT"]

            loader = ConfigLoader(config_path=config_file)
            config = loader.load()

            assert config["backends"]["test"]["config"]["port"] == "8080"

    def test_substitute_env_vars_missing_no_default(self):
        """Test environment variable substitution when var is missing and no default"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
plugin_manager:
  plugin_directory: "./plugins"

backends:
  test:
    enabled: true
    plugin_file: "test.py"
    config:
      missing: "${MISSING_VAR}"
"""
            config_file.write_text(config_content)

            if "MISSING_VAR" in os.environ:
                del os.environ["MISSING_VAR"]

            loader = ConfigLoader(config_path=config_file)
            config = loader.load()

            # Should use empty string
            assert config["backends"]["test"]["config"]["missing"] == ""

    def test_substitute_env_vars_nested(self):
        """Test environment variable substitution in nested structures"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
plugin_manager:
  plugin_directory: "./plugins"

backends:
  test:
    enabled: true
    plugin_file: "test.py"
    config:
      database:
        host: "${DB_HOST:localhost}"
        credentials:
          username: "${DB_USER:admin}"
          password: "${DB_PASS}"
"""
            config_file.write_text(config_content)

            os.environ["DB_PASS"] = "secret"
            try:
                loader = ConfigLoader(config_path=config_file)
                config = loader.load()

                db_config = config["backends"]["test"]["config"]["database"]
                assert db_config["host"] == "localhost"
                assert db_config["credentials"]["username"] == "admin"
                assert db_config["credentials"]["password"] == "secret"
            finally:
                del os.environ["DB_PASS"]

    def test_substitute_env_vars_in_list(self):
        """Test environment variable substitution in lists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
plugin_manager:
  plugin_directory: "./plugins"

backends:
  test:
    enabled: true
    plugin_file: "test.py"
    config:
      hosts:
        - "${HOST1:host1}"
        - "${HOST2:host2}"
"""
            config_file.write_text(config_content)

            loader = ConfigLoader(config_path=config_file)
            config = loader.load()

            hosts = config["backends"]["test"]["config"]["hosts"]
            assert hosts[0] == "host1"
            assert hosts[1] == "host2"

    def test_validate_config_missing_plugin_file(self):
        """Test validation fails when enabled plugin is missing plugin_file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
plugin_manager:
  enable_hot_reload: false
  plugin_directory: "./plugins"

backends:
  bad_backend:
    enabled: true
    # missing plugin_file!
"""
            config_file.write_text(config_content)

            loader = ConfigLoader(config_path=config_file)

            with pytest.raises(PluginConfigError, match="missing 'plugin_file'"):
                loader.load()

    def test_validate_config_warnings(self):
        """Test validation that plugin_manager is required"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
# Missing plugin_manager section
backends: {}
"""
            config_file.write_text(config_content)

            loader = ConfigLoader(config_path=config_file)

            # Should raise error because plugin_manager is required
            with pytest.raises(PluginConfigError, match="plugin_manager"):
                loader.load()

    def test_get_observability_config(self):
        """Test getting observability configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
plugin_manager:
  enable_hot_reload: false
  plugin_directory: "./plugins"

observability:
  metrics:
    enabled: true
  logging:
    level: "DEBUG"
"""
            config_file.write_text(config_content)

            loader = ConfigLoader(config_path=config_file)
            obs_config = loader.get_observability_config()

            assert obs_config["metrics"]["enabled"] is True
            assert obs_config["logging"]["level"] == "DEBUG"

    def test_get_security_config(self):
        """Test getting security configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
plugin_manager:
  enable_hot_reload: false
  plugin_directory: "./plugins"

security:
  auth_required: true
  api_key: "test123"
"""
            config_file.write_text(config_content)

            loader = ConfigLoader(config_path=config_file)
            sec_config = loader.get_security_config()

            assert sec_config["auth_required"] is True
            assert sec_config["api_key"] == "test123"

    def test_get_config_loader_singleton(self):
        """Test global config loader singleton"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
plugin_manager:
  enable_hot_reload: true
  plugin_directory: "./plugins"
"""
            config_file.write_text(config_content)

            # Reset global instance
            import ollama_chatbot.plugins.config_loader as config_module

            config_module._config_loader = None

            loader1 = get_config_loader(config_file)
            loader2 = get_config_loader()

            # Should return same instance
            assert loader1 is loader2

            # Reset for other tests
            config_module._config_loader = None

    def test_reload_config_function(self):
        """Test global reload_config function"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
plugin_manager:
  enable_hot_reload: false
  plugin_directory: "./plugins"
"""
            config_file.write_text(config_content)

            # Reset and initialize
            import ollama_chatbot.plugins.config_loader as config_module

            config_module._config_loader = ConfigLoader(config_file)

            reload_config()

            # Should have reloaded
            assert config_module._config_loader._loaded

            # Reset for other tests
            config_module._config_loader = None

    def test_find_plugin_file_not_found(self):
        """Test _find_plugin_file when plugin not found"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_content = """
plugin_manager:
  plugin_directory: "./plugins"

backends: {}
"""
            config_file.write_text(config_content)

            loader = ConfigLoader(config_path=config_file)
            loader.load()

            # Should return None for non-existent plugin
            result = loader._find_plugin_file("nonexistent")
            assert result is None

    def test_get_default_config(self):
        """Test _get_default_config returns proper structure"""
        loader = ConfigLoader()
        default_config = loader._get_default_config()

        assert "plugin_manager" in default_config
        assert "hooks" in default_config
        assert "backends" in default_config
        assert "message_processors" in default_config
        assert "features" in default_config
        assert "middleware" in default_config
        assert "observability" in default_config

        # Check plugin_manager defaults
        pm = default_config["plugin_manager"]
        assert pm["enable_hot_reload"] is False
        assert pm["enable_circuit_breaker"] is True
        assert pm["max_concurrent_plugins"] == 10
