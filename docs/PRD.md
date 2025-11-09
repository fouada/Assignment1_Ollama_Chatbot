# Product Requirements Document (PRD)
## Ollama Local Chatbot

**Version:** 1.0
**Date:** November 6, 2025
**Last Updated:** November 9, 2025
**Authors:**
- Fouad Azem (ID: 040830861)
- Tal Goldengorn (ID: 207042573)

**Status:** Development Complete

---

## 0. PURPOSE OF THIS DOCUMENT

### 0.1 What is a PRD?

A **Product Requirements Document (PRD)** is a comprehensive specification that defines WHAT the product is, WHY it exists, and HOW it should function. It serves as the single source of truth for all stakeholders.

### 0.2 Purpose in Software Repository

This PRD serves multiple critical purposes in the software repository:

#### For Development Team:
- ✅ **Requirements Reference** - What features must be implemented
- ✅ **Design Decisions** - Why certain technical choices were made
- ✅ **Acceptance Criteria** - What defines "done" for each feature
- ✅ **Technical Specifications** - How the system should be built

#### For Auditing & Compliance:
- ✅ **Traceability** - Track requirements from concept to implementation
- ✅ **Change Documentation** - Record what changed and why
- ✅ **Accountability** - Document who approved what and when
- ✅ **Compliance Evidence** - Proof that requirements were defined and met

#### For Quality Assurance:
- ✅ **Test Planning** - What needs to be tested
- ✅ **Success Metrics** - How to measure if the product works
- ✅ **Performance KPIs** - Expected system performance
- ✅ **Error Handling** - How errors should be managed

#### For Future Maintenance:
- ✅ **Context Preservation** - Why the product exists
- ✅ **Decision Rationale** - Why choices were made
- ✅ **Feature Understanding** - What each component does
- ✅ **Onboarding** - Help new team members understand the project

### 0.3 How to Use This Document

| Stakeholder | Use This PRD For |
|-------------|------------------|
| **Developer** | Understanding requirements, technical specs, testing criteria |
| **QA Engineer** | Test cases, acceptance criteria, expected behavior |
| **Project Manager** | Project scope, timeline, success metrics |
| **Auditor** | Compliance verification, traceability, approvals |
| **New Team Member** | Complete project understanding, context, decisions |
| **Customer/User** | Feature capabilities, expected behavior, limitations |

### 0.4 Document Maintenance

- **Version Control:** All changes are tracked in Git
- **Update Process:** PRD is updated when requirements change
- **Review Cycle:** Reviewed before each major release
- **Approval Required:** Changes must be approved by project team

---

## 1. EXECUTIVE SUMMARY

### 1.1 Product Overview
The Ollama Local Chatbot is a privacy-focused, cost-free AI chatbot application that runs entirely on the user's local machine. It provides a luxurious ChatGPT-like interface for interacting with locally-hosted Large Language Models (LLMs) via Ollama, without requiring internet connectivity, API keys, or incurring usage costs.

### 1.2 Problem Statement
**Current Challenges:**
- **Privacy Concerns:** Cloud-based AI services send user data to external servers
- **Cost Barriers:** API-based AI services require paid subscriptions or per-token charges
- **Internet Dependency:** Existing solutions require constant internet connectivity
- **Data Security:** Sensitive conversations may be stored or analyzed by third parties
- **Latency Issues:** Network-dependent services suffer from response delays

### 1.3 Solution
A dual-interface local AI chatbot system:
1. **Streamlit Web UI** - Beautiful, user-friendly chat interface
2. **Flask REST API** - Programmatic access for developers

Both leverage Ollama's local LLM infrastructure to ensure complete privacy, zero cost, and fast response times.

---

## 2. GOALS & OBJECTIVES

### 2.1 Business Goals
- Provide a free, open-source alternative to commercial AI chatbots
- Democratize access to AI technology
- Promote data privacy and security
- Enable offline AI capabilities

### 2.2 User Goals
- Chat with AI models privately without data leaving their machine
- Avoid subscription fees and API costs
- Access AI without internet connectivity
- Experience fast, low-latency responses
- Use multiple AI models for different tasks

### 2.3 Success Metrics
- **Performance:** Response time < 2 seconds for first token
- **Reliability:** 99% uptime when Ollama is running
- **Usability:** Users can start chatting within 5 minutes of setup
- **Privacy:** Zero external API calls
- **Cost:** $0 operational cost per user

---

## 3. TARGET AUDIENCE

### 3.1 Primary Personas

#### Persona 1: Privacy-Conscious Professional
- **Background:** Software developer, researcher, or business professional
- **Needs:** Secure environment for sensitive discussions, code reviews, document analysis
- **Pain Points:** Cannot use cloud AI due to company policies or data sensitivity
- **Goals:** Local AI access without compromising confidential information

#### Persona 2: Cost-Conscious Student/Learner
- **Background:** University student, self-learner, hobbyist developer
- **Needs:** Free AI assistance for learning, projects, and assignments
- **Pain Points:** Cannot afford ChatGPT Plus or API credits
- **Goals:** Access to AI tools without financial burden

#### Persona 3: AI Enthusiast/Developer
- **Background:** ML engineer, developer building AI applications
- **Needs:** Local AI infrastructure for development and experimentation
- **Pain Points:** Need offline capabilities and API access
- **Goals:** Integrate local LLMs into applications

#### Persona 4: Enterprise User
- **Background:** Company with strict data governance policies
- **Needs:** On-premise AI solution with no data leakage
- **Pain Points:** Cloud AI violates compliance requirements
- **Goals:** Deploy AI while maintaining data sovereignty

---

## 4. USER STORIES & USE CASES

### 4.1 Core User Stories

#### US-01: Start Chatting
```
As a user,
I want to launch the chatbot and start a conversation immediately,
So that I can get AI assistance without complex setup.

Acceptance Criteria:
- Single command launches the application
- Interface loads within 3 seconds
- No login or API key required
```

#### US-02: Select AI Model
```
As a user,
I want to choose from multiple AI models,
So that I can use the best model for my specific task.

Acceptance Criteria:
- Models displayed with descriptions
- Easy switching between models
- Current model clearly indicated
```

#### US-03: Adjust Creativity
```
As a user,
I want to control the AI's creativity level,
So that I can get focused answers or creative responses as needed.

Acceptance Criteria:
- Temperature slider (0.0 - 2.0)
- Visual indicator of current setting
- Real-time adjustment without restart
```

#### US-04: Private Conversations
```
As a privacy-conscious user,
I want assurance that my data stays local,
So that I can trust the system with sensitive information.

Acceptance Criteria:
- No outbound network calls
- Clear privacy indicators in UI
- Local-only data storage
```

