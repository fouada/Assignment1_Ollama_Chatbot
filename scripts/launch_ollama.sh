#!/bin/bash

#############################################
# Ollama Server Launcher
# This script starts the Ollama server and verifies it's running
#############################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
OLLAMA_API_URL="http://localhost:11434"
MAX_WAIT=30  # Maximum seconds to wait for Ollama to start

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Ollama Server Launcher${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

#############################################
# 1. Check if Ollama is already running
#############################################
echo -e "${YELLOW}[1/4] Checking Ollama status...${NC}"

if curl -s --max-time 2 "$OLLAMA_API_URL/api/tags" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama is already running${NC}"
    echo ""
    echo -e "${CYAN}Server URL: $OLLAMA_API_URL${NC}"
    echo ""

    # Show available models
    echo -e "${YELLOW}Available models:${NC}"
    curl -s "$OLLAMA_API_URL/api/tags" | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | while read -r model; do
        echo -e "  • $model"
    done
    echo ""
    exit 0
fi

echo -e "${CYAN}  ℹ Ollama is not running${NC}"
echo ""

#############################################
# 2. Check if Ollama is installed
#############################################
echo -e "${YELLOW}[2/4] Verifying Ollama installation...${NC}"

if ! command -v ollama &> /dev/null; then
    echo -e "${RED}✗ Ollama is not installed!${NC}"
    echo ""
    echo -e "${YELLOW}Install Ollama:${NC}"
    echo -e "  brew install ollama"
    echo ""
    exit 1
fi

OLLAMA_VERSION=$(ollama --version 2>/dev/null | head -1 || echo "unknown")
echo -e "${GREEN}✓ Ollama installed: $OLLAMA_VERSION${NC}"
echo ""

#############################################
# 3. Start Ollama Server
#############################################
echo -e "${YELLOW}[3/4] Starting Ollama server...${NC}"

# Try to start as a service first
if command -v brew &> /dev/null; then
    echo -e "${CYAN}  Starting as macOS service...${NC}"
    brew services start ollama > /dev/null 2>&1
    sleep 3
else
    # Start manually in background
    echo -e "${CYAN}  Starting in background...${NC}"
    nohup ollama serve > /dev/null 2>&1 &
    sleep 3
fi

echo -e "${GREEN}✓ Ollama start command executed${NC}"
echo ""

#############################################
# 4. Verify Ollama is responding
#############################################
echo -e "${YELLOW}[4/4] Verifying server response...${NC}"

WAIT_TIME=0
while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    if curl -s --max-time 2 "$OLLAMA_API_URL/api/tags" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama server is responding${NC}"
        echo ""
        break
    fi

    echo -e "${CYAN}  Waiting for server... (${WAIT_TIME}s)${NC}"
    sleep 2
    WAIT_TIME=$((WAIT_TIME + 2))
done

if [ $WAIT_TIME -ge $MAX_WAIT ]; then
    echo -e "${RED}✗ Ollama server failed to start within ${MAX_WAIT} seconds${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo -e "  1. Check logs: tail -f ~/Library/Logs/Homebrew/ollama/stdout"
    echo -e "  2. Try manual start: ollama serve"
    echo -e "  3. Check port 11434: lsof -i :11434"
    echo ""
    exit 1
fi

#############################################
# Success Summary
#############################################
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  ✅ Ollama Server Started Successfully!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${CYAN}Server Information:${NC}"
echo -e "  • URL: $OLLAMA_API_URL"
echo -e "  • Status: Running"
echo -e "  • Version: $OLLAMA_VERSION"
echo ""

# List available models
echo -e "${CYAN}Available Models:${NC}"
MODEL_COUNT=$(curl -s "$OLLAMA_API_URL/api/tags" | grep -o '"name":"[^"]*"' | wc -l | tr -d ' ')

if [ "$MODEL_COUNT" -eq 0 ]; then
    echo -e "  ${YELLOW}⚠ No models installed${NC}"
    echo ""
    echo -e "${YELLOW}Pull a model to get started:${NC}"
    echo -e "  ollama pull llama3.2"
    echo -e "  ollama pull phi3"
    echo -e "  ollama pull mistral"
else
    curl -s "$OLLAMA_API_URL/api/tags" | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | while read -r model; do
        echo -e "  • $model"
    done
fi

echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  Launch Streamlit: ./launch_streamlit.sh"
echo -e "  Launch Flask API: ./launch_flask.sh"
echo -e "  Stop Ollama: ./shutdown_all.sh"
echo ""
