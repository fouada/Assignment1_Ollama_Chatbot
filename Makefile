.PHONY: help install install-dev test test-unit test-integration test-quality coverage clean lint format run-flask run-streamlit docker-build docker-up docker-down docs

# Default target
help:
	@echo "🚀 Ollama Chatbot - Makefile Commands"
	@echo ""
	@echo "📦 Installation:"
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-unit        Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo "  make test-quality     Run quality compliance tests"
	@echo "  make coverage         Generate coverage report"
	@echo ""
	@echo "🔍 Code Quality:"
	@echo "  make lint             Run linters"
	@echo "  make format           Format code with black"
	@echo ""
	@echo "🚀 Running:"
	@echo "  make run-flask        Start Flask API server"
	@echo "  make run-streamlit    Start Streamlit UI"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-build     Build Docker images"
	@echo "  make docker-up        Start Docker containers"
	@echo "  make docker-down      Stop Docker containers"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean            Clean build artifacts"
	@echo "  make docs             Generate documentation"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,test]"
	pip install -r requirements-dev.txt

# Testing
test:
	pytest tests/ -v --cov=src/ollama_chatbot --cov-report=html --cov-report=term

test-unit:
	pytest tests/unit/ -v --cov=src/ollama_chatbot --cov-report=term

test-integration:
	pytest tests/integration/ -v

test-quality:
	pytest tests/quality/ -v

coverage:
	pytest tests/ --cov=src/ollama_chatbot --cov-report=html --cov-report=term
	@echo "📊 Coverage report generated in htmlcov/index.html"
	@command -v open >/dev/null 2>&1 && open htmlcov/index.html || echo "Open htmlcov/index.html in your browser"

# Code Quality
lint:
	@echo "🔍 Running flake8..."
	-flake8 src/ tests/ --max-line-length=120
	@echo "🔍 Running mypy..."
	-mypy src/ --ignore-missing-imports

format:
	@echo "✨ Formatting code with black..."
	black src/ tests/ examples/ --line-length=120
	@echo "✨ Sorting imports with isort..."
	isort src/ tests/ examples/

# Running Applications
run-flask:
	@echo "🚀 Starting Flask API server..."
	python -m ollama_chatbot.api.flask_app

run-streamlit:
	@echo "🚀 Starting Streamlit UI..."
	streamlit run src/ollama_chatbot/ui/streamlit_app.py

# Docker
docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose -f deployment/docker/docker-compose.yml build

docker-up:
	@echo "🐳 Starting Docker containers..."
	docker-compose -f deployment/docker/docker-compose.yml up -d
	@echo "✅ Containers started!"
	@echo "   Streamlit UI: http://localhost:8501"
	@echo "   Flask API: http://localhost:5000"

docker-down:
	@echo "🐳 Stopping Docker containers..."
	docker-compose -f deployment/docker/docker-compose.yml down

# Maintenance
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✅ Cleaned!"

docs:
	@echo "📚 Documentation available in docs/ directory"
	@echo "   Main: README.md"
	@echo "   Index: docs/index.md"
	@echo "   Navigation: NAVIGATION_GUIDE.md"

