# Screenshot Capture Guide

This guide provides **step-by-step instructions** for capturing all recommended screenshots to showcase the Ollama Chatbot functionality.

---

## 📋 Prerequisites

Before starting, ensure:
- ✅ Ollama is running (`brew services start ollama`)
- ✅ At least one model installed (`ollama pull llama3.2`)
- ✅ Virtual environment activated (`source .venv/bin/activate`)
- ✅ Dependencies installed (see below)

### Installing Dependencies

**For UI, API, and Feature screenshots:**
```bash
uv pip install -r requirements.txt
```
This installs runtime dependencies (Flask, Streamlit, Ollama client).

**For Testing & Coverage screenshots (Categories 6 & 9):**
```bash
uv pip install -r requirements-dev.txt
```
This installs testing tools (pytest, coverage, etc.).

**To install everything (recommended for complete guide):**
```bash
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt
```

### Quick Reference: Which Requirements File?

| Screenshot Category | Required File | Reason |
|-------------------|--------------|---------|
| UI (Flask/Streamlit) | `requirements.txt` | Runtime: Flask, Streamlit |
| Model Features | `requirements.txt` | Runtime: Ollama client |
| API Testing | `requirements.txt` | Runtime: Flask API |
| **Test Coverage** | `requirements-dev.txt` | **pytest, coverage tools** |
| Error Handling | `requirements.txt` | Runtime: Apps |
| Privacy Features | `requirements.txt` | Runtime: Apps |
| **System Scripts (tests)** | `requirements-dev.txt` | **pytest tools** |
| Scripts (launch) | `requirements.txt` | Runtime: Apps |
| Clear Chat History | `requirements.txt` | Runtime: Apps |
| CI/CD | N/A | GitHub Actions (cloud) |

**TL;DR:**
- 🟢 Most screenshots: `requirements.txt` only
- 🔴 Testing screenshots (Categories 6 & 9B): Need `requirements-dev.txt`
- 🟡 Complete guide: Install both

---

## 🎯 Required Screenshots (Already Done ✅)

You already have these screenshots:

1. ✅ `docs/screenshots/ui/flask/flask_UI_1_With_Model_Options.png`
2. ✅ `docs/screenshots/ui/flask/flask_UI_2_with_Model_chat.png`
3. ✅ `docs/screenshots/ui/streamlit/Streamlit_UI_1_With_Model_Options.png`
4. ✅ `docs/screenshots/ui/streamlit/Streamlit_UI_2_With_Model_Chat.png`

---

## 📸 Additional Recommended Screenshots

### Category 1: Model Comparison

#### Screenshot 1A: llama3.2 Response
**Location:** `docs/screenshots/features/model-comparison-llama32.png`

**Steps:**
1. Start Streamlit:
   ```bash
   cd scripts
   ./launch_streamlit.sh
   ```
2. Open browser: `http://localhost:8501`
3. In sidebar, select model: **llama3.2**
4. Set temperature: **0.7**
5. Type message: "Explain quantum computing in simple terms"
6. Press Enter and wait for complete response
7. Take screenshot (Cmd+Shift+4 on Mac, Windows+Shift+S on Windows)
8. Save as: `model-comparison-llama32.png`

#### Screenshot 1B: mistral Response
**Location:** `docs/screenshots/features/model-comparison-mistral.png`

**Steps:**
1. Keep Streamlit running
2. In sidebar, select model: **mistral**
3. Clear previous conversation (click "🗑️ Clear Chat History" button in sidebar)
4. Type same message: "Explain quantum computing in simple terms"
5. Wait for complete response
6. Take screenshot
7. Save as: `model-comparison-mistral.png`

#### Screenshot 1C: codellama Code Generation
**Location:** `docs/screenshots/features/code-generation-codellama.png`

**Steps:**
1. Select model: **codellama**
2. Clear conversation (click "🗑️ Clear Chat History" button)
3. Type message: "Write a Python function to calculate factorial recursively with comments"
4. Wait for complete code response
5. Take screenshot showing the generated code
6. Save as: `code-generation-codellama.png`

---

### Category 2: Temperature Control

#### Screenshot 2A: Low Temperature (Deterministic)
**Location:** `docs/screenshots/features/temperature-low-focused.png`

**Steps:**
1. Keep Streamlit running
2. Select model: **llama3.2**
3. Set temperature slider to: **0.2** (far left - "Focused")
4. Clear conversation
5. Type message: "What is 2+2?"
6. Take screenshot showing:
   - Temperature slider at 0.2
   - The question
   - The response (should be very direct and consistent)
7. Save as: `temperature-low-focused.png`

#### Screenshot 2B: High Temperature (Creative)
**Location:** `docs/screenshots/features/temperature-high-creative.png`

**Steps:**
1. Set temperature slider to: **1.8** (far right - "Creative")
2. Clear conversation
3. Type same message: "What is 2+2?"
4. Take screenshot showing:
   - Temperature slider at 1.8
   - The question
   - The response (may be more elaborate/creative)
5. Save as: `temperature-high-creative.png`

---

### Category 3: Streaming Response (Real-Time)

