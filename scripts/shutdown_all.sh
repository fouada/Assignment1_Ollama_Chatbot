#!/bin/bash

#############################################
# Ollama Chatbot - Shutdown All Services
# This script stops Streamlit, Flask, and Ollama server
#############################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Ollama Chatbot - Shutdown All${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

#############################################
# 1. Stop Streamlit
#############################################
echo -e "${YELLOW}[1/3] Stopping Streamlit...${NC}"

STREAMLIT_PIDS=$(pgrep -f "streamlit run.*app_streamlit.py" 2>/dev/null || true)

if [ -z "$STREAMLIT_PIDS" ]; then
    echo -e "${CYAN}  ℹ Streamlit is not running${NC}"
else
    echo "$STREAMLIT_PIDS" | while read -r pid; do
        kill "$pid" 2>/dev/null || true
    done
    sleep 1
    echo -e "${GREEN}✓ Streamlit stopped${NC}"
fi

#############################################
# 2. Stop Flask
#############################################
echo -e "${YELLOW}[2/3] Stopping Flask...${NC}"

FLASK_PIDS=$(pgrep -f "python.*app_flask.py" 2>/dev/null || true)

if [ -z "$FLASK_PIDS" ]; then
    echo -e "${CYAN}  ℹ Flask is not running${NC}"
else
    echo "$FLASK_PIDS" | while read -r pid; do
        kill "$pid" 2>/dev/null || true
    done
    sleep 1
    echo -e "${GREEN}✓ Flask stopped${NC}"
fi

#############################################
# 3. Stop Ollama Server
#############################################
echo -e "${YELLOW}[3/3] Stopping Ollama server...${NC}"

# Check if Ollama is running as a service
if brew services list | grep -q "ollama.*started"; then
    brew services stop ollama > /dev/null 2>&1
    sleep 2
    echo -e "${GREEN}✓ Ollama service stopped${NC}"
else
    # Check if Ollama is running as a process
    OLLAMA_PIDS=$(pgrep -f "ollama serve" 2>/dev/null || true)

    if [ -z "$OLLAMA_PIDS" ]; then
        echo -e "${CYAN}  ℹ Ollama is not running${NC}"
    else
        echo "$OLLAMA_PIDS" | while read -r pid; do
            kill "$pid" 2>/dev/null || true
        done
        sleep 2
        echo -e "${GREEN}✓ Ollama stopped${NC}"
    fi
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  ✅ All services stopped successfully!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${CYAN}Summary:${NC}"
echo -e "  • Streamlit: Stopped"
echo -e "  • Flask API: Stopped"
echo -e "  • Ollama Server: Stopped"
echo ""
echo -e "${YELLOW}To restart services:${NC}"
echo -e "  Streamlit: ./launch_streamlit.sh"
echo -e "  Flask API: ./launch_flask.sh"
echo -e "  Ollama:    brew services start ollama"
echo ""
