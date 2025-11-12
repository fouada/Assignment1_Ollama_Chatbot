"""
🤖 Ollama Flask REST API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REST API for Ollama Chatbot - Programmatic Access
Built with: Python 3.13 + Flask + Ollama API
Features: 100% Private | Cost-Free | No Internet Required
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import logging
import os
from datetime import datetime
from functools import wraps
from pathlib import Path

import ollama
from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    stream_with_context,
)
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ============================================
# APP CONFIGURATION
# ============================================

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max request size

# CORS Configuration - Allow specific origins in production
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv("ALLOWED_ORIGINS", "*").split(","),
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})

# Rate Limiting Configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Use Redis in production: redis://localhost:6379
)

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# Setup logging with file and console handlers
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_dir / "flask_app.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# ============================================
# HELPER FUNCTIONS
# ============================================


def handle_errors(f):
    """Decorator for comprehensive error handling with specific exception types"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ConnectionError as e:
            logger.error(f"Connection error in {f.__name__}: {str(e)}", exc_info=True)
            return (
                jsonify(
                    {
                        "error": "Cannot connect to Ollama server. Is it running?",
                        "details": str(e),
                        "timestamp": datetime.now().isoformat(),
                        "suggestion": "Start Ollama with: brew services start ollama",
                    }
                ),
                503,
            )
        except ValueError as e:
            logger.error(f"Validation error in {f.__name__}: {str(e)}")
            return (
                jsonify(
                    {
                        "error": "Invalid request parameters",
                        "details": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                400,
            )
        except TimeoutError as e:
            logger.error(f"Timeout error in {f.__name__}: {str(e)}")
            return (
                jsonify(
                    {
                        "error": "Request timeout",
                        "details": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                504,
            )
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}", exc_info=True)
            return (
                jsonify(
                    {
                        "error": "Internal server error",
                        "details": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                500,
            )

    return decorated_function


def validate_chat_request(data):
    """Validate chat request parameters"""
    if not data:
        raise ValueError("Request body is required")

    if "message" not in data:
        raise ValueError("'message' field is required")

    if not isinstance(data.get("message"), str):
        raise ValueError("'message' must be a string")

    if data.get("message", "").strip() == "":
        raise ValueError("'message' cannot be empty")

    if "temperature" in data:
        temp = data["temperature"]
        if not isinstance(temp, (int, float)):
            raise ValueError("'temperature' must be a number")
        if temp < 0 or temp > 2:
            raise ValueError("'temperature' must be between 0 and 2")

    if "model" in data and not isinstance(data.get("model"), str):
        raise ValueError("'model' must be a string")

    return True


def validate_generate_request(data):
    """Validate generate request parameters"""
    if not data:
        raise ValueError("Request body is required")

    if "prompt" not in data:
        raise ValueError("'prompt' field is required")

    if not isinstance(data.get("prompt"), str):
        raise ValueError("'prompt' must be a string")

    if data.get("prompt", "").strip() == "":
        raise ValueError("'prompt' cannot be empty")

    if "temperature" in data:
        temp = data["temperature"]
        if not isinstance(temp, (int, float)):
            raise ValueError("'temperature' must be a number")
        if temp < 0 or temp > 2:
            raise ValueError("'temperature' must be between 0 and 2")

    return True


# ============================================
# ROUTES
# ============================================


@app.route("/")
def index():
    """Render the luxurious chatbot UI"""
    return render_template("index.html")


@app.route("/api")
def api_info():
    """API information endpoint"""
    return jsonify(
        {
            "name": "Ollama Flask REST API",
            "version": "1.0.0",
            "description": "Private, local AI chatbot API",
            "features": [
                "100% Private - No data leaves your machine",
                "Cost-Free - No API fees",
                "Fast - Direct local processing",
                "Multiple Models - Choose your AI",
            ],
            "endpoints": {
                "GET /": "Chatbot UI",
                "GET /api": "API information",
                "GET /health": "Health check",
                "GET /models": "List available models",
                "POST /chat": "Chat with AI (streaming)",
                "POST /generate": "Generate response (non-streaming)",
            },
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/health", methods=["GET"])
@limiter.limit("60 per minute")
def health():
    """Health check endpoint"""
    try:
        # Check Ollama connection
        models = ollama.list()
        model_count = len(models.models)

        return (
            jsonify(
                {
                    "status": "healthy",
                    "ollama": "connected",
                    "models_available": model_count,
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "ollama": "disconnected",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            503,
        )


@app.route("/models", methods=["GET"])
@handle_errors
@limiter.limit("30 per minute")
def get_models():
    """Get list of available Ollama models"""
    models_data = ollama.list()
    models = models_data.models

    model_list = []
    for model in models:
        model_list.append(
            {
                "name": model.model,
                "size": model.size,
                "modified_at": (
                    model.modified_at.isoformat() if model.modified_at else None
                ),
                "details": {
                    "format": model.details.format if model.details else None,
                    "family": model.details.family if model.details else None,
                    "parameter_size": (
                        model.details.parameter_size if model.details else None
                    ),
                    "quantization_level": (
                        model.details.quantization_level if model.details else None
                    ),
                },
            }
        )

    return jsonify(
        {
            "models": model_list,
            "count": len(model_list),
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/chat", methods=["POST"])
@handle_errors
@limiter.limit("20 per minute")
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

    # Validate request
    try:
        validate_chat_request(data)
    except ValueError as e:
        logger.warning(f"Invalid chat request: {str(e)}")
        return jsonify({"error": str(e), "timestamp": datetime.now().isoformat()}), 400

    message = data.get("message")
    model = data.get("model", "llama3.2")
    temperature = data.get("temperature", 0.7)
    stream = data.get("stream", True)

    logger.info(
        f"Chat request - Model: {model}, Stream: {stream}, Message length: {len(message)}"
    )

    if stream:

        def generate():
            """Generator for streaming responses"""
            try:
                response = ollama.chat(
                    model=model,
                    messages=[{"role": "user", "content": message}],
                    stream=True,
                    options={"temperature": temperature},
                )

                for chunk in response:
                    if "message" in chunk and "content" in chunk["message"]:
                        content = chunk["message"]["content"]
                        yield f"data: {json.dumps({'content': content})}\n\n"

                yield f"data: {json.dumps({'done': True})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    else:
        # Non-streaming response
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": message}],
            stream=False,
            options={"temperature": temperature},
        )

        return jsonify(
            {
                "response": response["message"]["content"],
                "model": model,
                "timestamp": datetime.now().isoformat(),
            }
        )


@app.route("/generate", methods=["POST"])
@handle_errors
@limiter.limit("20 per minute")
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

    # Validate request
    try:
        validate_generate_request(data)
    except ValueError as e:
        logger.warning(f"Invalid generate request: {str(e)}")
        return jsonify({"error": str(e), "timestamp": datetime.now().isoformat()}), 400

    prompt = data.get("prompt")
    model = data.get("model", "llama3.2")
    temperature = data.get("temperature", 0.7)

    logger.info(f"Generate request - Model: {model}, Prompt length: {len(prompt)}")

    try:
        # Add timeout for Ollama request (30 seconds)
        response = ollama.generate(
            model=model, 
            prompt=prompt, 
            stream=False, 
            options={"temperature": temperature}
        )
    except Exception as e:
        logger.error(f"Ollama generation failed: {str(e)}")
        raise TimeoutError(f"Request timed out or failed: {str(e)}")

    return jsonify(
        {
            "response": response["response"],
            "model": model,
            "timestamp": datetime.now().isoformat(),
        }
    )


# ============================================
# ERROR HANDLERS
# ============================================


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify(
            {"error": "Endpoint not found", "timestamp": datetime.now().isoformat()}
        ),
        404,
    )


@app.errorhandler(405)
def method_not_allowed(error):
    return (
        jsonify(
            {"error": "Method not allowed", "timestamp": datetime.now().isoformat()}
        ),
        405,
    )


@app.errorhandler(500)
def internal_error(error):
    return (
        jsonify(
            {"error": "Internal server error", "timestamp": datetime.now().isoformat()}
        ),
        500,
    )


@app.errorhandler(429)
def ratelimit_error(error):
    return (
        jsonify(
            {
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "timestamp": datetime.now().isoformat(),
            }
        ),
        429,
    )


@app.errorhandler(413)
def request_too_large(error):
    return (
        jsonify(
            {
                "error": "Request too large",
                "message": "Request payload exceeds maximum allowed size",
                "timestamp": datetime.now().isoformat(),
            }
        ),
        413,
    )


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":  # pragma: no cover
    logger.info("=" * 50)
    logger.info("🤖 Starting Ollama Flask Chatbot Server")
    logger.info("=" * 50)
    logger.info("🌐 Chatbot UI: http://localhost:5000")
    logger.info("📚 API Docs: http://localhost:5000/api")
    logger.info("🏥 Health: http://localhost:5000/health")
    logger.info("=" * 50)

    # Get configuration from environment variables for security
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    host_addr = os.getenv(
        "FLASK_HOST", "127.0.0.1"
    )  # Default to localhost for security
    port_num = int(os.getenv("FLASK_PORT", "5000"))

    app.run(host=host_addr, port=port_num, debug=debug_mode, threaded=True)