#!/bin/bash

#############################################
# Ollama Chatbot - Shutdown Flask API
# This script stops only the Flask API server
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
echo -e "${BLUE}  Shutdown Flask API${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

#############################################
# Stop Flask
#############################################
echo -e "${YELLOW}Stopping Flask API...${NC}"

FLASK_PIDS=$(pgrep -f "python.*app_flask.py" 2>/dev/null || true)

if [ -z "$FLASK_PIDS" ]; then
    echo -e "${CYAN}ℹ Flask API is not running${NC}"
    echo ""
    exit 0
fi

# Display found processes
echo -e "${CYAN}Found Flask process(es):${NC}"
echo "$FLASK_PIDS" | while read -r pid; do
    echo -e "  PID: $pid"
done
echo ""

# Stop processes
echo "$FLASK_PIDS" | while read -r pid; do
    kill "$pid" 2>/dev/null || true
done

# Wait for processes to stop
sleep 1

# Verify stopped
REMAINING=$(pgrep -f "python.*app_flask.py" 2>/dev/null || true)
if [ -z "$REMAINING" ]; then
    echo -e "${GREEN}✓ Flask API stopped successfully${NC}"
else
    echo -e "${YELLOW}⚠ Some processes may still be running${NC}"
    echo -e "${YELLOW}  Trying force kill...${NC}"
    echo "$REMAINING" | while read -r pid; do
        kill -9 "$pid" 2>/dev/null || true
    done
    sleep 1
    echo -e "${GREEN}✓ Flask API force stopped${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  ✅ Flask API stopped${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}To restart Flask API:${NC}"
echo -e "  ./launch_flask.sh"
echo ""
