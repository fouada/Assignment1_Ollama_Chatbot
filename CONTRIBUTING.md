# Contributing to Ollama Chatbot Plugin System

First off, thank you for considering contributing to this project! 🎉

This document provides guidelines and instructions for contributing. Following these guidelines helps communicate that you respect the time of the developers managing and developing this open source project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [What Can I Contribute?](#what-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Plugin Development](#plugin-development)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Standards](#documentation-standards)
- [Submitting Changes](#submitting-changes)
- [Community](#community)

---

## Code of Conduct

This project adheres to a Code of Conduct (see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## What Can I Contribute?

### 🐛 Bug Reports

Found a bug? Help us fix it by:

1. **Check existing issues** - Your bug might already be reported
2. **Create detailed report** - Use the bug report template
3. **Include**:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, Ollama version)
   - Logs or error messages
   - Screenshots if applicable

**Example bug report:**
```markdown
**Bug:** Circuit breaker not recovering after timeout

**Environment:**
- OS: macOS 14.0
- Python: 3.11.5
- Ollama: 0.1.20

**Steps to reproduce:**
1. Start chatbot with circuit breaker enabled
2. Stop Ollama service
3. Make 5 requests (triggers circuit breaker)
4. Wait 60 seconds (timeout period)
5. Restart Ollama
6. Make request

**Expected:** Circuit breaker enters half_open state and retries
**Actual:** Circuit breaker stays open indefinitely

**Logs:**
```
[ERROR] Circuit breaker OPEN for ollama_backend
[ERROR] Cannot execute - circuit breaker is OPEN
```
```

### ✨ Feature Requests

Have an idea for a new feature? We'd love to hear it!

1. **Check existing requests** - Maybe someone already suggested it
2. **Open discussion** - Create issue with "feature request" label
3. **Describe**:
   - Problem you're trying to solve
   - Proposed solution
   - Alternative solutions considered
   - Impact on existing functionality

**Example feature request:**
```markdown
**Feature:** Add Redis caching plugin

**Problem:**
Current in-memory cache doesn't persist across restarts and can't be shared across multiple instances.

**Proposed Solution:**
Create a Redis-based caching plugin that:
- Stores responses in Redis with TTL
- Supports cache invalidation
- Works with Redis Cluster
- Maintains backward compatibility

**Alternatives Considered:**
- Memcached (less feature-rich)
- DynamoDB (adds AWS dependency)

**Impact:**
- New optional plugin (zero impact if not enabled)
- Requires Redis as optional dependency
- Config changes needed for Redis connection
```

### 📝 Documentation Improvements

Documentation is critical! You can help by:

- Fixing typos or unclear explanations
- Adding examples
- Improving API documentation
- Writing tutorials
- Translating documentation

### 🔌 New Plugins

Want to create a plugin? Awesome! See [Plugin Development](#plugin-development) section.

### 🎨 Code Contributions

Improvements to core functionality, performance optimizations, refactoring, etc.

---

## Getting Started

### Prerequisites

1. **Python 3.10+** installed
2. **Ollama** installed and running
3. **Git** for version control
4. **pytest** for running tests

### Fork and Clone

```bash
# 1. Fork the repository on GitHub (click "Fork" button)

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/ollama-chatbot.git
cd ollama-chatbot

# 3. Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/ollama-chatbot.git

# 4. Verify remotes
git remote -v
# Should show:
#   origin    https://github.com/YOUR_USERNAME/ollama-chatbot.git (fetch)
#   origin    https://github.com/YOUR_USERNAME/ollama-chatbot.git (push)
#   upstream  https://github.com/ORIGINAL_OWNER/ollama-chatbot.git (fetch)
#   upstream  https://github.com/ORIGINAL_OWNER/ollama-chatbot.git (push)
```

### Set Up Development Environment

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install development dependencies
pip install pytest pytest-cov pytest-asyncio black flake8 mypy

# 4. Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install

# 5. Verify installation
python -c "import ollama; print('Ollama SDK installed')"
pytest --version
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_plugin_system.py

# Run tests with verbose output
pytest -v

# Run only unit tests (fast)
pytest tests/ -k "not integration"

# Run only integration tests
pytest tests/test_integration.py
```

---

## Development Workflow

### 1. Create a Branch

Always create a new branch for your work:

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description

# Branch naming conventions:
#   feature/  - New features
#   fix/      - Bug fixes
#   docs/     - Documentation changes
#   refactor/ - Code refactoring
#   test/     - Test improvements
```

### 2. Make Changes

Follow these guidelines:

**Code Style:**
- Follow PEP 8 (enforced by `flake8`)
- Use type hints (checked by `mypy`)
- Format with `black` (line length: 88)
- Use descriptive variable names
- Add docstrings to all functions/classes

**Example:**
```python
async def calculate_response_time(
    start_time: float,
    end_time: float,
    include_overhead: bool = False
) -> float:
    """
    Calculate response time in seconds.

    Args:
        start_time: Request start timestamp
        end_time: Request end timestamp
        include_overhead: Whether to include processing overhead

    Returns:
        Response time in seconds

    Raises:
        ValueError: If end_time is before start_time

    Example:
        >>> calculate_response_time(100.0, 105.5)
        5.5
    """
    if end_time < start_time:
        raise ValueError("end_time cannot be before start_time")

    duration = end_time - start_time

    if include_overhead:
        duration += PROCESSING_OVERHEAD

    return duration
```

### 3. Write Tests

**Every contribution must include tests:**

```python
# tests/test_your_feature.py
import pytest
from your_module import your_function


def test_your_function_basic():
    """Test basic functionality"""
    result = your_function("input")
    assert result == "expected_output"


def test_your_function_edge_case():
    """Test edge case handling"""
    with pytest.raises(ValueError):
        your_function(None)


@pytest.mark.asyncio
async def test_your_async_function():
    """Test async function"""
    result = await your_async_function()
    assert result is not None


@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
    ("test3", "result3"),
])
def test_your_function_parametrized(input, expected):
    """Test with multiple inputs"""
    assert your_function(input) == expected
```

### 4. Run Quality Checks

Before committing, ensure all checks pass:

```bash
# Format code
black .

# Check formatting (without modifying)
black --check .

# Lint
flake8 .

# Type check
mypy .

# Run tests
pytest

# Check coverage
pytest --cov=. --cov-report=term-missing

# All in one (recommended)
black . && flake8 . && mypy . && pytest --cov=.
```

### 5. Commit Changes

Write clear, descriptive commit messages:

```bash
# Stage changes
git add .

# Commit with message
git commit -m "feat: Add Redis caching plugin

- Implement RedisCache class with async support
- Add configuration options for Redis connection
- Include TTL and namespace support
- Add comprehensive tests (95% coverage)

Closes #123"
```

**Commit Message Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `test:` - Test additions or changes
- `chore:` - Maintenance tasks

**Example:**
```
feat: Add plugin hot-reload capability

- Implement file watcher for plugin directory
- Add reload_plugins() method to PluginManager
- Support graceful reload without downtime
- Add tests for reload scenarios

Closes #45
```

### 6. Push Changes

```bash
# Push to your fork
git push origin feature/your-feature-name

# If you need to update your branch with latest main
git checkout main
git pull upstream main
git checkout feature/your-feature-name
git rebase main
git push origin feature/your-feature-name --force-with-lease
```

---

## Plugin Development

### Plugin Structure

Create a new plugin following this template:

```python
# plugins/custom/my_awesome_plugin.py
"""
My Awesome Plugin
Provides [brief description of functionality]
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from plugins.plugin_interface import PluginInterface, PluginResult


@dataclass
class MyAwesomePluginConfig:
    """Configuration for MyAwesome plugin"""
    setting1: str = "default_value"
    setting2: int = 100
    enabled: bool = True


class MyAwesomePlugin(PluginInterface):
    """
    My Awesome Plugin

    Provides [detailed description]

    Configuration:
        setting1 (str): Description of setting1
        setting2 (int): Description of setting2
        enabled (bool): Enable/disable plugin

    Example:
        >>> plugin = MyAwesomePlugin()
        >>> await plugin.initialize(config)
        >>> result = await plugin.process(context)
    """

    def __init__(self):
        self.plugin_name = "my_awesome"
        self.plugin_version = "1.0.0"
        self.plugin_description = "Brief description"
        self._config: Optional[MyAwesomePluginConfig] = None

    async def initialize(self, config: Dict) -> PluginResult[None]:
        """Initialize plugin with configuration"""
        try:
            self._config = MyAwesomePluginConfig(**config)

            # Validate configuration
            if not self._config.enabled:
                return PluginResult(
                    success=True,
                    data=None,
                    metadata={"status": "disabled"}
                )

            # Perform initialization
            # ... your init logic here ...

            return PluginResult.ok(None)

        except Exception as e:
            return PluginResult.fail(f"Initialization failed: {e}")

    async def process(self, context: Dict) -> PluginResult[Dict]:
        """Main processing logic"""
        if not self._config or not self._config.enabled:
            return PluginResult.ok(context)

        try:
            # Your processing logic here
            result = self._do_something(context)

            # Add metadata
            context["my_awesome_metadata"] = {
                "processed": True,
                "setting1": self._config.setting1
            }

            return PluginResult.ok(context)

        except Exception as e:
            return PluginResult.fail(f"Processing failed: {e}")

    def _do_something(self, context: Dict) -> Any:
        """Helper method - your logic"""
        pass

    async def cleanup(self) -> PluginResult[None]:
        """Cleanup resources"""
        # Release resources, close connections, etc.
        return PluginResult.ok(None)

    async def health_check(self) -> PluginResult[Dict]:
        """Health check for monitoring"""
        return PluginResult.ok({
            "status": "healthy",
            "plugin": self.plugin_name,
            "version": self.plugin_version
        })
```

### Plugin Configuration

Add your plugin to `plugins/config.yaml`:

```yaml
custom:
  my_awesome:
    enabled: true
    plugin_file: "custom/my_awesome_plugin.py"
    config:
      setting1: "custom_value"
      setting2: 200
      enabled: true
    priority: "NORMAL"  # CRITICAL, HIGH, NORMAL, LOW, MONITORING
```

### Plugin Tests

Create comprehensive tests:

```python
# tests/test_my_awesome_plugin.py
import pytest
from plugins.custom.my_awesome_plugin import MyAwesomePlugin, MyAwesomePluginConfig


@pytest.fixture
def plugin():
    """Fixture providing plugin instance"""
    return MyAwesomePlugin()


@pytest.fixture
def config():
    """Fixture providing test configuration"""
    return {
        "setting1": "test_value",
        "setting2": 42,
        "enabled": True
    }


@pytest.mark.asyncio
async def test_plugin_initialization(plugin, config):
    """Test plugin initializes correctly"""
    result = await plugin.initialize(config)

    assert result.success is True
    assert plugin._config.setting1 == "test_value"
    assert plugin._config.setting2 == 42


@pytest.mark.asyncio
async def test_plugin_process(plugin, config):
    """Test plugin processing"""
    await plugin.initialize(config)

    context = {"test": "data"}
    result = await plugin.process(context)

    assert result.success is True
    assert "my_awesome_metadata" in result.data


@pytest.mark.asyncio
async def test_plugin_disabled(plugin):
    """Test plugin behavior when disabled"""
    config = {"enabled": False}
    await plugin.initialize(config)

    context = {"test": "data"}
    result = await plugin.process(context)

    assert result.success is True
    assert "my_awesome_metadata" not in result.data


@pytest.mark.asyncio
async def test_plugin_error_handling(plugin, config):
    """Test plugin handles errors gracefully"""
    await plugin.initialize(config)

    # Test with invalid input
    result = await plugin.process(None)

    assert result.success is False
    assert "error" in result.error.lower()


@pytest.mark.asyncio
async def test_plugin_cleanup(plugin, config):
    """Test plugin cleanup"""
    await plugin.initialize(config)
    result = await plugin.cleanup()

    assert result.success is True


@pytest.mark.asyncio
async def test_plugin_health_check(plugin, config):
    """Test plugin health check"""
    await plugin.initialize(config)
    result = await plugin.health_check()

    assert result.success is True
    assert result.data["status"] == "healthy"
```

### Plugin Documentation

Document your plugin in `docs/plugins/my_awesome.md`:

```markdown
# My Awesome Plugin

## Overview

Brief description of what the plugin does and why it's useful.

## Installation

```bash
# Any special dependencies
pip install redis  # if needed
```

## Configuration

```yaml
custom:
  my_awesome:
    enabled: true
    plugin_file: "custom/my_awesome_plugin.py"
    config:
      setting1: "value"    # Description of setting1
      setting2: 100        # Description of setting2
    priority: "NORMAL"
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `setting1` | str | "default" | What this does |
| `setting2` | int | 100 | What this does |

## Usage

### Basic Usage

```python
# Example code showing how to use the plugin
```

### Advanced Usage

```python
# More complex examples
```

## API Reference

### Methods

#### `process(context: Dict) -> PluginResult[Dict]`

Description of what this method does.

**Parameters:**
- `context` (Dict): Input context

**Returns:**
- `PluginResult[Dict]`: Result with processed context

**Example:**
```python
result = await plugin.process(context)
```

## Examples

### Example 1: Basic Use Case

```python
# Complete working example
```

### Example 2: Advanced Use Case

```python
# Another example
```

## Troubleshooting

### Issue: Plugin not loading

**Solution:** Check that...

### Issue: Configuration error

**Solution:** Verify that...

## Contributing

Contributions welcome! See [CONTRIBUTING.md](../../CONTRIBUTING.md).

## License

MIT License - see [LICENSE](../../LICENSE).
```

---

## Testing Guidelines

### Test Coverage Requirements

- **Minimum coverage:** 80% for new code
- **Target coverage:** 100% for plugins
- **Integration tests:** Required for new features

### Running Tests

```bash
# Unit tests only (fast)
pytest tests/ -k "not integration"

# Integration tests (slower, requires Ollama)
pytest tests/test_integration.py

# Specific plugin tests
pytest tests/test_my_awesome_plugin.py

# With coverage report
pytest --cov=plugins/custom --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── test_plugin_system.py    # Core system tests
├── test_my_plugin.py        # Plugin-specific tests
└── test_integration.py      # End-to-end tests
```

### Writing Good Tests

1. **Test one thing** - Each test should verify one behavior
2. **Use descriptive names** - Test name explains what's being tested
3. **Follow AAA pattern** - Arrange, Act, Assert
4. **Include edge cases** - Test boundaries and error conditions
5. **Mock external dependencies** - Use `pytest-mock` for external services

**Example:**
```python
@pytest.mark.asyncio
async def test_cache_plugin_expires_after_ttl():
    """Test that cached entries expire after TTL"""
    # Arrange
    plugin = CachePlugin()
    await plugin.initialize({"ttl_seconds": 1})
    context = {"key": "test", "value": "data"}

    # Act
    await plugin.process(context)  # Cache the value
    await asyncio.sleep(2)  # Wait for TTL to expire
    result = await plugin.process({"key": "test"})

    # Assert
    assert "cached_value" not in result.data  # Should be expired
```

---

## Documentation Standards

### Code Documentation

**All public functions/classes must have docstrings:**

```python
def process_message(
    message: str,
    model: str,
    temperature: float = 0.7
) -> Dict[str, Any]:
    """
    Process a user message and generate a response.

    This function sends the message to the specified model and returns
    the generated response along with metadata about the generation.

    Args:
        message: The user's input message
        model: Name of the Ollama model to use
        temperature: Sampling temperature (0.0 to 2.0)
            - 0.0: Deterministic, focused responses
            - 1.0: Balanced creativity and coherence
            - 2.0: Maximum creativity and randomness

    Returns:
        Dictionary containing:
            - response (str): Generated response text
            - model (str): Model used for generation
            - tokens (int): Number of tokens generated
            - duration (float): Generation time in seconds

    Raises:
        ConnectionError: If Ollama server is not accessible
        ValueError: If temperature is outside valid range
        ModelNotFoundError: If specified model is not available

    Example:
        >>> result = process_message("Hello!", "llama3.2", 0.7)
        >>> print(result["response"])
        "Hello! How can I help you today?"

    Note:
        Higher temperatures increase creativity but may reduce coherence.
        For production use, temperature between 0.5-0.9 is recommended.

    See Also:
        - generate_response: Streaming version of this function
        - list_models: Get available models
    """
    # Implementation...
```

### Markdown Documentation

Use clear structure and examples:

```markdown
# Feature Name

## Overview

Brief description of the feature and its purpose.

## Quick Start

```bash
# Minimum viable example
python example.py
```

## Installation

Step-by-step installation instructions.

## Configuration

Detailed configuration options with examples.

## Usage

### Basic Usage

Simple examples for common use cases.

### Advanced Usage

Complex examples for power users.

## API Reference

Detailed API documentation.

## Troubleshooting

Common issues and solutions.

## FAQs

Frequently asked questions.

## Contributing

How to contribute to this feature.
```

---

## Submitting Changes

### Pull Request Process

1. **Update documentation** - Add/update relevant docs
2. **Add tests** - Ensure tests pass and coverage is adequate
3. **Update CHANGELOG** - Document your changes
4. **Squash commits** (optional) - Clean up commit history
5. **Create pull request** - Use the PR template

### Pull Request Template

When creating a PR, include:

```markdown
## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing

- [ ] Unit tests pass locally
- [ ] Integration tests pass locally
- [ ] Added new tests for this change
- [ ] All tests pass in CI

## Checklist

- [ ] Code follows style guidelines (black, flake8, mypy)
- [ ] Self-reviewed my code
- [ ] Commented complex logic
- [ ] Updated documentation
- [ ] No new warnings generated
- [ ] Added tests that prove fix/feature works
- [ ] New and existing tests pass locally
- [ ] Dependent changes have been merged

## Related Issues

Closes #123
Relates to #456

## Screenshots (if applicable)

Include screenshots for UI changes.

## Additional Notes

Any additional information for reviewers.
```

### Review Process

1. **Automated checks** - CI runs tests, linting, type checking
2. **Code review** - Maintainer reviews your code
3. **Requested changes** - Address any feedback
4. **Approval** - Once approved, maintainer will merge

### After Merging

1. **Delete branch** - Clean up your feature branch
2. **Update local** - Pull latest changes
3. **Celebrate** 🎉 - You've contributed to open source!

```bash
# After PR is merged
git checkout main
git pull upstream main
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

---

## Community

### Communication Channels

- **GitHub Issues** - Bug reports, feature requests
- **GitHub Discussions** - General questions, ideas
- **Pull Requests** - Code contributions, reviews

### Getting Help

**Before asking for help:**

1. Check [README.md](README.md)
2. Search existing issues
3. Read relevant documentation
4. Try debugging yourself

**When asking for help, include:**

- Clear description of the problem
- What you've tried
- Minimal reproducible example
- Environment details
- Error messages/logs

### Recognition

Contributors are recognized in:

- [CONTRIBUTORS.md](CONTRIBUTORS.md) - All contributors
- Release notes - Feature authors
- README badges - Contributor count

---

## Additional Resources

### Documentation

- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [PLUGIN_ARCHITECTURE.md](docs/PLUGIN_ARCHITECTURE.md) - Plugin design
- [API_REFERENCE.md](docs/API_REFERENCE.md) - API documentation

### Examples

- [plugins/examples/](plugins/examples/) - Example plugins
- [tests/](tests/) - Test examples
- [docs/tutorials/](docs/tutorials/) - Step-by-step tutorials

### Tools

- [pytest](https://docs.pytest.org/) - Testing framework
- [black](https://black.readthedocs.io/) - Code formatter
- [flake8](https://flake8.pycqa.org/) - Linter
- [mypy](https://mypy.readthedocs.io/) - Type checker

---

## Questions?

If you have questions not covered here:

1. Check [GitHub Discussions](../../discussions)
2. Open an issue with "question" label
3. Read through existing issues for similar questions

---

**Thank you for contributing! Every contribution, no matter how small, is valuable and appreciated.** 🙏

**Happy coding!** 💻
