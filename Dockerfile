# Ollama Chatbot - Production Dockerfile
# Multi-stage build for optimized production image

FROM python:3.13-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install UV for fast package installation
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy requirements
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN uv venv /opt/venv
RUN . /opt/venv/bin/activate && uv pip install -r requirements.txt

# ============================================
# Production stage
# ============================================
FROM python:3.13-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application files
COPY apps/ ./apps/
COPY scripts/ ./scripts/
COPY README.md CHANGELOG.md CONTRIBUTING.md ./
COPY docs/ ./docs/

# Create logs directory
RUN mkdir -p logs

# Set permissions
RUN chmod +x scripts/*.sh

# Expose ports
EXPOSE 8501 5000 11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO \
    OLLAMA_HOST=0.0.0.0

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Starting Ollama server..."\n\
ollama serve &\n\
OLLAMA_PID=$!\n\
sleep 10\n\
echo "Pulling default model..."\n\
ollama pull llama3.2 || echo "Model pull failed, continuing..."\n\
echo "Starting Flask API..."\n\
python apps/app_flask.py &\n\
FLASK_PID=$!\n\
echo "Starting Streamlit UI..."\n\
streamlit run apps/app_streamlit.py --server.port=8501 --server.address=0.0.0.0 &\n\
STREAMLIT_PID=$!\n\
echo "All services started"\n\
echo "Flask API: http://localhost:5000"\n\
echo "Streamlit UI: http://localhost:8501"\n\
echo "Ollama API: http://localhost:11434"\n\
wait $OLLAMA_PID $FLASK_PID $STREAMLIT_PID\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start services
CMD ["/app/start.sh"]

