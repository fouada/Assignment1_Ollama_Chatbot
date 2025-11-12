"""
Configuration Loader for Plugin System
Production-grade configuration management with validation

Features:
- YAML configuration loading
- Environment variable substitution
- Configuration validation
- Schema enforcement
- Default value handling
"""

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None

from .types import HookPriority, PluginConfig, PluginConfigError

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Load and validate plugin configuration

    Supports:
    - YAML configuration files
    - Environment variable substitution (${VAR_NAME})
    - Schema validation
    - Default values
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration loader

        Args:
            config_path: Path to configuration file (default: plugins/config.yaml)
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"

        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self._loaded = False

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file

        Returns:
            Configuration dictionary

        Raises:
            PluginConfigError: If loading fails
        """
        if yaml is None:
            raise PluginConfigError("PyYAML not installed. Install with: pip install pyyaml")

        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return self._get_default_config()

        try:
            with open(self.config_path, "r") as f:
                raw_config = yaml.safe_load(f)

            if raw_config is None:
                logger.warning("Empty configuration file, using defaults")
                return self._get_default_config()

            # Substitute environment variables
            self._config = self._substitute_env_vars(raw_config)

            # Validate configuration
            self._validate_config()

            self._loaded = True
            logger.info(f"Configuration loaded from {self.config_path}")

            return self._config

        except yaml.YAMLError as e:
            raise PluginConfigError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            raise PluginConfigError(f"Failed to load configuration: {e}")

    def get_plugin_manager_config(self) -> Dict[str, Any]:
        """Get plugin manager configuration"""
        if not self._loaded:
            self.load()

        return self._config.get("plugin_manager", {})

    def get_backend_configs(self) -> Dict[str, PluginConfig]:
        """
        Get backend plugin configurations

        Returns:
            Dictionary mapping backend name to PluginConfig
        """
        if not self._loaded:
            self.load()

        backends = self._config.get("backends", {})
        configs = {}

        for name, backend_config in backends.items():
            if not backend_config.get("enabled", False):
                continue

            configs[name] = self._create_plugin_config(backend_config)

        return configs

    def get_message_processor_configs(self) -> Dict[str, PluginConfig]:
        """Get message processor configurations"""
        if not self._loaded:
            self.load()

        processors = self._config.get("message_processors", {})
        configs = {}

        for name, proc_config in processors.items():
            if not proc_config.get("enabled", False):
                continue

            configs[name] = self._create_plugin_config(proc_config)

        return configs

    def get_feature_configs(self) -> Dict[str, PluginConfig]:
        """Get feature extension configurations"""
        if not self._loaded:
            self.load()

        features = self._config.get("features", {})
        configs = {}

        for name, feature_config in features.items():
            if not feature_config.get("enabled", False):
                continue

            configs[name] = self._create_plugin_config(feature_config)

        return configs

    def get_middleware_configs(self) -> Dict[str, PluginConfig]:
        """Get middleware configurations"""
        if not self._loaded:
            self.load()

        middleware = self._config.get("middleware", {})
        configs = {}

        for name, mid_config in middleware.items():
            if not mid_config.get("enabled", False):
                continue

            configs[name] = self._create_plugin_config(mid_config)

        return configs

    def get_all_plugin_configs(self) -> List[tuple[str, Path, PluginConfig]]:
        """
        Get all enabled plugin configurations

        Returns:
            List of (plugin_name, plugin_file_path, PluginConfig) tuples
        """
        all_configs = []

        # Get all plugin types
        for getter in [
            self.get_backend_configs,
            self.get_message_processor_configs,
            self.get_feature_configs,
            self.get_middleware_configs,
        ]:
            configs = getter()
            for name, config in configs.items():
                # Find plugin file path
                plugin_file = self._find_plugin_file(name)
                if plugin_file:
                    all_configs.append((name, plugin_file, config))

        return all_configs

    def _create_plugin_config(self, config_dict: Dict[str, Any]) -> PluginConfig:
        """Create PluginConfig from configuration dictionary"""
        priority_str = config_dict.get("priority", "NORMAL")
        priority = getattr(HookPriority, priority_str, HookPriority.NORMAL)

        return PluginConfig(
            enabled=config_dict.get("enabled", True),
            priority=priority,
            config=config_dict.get("config", {}),
            max_retries=config_dict.get("max_retries", 3),
            timeout_seconds=config_dict.get("timeout", 30.0),
            environment="production",
        )

    def _find_plugin_file(self, plugin_name: str) -> Optional[Path]:
        """Find plugin file from configuration"""
        # Search in all sections for plugin file
        for section in ["backends", "message_processors", "features", "middleware"]:
            plugins = self._config.get(section, {})
            if plugin_name in plugins:
                plugin_file = plugins[plugin_name].get("plugin_file")
                if plugin_file:
                    # Resolve relative to plugins directory
                    base_dir = self.config_path.parent
                    return base_dir / plugin_file

        return None

    def _substitute_env_vars(self, config: Any) -> Any:
        """
        Recursively substitute environment variables in configuration

        Supports:
        - ${VAR_NAME} - Replace with environment variable
        - ${VAR_NAME:default} - Use default if variable not set
        - \\${VAR_NAME} - Escaped literal (becomes ${VAR_NAME})

        Examples:
            "path": "${HOME}/config"  -> "/home/user/config"
            "port": "${PORT:8080}"    -> "8080" (if PORT not set)
            "literal": "\\${NOT_VAR}" -> "${NOT_VAR}"
        """
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str):
            # First, handle escaped literals: \${...} -> ${...}
            # Use a placeholder to protect escaped sequences
            ESCAPE_MARKER = "\x00ESCAPED_VAR\x00"
            config = config.replace("\\${", ESCAPE_MARKER)

            # Match ${VAR_NAME} or ${VAR_NAME:default}
            # Pattern breakdown:
            # \$\{ - literal ${
            # ([^}:]+) - variable name (no } or :)
            # (?::([^}]+))? - optional :default_value
            # \} - literal }
            pattern = r"\$\{([^}:]+)(?::([^}]+))?\}"

            def replace_var(match):
                var_name = match.group(1).strip()
                default_value = match.group(2)
                value = os.getenv(var_name)

                if value is None:
                    if default_value is not None:
                        return default_value
                    logger.warning(
                        f"Environment variable '{var_name}' not set and no default provided, "
                        f"using empty string"
                    )
                    return ""

                return value

            result = re.sub(pattern, replace_var, config)

            # Restore escaped literals
            result = result.replace(ESCAPE_MARKER, "${")

            return result
        else:
            return config

    def _validate_config(self) -> None:
        """
        Validate configuration structure with strict requirements

        Raises:
            PluginConfigError: If configuration is invalid or missing critical sections
        """
        # Check required top-level keys (strict - raise errors)
        required_keys = ["plugin_manager"]
        for key in required_keys:
            if key not in self._config:
                raise PluginConfigError(
                    f"Missing required configuration section: '{key}'. "
                    f"Configuration must include '{key}' section."
                )

        # Validate plugin manager config (strict validation)
        pm_config = self._config.get("plugin_manager", {})

        # Critical settings that should be explicitly set
        critical_settings = {
            "enable_hot_reload": (bool, False),
            "enable_circuit_breaker": (bool, True),
            "plugin_directory": (str, None)
        }

        for setting, (expected_type, default) in critical_settings.items():
            if setting not in pm_config:
                if default is not None:
                    logger.info(f"'{setting}' not configured, using default: {default}")
                    pm_config[setting] = default
                else:
                    raise PluginConfigError(
                        f"Missing required plugin_manager setting: '{setting}'. "
                        f"Please explicitly configure this in your config file."
                    )
            else:
                # Validate type
                value = pm_config[setting]
                if not isinstance(value, expected_type):
                    raise PluginConfigError(
                        f"Invalid type for '{setting}': expected {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )

        # Validate enabled plugins have plugin_file
        for section in ["backends", "message_processors", "features", "middleware"]:
            plugins = self._config.get(section, {})
            for name, config in plugins.items():
                if not isinstance(config, dict):
                    raise PluginConfigError(
                        f"Plugin '{name}' in section '{section}' must be a dictionary/object"
                    )
                if config.get("enabled", False) and "plugin_file" not in config:
                    raise PluginConfigError(
                        f"Plugin '{name}' is enabled but missing 'plugin_file' setting"
                    )

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration when file not found

        Returns minimal working configuration
        """
        return {
            "plugin_manager": {
                "enable_hot_reload": False,
                "enable_circuit_breaker": True,
                "max_concurrent_plugins": 10,
                "default_timeout": 30.0,
            },
            "hooks": {
                "default_timeout": 30.0,
                "max_concurrent_hooks": 10,
            },
            "backends": {},
            "message_processors": {},
            "features": {},
            "middleware": {},
            "observability": {
                "metrics": {"enabled": True},
                "logging": {"level": "INFO"},
            },
        }

    def get_observability_config(self) -> Dict[str, Any]:
        """Get observability configuration"""
        if not self._loaded:
            self.load()

        return self._config.get("observability", {})

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        if not self._loaded:
            self.load()

        return self._config.get("security", {})


# ============================================================================
# Global Configuration Instance
# ============================================================================

_config_loader: Optional[ConfigLoader] = None


def get_config_loader(config_path: Optional[Path] = None) -> ConfigLoader:
    """
    Get global configuration loader instance (singleton pattern)

    Args:
        config_path: Optional configuration file path

    Returns:
        ConfigLoader instance
    """
    global _config_loader

    if _config_loader is None:
        _config_loader = ConfigLoader(config_path)
        _config_loader.load()

    return _config_loader


def reload_config() -> None:
    """Reload configuration from file"""
    if _config_loader:
        _config_loader.load()
