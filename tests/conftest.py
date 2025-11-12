"""
Pytest configuration and shared fixtures
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

# Add src directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


@pytest.fixture
def mock_ollama_list():
    """Mock ollama.list() response"""
    mock_response = Mock()
    mock_model = Mock()
    mock_model.model = "llama3.2:latest"
    mock_model.size = 2000000000
    mock_model.modified_at = None
    mock_model.details = Mock()
    mock_model.details.format = "gguf"
    mock_model.details.family = "llama"
    mock_model.details.parameter_size = "3.2B"
    mock_model.details.quantization_level = "Q4_0"
    mock_response.models = [mock_model]
    return mock_response


@pytest.fixture
def mock_ollama_chat():
    """Mock ollama.chat() response"""
    return {
        "message": {"role": "assistant", "content": "This is a test response"},
        "done": True,
    }


@pytest.fixture
def mock_ollama_chat_stream():
    """Mock streaming ollama.chat() response"""
    chunks = [
        {"message": {"content": "This "}, "done": False},
        {"message": {"content": "is "}, "done": False},
        {"message": {"content": "a "}, "done": False},
        {"message": {"content": "test"}, "done": False},
        {"message": {"content": ""}, "done": True},
    ]
    return iter(chunks)


@pytest.fixture
def mock_ollama_generate():
    """Mock ollama.generate() response"""
    return {"response": "Generated test response", "done": True}


@pytest.fixture
def sample_chat_request():
    """Sample chat request data"""
    return {
        "message": "Hello, AI!",
        "model": "llama3.2",
        "temperature": 0.7,
        "stream": False,
    }


@pytest.fixture
def sample_generate_request():
    """Sample generate request data"""
    return {"prompt": "def hello():", "model": "codellama", "temperature": 0.3}


@pytest.fixture
def flask_client():
    """Flask test client"""
    # Import here to avoid circular imports
    from ollama_chatbot.api.flask_app import app

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components"""
    mock = MagicMock()
    return mock