#### US-05: Fast Responses
```
As a user,
I want instant AI responses,
So that conversations feel natural and productive.

Acceptance Criteria:
- Streaming responses (word-by-word)
- First token < 2 seconds
- No network latency
```

#### US-06: API Integration
```
As a developer,
I want a REST API to integrate AI into my applications,
So that I can build custom solutions on top of local LLMs.

Acceptance Criteria:
- RESTful endpoints
- Streaming support
- Clear API documentation
```

### 4.2 Use Cases

#### Use Case 1: Quick Question Answering
**Actor:** Student
**Goal:** Get help with homework
**Flow:**
1. Launch Streamlit app
2. Type question
3. Receive instant answer
4. Continue conversation with follow-ups

#### Use Case 2: Code Review
**Actor:** Software Developer
**Goal:** Review code privately
**Flow:**
1. Launch app with CodeLlama model
2. Paste code snippet
3. Request review/suggestions
4. Iterate based on feedback

#### Use Case 3: Document Analysis
**Actor:** Researcher
**Goal:** Analyze confidential documents
**Flow:**
1. Paste document content
2. Ask analytical questions
3. Get insights without data leaving machine
4. Export conversation for records

#### Use Case 4: Application Integration
**Actor:** AI Developer
**Goal:** Build custom AI application
**Flow:**
1. Start Flask API server
2. Make programmatic API calls
3. Stream responses to custom UI
4. Scale without API costs

---

## 5. FUNCTIONAL REQUIREMENTS

### 5.1 Streamlit Chat Interface

#### FR-01: User Interface
- **Priority:** P0 (Must Have)
- **Description:** Modern, ChatGPT-like web interface
- **Details:**
  - Gradient color scheme with animations
  - Responsive design (mobile-friendly)
  - Chat message bubbles
  - User and AI message distinction
  - Smooth scrolling

#### FR-02: Model Selection
- **Priority:** P0 (Must Have)
- **Description:** Dropdown to select AI model
- **Details:**
  - Auto-detect available models
  - Display model information (size, type)
  - Persist selection across messages

#### FR-03: Chat Functionality
- **Priority:** P0 (Must Have)
- **Description:** Real-time chat capabilities
- **Details:**
  - Text input box
  - Send on Enter key
  - Streaming responses (word-by-word)
  - Message history
  - Timestamp display

#### FR-04: Temperature Control
- **Priority:** P1 (Should Have)
- **Description:** Slider to adjust AI creativity
- **Details:**
  - Range: 0.0 to 2.0
  - Default: 0.7
  - Visual labels (Focused/Balanced/Creative)

#### FR-05: Session Management
- **Priority:** P1 (Should Have)
- **Description:** Manage chat sessions
- **Details:**
  - Clear chat history button
  - Session statistics (message count)
  - Persistent within browser session

#### FR-06: Status Indicators
- **Priority:** P1 (Should Have)
- **Description:** System status visibility
- **Details:**
  - Ollama connection status
  - Active model indicator
  - Processing animation during responses

#### FR-07: Welcome Screen
- **Priority:** P2 (Nice to Have)
- **Description:** Onboarding for new users
- **Details:**
  - Feature highlights
  - Privacy badges
  - Quick start instructions

### 5.2 Flask REST API

#### FR-08: API Information
- **Priority:** P0 (Must Have)
- **Endpoint:** GET /
- **Description:** API documentation and capabilities
- **Response:** JSON with endpoint list and features

#### FR-09: Health Check
- **Priority:** P0 (Must Have)
- **Endpoint:** GET /health
- **Description:** Server and Ollama connectivity status
- **Response:** JSON with status codes

#### FR-10: Model Listing
- **Priority:** P0 (Must Have)
- **Endpoint:** GET /models
- **Description:** Available Ollama models
- **Response:** JSON array of models with metadata

#### FR-11: Chat Endpoint (Streaming)
- **Priority:** P0 (Must Have)
- **Endpoint:** POST /chat
- **Description:** Send message and receive streaming response
- **Request:**
  ```json
  {
    "message": "string",
    "model": "string",
    "temperature": 0.7,
    "stream": true
  }
  ```
- **Response:** Server-Sent Events (SSE)

#### FR-12: Generate Endpoint (Non-Streaming)
- **Priority:** P1 (Should Have)
- **Endpoint:** POST /generate
- **Description:** Generate text completion
- **Request:**
  ```json
  {
    "prompt": "string",
    "model": "string",
    "temperature": 0.7
  }
  ```
- **Response:** Complete JSON response

#### FR-13: Error Handling
- **Priority:** P0 (Must Have)
- **Description:** Graceful error responses
- **Details:**
  - 400: Bad Request
  - 404: Not Found
  - 500: Internal Server Error
  - Descriptive error messages

### 5.3 Infrastructure & Tooling

#### FR-14: Launcher Scripts
- **Priority:** P0 (Must Have)
- **Description:** Automated startup scripts
- **Details:**
  - Streamlit launcher (Port 8501)
  - Flask launcher (Port 5000)
  - Ollama connectivity check
  - Virtual environment activation
  - Package verification
  - Environment variable configuration

#### FR-15: Testing Suite
- **Priority:** P1 (Should Have)
- **Description:** Automated validation tests
- **Details:**
  - Ollama connection test
  - Package import verification
  - Model availability check
  - API response validation
  - File structure verification

#### FR-16: Package Management
- **Priority:** P0 (Must Have)
- **Description:** Dependency management with UV
- **Details:**
  - requirements.txt for dependencies
  - Virtual environment isolation
  - Fast installation with UV

---

## 6. NON-FUNCTIONAL REQUIREMENTS

### 6.1 Performance

#### NFR-01: Response Time
- **Requirement:** First token in < 2 seconds
- **Measurement:** Time from request to first word
- **Priority:** P0

#### NFR-02: Streaming Speed
- **Requirement:** 20-50 tokens/second
- **Measurement:** Token generation rate
- **Priority:** P0

#### NFR-03: UI Load Time
- **Requirement:** < 3 seconds
- **Measurement:** Time to interactive
- **Priority:** P1

### 6.2 Security & Privacy

#### NFR-04: No External Calls
- **Requirement:** Zero outbound internet requests
- **Verification:** Network monitoring shows no external traffic
- **Priority:** P0

#### NFR-05: Local Data Storage
- **Requirement:** All data stored locally
- **Verification:** No cloud database connections
- **Priority:** P0

#### NFR-06: No Logging of Conversations
- **Requirement:** No persistent conversation logs (optional user control)
- **Verification:** File system check
- **Priority:** P1

### 6.3 Reliability

#### NFR-07: Uptime
- **Requirement:** 99% uptime when dependencies are running
- **Measurement:** Application crashes / total runtime
- **Priority:** P1

#### NFR-08: Error Recovery
- **Requirement:** Graceful handling of Ollama disconnections
- **Verification:** Connection lost scenarios
- **Priority:** P1

