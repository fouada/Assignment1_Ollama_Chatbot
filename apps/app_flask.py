"""
🤖 Ollama Flask REST API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REST API for Ollama Chatbot - Programmatic Access
Built with: Python 3.13 + Flask + Ollama API
Features: 100% Private | Cost-Free | No Internet Required
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from flask import Flask, request, jsonify, Response, stream_with_context
import ollama
import json
import logging
from datetime import datetime
from functools import wraps

# ============================================
# APP CONFIGURATION
# ============================================

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# HELPER FUNCTIONS
# ============================================

def handle_errors(f):
    """Decorator for error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    return decorated_function

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    """API information endpoint"""
    return jsonify({
        'name': 'Ollama Flask REST API',
        'version': '1.0.0',
        'description': 'Private, local AI chatbot API',
        'features': [
            '100% Private - No data leaves your machine',
            'Cost-Free - No API fees',
            'Fast - Direct local processing',
            'Multiple Models - Choose your AI'
        ],
        'endpoints': {
            'GET /': 'API information',
            'GET /health': 'Health check',
            'GET /models': 'List available models',
            'POST /chat': 'Chat with AI (streaming)',
            'POST /generate': 'Generate response (non-streaming)'
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
@handle_errors
def health():
    """Health check endpoint"""
    try:
        # Check Ollama connection
        models = ollama.list()
        model_count = len(models.get('models', []))

        return jsonify({
            'status': 'healthy',
            'ollama': 'connected',
            'models_available': model_count,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'ollama': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@app.route('/models', methods=['GET'])
@handle_errors
def get_models():
    """Get list of available Ollama models"""
    models_data = ollama.list()
    models = models_data.get('models', [])

    model_list = []
    for model in models:
        model_list.append({
            'name': model.get('name'),
            'size': model.get('size'),
            'modified_at': model.get('modified_at'),
            'details': model.get('details', {})
        })

    return jsonify({
        'models': model_list,
        'count': len(model_list),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/chat', methods=['POST'])
@handle_errors
def chat():
    """
    Chat endpoint with streaming support

    Request JSON:
    {
        "message": "Your message here",
        "model": "llama3.2",
        "temperature": 0.7,
        "stream": true
    }
    """
    data = request.json

    if not data or 'message' not in data:
        return jsonify({'error': 'Missing "message" in request'}), 400

    message = data.get('message')
    model = data.get('model', 'llama3.2')
    temperature = data.get('temperature', 0.7)
    stream = data.get('stream', True)

    logger.info(f"Chat request - Model: {model}, Stream: {stream}")

    if stream:
        def generate():
            """Generator for streaming responses"""
            try:
                response = ollama.chat(
                    model=model,
                    messages=[{'role': 'user', 'content': message}],
                    stream=True,
                    options={'temperature': temperature}
                )

                for chunk in response:
                    if 'message' in chunk and 'content' in chunk['message']:
                        content = chunk['message']['content']
                        yield f"data: {json.dumps({'content': content})}\n\n"

                yield f"data: {json.dumps({'done': True})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    else:
        # Non-streaming response
        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': message}],
            stream=False,
            options={'temperature': temperature}
        )

        return jsonify({
            'response': response['message']['content'],
            'model': model,
            'timestamp': datetime.now().isoformat()
        })

@app.route('/generate', methods=['POST'])
@handle_errors
def generate():
    """
    Generate text completion (non-streaming)

    Request JSON:
    {
        "prompt": "Your prompt here",
        "model": "llama3.2",
        "temperature": 0.7
    }
    """
    data = request.json

    if not data or 'prompt' not in data:
        return jsonify({'error': 'Missing "prompt" in request'}), 400

    prompt = data.get('prompt')
    model = data.get('model', 'llama3.2')
    temperature = data.get('temperature', 0.7)

    logger.info(f"Generate request - Model: {model}")

    response = ollama.generate(
        model=model,
        prompt=prompt,
        stream=False,
        options={'temperature': temperature}
    )

    return jsonify({
        'response': response['response'],
        'model': model,
        'timestamp': datetime.now().isoformat()
    })

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method not allowed',
        'timestamp': datetime.now().isoformat()
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    logger.info("="*50)
    logger.info("🤖 Starting Ollama Flask API Server")
    logger.info("="*50)
    logger.info("🌐 Server: http://localhost:5000")
    logger.info("📚 API Docs: http://localhost:5000/")
    logger.info("🏥 Health: http://localhost:5000/health")
    logger.info("="*50)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
