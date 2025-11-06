#!/bin/bash

#############################################
# Streamlit Ollama Chatbot Launcher
# This script handles environment setup, validation, and launching
#############################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="Ollama Chatbot (Streamlit)"
VENV_PATH="../.venv"
APP_FILE="../apps/app_streamlit.py"
PORT=8501  # Default Streamlit port
LOG_LEVEL="INFO"  # Options: DEBUG, INFO, WARNING, ERROR
OLLAMA_API_URL="http://localhost:11434"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  $APP_NAME Launcher${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

#############################################
# 1. Check Ollama Server Status
#############################################
echo -e "${YELLOW}[1/5] Checking Ollama server...${NC}"
if curl -s --max-time 5 "$OLLAMA_API_URL/api/tags" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama server is running${NC}"
else
    echo -e "${RED}✗ Ollama server is NOT running!${NC}"
    echo ""
    echo "Please start Ollama first:"
    echo "  brew services start ollama"
    echo "  OR"
    echo "  ollama serve"
    echo ""
    exit 1
fi

#############################################
# 2. Activate Virtual Environment
#############################################
echo -e "${YELLOW}[2/5] Activating virtual environment...${NC}"
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}✗ Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    uv venv
fi

source "$VENV_PATH/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${NC}"

#############################################
# 3. Verify Required Packages
#############################################
echo -e "${YELLOW}[3/5] Verifying packages...${NC}"

REQUIRED_PACKAGES=("streamlit" "requests" "ollama")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}  ✓ $package${NC}"
    else
        echo -e "${RED}  ✗ $package (missing)${NC}"
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
    echo -e "${RED}Missing packages detected!${NC}"
    echo "Installing missing packages..."
    uv pip install -r ../requirements.txt
fi

echo -e "${GREEN}✓ All packages verified${NC}"

#############################################
# 4. Set Environment Variables
#############################################
echo -e "${YELLOW}[4/5] Setting environment variables...${NC}"
export STREAMLIT_SERVER_PORT=$PORT
export STREAMLIT_LOGGER_LEVEL=$LOG_LEVEL
export OLLAMA_API_URL=$OLLAMA_API_URL

echo -e "${GREEN}  ✓ Port: $PORT${NC}"
echo -e "${GREEN}  ✓ Log Level: $LOG_LEVEL${NC}"
echo -e "${GREEN}  ✓ Ollama API: $OLLAMA_API_URL${NC}"

#############################################
# 5. Launch Streamlit App
#############################################
echo -e "${YELLOW}[5/5] Launching Streamlit application...${NC}"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  $APP_NAME is starting...${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "  🌐 URL: ${BLUE}http://localhost:$PORT${NC}"
echo -e "  📝 Log Level: $LOG_LEVEL"
echo -e "  🤖 Ollama: Connected"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Launch Streamlit
streamlit run "$APP_FILE" \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --logger.level=$LOG_LEVEL \
    --browser.gatherUsageStats=false

# Cleanup on exit
deactivate