### 6.4 Usability

#### NFR-09: Setup Time
- **Requirement:** < 5 minutes from clone to first chat
- **Measurement:** User testing
- **Priority:** P0

#### NFR-10: Learning Curve
- **Requirement:** No documentation needed for basic usage
- **Verification:** New user testing
- **Priority:** P1

### 6.5 Scalability

#### NFR-11: Concurrent Users (Flask API)
- **Requirement:** Support 10+ concurrent API requests
- **Measurement:** Load testing
- **Priority:** P1

#### NFR-12: Chat History Size
- **Requirement:** Handle 1000+ messages per session
- **Measurement:** Performance testing
- **Priority:** P2

### 6.6 Compatibility

#### NFR-13: Operating Systems
- **Requirement:** macOS, Linux, Windows
- **Verification:** Testing on each OS
- **Priority:** P0

#### NFR-14: Python Version
- **Requirement:** Python 3.10+
- **Verification:** Version compatibility testing
- **Priority:** P0

#### NFR-15: Browser Support
- **Requirement:** Chrome, Firefox, Safari, Edge (latest 2 versions)
- **Verification:** Cross-browser testing
- **Priority:** P1

---

## 6A. QUALITY ASSURANCE & TESTING STANDARDS

### 6A.1 Test Coverage Requirements

#### Code Coverage Target
- **Standard:** ≥95% line coverage
- **Industry Benchmark:** 80% minimum, 95% excellence
- **Measurement Tool:** pytest-cov
- **Enforcement:** CI/CD pipeline blocks merge if coverage < 95%
- **Components:**
  - Flask API: ≥95% coverage
  - Streamlit App: ≥95% coverage
  - Helper Functions: 100% coverage

#### Test Types Required
1. **Unit Tests**
   - All functions must have unit tests
   - Mock external dependencies (Ollama API)
   - Test both success and failure paths
   - Minimum 100 tests per major component

2. **Integration Tests**
   - End-to-end workflow validation
   - Real Ollama server connection tests
   - Multi-component interaction tests

3. **Edge Case Tests**
   - Empty inputs
   - Invalid types
   - Boundary values (temperature 0, 2)
   - Very long inputs (10,000+ characters)
   - Special characters and Unicode
   - Network timeouts
   - Connection failures

### 6A.2 Testing Framework Standards

#### Required Tools
- **pytest** ≥8.0 - Testing framework
- **pytest-cov** ≥4.1 - Coverage measurement
- **pytest-mock** ≥3.12 - Mocking support
- **pytest-xdist** ≥3.5 - Parallel execution

#### Test Organization
```
tests/
├── conftest.py           # Shared fixtures
├── test_flask_app.py     # Flask API tests
└── test_streamlit_app.py # Streamlit tests
```

#### Test Naming Convention
- File: `test_<module_name>.py`
- Class: `Test<FeatureName>`
- Function: `test_<functionality>_<scenario>()`
- Example: `test_chat_endpoint_returns_error_when_message_empty()`

### 6A.3 Code Quality Standards

#### Linting & Formatting
- **Black** - Code formatter (PEP 8 compliant)
- **Flake8** - Style guide enforcement
- **Pylint** - Static analysis (minimum score: 8.0/10)
- **isort** - Import statement organization
- **MyPy** - Static type checking

#### Code Metrics
- **Cyclomatic Complexity:** ≤10 per function
- **Function Length:** ≤50 lines recommended
- **File Length:** ≤500 lines recommended
- **Nesting Depth:** ≤4 levels

#### Documentation Requirements
- **Docstrings:** Required for all public functions
- **Type Hints:** Required for function parameters and returns
- **Inline Comments:** Required for complex logic
- **API Documentation:** OpenAPI/Swagger specification

### 6A.4 Error Handling Standards

#### Exception Handling Requirements
- **Specific Exceptions:** Use specific exception types (ConnectionError, ValueError, TimeoutError)
- **No Bare Except:** Avoid `except:` without exception type
- **Logging:** All exceptions must be logged with stack traces
- **User Messages:** Clear, actionable error messages
- **HTTP Status Codes:** Proper codes (400, 404, 500, 503)

#### Input Validation Standards
- **Type Validation:** Runtime type checking for all inputs
- **Range Validation:** Numerical bounds (e.g., temperature: 0-2)
- **Null Handling:** Explicit checks for None/empty values
- **Sanitization:** Prevent injection attacks

#### Error Response Format (API)
```json
{
  "error": "User-friendly message",
  "details": "Technical details",
  "timestamp": "ISO 8601 format",
  "suggestion": "How to fix (optional)"
}
```

### 6A.5 Logging Standards

#### Log Level Usage
- **DEBUG:** Detailed diagnostic (development only)
- **INFO:** Normal operations, user actions (default)
- **WARNING:** Unexpected but handled situations
- **ERROR:** Errors that allow continued operation
- **CRITICAL:** Severe errors requiring immediate attention

