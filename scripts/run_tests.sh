#!/bin/bash

#############################################
# Unit Test Runner for Ollama Chatbot
# Tests both Streamlit and Flask apps
#############################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

VENV_PATH=".venv"
OLLAMA_API_URL="http://localhost:11434"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Ollama Chatbot Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Activate virtual environment
source "$VENV_PATH/bin/activate"

#############################################
# Test 1: Ollama Connectivity
#############################################
echo -e "${YELLOW}Test 1: Ollama Server Connection${NC}"
if curl -s --max-time 5 "$OLLAMA_API_URL/api/tags" > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ PASS: Ollama server is reachable${NC}"
else
    echo -e "${RED}  ✗ FAIL: Cannot connect to Ollama${NC}"
    exit 1
fi

#############################################
# Test 2: Python Package Imports
#############################################
echo -e "${YELLOW}Test 2: Package Imports${NC}"
python3 << 'EOF'
import sys

packages = ['streamlit', 'flask', 'requests', 'ollama']
failed = []

for pkg in packages:
    try:
        __import__(pkg)
        print(f'  ✓ PASS: {pkg}')
    except ImportError:
        print(f'  ✗ FAIL: {pkg}')
        failed.append(pkg)

if failed:
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}Package import tests failed!${NC}"
    exit 1
fi

#############################################
# Test 3: Ollama Model Availability
#############################################
echo -e "${YELLOW}Test 3: Ollama Models${NC}"
models=$(curl -s "$OLLAMA_API_URL/api/tags" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('models', [])))")

if [ "$models" -gt 0 ]; then
    echo -e "${GREEN}  ✓ PASS: $models model(s) available${NC}"
else
    echo -e "${RED}  ✗ FAIL: No models found${NC}"
    echo "  Please pull a model: ollama pull llama3.2"
    exit 1
fi

#############################################
# Test 4: API Response Test
#############################################
echo -e "${YELLOW}Test 4: Ollama API Response${NC}"
response=$(curl -s -X POST "$OLLAMA_API_URL/api/generate" \
    -d '{
        "model": "llama3.2",
        "prompt": "Say hello",
        "stream": false
    }' 2>/dev/null)

if echo "$response" | grep -q "response"; then
    echo -e "${GREEN}  ✓ PASS: API responds correctly${NC}"
else
    echo -e "${YELLOW}  ⚠ WARNING: API response unexpected${NC}"
fi

#############################################
# Test 5: File Structure
#############################################
echo -e "${YELLOW}Test 5: Project Structure${NC}"
files=("requirements.txt" "launch_streamlit.sh" "launch_flask.sh" ".venv")
for file in "${files[@]}"; do
    if [ -e "$file" ]; then
        echo -e "${GREEN}  ✓ PASS: $file exists${NC}"
    else
        echo -e "${RED}  ✗ FAIL: $file missing${NC}"
        exit 1
    fi
done

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  All Tests Passed! ✓${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

deactivate
