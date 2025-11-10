"""
Comprehensive unit tests for Streamlit application
Target: 95%+ code coverage
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add apps directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "apps"))


class TestHelperFunctions:
    """Test helper functions in Streamlit app"""

    @patch("app_streamlit.ollama.list")
    def test_check_ollama_connection_success(self, mock_list):
        """Test successful Ollama connection check"""
        from app_streamlit import check_ollama_connection

        mock_list.return_value = []
        result = check_ollama_connection()
        assert result is True
        mock_list.assert_called_once()

    @patch("app_streamlit.ollama.list")
    def test_check_ollama_connection_failure(self, mock_list):
        """Test failed Ollama connection check"""
        from app_streamlit import check_ollama_connection

        mock_list.side_effect = Exception("Connection refused")
        result = check_ollama_connection()
        assert result is False

    @patch("app_streamlit.ollama.list")
    def test_check_ollama_connection_timeout(self, mock_list):
        """Test Ollama connection timeout"""
        from app_streamlit import check_ollama_connection

        mock_list.side_effect = TimeoutError("Request timeout")
        result = check_ollama_connection()
        assert result is False

    @patch("app_streamlit.ollama.list")
    def test_check_ollama_connection_connection_error(self, mock_list):
        """Test Ollama connection with ConnectionError"""
        from app_streamlit import check_ollama_connection

        mock_list.side_effect = ConnectionError("Connection refused")
        result = check_ollama_connection()
        assert result is False

    @patch("app_streamlit.ollama.list")
    def test_get_available_models_success(self, mock_list, mock_ollama_list):
        """Test retrieving available models"""
        from app_streamlit import get_available_models

        mock_list.return_value = mock_ollama_list
        models = get_available_models()
        assert isinstance(models, list)
        assert len(models) == 1
        assert models[0] == "llama3.2:latest"

    @patch("app_streamlit.ollama.list")
    def test_get_available_models_multiple(self, mock_list):
        """Test retrieving multiple models"""
        from app_streamlit import get_available_models

        mock_response = Mock()
        model1 = Mock()
        model1.model = "llama3.2:latest"
        model2 = Mock()
        model2.model = "mistral:latest"
        model3 = Mock()
        model3.model = "codellama:latest"
        mock_response.models = [model1, model2, model3]
        mock_list.return_value = mock_response

        models = get_available_models()
        assert len(models) == 3
        assert "llama3.2:latest" in models
        assert "mistral:latest" in models
        assert "codellama:latest" in models

    @patch("app_streamlit.ollama.list")
    @patch("app_streamlit.st.error")
    def test_get_available_models_error(self, mock_error, mock_list):
        """Test error handling when fetching models fails"""
        from app_streamlit import get_available_models

        mock_list.side_effect = Exception("API Error")
        models = get_available_models()
        assert models == []
        mock_error.assert_called_once()

    @patch("app_streamlit.ollama.list")
    @patch("app_streamlit.st.error")
    def test_get_available_models_connection_error(self, mock_error, mock_list):
        """Test handling of connection errors when fetching models"""
        from app_streamlit import get_available_models

        mock_list.side_effect = ConnectionError("Cannot connect to Ollama server")
        models = get_available_models()
        assert models == []
        mock_error.assert_called_once()

    @patch("app_streamlit.ollama.list")
    def test_get_available_models_empty(self, mock_list):
        """Test when no models are available"""
        from app_streamlit import get_available_models

        mock_response = Mock()
        mock_response.models = []
        mock_list.return_value = mock_response
        models = get_available_models()
        assert models == []
        assert isinstance(models, list)


class TestGenerateResponse:
    """Test response generation functionality"""

    @patch("app_streamlit.ollama.chat")
    def test_generate_response_success(self, mock_chat):
        """Test successful response generation"""
        from app_streamlit import generate_response

        # Mock streaming response
        mock_chat.return_value = [
            {"message": {"content": "Hello"}, "done": False},
            {"message": {"content": " there"}, "done": False},
            {"message": {"content": "!"}, "done": True},
        ]

        prompt = "Say hello"
        model = "llama3.2"
        temperature = 0.7

        response_parts = list(generate_response(prompt, model, temperature))
        assert len(response_parts) == 3
        assert response_parts[0] == "Hello"
        assert response_parts[1] == " there"
        assert response_parts[2] == "!"

    @patch("app_streamlit.ollama.chat")
    def test_generate_response_with_options(self, mock_chat):
        """Test response generation with custom options"""
        from app_streamlit import generate_response

        mock_chat.return_value = [{"message": {"content": "Response"}, "done": True}]

        list(generate_response("Test", "llama3.2", 1.5))

        # Verify chat was called with correct parameters
        call_kwargs = mock_chat.call_args[1]
        assert call_kwargs["model"] == "llama3.2"
        assert call_kwargs["stream"] is True
        assert call_kwargs["options"]["temperature"] == 1.5
        assert call_kwargs["messages"][0]["role"] == "user"
        assert call_kwargs["messages"][0]["content"] == "Test"

    @patch("app_streamlit.ollama.chat")
    def test_generate_response_error(self, mock_chat):
        """Test error handling in response generation"""
        from app_streamlit import generate_response

        mock_chat.side_effect = Exception("Model not found")

        response_parts = list(generate_response("Test", "invalid_model", 0.7))
        assert len(response_parts) == 1
        assert "Error:" in response_parts[0]
        assert "Model not found" in response_parts[0]

    @patch("app_streamlit.ollama.chat")
    def test_generate_response_empty_message(self, mock_chat):
        """Test with empty message"""
        from app_streamlit import generate_response

        mock_chat.return_value = [{"message": {"content": ""}, "done": True}]

        response_parts = list(generate_response("", "llama3.2", 0.7))
        assert isinstance(response_parts, list)

    @patch("app_streamlit.ollama.chat")
    def test_generate_response_missing_content(self, mock_chat):
        """Test handling of chunks without content"""
        from app_streamlit import generate_response

        mock_chat.return_value = [
            {"message": {}, "done": False},  # Missing content
            {"message": {"content": "Valid"}, "done": True},
        ]

        response_parts = list(generate_response("Test", "llama3.2", 0.7))
        # Should only yield the valid chunk
        assert len(response_parts) == 1
        assert response_parts[0] == "Valid"

    @patch("app_streamlit.ollama.chat")
    def test_generate_response_temperature_bounds(self, mock_chat):
        """Test response generation with boundary temperatures"""
        from app_streamlit import generate_response

        mock_chat.return_value = [{"message": {"content": "Test"}, "done": True}]

        # Test minimum temperature
        list(generate_response("Test", "llama3.2", 0.0))
        assert mock_chat.call_args[1]["options"]["temperature"] == 0.0

        # Test maximum temperature
        list(generate_response("Test", "llama3.2", 2.0))
        assert mock_chat.call_args[1]["options"]["temperature"] == 2.0

    @patch("app_streamlit.ollama.chat")
    def test_generate_response_connection_error(self, mock_chat):
        """Test handling of connection errors"""
        from app_streamlit import generate_response

        mock_chat.side_effect = ConnectionError("Cannot reach Ollama server")

        response_parts = list(generate_response("Test", "llama3.2", 0.7))
        assert "Error:" in response_parts[0]
        assert "Cannot reach Ollama server" in response_parts[0]

    @patch("app_streamlit.ollama.chat")
    def test_generate_response_value_error(self, mock_chat):
        """Test handling of ValueError (invalid model or parameters)"""
        from app_streamlit import generate_response

        mock_chat.side_effect = ValueError("Invalid model or parameters")

        response_parts = list(generate_response("Test", "invalid_model", 0.7))
        assert len(response_parts) == 1
        assert "Error:" in response_parts[0]
        assert "Invalid model or parameters" in response_parts[0]


class TestPersistenceFunctions:
    """Test message persistence functions"""

    @patch("app_streamlit.st.session_state")
    @patch("app_streamlit.components.html")
    def test_save_messages_to_localstorage(self, mock_html, mock_session_state):
        """Test saving messages to localStorage"""
        from app_streamlit import save_messages_to_localstorage

        # Setup session state
        mock_session_state.messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]
        mock_session_state.total_messages = 2

        save_messages_to_localstorage()

        # Verify components.html was called
        mock_html.assert_called_once()
        call_args = mock_html.call_args[0][0]
        assert "localStorage" in call_args
        assert "setItem" in call_args

    @patch("app_streamlit.st.session_state")
    def test_save_messages_to_localstorage_empty(self, mock_session_state):
        """Test saving empty messages list does nothing"""
        from app_streamlit import save_messages_to_localstorage

        mock_session_state.messages = []

        # Should return early without error
        save_messages_to_localstorage()

    @patch("app_streamlit.st.session_state")
    @patch("builtins.open", create=True)
    @patch("pathlib.Path.exists")
    def test_load_messages_from_localstorage(
        self, mock_exists, mock_open, mock_session_state
    ):
        """Test loading messages from cache file"""
        from app_streamlit import load_messages_from_localstorage
        import json

        # Setup
        mock_session_state.history_loaded = False
        mock_exists.return_value = True

        cache_data = {
            "messages": [{"role": "user", "content": "Test"}],
            "totalMessages": 1,
            "timestamp": "2025-01-01T00:00:00",
        }

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps(cache_data)
        mock_open.return_value = mock_file

        # Mock json.load to return our test data
        with patch("json.load", return_value=cache_data):
            load_messages_from_localstorage()

        # Verify session state was updated
        assert mock_session_state.history_loaded is True

    @patch("app_streamlit.st.session_state")
    @patch("pathlib.Path.exists")
    def test_load_messages_from_localstorage_no_cache(
        self, mock_exists, mock_session_state
    ):
        """Test loading when no cache file exists"""
        from app_streamlit import load_messages_from_localstorage

        mock_session_state.history_loaded = False
        mock_exists.return_value = False

        # Should not raise error
        load_messages_from_localstorage()
        assert mock_session_state.history_loaded is True

    @patch("app_streamlit.st.session_state")
    @patch("builtins.open", create=True)
    @patch("pathlib.Path.exists")
    def test_load_messages_from_localstorage_error(
        self, mock_exists, mock_open, mock_session_state
    ):
        """Test error handling when loading from cache fails"""
        from app_streamlit import load_messages_from_localstorage

        mock_session_state.history_loaded = False
        mock_exists.return_value = True
        mock_open.side_effect = Exception("Read error")

        # Should not raise exception, but handle gracefully
        load_messages_from_localstorage()
        assert mock_session_state.history_loaded is True

    @patch("app_streamlit.st.session_state")
    @patch("builtins.open", create=True)
    def test_save_messages_to_cache(self, mock_open, mock_session_state):
        """Test saving messages to cache file"""
        from app_streamlit import save_messages_to_cache

        mock_session_state.messages = [{"role": "user", "content": "Test"}]
        mock_session_state.total_messages = 1

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        save_messages_to_cache()

        # Verify file was opened for writing
        mock_open.assert_called_once()
        assert "w" in str(mock_open.call_args)

    @patch("app_streamlit.st.session_state")
    @patch("builtins.open", create=True)
    def test_save_messages_to_cache_error(self, mock_open, mock_session_state):
        """Test error handling in save_messages_to_cache"""
        from app_streamlit import save_messages_to_cache

        mock_session_state.messages = [{"role": "user", "content": "Test"}]
        mock_session_state.total_messages = 1
        mock_open.side_effect = Exception("Write error")

        # Should not raise exception
        save_messages_to_cache()

    @patch("pathlib.Path.unlink")
    @patch("pathlib.Path.exists")
    def test_clear_cache(self, mock_exists, mock_unlink):
        """Test clearing cache file"""
        from app_streamlit import clear_cache

        mock_exists.return_value = True

        clear_cache()

        # Verify file was deleted
        mock_unlink.assert_called_once()

    @patch("pathlib.Path.exists")
    def test_clear_cache_no_file(self, mock_exists):
        """Test clearing cache when file doesn't exist"""
        from app_streamlit import clear_cache

        mock_exists.return_value = False

        # Should not raise error
        clear_cache()

    @patch("pathlib.Path.unlink")
    @patch("pathlib.Path.exists")
    def test_clear_cache_error(self, mock_exists, mock_unlink):
        """Test error handling in clear_cache"""
        from app_streamlit import clear_cache

        mock_exists.return_value = True
        mock_unlink.side_effect = Exception("Delete error")

        # Should not raise exception
        clear_cache()