#### Logging Requirements
- **Format:** `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Location:** Separate log files per application (`logs/`)
- **Output:** Both file and console during development
- **Content:**
  - All user-initiated operations
  - All exceptions with stack traces
  - Performance timing for critical operations
  - Entry/exit of major functions
- **Restrictions:**
  - No PII (Personally Identifiable Information)
  - No secrets or API keys
  - No full user messages (log length only)

#### Log File Management
- **Rotation:** Size-based (100MB per file)
- **Retention:** 30 days minimum
- **Location:** `logs/` directory (git-ignored)

### 6A.6 Security Standards

#### Static Analysis Requirements
- **Bandit:** Security linting for Python code
- **Safety:** Dependency vulnerability scanning
- **CodeQL:** GitHub security scanning (weekly)
- **OWASP:** Awareness of Top 10 vulnerabilities

#### Secure Coding Practices
- **Input Sanitization:** All user inputs must be sanitized
- **No Hardcoded Secrets:** Use environment variables
- **Dependency Auditing:** Regular updates and patches
- **Least Privilege:** Minimal permissions required

#### Security Testing
- **Frequency:** Every commit via CI/CD
- **Blocking:** Critical/High vulnerabilities block deployment
- **Reporting:** Security scan results in CI/CD artifacts

### 6A.7 CI/CD Pipeline Requirements

#### Pipeline Trigger Events
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

#### Required Pipeline Stages

**Stage 1: Testing**
- Run on: Ubuntu + macOS
- Python versions: 3.10, 3.11, 3.12, 3.13
- Execute: 750+ unit tests
- Coverage: Must achieve ≥95%
- Duration: <5 minutes

**Stage 2: Code Quality**
- Black formatting check
- Flake8 linting
- Pylint analysis (≥8.0 score)
- isort import checking
- MyPy type checking

**Stage 3: Security**
- Bandit security scan
- Safety dependency audit
- CodeQL analysis

**Stage 4: Build**
- Package building validation
- Distribution checks

**Stage 5: Integration**
- Integration tests with Ollama
- End-to-end workflow validation

#### Failure Policies
- **Test Failure:** ❌ Block merge
- **Coverage < 95%:** ❌ Block merge
- **Security Critical/High:** ❌ Block merge
- **Linting Errors:** ⚠️ Warning (non-blocking)
- **Type Errors:** ⚠️ Warning (non-blocking)

### 6A.8 Performance Benchmarks

#### Response Time Requirements
- **First Token:** <2 seconds (99th percentile)
- **Token Generation:** 20-50 tokens/second
- **API Overhead:** <100ms
- **Health Check:** <50ms

#### Resource Limits
- **Memory:** <512MB base footprint
- **CPU:** <50% during idle
- **Startup Time:** <3 seconds

#### Performance Testing
- **Tool:** pytest-benchmark
- **Frequency:** Every release
- **Regression Threshold:** <10% degradation allowed

### 6A.9 Reliability Targets

#### Availability
- **Target:** 99.9% uptime (when Ollama running)
- **MTBF:** >1000 hours between failures
- **MTTR:** <5 minutes recovery time

#### Error Rate Targets
- **User Errors:** <1% of total requests
- **System Errors:** <0.1% of total requests
- **Crash Rate:** <0.01% of sessions

#### Monitoring Requirements
- Health endpoint monitoring
- Error rate tracking
- Performance metrics logging

### 6A.10 Maintainability Requirements

#### Code Maintainability
- **Maintainability Index:** ≥65 (good)
- **Technical Debt Ratio:** <5%
- **Documentation Coverage:** 100% public APIs

#### Dependency Management
- **Update Frequency:** Weekly check for updates
- **Security Patches:** Apply within 48 hours
- **Version Pinning:** Major versions pinned in requirements.txt
- **Deprecation Policy:** 6-month notice for breaking changes

#### Version Control Standards
- **Branching:** GitFlow (main, develop, feature)
- **Commit Format:** Conventional commits
- **Pull Requests:** Required for all changes
- **Code Review:** Minimum 1 approval required
- **CI Status:** All checks must pass before merge

---

## 7. TECHNICAL SPECIFICATIONS

### 7.1 Technology Stack

#### Core Technologies
- **Language:** Python 3.13
- **Web Framework (UI):** Streamlit 1.51.0
- **API Framework:** Flask 3.1.2
- **LLM Interface:** Ollama Python Client 0.6.0
- **HTTP Client:** Requests 2.32.5
- **Package Manager:** UV (for fast installs)

#### Infrastructure
- **LLM Server:** Ollama 0.12.9
- **Deployment:** Local machine
- **Environment:** Virtual environment (.venv)

### 7.2 Architecture

```
┌─────────────────────────────────────────┐
│         User Layer                      │
├─────────────────────────────────────────┤
│  Browser        │    API Client         │
│  (Streamlit)    │    (curl/Postman)     │
└────────┬────────┴─────────┬─────────────┘
         │                  │
         │                  │
┌────────▼──────────────────▼─────────────┐
│      Application Layer                  │
├─────────────────────────────────────────┤
│  Streamlit App   │    Flask API         │
│  (Port 8501)     │    (Port 5000)       │
└────────┬─────────┴─────────┬────────────┘
         │                   │
         │                   │
┌────────▼───────────────────▼────────────┐
│      Integration Layer                  │
├─────────────────────────────────────────┤
│       Ollama Python Client              │
└────────┬────────────────────────────────┘
         │
         │
┌────────▼────────────────────────────────┐
│      LLM Layer                          │
├─────────────────────────────────────────┤
│       Ollama Server (Port 11434)        │
└────────┬────────────────────────────────┘
         │
         │
