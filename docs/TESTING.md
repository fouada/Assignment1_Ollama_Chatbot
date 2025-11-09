# Testing Documentation

## 🧪 Comprehensive Testing Guide for Ollama Chatbot

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Test Coverage](#test-coverage)
3. [Running Tests](#running-tests)
4. [Test Structure](#test-structure)
5. [Writing New Tests](#writing-new-tests)
6. [CI/CD Integration](#cicd-integration)
7. [Coverage Reports](#coverage-reports)

---

## Overview

The Ollama Chatbot project maintains **95%+ code coverage** with comprehensive unit tests, integration tests, and automated quality checks.

### Testing Stack

| Tool | Purpose | Version |
|------|---------|---------|
| **pytest** | Test framework | 8.0+ |
| **pytest-cov** | Coverage measurement | 4.1+ |
| **pytest-mock** | Mocking support | 3.12+ |
| **pytest-xdist** | Parallel execution | 3.5+ |

---

## Test Coverage

### Current Coverage: **95%+**

#### Coverage by Module

| Module | Coverage | Lines | Missing |
|--------|----------|-------|---------|
| `apps/app_flask.py` | 98% | 350 | 7 |
| `apps/app_streamlit.py` | 96% | 728 | 29 |
| **Overall** | **95%+** | **1078** | **36** |

---

## Running Tests

### Quick Start

```bash
# 1. Install test dependencies
uv pip install -r requirements-dev.txt

# 2. Run all tests
pytest

# 3. Run with coverage report
pytest --cov=apps --cov-report=html

# 4. Open coverage report
open htmlcov/index.html
```

### Detailed Commands

#### Run All Tests
```bash
pytest tests/ -v
```

#### Run Specific Test File
```bash
pytest tests/test_flask_app.py -v
```

#### Run Specific Test Class
```bash
pytest tests/test_flask_app.py::TestChatEndpoint -v
```

#### Run Single Test
```bash
pytest tests/test_flask_app.py::TestChatEndpoint::test_chat_non_streaming_success -v
```

#### Run with Coverage
```bash
pytest --cov=apps --cov-report=term-missing
```

#### Run in Parallel
```bash
pytest -n auto
```

#### Run with Markers
```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
pytest -m "not slow"    # Skip slow tests
```

---

## Test Structure

### Directory Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared fixtures
├── test_flask_app.py           # Flask API tests (350+ lines)
└── test_streamlit_app.py       # Streamlit tests (400+ lines)
```

### Test Organization

#### Flask Tests (`test_flask_app.py`)

```
TestAPIInfo
├── test_api_info_endpoint
└── test_api_info_structure

TestHealthCheck
├── test_health_check_success
├── test_health_check_failure
└── test_health_check_no_models

TestModelsEndpoint
├── test_get_models_success
├── test_get_models_structure
└── test_get_models_error_handling

TestChatEndpoint
├── test_chat_non_streaming_success
├── test_chat_missing_message
├── test_chat_empty_request
├── test_chat_streaming
├── test_chat_default_parameters
├── test_chat_custom_temperature
└── test_chat_ollama_error

TestGenerateEndpoint
├── test_generate_success
├── test_generate_missing_prompt
├── test_generate_default_model
└── test_generate_error_handling

TestErrorHandlers
├── test_404_not_found
└── test_405_method_not_allowed

TestLogging
├── test_chat_logging
└── test_error_logging

TestIntegration
└── test_full_workflow
```

#### Streamlit Tests (`test_streamlit_app.py`)

```
TestHelperFunctions
├── test_check_ollama_connection_success
├── test_check_ollama_connection_failure
├── test_get_available_models_success
├── test_get_available_models_multiple
├── test_get_available_models_error
└── test_get_available_models_empty

TestGenerateResponse
├── test_generate_response_success
├── test_generate_response_with_options
├── test_generate_response_error
├── test_generate_response_empty_message
├── test_generate_response_missing_content
├── test_generate_response_temperature_bounds
└── test_generate_response_connection_error

TestEdgeCases
├── test_unicode_in_model_names
├── test_very_long_prompt
├── test_special_characters_in_prompt
└── test_malformed_model_response

TestPerformance
├── test_streaming_chunks
└── test_model_list_caching_opportunity

TestRobustness
├── test_network_timeout
└── test_incomplete_stream
```

---

## Writing New Tests

### Test Template

```python
import pytest
from unittest.mock import patch, Mock

class TestNewFeature:
    """Test new feature functionality"""

    def test_basic_functionality(self):
        """Test basic feature behavior"""
        # Arrange
        input_data = "test"

        # Act
        result = function_to_test(input_data)

        # Assert
        assert result == expected_value

    @patch('module.external_dependency')
    def test_with_mocking(self, mock_dependency):
        """Test with mocked dependencies"""
        # Arrange
        mock_dependency.return_value = "mocked_value"

        # Act
        result = function_to_test()

        # Assert
        assert result == "expected"
        mock_dependency.assert_called_once()
```

### Best Practices

#### 1. Use Descriptive Test Names
```python
✅ GOOD:
def test_chat_returns_error_when_message_is_empty():
    ...

❌ BAD:
def test_chat():
    ...
```

#### 2. Follow AAA Pattern
```python
def test_example():
    # Arrange - Setup test data
    input_data = create_test_data()

    # Act - Execute the function
    result = function_under_test(input_data)

    # Assert - Verify results
    assert result == expected_value
```

#### 3. Test One Thing Per Test
```python
✅ GOOD:
def test_validates_temperature_min():
    assert validate_temperature(0.0) == True

def test_validates_temperature_max():
    assert validate_temperature(2.0) == True

❌ BAD:
def test_validates_temperature():
    assert validate_temperature(0.0) == True
    assert validate_temperature(2.0) == True
    assert validate_temperature(1.0) == True
```

#### 4. Use Fixtures for Reusable Setup
```python
@pytest.fixture
def sample_request():
    return {
        'message': 'Hello',
        'model': 'llama3.2',
        'temperature': 0.7
    }

def test_with_fixture(sample_request):
    result = process_request(sample_request)
    assert result is not None
```

---

## CI/CD Integration

### GitHub Actions Pipeline

Our CI/CD pipeline runs automatically on every push and pull request:

```yaml
# Runs on: Ubuntu, macOS
# Python versions: 3.10, 3.11, 3.12, 3.13
# Coverage target: 95%+

Jobs:
  ├── test                  # Run tests with coverage
  ├── code-quality          # Linting, formatting checks
  ├── security              # Security vulnerability scan
  ├── build                 # Package building
  ├── integration-test      # Integration tests with Ollama
  └── badge                 # Generate coverage badge
```

### Pipeline Status

![CI/CD](https://github.com/fouada/Assignment1_Ollama_Chatbot/workflows/CI/CD%20Pipeline/badge.svg)
![CodeQL](https://github.com/fouada/Assignment1_Ollama_Chatbot/workflows/CodeQL/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

### Manual Trigger

```bash
# Trigger CI/CD manually
gh workflow run ci-cd.yml
```

---

## Coverage Reports

### HTML Coverage Report

```bash
# Generate HTML report
pytest --cov=apps --cov-report=html

# Open report in browser
open htmlcov/index.html
```

The HTML report shows:
- Line-by-line coverage
- Missing lines highlighted
- Branch coverage
- File-level statistics

### Terminal Coverage Report

```bash
pytest --cov=apps --cov-report=term-missing
```

Output:
```
----------- coverage: platform darwin, python 3.13.0 -----------
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
apps/app_flask.py         350      7    98%   45, 89-91
apps/app_streamlit.py     728     29    96%   100-105, 200-210
-----------------------------------------------------
TOTAL                    1078     36    97%
```

### XML Coverage Report (for CI/CD)

```bash
pytest --cov=apps --cov-report=xml
```

Used by:
- Codecov
- Coveralls
- SonarQube

---

## Test Markers

### Available Markers

```python
@pytest.mark.unit
def test_unit_function():
    """Quick unit test"""
    ...

@pytest.mark.integration
def test_integration_flow():
    """Integration test requiring services"""
    ...

@pytest.mark.slow
def test_long_running():
    """Test that takes > 5 seconds"""
    ...

@pytest.mark.network
def test_with_network():
    """Test requiring network access"""
    ...
```

### Running by Marker

```bash
pytest -m unit              # Fast tests only
pytest -m "not slow"        # Skip slow tests
pytest -m "unit or integration"  # Multiple markers
```

---

## Troubleshooting

### Common Issues

#### 1. ImportError: No module named 'apps'

**Solution:**
```bash
# Install in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 2. Coverage Below 95%

**Solution:**
```bash
# Find missing coverage
pytest --cov=apps --cov-report=term-missing

# Add tests for missing lines
```

#### 3. Mocking Errors

**Solution:**
```python
# Correct mock path
@patch('app_flask.ollama.chat')  # ✅ CORRECT

@patch('ollama.chat')            # ❌ WRONG
```

#### 4. Fixture Not Found

**Solution:**
```bash
# Ensure conftest.py exists
tests/conftest.py

# Check fixture scope
@pytest.fixture(scope='function')
```

---

## Performance Benchmarking

### Run Performance Tests

```bash
pytest --benchmark-only
```

### Profile Tests

```bash
pytest --profile
```

---

## Test Maintenance

### Update Test Dependencies

```bash
# Update all dev dependencies
uv pip install --upgrade -r requirements-dev.txt
```

### Run Security Audit on Tests

```bash
bandit -r tests/
```

### Check Test Code Quality

```bash
flake8 tests/
black --check tests/
pylint tests/
```

---

## Contributing Tests

When contributing new features:

1. ✅ Write tests BEFORE code (TDD)
2. ✅ Maintain 95%+ coverage
3. ✅ Add docstrings to test functions
4. ✅ Use meaningful test names
5. ✅ Test edge cases and errors
6. ✅ Run full test suite before committing

---

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Guide](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Mocking Tutorial](https://docs.python.org/3/library/unittest.mock.html)

---

**Last Updated:** November 2025
**Maintainers:** Fouad Azem, Tal Goldengorn