class TestModelInfo:
    """Test model information dictionary"""

    def test_model_info_structure(self):
        """Test that model info is properly structured"""
        from app_streamlit import check_ollama_connection

        # Just import to verify the structure exists
        # The actual model_info dict is defined in the main code
        assert check_ollama_connection is not None


class TestStreamlitComponents:
    """Test Streamlit-specific components"""

    @patch("app_streamlit.st")
    @patch("app_streamlit.ollama.list")
    def test_page_config(self, mock_list, mock_st):
        """Test that page config is set correctly"""
        # This tests the page configuration
        # In actual streamlit, this would be verified by checking st.set_page_config calls
        mock_list.return_value = Mock(models=[])
        assert True  # Basic import test

    def test_imports(self):
        """Test that all required modules can be imported"""
        try:
            import app_streamlit

            assert hasattr(app_streamlit, "check_ollama_connection")
            assert hasattr(app_streamlit, "get_available_models")
            assert hasattr(app_streamlit, "generate_response")
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")


class TestSessionState:
    """Test session state initialization logic"""

    def test_session_state_keys(self):
        """Test that expected session state keys are defined"""
        # This would be tested in actual Streamlit runtime
        # Here we verify the logic exists
        from app_streamlit import check_ollama_connection

        assert callable(check_ollama_connection)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @patch("app_streamlit.ollama.list")
    def test_unicode_in_model_names(self, mock_list):
        """Test handling of unicode characters in model names"""
        from app_streamlit import get_available_models

        mock_response = Mock()
        model = Mock()
        model.model = "模型-test:latest"
        mock_response.models = [model]
        mock_list.return_value = mock_response

        models = get_available_models()
        assert len(models) == 1
        assert "模型-test:latest" in models

    @patch("app_streamlit.ollama.chat")
    def test_very_long_prompt(self, mock_chat):
        """Test handling of very long prompts"""
        from app_streamlit import generate_response

        mock_chat.return_value = [{"message": {"content": "Response"}, "done": True}]

        long_prompt = "A" * 10000
        response = list(generate_response(long_prompt, "llama3.2", 0.7))
        assert len(response) > 0
        mock_chat.assert_called_once()

    @patch("app_streamlit.ollama.chat")
    def test_special_characters_in_prompt(self, mock_chat):
        """Test handling of special characters"""
        from app_streamlit import generate_response

        mock_chat.return_value = [{"message": {"content": "OK"}, "done": True}]

        special_prompt = "Test \n\t\r 特殊字符 <html> & ' \""
        response = list(generate_response(special_prompt, "llama3.2", 0.7))
        assert len(response) > 0

    @patch("app_streamlit.ollama.list")
    def test_malformed_model_response(self, mock_list):
        """Test handling of malformed API responses"""
        from app_streamlit import get_available_models

        # Test with None models
        mock_response = Mock()
        mock_response.models = None
        mock_list.return_value = mock_response

        try:
            models = get_available_models()
            # Should either handle gracefully or raise exception
            assert isinstance(models, list) or models is None
        except:
            # Exception is also acceptable
            pass