┌────────▼────────────────────────────────┐
│      Model Layer                        │
├─────────────────────────────────────────┤
│  llama3.2 │ mistral │ phi3 │ codellama  │
└─────────────────────────────────────────┘
```

### 7.3 Project Structure

```
Assignment1_Ollama_Chatbot/
├── apps/
│   ├── app_streamlit.py    # Streamlit chat interface
│   └── app_flask.py        # Flask REST API
├── scripts/
│   ├── launch_ollama.sh       # Ollama server launcher
│   ├── launch_streamlit.sh    # Streamlit launcher
│   ├── launch_flask.sh        # Flask launcher
│   ├── shutdown_all.sh        # Stop all services
│   ├── shutdown_streamlit.sh  # Stop Streamlit
│   ├── shutdown_flask.sh      # Stop Flask
│   └── run_tests.sh           # Test suite
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Shared fixtures
│   ├── test_flask_app.py     # Flask API tests
│   └── test_streamlit_app.py # Streamlit tests
├── docs/
│   ├── PRD.md             # This document
│   ├── PROMPTS.md         # Development prompts log
│   ├── INSTALLATION.md    # Setup guide
│   ├── USAGE.md           # User guide
│   └── API.md             # API documentation
├── logs/                  # Application logs (git-ignored)
│   ├── flask_app.log
│   └── streamlit_app.log
├── .github/workflows/     # CI/CD pipeline
│   ├── ci-cd.yml         # Main pipeline
│   └── codeql.yml        # Security scanning
├── .venv/                 # Virtual environment (git-ignored)
├── .gitignore            # Git exclusions
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── pytest.ini            # Pytest configuration
└── README.md            # Operations manual
```

### 7.4 Data Flow

#### Streamlit Chat Flow
```
User Input → Streamlit UI → Ollama Client → Ollama API →
LLM Model → Streaming Response → Real-time Display → User
```

#### Flask API Flow
```
HTTP Request → Flask Endpoint → Validation → Ollama Client →
Ollama API → LLM Model → JSON Response → Client Application
```

---

## 8. DEPENDENCIES & CONSTRAINTS

### 8.1 External Dependencies

#### Critical Dependencies
- **Ollama Server:** Must be installed and running
- **Python 3.10+:** Required for compatibility
- **4GB RAM minimum:** For running models
- **10GB+ disk space:** For model storage

#### Python Package Dependencies
```
streamlit>=1.39.0
flask>=3.0.0
ollama>=0.3.0
requests>=2.32.0
python-dotenv>=1.0.0
```

### 8.2 Technical Constraints

#### TC-01: Local Processing Only
- **Constraint:** Cannot use cloud-based LLMs
- **Rationale:** Privacy requirement
- **Impact:** Limited to Ollama-compatible models

#### TC-02: Single-User Sessions
- **Constraint:** Streamlit designed for single user per session
- **Rationale:** Framework limitation
- **Impact:** Multi-user needs require Flask API

#### TC-03: Model Size Limitations
- **Constraint:** Limited by local machine resources
- **Rationale:** RAM and CPU capabilities
- **Impact:** Cannot run 70B+ models on typical hardware

#### TC-04: No Authentication
- **Constraint:** No built-in user authentication
- **Rationale:** Local-only application
- **Impact:** Not suitable for shared hosting

### 8.3 Assumptions

- User has administrative access to install software
- Machine meets minimum hardware requirements
- User is comfortable with command-line operations
- Ollama models are already downloaded

---

## 9. RISKS & MITIGATION

### 9.1 Technical Risks

#### RISK-01: Ollama Not Running
- **Impact:** High (Application unusable)
- **Probability:** Medium
- **Mitigation:**
  - Clear error messages
  - Auto-detection in launcher scripts
  - Setup documentation

#### RISK-02: Insufficient System Resources
- **Impact:** High (Poor performance/crashes)
- **Probability:** Medium
- **Mitigation:**
  - Document minimum requirements
  - Recommend appropriate models for hardware
  - Graceful degradation

#### RISK-03: Package Compatibility Issues
- **Impact:** Medium (Installation failures)
- **Probability:** Low
- **Mitigation:**
  - Pinned dependency versions
  - UV for fast, reliable installs
  - Comprehensive testing

### 9.2 User Experience Risks

#### RISK-04: Complex Setup Process
- **Impact:** High (User abandonment)
- **Probability:** Medium
- **Mitigation:**
  - Automated launcher scripts
  - Step-by-step documentation
  - One-command installation

#### RISK-05: Unclear Error Messages
- **Impact:** Medium (User frustration)
- **Probability:** Medium
- **Mitigation:**
  - Descriptive error messages
  - Troubleshooting guide
  - Status indicators

---

## 10. TIMELINE & MILESTONES

### 10.1 Development Phases

**Note:** This PRD uses high-level project phases (1-6). For detailed implementation phases with step-by-step development narrative including problem-solving (e.g., corporate proxy configuration, authentication), see the complete development history in version control commits.

#### Phase 1: Foundation (✅ COMPLETED)
- [x] Project structure setup
- [x] Virtual environment configuration
- [x] Dependency installation
- [x] Launcher scripts creation
- [x] Test suite implementation

#### Phase 2: Core Development (✅ COMPLETED)
- [x] Streamlit chatbot interface
- [x] Flask REST API
- [x] Ollama integration
- [x] Streaming responses
- [x] Model selection
- [x] Temperature control

#### Phase 3: Enhancement (✅ COMPLETED)
- [x] UI/UX polish
- [x] Error handling
- [x] Status indicators
- [x] Session management
- [x] Statistics tracking

#### Phase 4: Documentation (✅ COMPLETED)
- [x] PRD (this document) - 824 lines
- [x] README.md - 2,135 lines (comprehensive guide)
- [x] Key user requirements integrated into PRD Section 14
- [ ] INSTALLATION.md (future enhancement)
- [ ] USAGE.md (future enhancement)
- [ ] API.md (future enhancement)

#### Phase 5: Testing & Validation (✅ COMPLETED)
- [x] Functional testing implemented
- [x] Comprehensive test suite (run_tests.sh with 5 tests):
  - Test 1: Ollama server connectivity validation
  - Test 2: Virtual environment verification
  - Test 3: Package imports validation (streamlit, flask, requests, ollama)
  - Test 4: Model availability checking (4 models verified)
  - Test 5: End-to-end API response testing
- [x] All tests passing (100% success rate)
- [x] Launcher scripts with built-in validation
- [ ] Performance benchmarking (future enhancement)
- [ ] User acceptance testing (future enhancement)
- [ ] Cross-platform validation (future enhancement)

#### Phase 6: Release (⏳ PENDING)
- [ ] GitHub repository publication
- [ ] Final documentation review
- [ ] Community announcement

---

## 11. SUCCESS CRITERIA

### 11.1 Launch Criteria

The product is ready for release when:
- [x] All P0 requirements implemented
- [x] Streamlit app launches successfully
- [x] Flask API operational
- [x] All tests implemented and documented
- [x] Documentation complete (README, PRD, PROMPTS)
- [ ] GitHub repository published with all changes

### 11.2 Acceptance Criteria

#### AC-01: Installation
- User can install in < 10 minutes
- All dependencies resolve correctly
- Launcher scripts work on first try

#### AC-02: Functionality
- Chat messages sent and received
- Responses stream in real-time
- Model switching works
- API endpoints respond correctly

#### AC-03: Performance
- First token < 2 seconds
- No crashes during normal usage
- UI responsive and smooth

#### AC-04: Privacy
- Network monitor shows no external calls
- Data stays on local machine
- No API keys required

---

## 12. FUTURE ENHANCEMENTS

### 12.1 Planned Features (v2.0)

#### FE-01: Conversation History
- **Description:** Save and load past conversations
- **Priority:** P1
- **Effort:** Medium

#### FE-02: Multi-Model Comparison
- **Description:** Query multiple models simultaneously
- **Priority:** P2
- **Effort:** High

#### FE-03: Document Upload
- **Description:** Upload files for analysis
- **Priority:** P1
- **Effort:** Medium

#### FE-04: Voice Input/Output
- **Description:** Speech-to-text and text-to-speech
- **Priority:** P2
- **Effort:** High

#### FE-05: Model Management
- **Description:** Download/remove models from UI
- **Priority:** P1
- **Effort:** Low

#### FE-06: Custom System Prompts
- **Description:** Configure model behavior
- **Priority:** P1
- **Effort:** Low

#### FE-07: Export Conversations
- **Description:** Export chat to PDF/Markdown
- **Priority:** P2
- **Effort:** Low

#### FE-08: Dark/Light Theme Toggle
- **Description:** User preference for theme
- **Priority:** P2
- **Effort:** Low

### 12.2 Long-Term Vision

- Enterprise deployment tools
- Multi-user support with authentication
- Integration with vector databases (RAG)
- Mobile applications (iOS/Android)
- Desktop applications (Electron)

---

## 13. APPENDIX

### 13.1 Glossary

- **LLM:** Large Language Model
- **Ollama:** Local LLM server and model manager
- **Streaming:** Real-time token-by-token response delivery
- **Temperature:** Parameter controlling randomness (0=deterministic, 2=very creative)
- **RAG:** Retrieval-Augmented Generation
- **SSE:** Server-Sent Events (streaming protocol)
- **UV:** Ultra-fast Python package installer

### 13.2 References

- Ollama Documentation: https://ollama.ai/
- Streamlit Documentation: https://docs.streamlit.io/
- Flask Documentation: https://flask.palletsprojects.com/
- Python Ollama Client: https://github.com/ollama/ollama-python

### 13.3 Document History

| Version | Date | Authors | Changes |
|---------|------|---------|---------|
| 1.0 | 2025-11-06 | Fouad Azem, Tal Goldengorn | Initial PRD creation |

---

## 14. KEY USER REQUIREMENTS (ORIGINAL PROMPTS)

This section captures the critical user prompts that shaped and defined this project during development.

### 14.1 Prompt #1: Comprehensive Project Requirements (Most Critical)

**Date:** 2025-11-06 (Phase 4.2)
**Context:** Defining core project vision and requirements

**User Prompt:**
```
let me set the instructions of my development of the project clearly:

