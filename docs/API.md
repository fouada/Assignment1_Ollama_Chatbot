# Ollama Flask REST API Documentation

## 📡 Complete API Reference

**Version**: 1.0.0  
**Base URL**: `http://localhost:5000`

---

## Overview

The Ollama Flask REST API provides programmatic access to local AI models. All processing happens locally with no external API calls.

### Key Features
- 🔒 **100% Private** - No data leaves your machine
- 💰 **Cost-Free** - No API fees or subscriptions
- ⚡ **Fast** - Direct local processing
- 🌐 **RESTful** - Standard HTTP methods

---

## Endpoints

### 1. API Information - `GET /`

Returns API metadata and available endpoints.

**Request:**
```bash
curl http://localhost:5000/
```

**Response:**
```json
{
  "name": "Ollama Flask REST API",
  "version": "1.0.0",
  "description": "Private, local AI chatbot API",
  "endpoints": {
    "GET /": "API information",
    "GET /health": "Health check",
    "GET /models": "List available models",
    "POST /chat": "Chat with AI",
    "POST /generate": "Generate response"
  }
}
```

---

### 2. Health Check - `GET /health`

Check API and Ollama server status.

**Request:**
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "ollama": "connected",
  "models_available": 4,
  "timestamp": "2025-11-09T10:30:00"
}
```

---

### 3. List Models - `GET /models`

Retrieve list of available models.

**Request:**
```bash
curl http://localhost:5000/models
```

**Response:**
```json
{
  "models": [
    {
      "name": "llama3.2:latest",
      "size": 2000000000,
      "details": {
        "format": "gguf",
        "family": "llama",
        "parameter_size": "3.2B"
      }
    }
  ],
  "count": 4
}
```

---

### 4. Chat - `POST /chat`

Send message and receive AI response.

**Request:**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain quantum computing",
    "model": "llama3.2",
    "temperature": 0.7,
    "stream": false
  }'
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `message` | string | Yes | - | User's input message |
| `model` | string | No | "llama3.2" | Model name |
| `temperature` | number | No | 0.7 | Creativity (0.0-2.0) |
| `stream` | boolean | No | false | Enable streaming |

**Response (Non-Streaming):**
```json
{
  "response": "Quantum computing is...",
  "model": "llama3.2",
  "timestamp": "2025-11-09T10:30:00"
}
```

**Response (Streaming):**
```
data: {"content": "Quantum"}
data: {"content": " computing"}
data: {"done": true}
```

---

### 5. Generate - `POST /generate`

Generate text completion from prompt.

**Request:**
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "def factorial(n):",
    "model": "codellama",
    "temperature": 0.3
  }'
```

**Response:**
```json
{
  "response": "\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n - 1)",
  "model": "codellama"
}
```

---

## Error Handling

All errors return consistent JSON format:

```json
{
  "error": "Human-readable error message",
  "timestamp": "2025-11-09T10:30:00"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters |
| 404 | Not Found | Endpoint doesn't exist |
| 500 | Internal Server Error | Unexpected error |
| 503 | Service Unavailable | Ollama disconnected |

---

## Examples

### Python
```python
import requests

response = requests.post('http://localhost:5000/chat', json={
    'message': 'Hello!',
    'model': 'llama3.2'
})
print(response.json()['response'])
```

### JavaScript
```javascript
const response = await fetch('http://localhost:5000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Hello!',
    model: 'llama3.2'
  })
});
const data = await response.json();
console.log(data.response);
```

### Shell
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","model":"llama3.2"}'
```

---

For complete API documentation, examples, and best practices, see the main [README.md](../README.md).

