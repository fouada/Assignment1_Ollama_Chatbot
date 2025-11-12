#!/bin/bash

#############################################
# Integration Tests for Ollama Chatbot
# Tests all services: Ollama, Flask, Streamlit
#############################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
VENV_PATH="$PROJECT_ROOT/.venv"

# API URLs
OLLAMA_URL="http://localhost:11434"
FLASK_URL="http://localhost:5000"
STREAMLIT_URL="http://localhost:8501"

# PID tracking
FLASK_PID=""
STREAMLIT_PID=""

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Integration Tests - Ollama Chatbot${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

#############################################
# Cleanup function
#############################################
cleanup() {
    echo ""
    echo -e "${YELLOW}Cleaning up services...${NC}"

    if [ ! -z "$FLASK_PID" ]; then
        echo "  Stopping Flask (PID: $FLASK_PID)..."
        kill $FLASK_PID 2>/dev/null || true
    fi

    if [ ! -z "$STREAMLIT_PID" ]; then
        echo "  Stopping Streamlit (PID: $STREAMLIT_PID)..."
        kill $STREAMLIT_PID 2>/dev/null || true
    fi

    # Kill any remaining processes
    pkill -f "streamlit run" 2>/dev/null || true
    pkill -f "flask run" 2>/dev/null || true
    pkill -f "app_flask.py" 2>/dev/null || true

    echo -e "${GREEN}  Cleanup complete${NC}"
}

trap cleanup EXIT

#############################################
# Test 1: Ollama Server Status
#############################################
echo -e "${CYAN}[Test 1/10] Checking Ollama Server...${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

if curl -s --max-time 5 "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ PASSED: Ollama server is running${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}  ✗ FAILED: Ollama server not reachable${NC}"
    echo -e "${YELLOW}  → Expected: HTTP 200 from $OLLAMA_URL/api/tags${NC}"
    echo -e "${YELLOW}  → Fix: Run 'brew services start ollama'${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    exit 1
fi

#############################################
# Test 2: Ollama Models Available
#############################################
echo -e "${CYAN}[Test 2/10] Checking Ollama Models...${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

MODEL_COUNT=$(curl -s "$OLLAMA_URL/api/tags" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('models', [])))" 2>/dev/null || echo "0")

if [ "$MODEL_COUNT" -gt 0 ]; then
    echo -e "${GREEN}  ✓ PASSED: $MODEL_COUNT model(s) available${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}  ✗ FAILED: No models found${NC}"
    echo -e "${YELLOW}  → Expected: At least 1 model installed${NC}"
    echo -e "${YELLOW}  → Fix: Run 'ollama pull llama3.2'${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    exit 1
fi

#############################################
# Test 3: Start Flask Server
#############################################
echo -e "${CYAN}[Test 3/10] Starting Flask Server...${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

cd "$PROJECT_ROOT"
source "$VENV_PATH/bin/activate"

# Start Flask in background
export FLASK_APP=apps/app_flask.py
python3 -m flask run --port 5000 > /dev/null 2>&1 &
FLASK_PID=$!

# Wait for Flask to start
sleep 3

if curl -s "$FLASK_URL/api" > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ PASSED: Flask server started (PID: $FLASK_PID)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}  ✗ FAILED: Flask server did not start${NC}"
    echo -e "${YELLOW}  → Expected: HTTP 200 from $FLASK_URL/api${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    exit 1
fi

#############################################
# Test 4: Flask API Info Endpoint
#############################################
echo -e "${CYAN}[Test 4/10] Testing Flask API Info...${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

API_RESPONSE=$(curl -s "$FLASK_URL/api")
API_NAME=$(echo "$API_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('name', ''))" 2>/dev/null || echo "")

if [ "$API_NAME" = "Ollama Flask REST API" ]; then
    echo -e "${GREEN}  ✓ PASSED: API info endpoint works${NC}"
    echo -e "  → Response: $API_NAME (version 1.0.0)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}  ✗ FAILED: API info incorrect${NC}"
    echo -e "${YELLOW}  → Expected: 'Ollama Flask REST API'${NC}"
    echo -e "${YELLOW}  → Received: '$API_NAME'${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

#############################################
# Test 5: Flask Health Check
#############################################
echo -e "${CYAN}[Test 5/10] Testing Flask Health Check...${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

HEALTH_RESPONSE=$(curl -s "$FLASK_URL/health")
HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null || echo "")