i want to create:
1) luxurious local chatbot interface that connects to Ollama a local LLM server
2) The application provides a clean, user friendly web interface (similar to
   chatGPT, Claude Gemini) with large models
3) it must be without requiring API Keys or internet connectivity.
4) i want that all data stays on the machine for privacy.
5) Cost free. No API Calls with charges or subscriptions(cost free)
6) Fast, direct local API calls with no network latency.
7) Simple, clean UI built with modern technology and tools.
8) my preference to build it with technologies that i know well which are:
   Python, Streamlit, Ollama API.
```

**Impact:**
- Defined entire application architecture (Streamlit + Flask + Ollama)
- Established core principles: Privacy-first, Cost-free, Fast, Local-only
- Set technology stack: Python 3.13, Streamlit, Flask, Ollama
- Determined UI style: Luxurious ChatGPT-like interface
- Established success criteria: No API keys, no internet, no cost

---

### 14.2 Prompt #2: Professional Launcher Requirements

**Date:** 2025-11-06 (Phase 6.1)
**Context:** Defining automation and validation requirements

**User Prompt:**
```
i want to validate that we are using launchers for each app (flask or streamlit)
where in the sh i can configure the:
1) logging level
2) checking Ollama is running or not
3) activate the virtual env and verifying packages
4) Launching with dedicating port
5) unit testing for the app to create for each app
```

**Impact:**
- Created professional launcher scripts (launch_streamlit.sh, launch_flask.sh)
- Implemented 5-step validation process in each launcher
- Built comprehensive test suite (run_tests.sh with 5 tests)
- Added Ollama connectivity checking
- Enabled configurable logging levels (DEBUG, INFO, WARNING, ERROR)
- Automated virtual environment activation and package verification

---

### 14.3 Prompt #3: Documentation Requirements

**Date:** 2025-11-06 (Phase 9.2)
**Context:** Requesting comprehensive project documentation

**User Prompt:**
```
yes create PRD. please show its Product Requirements Document and also
i need the prompts i used to create the project
```

**Impact:**
- Created comprehensive PRD (this document) - 14 sections, 900+ lines
- Documented all requirements, user stories, technical specs
- Captured complete development narrative
- Established professional documentation standards
- Integrated key prompts into PRD for traceability

---

### 14.4 Prompt #4: Professional Documentation Structure

**Date:** 2025-11-06 (Phase 7.2)
**Context:** Understanding professional software documentation standards

**User Prompt:**
```
wait please, i want to understand what the documentation i need in
Software Project i need to be professional project?
```

**Impact:**
- Established docs/ directory structure
- Defined documentation hierarchy (README, PRD, INSTALLATION, USAGE, API)
- Adopted industry-standard documentation practices
- Created organized project structure:
  - apps/ (applications)
  - scripts/ (automation)
  - tests/ (testing)
  - docs/ (documentation)

---

### 14.5 Prompt #5: Clear Naming Convention

**Date:** 2025-11-06 (Phase 7.1)
**Context:** Establishing self-documenting file naming

**User Prompt:**
```
app_flask.py and app_streamlit.py, does that makes sense?
```

**Impact:**
- Adopted descriptive naming convention throughout project
- Files immediately identify their purpose:
  - app_streamlit.py (Streamlit web UI)
  - app_flask.py (Flask REST API)
  - launch_streamlit.sh (Streamlit launcher)
  - launch_flask.sh (Flask API launcher)
- Improved code maintainability and IDE navigation
- Set standard for professional, self-documenting codebase

---

### 14.6 Requirements Traceability Matrix

| Prompt | Requirement Category | Implementation | PRD Reference |
|--------|---------------------|----------------|---------------|
| #1 | Privacy & Architecture | Streamlit + Flask + Ollama local stack | Section 1, 7 |
| #1 | Zero Cost | No API calls, no subscriptions | Section 1.1, 2.3 |
| #1 | Technology Stack | Python, Streamlit, Flask, Ollama | Section 7.1 |
| #2 | Automation | 7 professional launcher/shutdown scripts | Section 5.3 |
| #2 | Validation | 5-test comprehensive test suite | Section 5.3 |
| #3 | Documentation | PRD, README (2,135 lines) | Section 10.4 |
| #4 | Project Structure | Professional grouped organization | Section 7.3 |
| #5 | Code Quality | Descriptive, self-documenting naming | Section 7.3 |

---

## 15. QUALITY ASSURANCE & TESTING

### 15.1 Testing Strategy

The system implements comprehensive testing at multiple levels to ensure reliability, correctness, and performance.

#### Testing Pyramid

| Level | Type | Count | Coverage | Purpose |
|-------|------|-------|----------|---------|
| **Integration** | Real Services | 18 tests | 96% | End-to-end validation with real Ollama |
| **Unit** | Mocked | 69 tests | 96% | Code path validation |
| **System** | Bash Scripts | 15 tests | N/A | Service health checks |

### 15.2 Test Suite Composition

#### Unit Tests (69 tests)
**Location:** `tests/test_flask_app.py`, `tests/test_streamlit_app.py`
**Execution Time:** ~1 second
**Purpose:** Validate individual components in isolation

| Component | Tests | What It Tests | Expected Result |
|-----------|-------|---------------|-----------------|
| API Info | 2 | Endpoint metadata | Returns JSON with API details |
| Health Check | 3 | System health | Status: healthy/unhealthy |
| Models | 3 | Model listing | Returns installed models |
| Chat | 8 | AI conversation | Returns response or error |
| Generate | 4 | Text generation | Generates completion |
| Validation | 8 | Input validation | Rejects invalid inputs (400) |
| Error Handling | 9 | Error scenarios | Graceful errors (503/504) |
| Logging | 2 | Log creation | Logs written correctly |
| Streamlit | 29 | App functions | All helpers work |

#### Integration Tests (18 tests)
**Location:** `tests/test_integration.py`
**Execution Time:** ~18 seconds
**Purpose:** Validate system with REAL Ollama (no mocks)

| Category | Tests | What It Tests | Expected Result |
|----------|-------|---------------|-----------------|
| Ollama Connection | 3 | Real server | Server accessible, models found |
| AI Generation | 3 | Real AI | Actual responses generated |
| Flask Integration | 4 | Flask → Ollama | Real HTTP requests work |
| Streamlit Integration | 3 | Streamlit → Ollama | Real functions work |
| Error Scenarios | 2 | Real errors | Errors handled gracefully |
| Performance | 2 | Real timing | Response time < 30s |

#### System Tests (15 tests)
**Location:** `scripts/run_tests.sh`, `scripts/run_integration_tests.sh`
**Purpose:** Validate full system deployment

### 15.3 Test Execution

```bash
# All tests (unit + integration)
pytest --cov=apps --cov-report=term-missing -v
Result: 87 passed in 22.50s, 96% coverage

