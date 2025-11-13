# System Architecture Documentation
## Ollama Chatbot - Complete System Design

**Version:** 1.0.0
**Status:** Production
**Last Updated:** November 13, 2025
**Classification:** Technical Architecture

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [System Context](#2-system-context)
3. [Container Architecture](#3-container-architecture)
4. [Component Architecture](#4-component-architecture)
5. [Data Flow Architecture](#5-data-flow-architecture)
6. [Integration Architecture](#6-integration-architecture)
7. [Quality Attributes](#7-quality-attributes)
8. [Architecture Decisions](#8-architecture-decisions)

---

## 1. Architecture Overview

### 1.1 Executive Summary

The Ollama Chatbot implements a **dual-interface, plugin-extensible architecture** that provides both interactive UI and programmatic API access to local LLM models. The system is designed for privacy, offline operation, and zero-cost usage.

### 1.2 Architectural Style

**Primary Pattern:** Layered Architecture + Plugin Architecture + Microkernel Pattern

```
┌─────────────────────────────────────────────────────────┐
│           Presentation Layer (Dual Interface)            │
├───────────────────────┬─────────────────────────────────┤
│   Streamlit Web UI    │     Flask REST API              │
│   (Port 8501)         │     (Port 5000)                 │
└───────────────────────┴─────────────────────────────────┘
                           │
┌──────────────────────────────────────────────────────────┐
│              Business Logic Layer                         │
├──────────────────────────────────────────────────────────┤
│  Plugin Manager │ Hook System │ Circuit Breaker          │
│  Message Processing │ Auth │ Rate Limiting │ Audit       │
└──────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────────────────────────────────────┐
│              Integration Layer                            │
├──────────────────────────────────────────────────────────┤
│         Ollama Client (HTTP REST API)                     │
└──────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────────────────────────────────────┐
│              External System                              │
├──────────────────────────────────────────────────────────┤
│         Ollama Server (localhost:11434)                   │
│         LLM Models (llama3.2, mistral, phi3)              │
└──────────────────────────────────────────────────────────┘
```

### 1.3 Key Architectural Principles

| Principle | Implementation | Benefit |
|-----------|----------------|---------|
| **Separation of Concerns** | Layered architecture, plugin isolation | Easy to understand, modify, test |
| **Plugin Extensibility** | Microkernel with plugin system | Add features without core changes |
| **Fault Isolation** | Circuit breakers, try-catch blocks | One failure doesn't crash system |
| **Privacy by Design** | All processing local, no external calls | 100% data privacy |
| **Zero Dependencies** | Self-contained, no cloud services | Works offline, zero cost |
| **Dual Interface** | Streamlit + Flask in parallel | Serves both users and APIs |

---

## 2. System Context

### 2.1 System Context Diagram (C4 Level 1)

```
                    ┌─────────────────┐
                    │   End Users     │
                    │ (Web Browser)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Streamlit UI   │
                    │  (Port 8501)    │
                    └────────┬────────┘
                             │
    ┌────────────────────────┼────────────────────────┐
    │                        │                        │
┌───▼──────────┐   ┌────────▼────────┐   ┌─────────▼────────┐
│  Developers  │   │ OLLAMA CHATBOT  │   │  System Admin    │
│   (HTTP)     │───│   Application   │───│  (Monitoring)    │
└──────────────┘   │                 │   └──────────────────┘
                   └────────┬────────┘
                            │
                   ┌────────▼────────┐
                   │  Ollama Server  │
                   │  (localhost)    │
                   └────────┬────────┘
                            │
                   ┌────────▼────────┐
                   │   LLM Models    │
                   │ (llama3.2, etc) │
                   └─────────────────┘
```

### 2.2 External Dependencies

| System | Type | Purpose | Protocol | Status |
|--------|------|---------|----------|--------|
| **Ollama Server** | External | LLM inference engine | HTTP REST | Required |
| **LLM Models** | Data | AI models (llama3.2, mistral, phi3) | Binary files | Required |
| **Web Browser** | Client | UI access for Streamlit | HTTP/WebSocket | Optional |
| **HTTP Client** | Client | API access for Flask | HTTP REST | Optional |

### 2.3 User Personas

#### Persona 1: Privacy-Conscious User
- **Needs:** Secure, offline AI chatbot
- **Uses:** Streamlit UI for interactive chat
- **Key Feature:** 100% local processing, no data leaves machine

#### Persona 2: Developer/Integrator
- **Needs:** Programmatic API access
- **Uses:** Flask REST API for automation
- **Key Feature:** RESTful endpoints with JSON responses

#### Persona 3: System Administrator
- **Needs:** Monitoring, logging, health checks
- **Uses:** Both interfaces + log files
- **Key Feature:** Health endpoints, audit trails

---

## 3. Container Architecture

### 3.1 Container Diagram (C4 Level 2)

```
┌────────────────────────────────────────────────────────────────┐
│                     Ollama Chatbot System                       │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────┐   ┌─────────────────────────┐   │
│  │   Streamlit Container   │   │    Flask Container       │   │
│  ├─────────────────────────┤   ├─────────────────────────┤   │
│  │ Technology:             │   │ Technology:              │   │
│  │ - Python 3.13           │   │ - Python 3.13            │   │
│  │ - Streamlit 1.51.0      │   │ - Flask 3.1.2            │   │
│  │ - WebSocket             │   │ - REST API               │   │
│  │                         │   │ - JSON                   │   │
│  │ Responsibilities:       │   │ Responsibilities:        │   │
│  │ - Web UI rendering      │   │ - HTTP API endpoints     │   │
│  │ - User session mgmt     │   │ - Request validation     │   │
│  │ - Real-time streaming   │   │ - Response formatting    │   │
│  │ - Chat history          │   │ - Error handling         │   │
│  │                         │   │                          │   │
│  │ Port: 8501              │   │ Port: 5000               │   │
│  └────────────┬────────────┘   └────────────┬─────────────┘   │
│               │                             │                  │
│               └──────────────┬──────────────┘                  │
│                              │                                 │
│              ┌───────────────▼────────────────┐                │
│              │   Plugin System Container      │                │
│              ├────────────────────────────────┤                │
│              │ Technology:                    │                │
│              │ - Python 3.13                  │                │
│              │ - Async/await                  │                │
│              │ - Protocol-based plugins       │                │
│              │                                │                │
│              │ Components:                    │                │
│              │ - PluginManager                │                │
│              │ - HookManager                  │                │
│              │ - CircuitBreaker               │                │
│              │ - ConfigLoader                 │                │
│              │                                │                │
│              │ Plugins:                       │                │
│              │ - Auth Plugin                  │                │
│              │ - Rate Limit Plugin            │                │
│              │ - Audit Plugin                 │                │
│              │ - Content Filter Plugin        │                │
│              └───────────────┬────────────────┘                │
│                              │                                 │
│              ┌───────────────▼────────────────┐                │
│              │  Ollama Client Container       │                │
│              ├────────────────────────────────┤                │
│              │ Technology:                    │                │
│              │ - Python ollama library        │                │
│              │ - HTTP REST client             │                │
│              │ - Async streaming              │                │
│              │                                │                │
│              │ Responsibilities:              │                │
│              │ - Model listing                │                │
│              │ - Chat requests                │                │
│              │ - Generate requests            │                │
│              │ - Streaming responses          │                │
│              │ - Error handling               │                │
│              └───────────────┬────────────────┘                │
└──────────────────────────────┼─────────────────────────────────┘
                               │
                               │ HTTP REST
                               │ localhost:11434
                               │
┌──────────────────────────────▼─────────────────────────────────┐
│                     Ollama Server                               │
│                   (External System)                             │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Container Responsibilities

#### **Streamlit Container**
- **Purpose:** Interactive web UI for end users
- **Technology Stack:** Python 3.13, Streamlit 1.51.0
- **Key Features:**
  - Real-time message streaming with WebSocket
  - Session state management
  - Chat history persistence (JSON files)
  - Model and temperature selection
  - Responsive CSS styling
- **Dependencies:** Plugin System Container, Ollama Client Container
- **Deployment:** Python script launched via launcher

#### **Flask Container**
- **Purpose:** RESTful API for programmatic access
- **Technology Stack:** Python 3.13, Flask 3.1.2
- **Key Features:**
  - 5 REST endpoints (/, /health, /models, /chat, /generate)
  - JSON request/response
  - Streaming support via Server-Sent Events
  - CORS enabled
  - Error handling middleware
- **Dependencies:** Plugin System Container, Ollama Client Container
- **Deployment:** WSGI server via launcher

#### **Plugin System Container**
- **Purpose:** Extensibility framework for adding features
- **Technology Stack:** Python 3.13, Async/await
- **Key Features:**
  - Protocol-based plugin interfaces
  - Hook system with priority queues
  - Dependency injection
  - Circuit breakers for fault tolerance
  - Hot-reload support
- **Dependencies:** None (core system)
- **Deployment:** Loaded by application containers

#### **Ollama Client Container**
- **Purpose:** Integration with Ollama LLM server
- **Technology Stack:** Python ollama library
- **Key Features:**
  - Async HTTP client
  - Streaming response handling
  - Model management
  - Error propagation
- **Dependencies:** Ollama Server (external)
- **Deployment:** Library imported by containers

---

## 4. Component Architecture

### 4.1 Component Diagram (C4 Level 3)

#### Streamlit Application Components

```
┌──────────────────────────────────────────────────────────┐
│          Streamlit Application (app_streamlit.py)        │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │         UI Component (Streamlit Native)         │    │
│  ├─────────────────────────────────────────────────┤    │
│  │ - st.title() - Header rendering                 │    │
│  │ - st.selectbox() - Model selection dropdown     │    │
│  │ - st.slider() - Temperature control             │    │
│  │ - st.chat_message() - Message display           │    │
│  │ - st.chat_input() - User input field            │    │
│  │ - st.markdown() - Custom CSS injection          │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│  ┌───────────────────────▼─────────────────────────┐    │
│  │      Session State Manager (st.session_state)   │    │
│  ├─────────────────────────────────────────────────┤    │
│  │ - messages: List[Dict] - Chat history           │    │
│  │ - selected_model: str - Current model           │    │
│  │ - temperature: float - Generation param         │    │
│  │ - session_id: str - Unique identifier           │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│  ┌───────────────────────▼─────────────────────────┐    │
│  │       History Manager (save/load functions)     │    │
│  ├─────────────────────────────────────────────────┤    │
│  │ - save_to_json() - Persist messages             │    │
│  │ - load_from_json() - Restore messages           │    │
│  │ - generate_session_id() - Create unique ID      │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│  ┌───────────────────────▼─────────────────────────┐    │
│  │      Message Processor (handle_user_message)    │    │
│  ├─────────────────────────────────────────────────┤    │
│  │ - Validate user input                           │    │
│  │ - Call Ollama client                            │    │
│  │ - Stream response                               │    │
│  │ - Update session state                          │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
└──────────────────────────┼───────────────────────────────┘
                           │
                    [Ollama Client]
```

#### Flask Application Components

```
┌──────────────────────────────────────────────────────────┐
│            Flask Application (app_flask.py)              │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │        Route Handlers (Flask @app.route)        │    │
│  ├─────────────────────────────────────────────────┤    │
│  │ - GET  /           - Landing page               │    │
│  │ - GET  /health     - Health check endpoint      │    │
│  │ - GET  /models     - List available models      │    │
│  │ - POST /chat       - Chat completion            │    │
│  │ - POST /generate   - Text generation            │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│  ┌───────────────────────▼─────────────────────────┐    │
│  │       Request Validator (validate_request)      │    │
│  ├─────────────────────────────────────────────────┤    │
│  │ - Check required fields                         │    │
│  │ - Validate data types                           │    │
│  │ - Sanitize inputs                               │    │
│  │ - Return 400 on invalid                         │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│  ┌───────────────────────▼─────────────────────────┐    │
│  │     Response Formatter (format_response)        │    │
│  ├─────────────────────────────────────────────────┤    │
│  │ - Convert to JSON                               │    │
│  │ - Add metadata (timestamp, model)               │    │
│  │ - Set HTTP status codes                         │    │
│  │ - Handle streaming (SSE)                        │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│  ┌───────────────────────▼─────────────────────────┐    │
│  │     Error Handler (@app.errorhandler)           │    │
│  ├─────────────────────────────────────────────────┤    │
│  │ - ConnectionError → 503                         │    │
│  │ - TimeoutError → 504                            │    │
│  │ - ValueError → 400                              │    │
│  │ - Exception → 500                               │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
└──────────────────────────┼───────────────────────────────┘
                           │
                    [Ollama Client]
```

### 4.2 Plugin System Components

See `docs/architecture/plugin-system.md` for detailed plugin architecture (1,277 lines).

---

## 5. Data Flow Architecture

### 5.1 Chat Request Flow (Streamlit)

```
┌────────────┐
│    User    │
└──────┬─────┘
       │ 1. Enter message
       │
┌──────▼─────────────────────────────────────────────────┐
│  Streamlit UI (st.chat_input)                          │
└──────┬─────────────────────────────────────────────────┘
       │ 2. Validate non-empty
       │
┌──────▼─────────────────────────────────────────────────┐
│  Session State (st.session_state.messages.append)      │
└──────┬─────────────────────────────────────────────────┘
       │ 3. Add user message to history
       │
┌──────▼─────────────────────────────────────────────────┐
│  Message Processor (handle_user_message)               │
└──────┬─────────────────────────────────────────────────┘
       │ 4. Prepare request dict
       │
┌──────▼─────────────────────────────────────────────────┐
│  Ollama Client (ollama.chat)                           │
└──────┬─────────────────────────────────────────────────┘
       │ 5. HTTP POST to Ollama Server
       │
┌──────▼─────────────────────────────────────────────────┐
│  Ollama Server (localhost:11434)                       │
└──────┬─────────────────────────────────────────────────┘
       │ 6. LLM inference
       │
┌──────▼─────────────────────────────────────────────────┐
│  Streaming Response (chunk by chunk)                   │
└──────┬─────────────────────────────────────────────────┘
       │ 7. st.write_stream() display
       │
┌──────▼─────────────────────────────────────────────────┐
│  Session State (append assistant message)              │
└──────┬─────────────────────────────────────────────────┘
       │ 8. Save to JSON file
       │
┌──────▼─────────────────────────────────────────────────┐
│  History File (chat_history_{session_id}.json)         │
└────────────────────────────────────────────────────────┘
```

### 5.2 API Request Flow (Flask)

```
┌────────────┐
│HTTP Client │
└──────┬─────┘
       │ 1. POST /chat with JSON body
       │
┌──────▼─────────────────────────────────────────────────┐
│  Flask Route Handler (@app.route('/chat'))             │
└──────┬─────────────────────────────────────────────────┘
       │ 2. Extract JSON data
       │
┌──────▼─────────────────────────────────────────────────┐
│  Request Validator (check required fields)             │
└──────┬─────────────────────────────────────────────────┘
       │ 3. Validate message field exists
       │
┌──────▼─────────────────────────────────────────────────┐
│  Plugin System (before_request hooks)                  │
└──────┬─────────────────────────────────────────────────┘
       │ 4. Rate limiting, auth, audit
       │
┌──────▼─────────────────────────────────────────────────┐
│  Ollama Client (ollama.chat)                           │
└──────┬─────────────────────────────────────────────────┘
       │ 5. HTTP POST to Ollama Server
       │
┌──────▼─────────────────────────────────────────────────┐
│  Ollama Server (localhost:11434)                       │
└──────┬─────────────────────────────────────────────────┘
       │ 6. LLM inference
       │
┌──────▼─────────────────────────────────────────────────┐
│  Response (streaming or complete)                      │
└──────┬─────────────────────────────────────────────────┘
       │ 7. Format JSON response
       │
┌──────▼─────────────────────────────────────────────────┐
│  Plugin System (after_response hooks)                  │
└──────┬─────────────────────────────────────────────────┘
       │ 8. Audit logging
       │
┌──────▼─────────────────────────────────────────────────┐
│  HTTP Response (200 OK with JSON body)                 │
└──────┬─────────────────────────────────────────────────┘
       │ 9. Return to client
       │
┌──────▼─────┐
│HTTP Client │
└────────────┘
```

### 5.3 Plugin Execution Flow

```
Request
   │
   ▼
┌──────────────────────────────────────┐
│    PluginManager.execute_hooks       │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│   Get plugins for hook type          │
│   (e.g., "before_request")           │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│   Sort plugins by priority           │
│   (topological sort if dependencies) │
└──────────────┬───────────────────────┘
               │
               ▼
      ┌────────┴────────┐
      │                 │
   ┌──▼──┐          ┌──▼──┐
   │P1   │          │P2   │  ... (for each plugin)
   │(10) │          │(20) │
   └──┬──┘          └──┬──┘
      │                │
      ▼                ▼
┌──────────────────────────────────────┐
│   Circuit Breaker Check              │
│   (is plugin healthy?)               │
└──────────────┬───────────────────────┘
               │
         ┌─────┴─────┐
         │           │
      Yes▼        No ▼
  ┌─────────┐   ┌────────┐
  │Execute  │   │Skip    │
  │Plugin   │   │Plugin  │
  └────┬────┘   └────┬───┘
       │             │
       └──────┬──────┘
              │
              ▼
┌──────────────────────────────────────┐
│   Aggregate results                  │
│   (all plugins executed)             │
└──────────────┬───────────────────────┘
               │
               ▼
           Response
```

---

## 6. Integration Architecture

### 6.1 External Integration: Ollama Server

**Protocol:** HTTP REST API
**Endpoint:** `http://localhost:11434`
**Authentication:** None (localhost only)

**Key APIs Used:**

| API Endpoint | Method | Purpose | Response Type |
|--------------|--------|---------|---------------|
| `/api/tags` | GET | List available models | JSON |
| `/api/chat` | POST | Chat completion | Streaming JSON |
| `/api/generate` | POST | Text generation | Streaming JSON |

**Integration Pattern:**
- **Polling:** No (push-based streaming)
- **Retry Logic:** Yes (handled by ollama library)
- **Timeout:** 30 seconds default
- **Error Handling:** Connection errors caught and reported

### 6.2 File System Integration

**Purpose:** Chat history persistence

**File Locations:**
- Streamlit: `./chat_history_{session_id}.json`
- Flask: No persistence (stateless)

**File Format:**
```json
{
  "session_id": "abc123",
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2025-11-13T10:30:00"
    },
    {
      "role": "assistant",
      "content": "Hi there!",
      "timestamp": "2025-11-13T10:30:05"
    }
  ]
}
```

---

## 7. Quality Attributes

### 7.1 Quality Attribute Scenarios

#### **Performance**
- **Scenario:** User sends chat message
- **Measure:** First token within 2 seconds
- **Current:** Depends on model (1-5 seconds)
- **Architecture Support:** Async streaming, no blocking

#### **Availability**
- **Scenario:** Ollama server temporarily unavailable
- **Measure:** System remains responsive
- **Current:** Graceful error messages, no crashes
- **Architecture Support:** Try-catch blocks, circuit breakers

#### **Scalability**
- **Scenario:** Multiple users (10+) using system
- **Measure:** No degradation in response time
- **Current:** Limited by Ollama server capacity
- **Architecture Support:** Stateless Flask API, session isolation

#### **Maintainability**
- **Scenario:** Add new plugin feature
- **Measure:** < 1 hour to implement and test
- **Current:** Well-documented plugin interface
- **Architecture Support:** Plugin architecture, SOLID principles

#### **Security**
- **Scenario:** Malicious input attempt
- **Measure:** System rejects invalid input
- **Current:** Input validation on all endpoints
- **Architecture Support:** Validation middleware, plugins

---

## 8. Architecture Decisions

### 8.1 ADR-001: Dual Interface (Streamlit + Flask)

**Status:** Accepted

**Context:** Need to serve both end users (UI) and developers (API).

**Decision:** Implement TWO complete applications (Streamlit for UI, Flask for API).

**Consequences:**
- ✅ Maximum flexibility (can use either or both)
- ✅ Clear separation of concerns
- ❌ Increased code to maintain (2 applications)
- ❌ Duplicate Ollama integration logic

**Alternatives Considered:**
- Single Flask app with HTML templates (rejected: less rich UI)
- Streamlit only with custom API endpoints (rejected: limited API flexibility)

---

### 8.2 ADR-002: Local-Only Architecture (No Cloud)

**Status:** Accepted

**Context:** Privacy concerns with cloud AI services.

**Decision:** All processing happens locally on user's machine.

**Consequences:**
- ✅ 100% data privacy
- ✅ Zero ongoing costs
- ✅ Works offline
- ❌ Requires local Ollama installation
- ❌ Limited by user's hardware

**Alternatives Considered:**
- Cloud API (OpenAI, Anthropic) - rejected: privacy/cost concerns
- Hybrid (local + cloud fallback) - rejected: complexity

---

### 8.3 ADR-003: Plugin Architecture for Extensibility

**Status:** Accepted

**Context:** Need to add features (auth, rate limiting) without modifying core code.

**Decision:** Implement microkernel pattern with plugin system.

**Consequences:**
- ✅ Easy to add new features
- ✅ Core code remains stable
- ✅ Plugins can be tested independently
- ❌ Complexity in plugin manager
- ❌ Performance overhead (minimal)

**Alternatives Considered:**
- Monolithic architecture - rejected: hard to extend
- Microservices - rejected: overkill for local app

---

### 8.4 ADR-004: Async/Await for Streaming

**Status:** Accepted

**Context:** LLM responses are streamed token-by-token.

**Decision:** Use Python async/await for non-blocking streaming.

**Consequences:**
- ✅ Responsive UI during generation
- ✅ Can cancel long-running requests
- ✅ Better resource utilization
- ❌ Complexity in async code
- ❌ Requires Python 3.7+

**Alternatives Considered:**
- Synchronous blocking - rejected: poor UX
- Threading - rejected: complexity, GIL issues

---

## 9. Deployment View

### 9.1 Deployment Diagram

```
┌─────────────────────────────────────────────────────────┐
│              User's Local Machine                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   Browser    │         │ HTTP Client  │             │
│  └──────┬───────┘         └──────┬───────┘             │
│         │                        │                      │
│         │ Port 8501              │ Port 5000            │
│         │                        │                      │
│  ┌──────▼────────────────────────▼──────┐              │
│  │   Python 3.13 Runtime                │              │
│  ├──────────────────────────────────────┤              │
│  │                                       │              │
│  │  ┌─────────────┐  ┌────────────┐    │              │
│  │  │  Streamlit  │  │   Flask    │    │              │
│  │  │   Process   │  │  Process   │    │              │
│  │  └─────────────┘  └────────────┘    │              │
│  │                                       │              │
│  │       Plugin System Shared           │              │
│  │                                       │              │
│  └───────────────────┬───────────────────┘             │
│                      │                                  │
│                      │ localhost:11434                  │
│                      │                                  │
│  ┌───────────────────▼───────────────────┐             │
│  │      Ollama Server Process            │             │
│  ├───────────────────────────────────────┤             │
│  │  - LLM Models (4-40GB RAM)            │             │
│  │  - HTTP Server (port 11434)           │             │
│  │  - Model inference engine             │             │
│  └───────────────────────────────────────┘             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 9.2 Deployment Modes

#### Mode 1: Dual Deployment (Both Interfaces)
```bash
# Terminal 1
./scripts/launch_streamlit.sh

# Terminal 2
./scripts/launch_flask.sh
```

#### Mode 2: Streamlit Only
```bash
./scripts/launch_streamlit.sh
```

#### Mode 3: Flask API Only
```bash
./scripts/launch_flask.sh
```

#### Mode 4: Docker Deployment
```bash
docker-compose up
```

---

## 10. Technology Stack

### 10.1 Complete Technology Inventory

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Language** | Python | 3.13 | Core language |
| **UI Framework** | Streamlit | 1.51.0 | Web UI |
| **API Framework** | Flask | 3.1.2 | REST API |
| **LLM Client** | ollama-python | 0.4.5 | Ollama integration |
| **Testing** | pytest | 8.3.4 | Unit/integration tests |
| **Coverage** | pytest-cov | 6.0.0 | Code coverage |
| **Async** | asyncio | Built-in | Async execution |
| **Type Checking** | mypy | 1.14.0 | Static type checking |
| **Linting** | ruff | 0.8.4 | Code quality |
| **Package Manager** | uv | 0.5.10 | Fast dependency mgmt |
| **Containerization** | Docker | Latest | Deployment |
| **Process Manager** | systemd | N/A | Service management |

---

## 11. Scalability Considerations

### 11.1 Current Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Single Ollama Instance** | Bottleneck for concurrent requests | Rate limiting plugin |
| **Local Hardware** | Limited by RAM/CPU | Model size selection |
| **No Load Balancing** | One machine serves all | Acceptable for local use |
| **Stateful Streamlit** | Session storage in memory | Acceptable for single user |

### 11.2 Future Scalability Options

If scaling needed (not current goal):
- **Horizontal:** Multiple Ollama instances with load balancer
- **Vertical:** Larger models on more powerful hardware
- **Distributed:** Cluster of machines running Ollama
- **Cloud:** Deploy to cloud VM with persistent storage

---

## 12. Monitoring and Observability

### 12.1 Health Checks

**Flask API:**
```bash
curl http://localhost:5000/health
# Response: {"status": "healthy", "ollama": "connected"}
```

**Streamlit UI:**
- Visual indicators in sidebar
- Connection status displayed

### 12.2 Logging

**Log Locations:**
- Streamlit: Console output (stdout)
- Flask: Console output + app.log (if configured)
- Ollama: `~/.ollama/logs/server.log`

**Log Levels:**
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Critical failures
- DEBUG: Detailed diagnostics

---

## 13. Security Architecture

See `docs/architecture/security-architecture.md` for comprehensive security design.

**Quick Summary:**
- ✅ All processing local (no external data transmission)
- ✅ Input validation on all endpoints
- ✅ Rate limiting to prevent abuse
- ✅ Audit logging for accountability
- ✅ No hardcoded secrets
- ✅ CORS configured for API

---

## Conclusion

This system architecture provides a **solid foundation** for a privacy-focused, offline AI chatbot with dual interfaces and plugin extensibility. The architecture prioritizes **simplicity, privacy, and extensibility** while maintaining **production-ready quality**.

**Key Architectural Strengths:**
- Dual interface serves multiple use cases
- Plugin system enables extensibility
- Local-only ensures 100% privacy
- Layered architecture promotes maintainability
- Fault isolation prevents cascading failures

**Architecture Maturity:** Production-ready for local deployment.

---

**Document Version:** 1.0.0
**Last Updated:** November 13, 2025
**Next Review:** Upon major architectural changes