if [ "$HEALTH_STATUS" = "healthy" ]; then
    MODELS_AVAIL=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('models_available', 0))" 2>/dev/null || echo "0")
    echo -e "${GREEN}  ✓ PASSED: Health check successful${NC}"
    echo -e "  → Status: healthy, Models: $MODELS_AVAIL${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}  ✗ FAILED: Health check failed${NC}"
    echo -e "${YELLOW}  → Expected: status='healthy'${NC}"
    echo -e "${YELLOW}  → Received: status='$HEALTH_STATUS'${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

#############################################
# Test 6: Flask Models Endpoint
#############################################
echo -e "${CYAN}[Test 6/10] Testing Flask Models Endpoint...${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

MODELS_RESPONSE=$(curl -s "$FLASK_URL/models")
MODEL_COUNT_API=$(echo "$MODELS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null || echo "0")

if [ "$MODEL_COUNT_API" -gt 0 ]; then
    echo -e "${GREEN}  ✓ PASSED: Models endpoint works${NC}"
    echo -e "  → Found: $MODEL_COUNT_API model(s)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}  ✗ FAILED: Models endpoint returned 0 models${NC}"
    echo -e "${YELLOW}  → Expected: count > 0${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

#############################################
# Test 7: Flask Chat Endpoint (Non-Streaming)
#############################################
echo -e "${CYAN}[Test 7/10] Testing Flask Chat (Non-Streaming)...${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

CHAT_RESPONSE=$(curl -s -X POST "$FLASK_URL/chat" \
    -H "Content-Type: application/json" \
    -d '{
        "message": "Say hello in 3 words",
        "model": "llama3.2",
        "stream": false,
        "temperature": 0.7
    }')

CHAT_REPLY=$(echo "$CHAT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('response', '')[:50])" 2>/dev/null || echo "")

if [ ! -z "$CHAT_REPLY" ]; then
    echo -e "${GREEN}  ✓ PASSED: Chat endpoint works${NC}"
    echo -e "  → AI Response: \"$CHAT_REPLY...\"${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}  ✗ FAILED: Chat endpoint returned no response${NC}"
    echo -e "${YELLOW}  → Expected: Non-empty response field${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

#############################################
# Test 8: Flask Generate Endpoint
#############################################
echo -e "${CYAN}[Test 8/10] Testing Flask Generate Endpoint...${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

GENERATE_RESPONSE=$(curl -s -X POST "$FLASK_URL/generate" \
    -H "Content-Type: application/json" \
    -d '{
        "prompt": "1+1=",
        "model": "llama3.2"
    }')

GENERATE_REPLY=$(echo "$GENERATE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('response', '')[:30])" 2>/dev/null || echo "")

if [ ! -z "$GENERATE_REPLY" ]; then
    echo -e "${GREEN}  ✓ PASSED: Generate endpoint works${NC}"
    echo -e "  → Generated: \"$GENERATE_REPLY...\"${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}  ✗ FAILED: Generate endpoint returned no response${NC}"
    echo -e "${YELLOW}  → Expected: Non-empty response field${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

#############################################
# Test 9: Start Streamlit Server
#############################################
echo -e "${CYAN}[Test 9/10] Starting Streamlit Server...${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

streamlit run apps/app_streamlit.py --server.port 8501 --server.headless true > /dev/null 2>&1 &
STREAMLIT_PID=$!

# Wait for Streamlit to start
sleep 5

if curl -s "$STREAMLIT_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ PASSED: Streamlit server started (PID: $STREAMLIT_PID)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}  ✗ FAILED: Streamlit server did not start${NC}"
    echo -e "${YELLOW}  → Expected: HTTP 200 from $STREAMLIT_URL${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

#############################################
# Test 10: Streamlit Server Accessible
#############################################
echo -e "${CYAN}[Test 10/10] Testing Streamlit Accessibility...${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$STREAMLIT_URL")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}  ✓ PASSED: Streamlit UI is accessible${NC}"
    echo -e "  → URL: $STREAMLIT_URL (HTTP $HTTP_CODE)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}  ✗ FAILED: Streamlit not accessible${NC}"
    echo -e "${YELLOW}  → Expected: HTTP 200${NC}"
    echo -e "${YELLOW}  → Received: HTTP $HTTP_CODE${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

#############################################
# Test Summary
#############################################
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "  Total Tests: ${TOTAL_TESTS}"
echo -e "${GREEN}  Passed: ${TESTS_PASSED}${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}  Failed: ${TESTS_FAILED}${NC}"
fi
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ✅ ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Services Running:"
    echo "  • Ollama:    $OLLAMA_URL"
    echo "  • Flask API: $FLASK_URL"
    echo "  • Streamlit: $STREAMLIT_URL"
    echo ""
    echo "Press Ctrl+C to stop all services"
    echo ""

    # Keep services running
    wait
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  ❌ SOME TESTS FAILED${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