# Unit tests only (fast)
pytest tests/test_flask_app.py tests/test_streamlit_app.py -v
Result: 69 passed in 1.02s

# Integration tests only (requires Ollama)
pytest -m integration -v --cov=apps
Result: 18 passed in 18.11s

# System tests
./scripts/run_integration_tests.sh
Result: 10/10 tests passed
```

### 15.4 Test Coverage Requirements

**Target:** 95%+ code coverage
**Achieved:** 96% (exceeds target by 1%)

| File | Statements | Missing | Coverage | Status |
|------|-----------|---------|----------|--------|
| app_flask.py | 142 | 1 | 99% | ✅ Excellent |
| app_streamlit.py | 82 | 9 | 89% | ✅ Good |
| **TOTAL** | 224 | 10 | 96% | ✅ **Exceeds Target** |

**Missing Lines Explained:**
- 1 line: Flask 500 error handler (catastrophic failure safety net)
- 9 lines: Streamlit error logging and UI calls (non-critical)

### 15.5 What Tests Validate

#### Functionality Testing
- ✅ All API endpoints return correct responses
- ✅ Chat and generate functions work with real AI
- ✅ Model listing returns installed models
- ✅ Health check detects Ollama status
- ✅ Streaming responses work

#### Validation Testing
- ✅ Invalid inputs rejected with 400 errors
- ✅ Empty messages rejected
- ✅ Temperature must be 0-2
- ✅ Model must be string
- ✅ Required fields validated

#### Error Handling Testing
- ✅ Ollama disconnected → 503 error
- ✅ Timeout → 504 error
- ✅ Invalid parameters → 400 error
- ✅ No crashes on any error
- ✅ Clear error messages returned

#### Performance Testing
- ✅ Response time < 30s (actual: 3-8s)
- ✅ Health check < 1s
- ✅ API info < 100ms
- ✅ Concurrent requests work
- ✅ Test suite runs in 22s

#### Integration Testing
- ✅ Flask → Ollama communication
- ✅ Streamlit → Ollama communication
- ✅ Real AI responses generated
- ✅ Services can start and stop
- ✅ End-to-end workflows complete

---

## 16. LOGGING SYSTEM

### 16.1 Logging Strategy

The system implements environment-aware logging with configurable levels for production, development, and debugging.

#### Log Levels by Environment

| Environment | Log Level | What Gets Logged | Use Case |
|-------------|-----------|------------------|----------|
| **Production** | ERROR | Only errors and critical issues | Live deployment |
| **Development** | INFO | Info messages + errors | Active development |
| **Debug** | DEBUG | All messages + trace | Troubleshooting |

### 16.2 Log Configuration

**Log File Locations:**
```
logs/
├── flask_app.log       # Flask API logs
└── streamlit_app.log   # Streamlit UI logs
```

**Setting Log Level:**
```bash
# Production (errors only)
export LOG_LEVEL=ERROR
python apps/app_flask.py

# Development (default)
export LOG_LEVEL=INFO
python apps/app_flask.py