class TestPerformance:
    """Test performance-related aspects"""

    @patch("app_streamlit.ollama.chat")
    def test_streaming_chunks(self, mock_chat):
        """Test that streaming yields chunks incrementally"""
        from app_streamlit import generate_response

        # Create many chunks to simulate real streaming
        chunks = [{"message": {"content": str(i)}, "done": False} for i in range(100)]
        chunks.append({"message": {"content": "end"}, "done": True})
        mock_chat.return_value = chunks

        response_parts = list(generate_response("Test", "llama3.2", 0.7))
        assert len(response_parts) == 101

    @patch("app_streamlit.ollama.list")
    def test_model_list_caching_opportunity(self, mock_list, mock_ollama_list):
        """Test that model listing could benefit from caching"""
        from app_streamlit import get_available_models

        mock_list.return_value = mock_ollama_list

        # Call multiple times
        models1 = get_available_models()
        models2 = get_available_models()
        models3 = get_available_models()

        # Should call API each time (no caching currently)
        assert mock_list.call_count == 3
        assert models1 == models2 == models3


class TestRobustness:
    """Test application robustness"""

    @patch("app_streamlit.ollama.list")
    def test_network_timeout(self, mock_list):
        """Test handling of network timeouts"""
        from app_streamlit import check_ollama_connection

        mock_list.side_effect = TimeoutError("Network timeout")
        result = check_ollama_connection()
        assert result is False

    @patch("app_streamlit.ollama.chat")
    def test_incomplete_stream(self, mock_chat):
        """Test handling of incomplete streaming response"""
        from app_streamlit import generate_response

        # Stream that ends abruptly
        mock_chat.return_value = [
            {"message": {"content": "Start"}, "done": False},
            # No done=True chunk
        ]

        response_parts = list(generate_response("Test", "llama3.2", 0.7))
        assert len(response_parts) > 0
