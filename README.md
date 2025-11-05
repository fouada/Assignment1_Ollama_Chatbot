# Assignment1 Ollama Chatbot

A chatbot application using Ollama local LLM server.

## Installed Models

- **llama3.2:latest** (2.0 GB) - General purpose model
- **mistral:latest** (4.4 GB) - Powerful general purpose model
- **phi:latest** (1.6 GB) - Compact and efficient model
- **codellama:latest** (3.8 GB) - Specialized for coding tasks

## Prerequisites

- Python 3.13+
- Ollama server

## Installation

1. Install Ollama:
```bash
brew install ollama
```

2. Start Ollama service:
```bash
brew services start ollama
```

3. Pull models:
```bash
ollama pull llama3.2
ollama pull mistral
ollama pull phi
ollama pull codellama
```

## Usage

Run a model:
```bash
ollama run llama3.2
```

Or use via API:
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Hello, how are you?"
}'
```

## Project Structure

```
Assignment1_Ollama_Chatbot/
├── README.md
└── (more files to be added)
```

## License

MIT
