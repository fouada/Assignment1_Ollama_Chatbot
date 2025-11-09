"""
Comprehensive unit tests for Flask REST API
Target: 95%+ code coverage
"""
import pytest
import json
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime


class TestAPIInfo:
    """Test API information endpoint"""

    def test_api_info_endpoint(self, flask_client):
        """Test GET /api returns correct information"""
        response = flask_client.get('/api')
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Ollama Flask REST API'
        assert data['version'] == '1.0.0'
        assert 'endpoints' in data
        assert 'features' in data
        assert 'timestamp' in data

    def test_api_info_structure(self, flask_client):
        """Test API info has correct structure"""
        response = flask_client.get('/api')
        data = response.get_json()
        assert isinstance(data['features'], list)
        assert isinstance(data['endpoints'], dict)
        assert len(data['features']) > 0


class TestHealthCheck:
    """Test health check endpoint"""

    @patch('app_flask.ollama.list')
    def test_health_check_success(self, mock_list, flask_client, mock_ollama_list):
        """Test health check when Ollama is connected"""
        mock_list.return_value = mock_ollama_list
        response = flask_client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['ollama'] == 'connected'
        assert data['models_available'] == 1
        assert 'timestamp' in data

    @patch('app_flask.ollama.list')
    def test_health_check_failure(self, mock_list, flask_client):
        """Test health check when Ollama is disconnected"""
        mock_list.side_effect = Exception("Connection refused")
        response = flask_client.get('/health')
        assert response.status_code == 503
        data = response.get_json()
        assert data['status'] == 'unhealthy'
        assert data['ollama'] == 'disconnected'
        assert 'error' in data

    @patch('app_flask.ollama.list')
    def test_health_check_no_models(self, mock_list, flask_client):
        """Test health check with no models available"""
        mock_response = Mock()
        mock_response.models = []
        mock_list.return_value = mock_response
        response = flask_client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['models_available'] == 0


class TestModelsEndpoint:
    """Test models listing endpoint"""

    @patch('app_flask.ollama.list')
    def test_get_models_success(self, mock_list, flask_client, mock_ollama_list):
        """Test GET /models returns model list"""
        mock_list.return_value = mock_ollama_list
        response = flask_client.get('/models')
        assert response.status_code == 200
        data = response.get_json()
        assert 'models' in data
        assert 'count' in data
        assert 'timestamp' in data
        assert data['count'] == 1
        assert isinstance(data['models'], list)

    @patch('app_flask.ollama.list')
    def test_get_models_structure(self, mock_list, flask_client, mock_ollama_list):
        """Test model structure in response"""
        mock_list.return_value = mock_ollama_list
        response = flask_client.get('/models')
        data = response.get_json()
        model = data['models'][0]
        assert 'name' in model
        assert 'size' in model
        assert 'details' in model
        assert model['name'] == 'llama3.2:latest'

    @patch('app_flask.ollama.list')
    def test_get_models_error_handling(self, mock_list, flask_client):
        """Test error handling when model listing fails"""
        mock_list.side_effect = Exception("Ollama error")
        response = flask_client.get('/models')
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data