#### Screenshot 3: Response Being Generated
**Location:** `docs/screenshots/features/streaming-response-in-progress.png`

**Steps:**
1. Set temperature to 0.7
2. Select llama3.2
3. Type a longer question: "Write a detailed explanation of how neural networks learn through backpropagation"
4. Press Enter
5. **QUICKLY** take screenshot while text is being generated (you'll see partial response)
6. Capture the moment when response is partially written
7. Save as: `streaming-response-in-progress.png`

**Tip:** If you miss it, just ask another long question and be ready to screenshot immediately

---

### Category 4: Error Handling

#### Screenshot 4A: Ollama Disconnected Error
**Location:** `docs/screenshots/error-handling/ollama-disconnected-error.png`

**Steps:**
1. Keep Streamlit UI open in browser
2. Open new terminal and stop Ollama:
   ```bash
   brew services stop ollama
   # OR if running manually, press Ctrl+C in Ollama terminal
   ```
3. Go back to Streamlit browser
4. Try to send a message: "Hello"
5. Take screenshot showing the error message
6. Save as: `ollama-disconnected-error.png`
7. Restart Ollama:
   ```bash
   brew services start ollama
   ```

#### Screenshot 4B: No Models Available Error
**Location:** `docs/screenshots/error-handling/no-models-warning.png`

**Steps:**
1. Stop Streamlit (Ctrl+C)
2. Stop Ollama./
3. Remove all models (BACKUP FIRST!):
   ```bash
   ollama list  # Note your models
   ollama rm llama3.2
   ollama rm mistral
   # Remove others if you have them
   ```
4. Start Ollama again
5. Start Streamlit again./
6. Take screenshot showing "No models found" warning
7. Save as: `no-models-warning.png`
8. Restore your models:
   ```bash
   ollama pull llama3.2
   ollama pull mistral
   ```

---

### Category 5: API Testing

#### Screenshot 5A: Health Check API
**Location:** `docs/screenshots/api/health-check-response.png`

**Steps:**
1. Make sure Ollama is running
2. Start Flask API:
   ```bash
   cd scripts
   ./launch_flask.sh
   ```
3. Open new terminal
4. Run command:
   ```bash
   curl http://localhost:5000/health | jq
   ```
5. Take screenshot showing:
   - The curl command
   - The JSON response with "healthy" status
6. Save as: `health-check-response.png`

#### Screenshot 5B: Models List API
**Location:** `docs/screenshots/api/models-list-response.png`

**Steps:**
1. Run command:
   ```bash
   curl http://localhost:5000/models | jq
   ```
2. Take screenshot showing:
   - The curl command
   - JSON array with all your models
3. Save as: `models-list-response.png`

#### Screenshot 5C: Chat API Request
**Location:** `docs/screenshots/api/chat-api-request-response.png`

**Steps:**
1. Run command:
   ```bash
   curl -X POST http://localhost:5000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "What is Python?", "model": "llama3.2", "stream": false}' | jq
   ```
2. Take screenshot showing:
   - The full curl command with parameters
   - The AI response in JSON format
3. Save as: `chat-api-request-response.png`

---

### Category 6: Test Coverage

> **⚠️ Prerequisites for Testing Screenshots:**
> Make sure you have dev dependencies installed:
> ```bash
> uv pip install -r requirements-dev.txt
> ```

#### Screenshot 6A: Running Tests
**Location:** `docs/screenshots/testing/pytest-running-all-tests.png`

**Steps:**
1. Stop Flask and Streamlit if running
2. Make sure Ollama is running
3. Ensure dev dependencies installed (`uv pip install -r requirements-dev.txt`)
4. Run tests:
   ```bash
   cd /path/to/Assignment1_Ollama_Chatbot
   source .venv/bin/activate
   pytest --cov=apps --cov-report=term-missing -v
   ```
5. Take screenshot showing:
   - All tests running
   - Tests passing (green PASSED)
   - Final summary: "87 passed"
   - Coverage: 96%
6. Save as: `pytest-running-all-tests.png`

**Tip:** You may need to take 2 screenshots if terminal output is long

#### Screenshot 6B: Coverage HTML Report
**Location:** `docs/screenshots/testing/coverage-html-report.png`

**Steps:**
1. Generate HTML coverage report:
   ```bash
   pytest --cov=apps --cov-report=html
   ```
2. Open in browser:
   ```bash
   open htmlcov/index.html
   ```
3. Take screenshot showing:
   - Coverage percentages for each file
   - 99% for app_flask.py
   - 89% for app_streamlit.py
   - 96% total
4. Save as: `coverage-html-report.png`

#### Screenshot 6C: Line-by-Line Coverage
**Location:** `docs/screenshots/testing/coverage-line-by-line.png`

**Steps:**
1. In coverage HTML report, click on `app_flask.py`
2. Take screenshot showing:
   - Green highlighted lines (tested)
   - Red highlighted lines (not tested, if any)
   - Line numbers
3. Save as: `coverage-line-by-line.png`

---

### Category 7: Long Conversation

#### Screenshot 7: Chat History
**Location:** `docs/screenshots/features/conversation-history-long.png`
**Alternative:** Use 2 screenshots if needed (see below)

**Steps:**
1. Start Streamlit
2. Have a conversation with 5-6 exchanges:
   - You: "What is machine learning?"
   - AI: [response]
   - You: "How does it differ from deep learning?"
   - AI: [response]
   - You: "Can you give an example?"
   - AI: [response]
   - You: "What are common applications?"
   - AI: [response]
3. Take screenshot showing entire conversation thread
4. Make sure session statistics in sidebar are visible
5. **NEW: Make sure the sidebar conversation history panel is visible**
6. Save as: `conversation-history-long.png`

**💡 Pro Tip: Using Multiple Screenshots for Long Conversations**

If your conversation is too long to fit in one screenshot, **you can and should take 2 screenshots**:

**Screenshot 7A - Top Portion:**
- Capture the beginning of the conversation + sidebar with history panel
- Save as: `docs/screenshots/features/conversation-history-long-part1.png`

**Screenshot 7B - Bottom Portion:**
- Scroll down and capture the rest of the conversation
- Save as: `docs/screenshots/features/conversation-history-long-part2.png`

**This is perfectly acceptable and demonstrates:**
- ✅ Complete conversation flow
- ✅ Scrollable sidebar history panel
- ✅ Full context visibility
- ✅ Attention to detail

---

### Category 8: Privacy Features

#### Screenshot 8A: Privacy Indicators
**Location:** `docs/screenshots/features/privacy-indicators.png`

**Steps:**
1. In Streamlit, take screenshot focusing on sidebar
2. Ensure these elements are visible:
   - Model selection dropdown
   - Temperature slider
   - Connection status (green checkmark)
   - Privacy features text:
     - "🔒 100% Private"
     - "💰 Cost-Free"
     - "🛡️ No Data Leaves Machine"
3. Save as: `privacy-indicators.png`

#### Screenshot 8B: Offline Mode (Optional)
**Location:** `docs/screenshots/features/offline-mode-working.png`

**Steps:**
1. Disconnect from WiFi
2. Open Network Preferences showing "Disconnected"
3. Go to Streamlit (should still work)
4. Send a message and get response
5. Take screenshot showing:
   - Network status: Offline
   - Chat still working
6. Save as: `offline-mode-working.png`
7. Reconnect WiFi

---

### Category 9: System Scripts

#### Screenshot 9A: Launch Script
**Location:** `docs/screenshots/scripts/launch-streamlit-script.png`

**Steps:**
1. Stop Streamlit if running
2. Run launch script:
   ```bash
   cd scripts
   ./launch_streamlit.sh
   ```
3. Take screenshot showing:
   - The validation steps
   - "Checking Ollama server... ✓"
   - "Activating virtual environment... ✓"
   - "Verifying packages... ✓"
   - "Launching Streamlit..."
4. Save as: `launch-streamlit-script.png`

#### Screenshot 9B: Test Script
**Location:** `docs/screenshots/scripts/run-tests-script.png`

> **⚠️ Note:** Requires dev dependencies: `uv pip install -r requirements-dev.txt`

**Steps:**
1. Ensure dev dependencies installed
2. Run test script:
   ```bash
   cd scripts
   ./run_tests.sh
   ```
3. Take screenshot showing:
   - All validation checks passing
   - Test summary
   - "✅ All tests passed!"
4. Save as: `run-tests-script.png`

---

### Category 10: Multiple Windows Side-by-Side

#### Screenshot 10: Flask + Streamlit Side-by-Side
**Location:** `docs/screenshots/features/dual-interface-side-by-side.png`

**Steps:**
1. Start both Flask and Streamlit
2. Open two browser windows/tabs
3. Arrange windows side-by-side:
   - Left: `http://localhost:8501` (Streamlit)
   - Right: `http://localhost:5000` (Flask API docs)
4. Take screenshot showing both interfaces
5. Save as: `dual-interface-side-by-side.png`

---

### Category 11: Clear Chat History Feature

#### Screenshot 11A: Before Clear
**Location:** `docs/screenshots/features/before-clear-conversation.png`

**Steps:**
1. Have 2-3 messages in conversation
2. Take screenshot showing conversation
3. Save as: `before-clear-conversation.png`

#### Screenshot 11B: After Clear
**Location:** `docs/screenshots/features/after-clear-conversation.png`

**Steps:**
1. Click "🗑️ Clear Chat History" button in sidebar
2. Take screenshot showing:
   - Empty chat area
   - Welcome message back
   - Reset session statistics (Messages count back to 0)
3. Save as: `after-clear-conversation.png`

---

### Category 12: CI/CD Pipeline

#### Screenshot 12A: GitHub Actions Workflow Overview
**Location:** `docs/screenshots/ci-cd/github-actions-workflows.png`

**Steps:**
1. Go to GitHub repository
2. Navigate to **Actions** tab
3. Take screenshot showing:
   - List of workflow runs
   - Status indicators (✓ passing)
   - Workflow names (e.g., "Python Tests", "Docker Build")
   - Recent run history
4. Save to: `docs/screenshots/ci-cd/github-actions-workflows.png`

**What to capture:**
- URL showing `.../actions`
- Workflow list with status badges
- Recent run timestamps

---

#### Screenshot 12B: Workflow Run Details - Tests Passing
**Location:** `docs/screenshots/ci-cd/workflow-tests-passing.png`

**Steps:**
1. Click on a successful workflow run (green checkmark)
2. Take screenshot showing:
   - All jobs completed successfully
   - Job names (Setup, Lint, Test, Build)
   - Execution times
   - Green checkmarks for each step
   - Total workflow duration
3. Save to: `docs/screenshots/ci-cd/workflow-tests-passing.png`

**What to capture:**
- Full workflow summary
- All jobs expanded showing steps
- Green success indicators

---

#### Screenshot 12C: Test Job Logs - Pytest Output
**Location:** `docs/screenshots/ci-cd/ci-pytest-output.png`

**Steps:**
1. In workflow run details, click on **Test** job
2. Expand the "Run tests" step
3. Take screenshot showing:
   - Pytest output with all tests passing
   - Test count (e.g., "87 passed")
   - Coverage percentage (96%)
   - Execution time
4. Save to: `docs/screenshots/ci-cd/ci-pytest-output.png`

**What to capture:**
- Terminal output from pytest
- Test summary line
- Coverage report

---

#### Screenshot 12D: Coverage Report in CI
**Location:** `docs/screenshots/ci-cd/ci-coverage-report.png`

**Steps:**
1. If using coverage reporting service (Codecov, Coveralls)
   - Go to coverage dashboard
   - Take screenshot showing coverage percentages by file
2. OR if using artifacts:
   - Download coverage HTML artifact
   - Open `htmlcov/index.html`
   - Take screenshot of coverage summary
3. Save to: `docs/screenshots/ci-cd/ci-coverage-report.png`

**What to capture:**
- Overall coverage: 96%
- Per-file breakdown
- Coverage trends (if available)

---

#### Screenshot 12E: Docker Build Success
**Location:** `docs/screenshots/ci-cd/docker-build-success.png`

**Steps:**
1. In workflow run, expand **Build Docker Image** job
2. Take screenshot showing:
   - Docker build steps
   - Layer building progress
   - "Successfully built" message
   - Image size
   - Docker tags applied
3. Save to: `docs/screenshots/ci-cd/docker-build-success.png`

**What to capture:**
- Docker build output
- Success message
- Image ID and size

---

#### Screenshot 12F: Branch Protection Rules
**Location:** `docs/screenshots/ci-cd/branch-protection-rules.png`

**Steps:**
1. Go to GitHub repository Settings
2. Navigate to **Branches** → **Branch protection rules**
3. Click on `main` branch rule
4. Take screenshot showing:
   - "Require status checks to pass before merging"
   - Required checks enabled
   - "Require branches to be up to date"
   - Any other protection rules
5. Save to: `docs/screenshots/ci-cd/branch-protection-rules.png`

**What to capture:**
- Protection rule settings
- Required status checks
- Merge requirements

---

#### Screenshot 12G: Pull Request with CI Checks
**Location:** `docs/screenshots/ci-cd/pr-with-ci-checks.png`

**Steps:**
1. Create or navigate to a Pull Request
2. Take screenshot showing:
   - PR description
   - CI checks section at bottom
   - All checks passing (green checkmarks)
   - Check details (Tests, Build, Lint)
   - "All checks have passed" message
3. Save to: `docs/screenshots/ci-cd/pr-with-ci-checks.png`

**What to capture:**
- PR interface
- Status checks panel
- Merge button state

---

#### Screenshot 12H: Failed Build (Optional - for documentation)
**Location:** `docs/screenshots/ci-cd/workflow-failed-example.png`

**Steps:**
1. Intentionally break a test OR find old failed run
2. Take screenshot showing:
   - Red X indicator
   - Failed job details
   - Error message in logs
   - Failed test name
3. Save to: `docs/screenshots/ci-cd/workflow-failed-example.png`

**What to capture:**
- Failure indicators
- Error logs
- Failed step details

**Note:** This is optional and demonstrates error detection

---

#### Screenshot 12I: Build Artifacts
**Location:** `docs/screenshots/ci-cd/build-artifacts.png`

**Steps:**
1. In workflow run details, scroll to bottom
2. Find **Artifacts** section
3. Take screenshot showing:
   - Available artifacts (e.g., "coverage-report", "test-results")
   - Artifact sizes
   - Expiration dates
   - Download buttons
4. Save to: `docs/screenshots/ci-cd/build-artifacts.png`

**What to capture:**
- Artifacts list
- File sizes
- Upload timestamps

---

#### Screenshot 12J: Deployment Pipeline (if applicable)
**Location:** `docs/screenshots/ci-cd/deployment-pipeline.png`

**Steps:**
1. If you have deployment automation:
   - Navigate to deployment workflow
   - Take screenshot showing deployment steps
   - Show successful deployment to staging/production
2. Save to: `docs/screenshots/ci-cd/deployment-pipeline.png`

**What to capture:**
- Deployment stages
- Environment names
- Deployment status

---

#### Screenshot 12K: Docker Hub / Container Registry
**Location:** `docs/screenshots/ci-cd/docker-registry.png`

**Steps:**
1. If pushing to Docker Hub or GitHub Container Registry:
   - Go to registry page
   - Take screenshot showing:
     - Repository name
     - Available tags
     - Image sizes
     - Push timestamps
     - Pull command
2. Save to: `docs/screenshots/ci-cd/docker-registry.png`

**What to capture:**
- Registry interface
- Image tags and versions
- Repository details

---

#### Screenshot 12L: GitHub Actions Configuration File
**Location:** `docs/screenshots/ci-cd/workflow-yaml-config.png`

**Steps:**
1. Open `.github/workflows/main.yml` (or your workflow file)
2. Take screenshot showing:
   - YAML configuration
   - Workflow triggers (on push, pull_request)
   - Jobs defined (test, build, deploy)
   - Steps in each job
3. Save to: `docs/screenshots/ci-cd/workflow-yaml-config.png`

**What to capture:**
- Workflow file content
- Configuration structure
- Key settings

---

## 📁 Organizing Screenshots

### Complete Folder Structure

Create all necessary directories for screenshots:

```bash
# Main screenshot directories
mkdir -p docs/screenshots/ui/flask
mkdir -p docs/screenshots/ui/streamlit
mkdir -p docs/screenshots/features
mkdir -p docs/screenshots/api
mkdir -p docs/screenshots/testing
mkdir -p docs/screenshots/error-handling
mkdir -p docs/screenshots/scripts
mkdir -p docs/screenshots/ci-cd
```

### Screenshot Location Reference Table

Use this table as a quick reference for where to save each screenshot:

| Category | Screenshot Name | Exact Save Location |
|----------|----------------|---------------------|
| **UI - Already Done ✅** | | |
| Flask UI | flask_UI_1_With_Model_Options.png | `docs/screenshots/ui/flask/` |
| Flask UI | flask_UI_2_with_Model_chat.png | `docs/screenshots/ui/flask/` |
| Streamlit UI | Streamlit_UI_1_With_Model_Options.png | `docs/screenshots/ui/streamlit/` |
| Streamlit UI | Streamlit_UI_2_With_Model_Chat.png | `docs/screenshots/ui/streamlit/` |
| **Model Features** | | |
| Model Comparison | model-comparison-llama32.png | `docs/screenshots/features/` |
| Model Comparison | model-comparison-mistral.png | `docs/screenshots/features/` |
| Code Generation | code-generation-codellama.png | `docs/screenshots/features/` |
| Temperature Control | temperature-low-focused.png | `docs/screenshots/features/` |
| Temperature Control | temperature-high-creative.png | `docs/screenshots/features/` |
| Streaming | streaming-response-in-progress.png | `docs/screenshots/features/` |
| Conversation | conversation-history-long.png | `docs/screenshots/features/` |
| Conversation (Alt) | conversation-history-long-part1.png | `docs/screenshots/features/` |
| Conversation (Alt) | conversation-history-long-part2.png | `docs/screenshots/features/` |
| Privacy | privacy-indicators.png | `docs/screenshots/features/` |
| Privacy | offline-mode-working.png | `docs/screenshots/features/` |
| Dual Interface | dual-interface-side-by-side.png | `docs/screenshots/features/` |
| Clear Chat | before-clear-conversation.png | `docs/screenshots/features/` |
| Clear Chat | after-clear-conversation.png | `docs/screenshots/features/` |
| **API Screenshots** | | |
| API Health | health-check-response.png | `docs/screenshots/api/` |
| API Models | models-list-response.png | `docs/screenshots/api/` |
| API Chat | chat-api-request-response.png | `docs/screenshots/api/` |
| **Testing Screenshots** | | |
| Pytest | pytest-running-all-tests.png | `docs/screenshots/testing/` |
| Coverage HTML | coverage-html-report.png | `docs/screenshots/testing/` |
| Coverage Details | coverage-line-by-line.png | `docs/screenshots/testing/` |
| **Error Handling** | | |
| Errors | ollama-disconnected-error.png | `docs/screenshots/error-handling/` |
| Errors | no-models-warning.png | `docs/screenshots/error-handling/` |
| **Scripts** | | |
| Launch | launch-streamlit-script.png | `docs/screenshots/scripts/` |
| Testing | run-tests-script.png | `docs/screenshots/scripts/` |
| **CI/CD Pipeline** | | |
| GitHub Actions | github-actions-workflows.png | `docs/screenshots/ci-cd/` |
| Workflow Details | workflow-tests-passing.png | `docs/screenshots/ci-cd/` |
| CI Tests | ci-pytest-output.png | `docs/screenshots/ci-cd/` |
| CI Coverage | ci-coverage-report.png | `docs/screenshots/ci-cd/` |
| Docker Build | docker-build-success.png | `docs/screenshots/ci-cd/` |
| Branch Protection | branch-protection-rules.png | `docs/screenshots/ci-cd/` |
| Pull Request | pr-with-ci-checks.png | `docs/screenshots/ci-cd/` |
| Failed Build | workflow-failed-example.png | `docs/screenshots/ci-cd/` |
| Artifacts | build-artifacts.png | `docs/screenshots/ci-cd/` |
| Deployment | deployment-pipeline.png | `docs/screenshots/ci-cd/` |
| Registry | docker-registry.png | `docs/screenshots/ci-cd/` |
| Config File | workflow-yaml-config.png | `docs/screenshots/ci-cd/` |

### Quick Commands to Create All Directories

**macOS/Linux:**
```bash
cd /path/to/Assignment1_Ollama_Chatbot
mkdir -p docs/screenshots/{ui/{flask,streamlit},features,api,testing,error-handling,scripts,ci-cd}
```

**Windows (PowerShell):**
```powershell
cd C:\path\to\Assignment1_Ollama_Chatbot
New-Item -ItemType Directory -Force -Path "docs\screenshots\ui\flask"
New-Item -ItemType Directory -Force -Path "docs\screenshots\ui\streamlit"
New-Item -ItemType Directory -Force -Path "docs\screenshots\features"
New-Item -ItemType Directory -Force -Path "docs\screenshots\api"
New-Item -ItemType Directory -Force -Path "docs\screenshots\testing"
New-Item -ItemType Directory -Force -Path "docs\screenshots\error-handling"
New-Item -ItemType Directory -Force -Path "docs\screenshots\scripts"
New-Item -ItemType Directory -Force -Path "docs\screenshots\ci-cd"
```

### File Naming Convention

**Rules for screenshot filenames:**
1. Use lowercase with hyphens (kebab-case)
2. Be descriptive but concise
3. Include category context in name
4. Use `.png` format for best quality

**Good Examples:**
- ✅ `github-actions-workflows.png`
- ✅ `workflow-tests-passing.png`
- ✅ `model-comparison-llama32.png`

**Bad Examples:**
- ❌ `Screenshot 2024-11-09.png` (not descriptive)
- ❌ `IMG_1234.png` (meaningless)
- ❌ `CICD.png` (too vague)

---

## 🎨 Screenshot Best Practices

### Quality Tips:
1. **Resolution:** Use at least 1920x1080
2. **Clean UI:** Close unnecessary tabs/windows
3. **Full Context:** Include enough context to understand what's happening
4. **Highlight Key Elements:** Use arrows or boxes if needed (can add later)
5. **Consistent Browser:** Use same browser for all screenshots
6. **Light Theme:** Use light theme for better visibility in docs

### macOS Screenshot Commands:
- **Full Screen:** `Cmd + Shift + 3`
- **Selection:** `Cmd + Shift + 4` (then drag to select area)
- **Window:** `Cmd + Shift + 4`, then press `Spacebar`, then click window

### Windows Screenshot Commands:
- **Snipping Tool:** `Windows + Shift + S`
- **Full Screen:** `PrtScn` key

### Linux Screenshot Commands:
- **GNOME:** `PrtScn` or `Shift + PrtScn`
- **Screenshot tool:** `gnome-screenshot`

---

## ✅ Checklist

Use this checklist to track your progress:

### Already Done ✅
- [x] Flask UI with Model Options
- [x] Flask UI with Chat
- [x] Streamlit UI with Model Options
- [x] Streamlit UI with Chat

### Recommended to Add:

#### Features
- [ ] Model Comparison (llama3.2)
- [ ] Model Comparison (mistral)
- [ ] Code Generation (codellama)
- [ ] Temperature Control - Low (0.2)
- [ ] Temperature Control - High (1.8)
- [ ] Streaming Response (mid-generation)
- [ ] Conversation History (long)
- [ ] Privacy Indicators
- [ ] Offline Mode Working (optional)
- [ ] Dual Interface Side-by-Side
- [ ] Clear Chat History (before/after)

#### API Testing
- [ ] API: Health Check Response
- [ ] API: Models List
- [ ] API: Chat Request/Response

#### Testing & Coverage
- [ ] Testing: Pytest Results
- [ ] Testing: Coverage HTML Report
- [ ] Testing: Line-by-Line Coverage

#### Error Handling
- [ ] Error: Ollama Disconnected
- [ ] Error: No Models Warning

#### Scripts
- [ ] Launch Script Output
- [ ] Test Script Output

#### CI/CD Pipeline (NEW ⭐)
- [ ] GitHub Actions: Workflow Overview
- [ ] GitHub Actions: Tests Passing
- [ ] CI: Pytest Output
- [ ] CI: Coverage Report
- [ ] Docker Build Success
- [ ] Branch Protection Rules
- [ ] Pull Request with CI Checks
- [ ] Failed Build Example (optional)
- [ ] Build Artifacts
- [ ] Deployment Pipeline (if applicable)
- [ ] Docker Registry / Container Registry
- [ ] Workflow YAML Configuration

---

## 🚀 Quick Start Workflow

If you have limited time, prioritize these **Top 7 Screenshots**:

1. **CI/CD Workflow Running** (Shows automation & professional dev practices)
   - `docs/screenshots/ci-cd/github-actions-workflows.png`
2. **Test Coverage Report** (Shows professionalism & code quality)
   - `docs/screenshots/testing/coverage-html-report.png`
3. **Pull Request with CI Checks** (Shows integration & quality gates)
   - `docs/screenshots/ci-cd/pr-with-ci-checks.png`
4. **Model Comparison** (Shows multi-model capability)
   - `docs/screenshots/features/model-comparison-llama32.png`
5. **API Testing with curl** (Shows REST API works)
   - `docs/screenshots/api/chat-api-request-response.png`
6. **Docker Build Success** (Shows containerization)
   - `docs/screenshots/ci-cd/docker-build-success.png`
7. **Error Handling** (Shows robustness)
   - `docs/screenshots/error-handling/ollama-disconnected-error.png`

---

## 📸 How to Take Screenshots

### macOS Screenshot Commands

| Action | Keyboard Shortcut | Result |
|--------|------------------|--------|
| **Full Screen** | `Cmd ⌘ + Shift ⇧ + 3` | Entire screen saved to Desktop |
| **Selection Area** | `Cmd ⌘ + Shift ⇧ + 4` | Crosshair appears, drag to select area |
| **Window Capture** | `Cmd ⌘ + Shift ⇧ + 4`, then `Space` | Click window to capture (includes shadow) |
| **Screenshot Tool** | `Cmd ⌘ + Shift ⇧ + 5` | Opens screenshot toolbar with options |
| **Copy to Clipboard** | Add `Control ⌃` to any above | Screenshot copied instead of saved |

**Recommended for this project:**
- Use `Cmd ⌘ + Shift ⇧ + 4` to select specific UI areas
- Use `Cmd ⌘ + Shift ⇧ + 5` for recording or timed captures

---

### Windows Screenshot Commands

| Action | Keyboard Shortcut | Result |
|--------|------------------|--------|
| **Snipping Tool** | `Windows ⊞ + Shift ⇧ + S` | Select area to capture (RECOMMENDED) |
| **Full Screen** | `PrtScn` or `Print Screen` | Entire screen to clipboard |
| **Active Window** | `Alt + PrtScn` | Active window to clipboard |
| **Save Screenshot** | `Windows ⊞ + PrtScn` | Full screen saved to Pictures/Screenshots |
| **Game Bar** | `Windows ⊞ + G` | Opens Game Bar for recording/screenshots |

**Recommended for this project:**
- Use `Windows ⊞ + Shift ⇧ + S` (Snipping Tool) for precise captures
- After capture, screenshot is in clipboard - paste into image editor and save

**Windows Screenshot Locations:**
- Snipping Tool: Copies to clipboard (paste into Paint/save)
- `Windows ⊞ + PrtScn`: Saves to `C:\Users\YourName\Pictures\Screenshots\`

---

### Linux Screenshot Commands

| Distribution | Keyboard Shortcut | Result |
|-------------|------------------|--------|
| **GNOME/Ubuntu** | `PrtScn` or `Print Screen` | Full screen screenshot |
| **GNOME/Ubuntu** | `Shift ⇧ + PrtScn` | Select area to capture |
| **GNOME/Ubuntu** | `Alt + PrtScn` | Active window screenshot |
| **KDE Plasma** | `PrtScn` | Opens Spectacle screenshot tool |

**Command Line Tools:**
```bash
# GNOME Screenshot
gnome-screenshot              # Full screen
gnome-screenshot -w           # Window
gnome-screenshot -a           # Area selection

# Spectacle (KDE)
spectacle -f                  # Full screen
spectacle -a                  # Active window
spectacle -r                  # Rectangular region

# Scrot (universal)
scrot                         # Full screen
scrot -s                      # Selection
scrot -u                      # Current window
```

**Recommended for this project:**
- GNOME: `Shift ⇧ + PrtScn` for area selection
- KDE: `PrtScn` to open Spectacle, then choose mode
- Screenshots typically saved to `~/Pictures/` or `~/Desktop/`

---

### After Taking Screenshots

**Step 1: Locate Your Screenshot**
- **macOS**: Desktop (by default) or use `Cmd ⌘ + Shift ⇧ + 5` to choose save location
- **Windows**: Clipboard (paste to save) or `Pictures\Screenshots\`
- **Linux**: `~/Pictures/` or `~/Desktop/`

**Step 2: Rename to Proper Name**
- Don't keep default names like "Screenshot 2024-11-09 at 3.45.12 PM.png"
- Rename to descriptive name: `github-actions-workflows.png`

**Step 3: Move to Correct Location**
```bash
# Example: Move screenshot from Desktop to correct folder
mv ~/Desktop/screenshot.png docs/screenshots/ci-cd/github-actions-workflows.png
```

**Step 4: Verify Image Quality**
- Open the file to ensure text is readable
- Check resolution (should be at least 1920x1080)
- Ensure no sensitive information is visible
- Verify correct content is captured

---

## 💡 Pro Tips

1. **Take screenshots at 100% zoom** - Clearer text
2. **Use clean test data** - Professional examples
3. **Show timestamps** - Proves real execution
4. **Include terminal prompt** - Shows real commands
5. **Capture success states** - Green checkmarks, PASSED tests
6. **Document file paths** - Where each screenshot should go

---

## 📞 Need Help?

If you encounter issues:
1. Check Ollama is running: `ollama list`
2. Check ports are free: `lsof -i :5000` and `lsof -i :8501`
3. Activate venv: `source .venv/bin/activate`
4. Check logs: `tail -f logs/flask_app.log`

---

## 📊 Summary of Screenshot Categories

This guide now covers **12 comprehensive categories** of screenshots:

| # | Category | Number of Screenshots | Folder Location | Priority |
|---|----------|----------------------|-----------------|----------|
| 1 | Model Comparison | 3 | `docs/screenshots/features/` | High |
| 2 | Temperature Control | 2 | `docs/screenshots/features/` | Medium |
| 3 | Streaming Response | 1 | `docs/screenshots/features/` | Medium |
| 4 | Error Handling | 2 | `docs/screenshots/error-handling/` | High |
| 5 | API Testing | 3 | `docs/screenshots/api/` | High |
| 6 | Test Coverage | 3 | `docs/screenshots/testing/` | Critical |
| 7 | Conversation History | 1 | `docs/screenshots/features/` | Low |
| 8 | Privacy Features | 2 | `docs/screenshots/features/` | Medium |
| 9 | System Scripts | 2 | `docs/screenshots/scripts/` | Medium |
| 10 | Dual Interface | 1 | `docs/screenshots/features/` | Low |
| 11 | Clear Chat History | 2 | `docs/screenshots/features/` | Low |
| 12 | **CI/CD Pipeline** ⭐ | **12** | **`docs/screenshots/ci-cd/`** | **CRITICAL** |

### CI/CD Screenshots Added (NEW) ⭐

The following **12 CI/CD screenshots** were added to demonstrate professional development practices:

1. **GitHub Actions Workflow Overview** - Show all workflows
2. **Workflow Run Details** - Tests passing with timing
3. **Test Job Logs** - Pytest output in CI
4. **Coverage Report** - Coverage results from CI
5. **Docker Build Success** - Container build logs
6. **Branch Protection Rules** - Repository protection settings
7. **Pull Request with CI Checks** - PR status checks
8. **Failed Build Example** - Error detection (optional)
9. **Build Artifacts** - Generated artifacts
10. **Deployment Pipeline** - Deployment automation (if applicable)
11. **Docker Registry** - Container registry interface
12. **Workflow YAML Config** - Configuration file

**Why CI/CD Screenshots Matter:**
- ✅ Demonstrates professional development workflow
- ✅ Shows automated testing and quality gates
- ✅ Proves code quality through CI validation
- ✅ Demonstrates DevOps best practices
- ✅ Shows containerization and deployment automation

---

## 📂 Complete Directory Structure

After following this guide, your screenshot folder should look like:

```
docs/screenshots/
├── ui/
│   ├── flask/
│   │   ├── flask_UI_1_With_Model_Options.png ✅
│   │   └── flask_UI_2_with_Model_chat.png ✅
│   └── streamlit/
│       ├── Streamlit_UI_1_With_Model_Options.png ✅
│       └── Streamlit_UI_2_With_Model_Chat.png ✅
├── features/
│   ├── model-comparison-llama32.png
│   ├── model-comparison-mistral.png
│   ├── code-generation-codellama.png
│   ├── temperature-low-focused.png
│   ├── temperature-high-creative.png
│   ├── streaming-response-in-progress.png
│   ├── conversation-history-long.png
│   ├── conversation-history-long-part1.png (alternative to above)
│   ├── conversation-history-long-part2.png (alternative to above)
│   ├── privacy-indicators.png
│   ├── offline-mode-working.png (optional)
│   ├── dual-interface-side-by-side.png
│   ├── before-clear-conversation.png
│   └── after-clear-conversation.png
├── api/
│   ├── health-check-response.png
│   ├── models-list-response.png
│   └── chat-api-request-response.png
├── testing/
│   ├── pytest-running-all-tests.png
│   ├── coverage-html-report.png
│   └── coverage-line-by-line.png
├── error-handling/
│   ├── ollama-disconnected-error.png
│   └── no-models-warning.png
├── scripts/
│   ├── launch-streamlit-script.png
│   └── run-tests-script.png
└── ci-cd/ ⭐ NEW
    ├── github-actions-workflows.png
    ├── workflow-tests-passing.png
    ├── ci-pytest-output.png
    ├── ci-coverage-report.png
    ├── docker-build-success.png
    ├── branch-protection-rules.png
    ├── pr-with-ci-checks.png
    ├── workflow-failed-example.png (optional)
    ├── build-artifacts.png
    ├── deployment-pipeline.png (if applicable)
    ├── docker-registry.png
    └── workflow-yaml-config.png
```

**Total Screenshots:** 46 (4 already done + 42 recommended)

---

**Last Updated:** November 9, 2025

**Note:** You don't need to take ALL these screenshots. The 4 you have are already great! However, CI/CD screenshots are now HIGHLY RECOMMENDED as they demonstrate professional development practices and are often a key differentiator in project evaluation.