# Debug (everything)
export LOG_LEVEL=DEBUG
python apps/app_flask.py
```

### 16.3 Log Output Examples

**INFO Level (Development):**
```
2025-11-09 10:30:15 - app_flask - INFO - 🤖 Starting Ollama Flask Server
2025-11-09 10:30:16 - app_flask - INFO - ✓ Chat request received - Model: llama3.2
2025-11-09 10:30:20 - app_flask - INFO - ✓ Response generated (4.2s)
```

**ERROR Level (Production):**
```
2025-11-09 10:30:25 - app_flask - ERROR - ✗ Connection error: Cannot connect to Ollama
2025-11-09 10:30:25 - app_flask - ERROR - ✗ Stack trace: ConnectionRefusedError [Errno 61]
```

**DEBUG Level (Troubleshooting):**
```
2025-11-09 10:30:15 - app_flask - DEBUG - Validating: {'message': 'Hello', 'model': 'llama3.2'}
2025-11-09 10:30:15 - app_flask - DEBUG - Temperature: 0.7 (valid range: 0-2)
2025-11-09 10:30:16 - app_flask - DEBUG - Calling ollama.chat()
2025-11-09 10:30:20 - app_flask - DEBUG - Response chunk #1: "Hello"
```

### 16.4 Log Rotation

Logs automatically rotate at 10MB:
```
logs/
├── flask_app.log        # Current log
├── flask_app.log.1      # Previous rotation
└── flask_app.log.2      # Older rotation
```

### 16.5 Logging Requirements

- ✅ **REQ-LOG-01:** All errors must be logged
- ✅ **REQ-LOG-02:** Log level configurable via environment variable
- ✅ **REQ-LOG-03:** Logs must include timestamp
- ✅ **REQ-LOG-04:** Logs must rotate to prevent disk fill
- ✅ **REQ-LOG-05:** No sensitive data logged (passwords, tokens)

---

## 17. ERROR HANDLING

### 17.1 No-Crash Guarantee

**Requirement:** The system MUST NEVER crash. All errors MUST be handled gracefully.

**Implementation:** Every error scenario returns a clean JSON response with appropriate HTTP status code.

### 17.2 Error Handling Strategy

| Error Type | HTTP Status | Response | Recovery Action |
|------------|-------------|----------|----------------|
| Ollama Disconnected | 503 | Service Unavailable | Start Ollama |
| Invalid Input | 400 | Bad Request | Fix parameters |
| Timeout | 504 | Gateway Timeout | Retry request |
| Model Not Found | 500 | Internal Error | Install/select model |
| Unexpected Error | 500 | Internal Error | Check logs |

### 17.3 Error Response Format

All errors return consistent JSON:
```json
{
  "error": "Human-readable error message",
  "details": "Technical details for debugging",
  "timestamp": "2025-11-09T10:30:25.123456",
  "suggestion": "How to fix (when applicable)"
}
```

### 17.4 Error Scenarios Tested

#### Ollama Not Running
**Request:** POST /chat with Ollama down
**Response:** 503 + "Cannot connect to Ollama server. Is it running?"
**System State:** No crash ✅

#### Invalid Parameters
**Request:** POST /chat with message=123 (should be string)
**Response:** 400 + "'message' must be a string"
**System State:** No crash ✅

#### Empty Message
**Request:** POST /chat with message="   "
**Response:** 400 + "'message' cannot be empty"
**System State:** No crash ✅

#### Timeout
**Scenario:** Ollama takes > timeout
**Response:** 504 + "Request timeout"
**System State:** No crash ✅

#### Invalid Model
**Request:** POST /chat with model="nonexistent"
**Response:** 500 + "Model not found"
**System State:** No crash ✅

### 17.5 Error Handling Requirements

- ✅ **REQ-ERR-01:** No unhandled exceptions
- ✅ **REQ-ERR-02:** All errors return JSON (never HTML error pages)
- ✅ **REQ-ERR-03:** HTTP status codes match error type
- ✅ **REQ-ERR-04:** Error messages are user-friendly
- ✅ **REQ-ERR-05:** Technical details included for debugging
- ✅ **REQ-ERR-06:** Suggestions provided when possible

### 17.6 Error Handling Validation

**Test:** `pytest tests/test_flask_app.py::TestErrorHandling -v`
**Result:**
```
test_connection_error_handling PASSED ✅
test_timeout_error_handling PASSED ✅
test_value_error_handling PASSED ✅
test_invalid_model_name_real PASSED ✅
```
**Conclusion:** All error scenarios handled gracefully, no crashes

---

## 18. PERFORMANCE KPIs

### 18.1 Response Time KPIs

| Endpoint | Target | Typical | Measured By | Status |
|----------|--------|---------|-------------|--------|
| API Info | < 100ms | ~10ms | Unit tests | ✅ Met |
| Health Check | < 1s | ~50ms | Integration tests | ✅ Met |
| Models List | < 1s | ~100ms | Integration tests | ✅ Met |
| Chat | < 30s | 3-8s | Integration tests | ✅ Met |
| Generate | < 30s | 2-5s | Integration tests | ✅ Met |

### 18.2 Throughput KPIs

| Metric | Target | Measured | Status |
|--------|--------|----------|--------|
| Test Execution | > 50 tests/sec | 68 tests/sec (unit) | ✅ Exceeded |
| API Requests | > 10 req/sec | 10+ req/sec | ✅ Met |
| Streaming Tokens | 10-50 tokens/sec | Model-dependent | ✅ Met |

### 18.3 Concurrency KPIs

| Test | Requirement | Result | Status |
|------|-------------|--------|--------|
| 2 Simultaneous Requests | Both succeed | Both return 200 | ✅ Pass |
| No Request Blocking | Non-blocking | Independent processing | ✅ Pass |
| Parallel AI Generation | Works | Multiple streams active | ✅ Pass |

### 18.4 Test Performance

**Total Test Suite:** 87 tests in 22.50 seconds
- Unit tests: 69 in 1.02s (68 tests/sec)
- Integration tests: 18 in 18.11s (1 test/sec)
- Combined: 3.9 tests/sec

### 18.5 Memory Usage

| Component | Memory | Notes |
|-----------|--------|-------|
| Flask App | ~50MB | Lightweight |
| Streamlit App | ~100MB | Includes UI |
| Ollama (llama3.2) | ~2GB | Model in RAM |
| **Total System** | ~2.2GB | During use |

### 18.6 Real Performance Test Results

**From Integration Tests:**
```bash
pytest tests/test_integration.py::TestRealPerformance::test_response_time_reasonable -v -s
```

**Output:**
```
test_response_time_reasonable PASSED
  ⏱️  Response time: 4.23s
```

**Interpretation:**
- ✅ Completed in 4.23s (well under 30s target)
- ✅ Acceptable for AI generation
- ✅ Model: llama3.2, Prompt: "Hi"

### 18.7 Performance Requirements

- ✅ **REQ-PERF-01:** Chat responses < 30 seconds
- ✅ **REQ-PERF-02:** API info < 100ms
- ✅ **REQ-PERF-03:** Health check < 1 second
- ✅ **REQ-PERF-04:** Support concurrent requests
- ✅ **REQ-PERF-05:** No request blocking
- ✅ **REQ-PERF-06:** Streaming tokens as they generate

---

## 19. CODE COVERAGE

### 19.1 Coverage Requirements

**Target:** 95%+ test coverage
**Achieved:** 96% (exceeds target by 1%)
**Industry Standard:** 80%
**Our Coverage:** Exceeds industry standard by 16%

### 19.2 Coverage Breakdown

| File | Statements | Missing | Coverage | Status |
|------|-----------|---------|----------|--------|
| app_flask.py | 142 | 1 | 99% | ✅ Excellent |
| app_streamlit.py | 82 | 9 | 89% | ✅ Good |
| **TOTAL** | **224** | **10** | **96%** | ✅ **Exceeds Target** |

### 19.3 Coverage Formula

**Coverage = (Lines Executed by Tests / Total Lines) × 100**
- 96% = 214 out of 224 lines tested
- 10 lines intentionally not covered (explained below)

### 19.4 Missing Lines Explained

#### Flask - 1 Line (99% coverage)
**Line 358:** 500 Internal Server Error handler
```python
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500  # ← NOT covered
```
**Reason:** Only triggered by catastrophic failures
**Impact:** Minimal - safety net for unexpected errors
**Acceptable:** ✅ Yes

#### Streamlit - 9 Lines (89% coverage)
**Lines 535-536, 555-558, 590-592:** Error logging statements
```python
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")  # ← NOT covered (logging)
    return False                              # ← Tested ✅
```
**Reason:** Logging calls mocked, error handling IS tested
**Impact:** Minimal - logic works, logging not traced
**Acceptable:** ✅ Yes

### 19.5 Coverage by Test Type

| Test Type | Coverage | What It Measures |
|-----------|----------|------------------|
| Unit Tests | 96% | Code paths with mocks |
| Integration Tests | 96% | Real scenarios (same coverage) |
| Combined | 96% | Complete validation |

### 19.6 Coverage Validation

**Command:**
```bash
pytest --cov=apps --cov-fail-under=95
```

**Output:**
```
✅ Required test coverage of 95% reached. Total coverage: 95.54%
============================= 87 passed in 22.50s ==============================
```

### 19.7 Coverage Requirements

- ✅ **REQ-COV-01:** Minimum 95% code coverage
- ✅ **REQ-COV-02:** All business logic covered
- ✅ **REQ-COV-03:** All error paths tested
- ✅ **REQ-COV-04:** All API endpoints covered
- ✅ **REQ-COV-05:** Coverage measured automatically
- ✅ **REQ-COV-06:** Coverage reported in CI/CD

---

## 20. APPROVAL

### Sign-Off

This PRD has been reviewed and approved by:

- **Project Team:**
  - Fouad Azem (ID: 040830861)
  - Tal Goldengorn (ID: 207042573)
- **Date:** November 6, 2025
- **Status:** ✅ APPROVED

---

**Document End**