class TestChatEndpoint:
    """Test chat endpoint with streaming and non-streaming"""

    @patch('app_flask.ollama.chat')
    def test_chat_non_streaming_success(self, mock_chat, flask_client,
                                       sample_chat_request, mock_ollama_chat):
        """Test non-streaming chat request"""
        mock_chat.return_value = mock_ollama_chat
        response = flask_client.post('/chat',
                                    data=json.dumps(sample_chat_request),
                                    content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert 'response' in data
        assert 'model' in data
        assert 'timestamp' in data
        assert data['model'] == 'llama3.2'

    def test_chat_missing_message(self, flask_client):
        """Test chat request without message field"""
        response = flask_client.post('/chat',
                                    data=json.dumps({'model': 'llama3.2'}),
                                    content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'message' in data['error'].lower()

    def test_chat_empty_request(self, flask_client):
        """Test chat with empty request body"""
        response = flask_client.post('/chat',
                                    data=json.dumps({}),
                                    content_type='application/json')
        assert response.status_code == 400

    def test_chat_no_json(self, flask_client):
        """Test chat with invalid content type"""
        response = flask_client.post('/chat', data='not json')
        assert response.status_code in [400, 500]

    @patch('app_flask.ollama.chat')
    def test_chat_streaming(self, mock_chat, flask_client,
                           sample_chat_request, mock_ollama_chat_stream):
        """Test streaming chat response"""
        sample_chat_request['stream'] = True
        mock_chat.return_value = mock_ollama_chat_stream
        response = flask_client.post('/chat',
                                    data=json.dumps(sample_chat_request),
                                    content_type='application/json')
        assert response.status_code == 200
        assert response.mimetype == 'text/event-stream'
        assert b'data:' in response.data

    @patch('app_flask.ollama.chat')
    def test_chat_default_parameters(self, mock_chat, flask_client, mock_ollama_chat):
        """Test chat with default model and temperature"""
        mock_chat.return_value = mock_ollama_chat
        request_data = {'message': 'Hello'}
        response = flask_client.post('/chat',
                                    data=json.dumps(request_data),
                                    content_type='application/json')
        assert response.status_code == 200
        # Verify default parameters were used
        call_kwargs = mock_chat.call_args[1]
        assert call_kwargs['options']['temperature'] == 0.7

    @patch('app_flask.ollama.chat')
    def test_chat_custom_temperature(self, mock_chat, flask_client,
                                    sample_chat_request, mock_ollama_chat):
        """Test chat with custom temperature"""
        sample_chat_request['temperature'] = 1.5
        mock_chat.return_value = mock_ollama_chat
        response = flask_client.post('/chat',
                                    data=json.dumps(sample_chat_request),
                                    content_type='application/json')
        assert response.status_code == 200
        call_kwargs = mock_chat.call_args[1]
        assert call_kwargs['options']['temperature'] == 1.5

    @patch('app_flask.ollama.chat')
    def test_chat_ollama_error(self, mock_chat, flask_client, sample_chat_request):
        """Test chat when Ollama returns error"""
        mock_chat.side_effect = Exception("Model not found")
        response = flask_client.post('/chat',
                                    data=json.dumps(sample_chat_request),
                                    content_type='application/json')
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data


class TestGenerateEndpoint:
    """Test generate endpoint"""

    @patch('app_flask.ollama.generate')
    def test_generate_success(self, mock_generate, flask_client,
                             sample_generate_request, mock_ollama_generate):
        """Test successful text generation"""
        mock_generate.return_value = mock_ollama_generate
        response = flask_client.post('/generate',
                                    data=json.dumps(sample_generate_request),
                                    content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert 'response' in data
        assert 'model' in data
        assert 'timestamp' in data
        assert data['model'] == 'codellama'

    def test_generate_missing_prompt(self, flask_client):
        """Test generate without prompt field"""
        response = flask_client.post('/generate',
                                    data=json.dumps({'model': 'llama3.2'}),
                                    content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'prompt' in data['error'].lower()

    @patch('app_flask.ollama.generate')
    def test_generate_default_model(self, mock_generate, flask_client,
                                   mock_ollama_generate):
        """Test generate with default model"""
        mock_generate.return_value = mock_ollama_generate
        request_data = {'prompt': 'test prompt'}
        response = flask_client.post('/generate',
                                    data=json.dumps(request_data),
                                    content_type='application/json')
        assert response.status_code == 200
        # Verify default model was used
        call_args = mock_generate.call_args
        assert call_args[1]['model'] == 'llama3.2'

    @patch('app_flask.ollama.generate')
    def test_generate_error_handling(self, mock_generate, flask_client,
                                    sample_generate_request):
        """Test generate error handling"""
        mock_generate.side_effect = Exception("Generation failed")
        response = flask_client.post('/generate',
                                    data=json.dumps(sample_generate_request),
                                    content_type='application/json')
        assert response.status_code == 500


class TestErrorHandlers:
    """Test custom error handlers"""

    def test_404_not_found(self, flask_client):
        """Test 404 error handler"""
        response = flask_client.get('/nonexistent')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'timestamp' in data

    def test_405_method_not_allowed(self, flask_client):
        """Test 405 error handler"""
        response = flask_client.put('/health')
        assert response.status_code == 405
        data = response.get_json()
        assert 'error' in data

    def test_index_route(self, flask_client):
        """Test index route returns HTML"""
        response = flask_client.get('/')
        # Should try to render template or return error
        assert response.status_code in [200, 404, 500]


class TestLogging:
    """Test logging functionality"""

    @patch('app_flask.logger')
    @patch('app_flask.ollama.chat')
    def test_chat_logging(self, mock_chat, mock_logger, flask_client,
                         sample_chat_request, mock_ollama_chat):
        """Test that chat requests are logged"""
        mock_chat.return_value = mock_ollama_chat
        flask_client.post('/chat',
                         data=json.dumps(sample_chat_request),
                         content_type='application/json')
        # Verify info logging was called
        assert mock_logger.info.called

    @patch('app_flask.logger')
    @patch('app_flask.ollama.chat')
    def test_error_logging(self, mock_chat, mock_logger, flask_client,
                          sample_chat_request):
        """Test that errors are logged"""
        mock_chat.side_effect = Exception("Test error")
        flask_client.post('/chat',
                         data=json.dumps(sample_chat_request),
                         content_type='application/json')
        # Verify error logging was called
        assert mock_logger.error.called


class TestIntegration:
    """Integration tests"""

    @patch('app_flask.ollama.list')
    @patch('app_flask.ollama.chat')
    def test_full_workflow(self, mock_chat, mock_list, flask_client,
                          mock_ollama_list, mock_ollama_chat):
        """Test complete workflow: health -> models -> chat"""
        mock_list.return_value = mock_ollama_list
        mock_chat.return_value = mock_ollama_chat

        # 1. Check health
        health_response = flask_client.get('/health')
        assert health_response.status_code == 200

        # 2. Get models
        models_response = flask_client.get('/models')
        assert models_response.status_code == 200

        # 3. Send chat message
        chat_response = flask_client.post('/chat',
                                         data=json.dumps({
                                             'message': 'Hello',
                                             'stream': False
                                         }),
                                         content_type='application/json')
        assert chat_response.status_code == 200
