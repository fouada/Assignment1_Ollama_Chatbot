# Reusable Components Guide
## Extract and Adapt Components from This Project

**Everything in this project is designed to be reusable. Here's your guide to taking what you need.**

---

## Table of Contents

- [Quick Reference](#quick-reference)
- [Plugin System](#plugin-system)
- [Quality Testing Framework](#quality-testing-framework)
- [Accessibility Patterns](#accessibility-patterns)
- [Security Components](#security-components)
- [Research Tools](#research-tools)
- [Documentation Templates](#documentation-templates)
- [Code Snippets Library](#code-snippets-library)

---

## Quick Reference

### What Can You Reuse?

| Component | Reusability | Adaptation Needed | License |
|-----------|-------------|-------------------|---------|
| **Plugin System** | ⭐⭐⭐⭐⭐ | Minimal | MIT |
| **ISO 25010 Tests** | ⭐⭐⭐⭐⭐ | Domain-specific | MIT |
| **WCAG Patterns** | ⭐⭐⭐⭐⭐ | None | MIT |
| **Security Plugins** | ⭐⭐⭐⭐ | Config only | MIT |
| **Research Tools** | ⭐⭐⭐⭐ | Model-specific | MIT |
| **Circuit Breaker** | ⭐⭐⭐⭐⭐ | None | MIT |
| **Audit Trail** | ⭐⭐⭐⭐ | Minimal | MIT |
| **Documentation** | ⭐⭐⭐⭐⭐ | Project-specific | MIT |

---

## Plugin System

### What Is It?

A production-grade, protocol-based plugin architecture that enables extensibility without modifying core code.

### Why Reuse It?

- ✅ Battle-tested design patterns
- ✅ Hot-reload capability
- ✅ Circuit breaker built-in
- ✅ Priority-based execution
- ✅ Comprehensive error handling

### Files to Copy

```bash
# Core plugin system (copy these files)
plugins/
├── plugin_interface.py    # Base plugin protocol
├── types.py               # Type definitions
├── plugin_manager.py      # Plugin loader and executor
├── hooks.py              # Hook system with circuit breaker
└── config_loader.py       # Configuration management
```

### Adaptation Steps

#### Step 1: Copy Files

```bash
# Create plugins directory in your project
mkdir -p your_project/plugins

# Copy core files
cp plugins/plugin_interface.py your_project/plugins/
cp plugins/types.py your_project/plugins/
cp plugins/plugin_manager.py your_project/plugins/
cp plugins/hooks.py your_project/plugins/
cp plugins/config_loader.py your_project/plugins/
```

#### Step 2: Adapt for Your Domain

```python
# Example: Adapting for a web scraping application

# your_project/plugins/scraping_plugin_interface.py
from plugins.plugin_interface import PluginInterface
from typing import Dict, List

class ScrapingPluginInterface(PluginInterface):
    """Extended interface for scraping plugins"""

    async def before_scrape(self, url: str, options: Dict) -> Dict:
        """Hook before scraping a URL"""
        pass

    async def after_scrape(self, url: str, data: Dict) -> Dict:
        """Hook after scraping a URL"""
        pass

    async def process_scraped_data(self, data: Dict) -> Dict:
        """Process scraped data"""
        pass
```

#### Step 3: Create Your First Plugin

```python
# your_project/plugins/custom/rate_limiter_scraper.py
from plugins.scraping_plugin_interface import ScrapingPluginInterface
from plugins.types import PluginResult
import asyncio

class RateLimiterScraperPlugin(ScrapingPluginInterface):
    """Rate limit scraping requests"""

    def __init__(self):
        self.plugin_name = "rate_limiter_scraper"
        self.plugin_version = "1.0.0"
        self.last_request_time = 0
        self.min_delay = 1.0  # 1 second between requests

    async def initialize(self, config: Dict) -> PluginResult[None]:
        self.min_delay = config.get("min_delay_seconds", 1.0)
        return PluginResult.ok(None)

    async def before_scrape(self, url: str, options: Dict) -> Dict:
        """Enforce rate limiting before scraping"""
        import time

        # Calculate time since last request
        now = time.time()
        elapsed = now - self.last_request_time

        # Wait if needed
        if elapsed < self.min_delay:
            wait_time = self.min_delay - elapsed
            await asyncio.sleep(wait_time)

        self.last_request_time = time.time()

        return options  # Return modified options
```

#### Step 4: Use in Your Application

```python
# your_project/main.py
from plugins.plugin_manager import PluginManager
from plugins.hooks import HookManager

async def main():
    # Initialize plugin system
    plugin_manager = PluginManager()
    await plugin_manager.load_plugins("plugins/custom/")

    hook_manager = HookManager()
    hook_manager.register_plugins(plugin_manager.get_all_plugins())

    # Use plugins in your scraping logic
    async def scrape_url(url: str):
        # Execute before_scrape hooks (includes rate limiting)
        options = {"url": url}
        options = await hook_manager.execute_hook("before_scrape", options)

        # Your scraping logic
        data = await your_scraping_function(url)

        # Execute after_scrape hooks
        data = await hook_manager.execute_hook("after_scrape", data)

        return data

    # Scrape multiple URLs with automatic rate limiting
    urls = ["http://example.com/page1", "http://example.com/page2"]
    for url in urls:
        data = await scrape_url(url)  # Automatically rate-limited!
```

### Real-World Examples

#### Example 1: FastAPI Middleware

```python
from fastapi import FastAPI, Request
from plugins.plugin_manager import PluginManager

app = FastAPI()
plugin_manager = PluginManager()

@app.on_event("startup")
async def startup():
    await plugin_manager.load_plugins("plugins/")

@app.middleware("http")
async def plugin_middleware(request: Request, call_next):
    # Before request - execute plugins
    context = {"request": request, "path": request.url.path}
    context = await plugin_manager.execute_hook("before_request", context)

    # Process request
    response = await call_next(request)

    # After request - execute plugins
    context["response"] = response
    context = await plugin_manager.execute_hook("after_request", context)

    return response
```

#### Example 2: Data Processing Pipeline

```python
from plugins.plugin_manager import PluginManager

class DataPipeline:
    """Data processing pipeline with plugins"""

    def __init__(self):
        self.plugin_manager = PluginManager()

    async def initialize(self):
        await self.plugin_manager.load_plugins("plugins/processors/")

    async def process(self, data: Dict) -> Dict:
        """Process data through plugin pipeline"""

        # Validation plugins
        data = await self.plugin_manager.execute_hook("validate", data)

        # Transformation plugins
        data = await self.plugin_manager.execute_hook("transform", data)

        # Enrichment plugins
        data = await self.plugin_manager.execute_hook("enrich", data)

        # Output plugins
        data = await self.plugin_manager.execute_hook("output", data)

        return data
```

---

## Quality Testing Framework

### What Is It?

Comprehensive ISO/IEC 25010 quality testing framework with 1,009 lines of tests covering all 8 quality characteristics.

### Why Reuse It?

- ✅ Systematic quality assurance
- ✅ International standard (ISO 25010)
- ✅ 100% test coverage methodology
- ✅ Academic/certification ready

### Files to Copy

```bash
tests/
├── test_iso25010_compliance.py   # Main quality tests (1,009 lines)
├── conftest.py                    # Pytest fixtures
└── test_accessibility.py          # Accessibility tests (398 lines)
```

### Adaptation Steps

#### Step 1: Copy Test Framework

```bash
# Copy test files
cp tests/test_iso25010_compliance.py your_project/tests/
cp tests/conftest.py your_project/tests/

# Install dependencies
pip install pytest pytest-cov pytest-asyncio
```

#### Step 2: Adapt for Your System

```python
# your_project/tests/test_my_app_quality.py
import pytest
from test_iso25010_compliance import ISO25010TestFramework

class TestMyAppQuality(ISO25010TestFramework):
    """Quality tests for My Application"""

    @pytest.fixture
    def app(self):
        """Fixture providing your application instance"""
        from your_app import create_app
        return create_app()

    # 1. Functional Suitability Tests
    def test_functional_completeness(self, app):
        """Test all required functions exist"""
        required_functions = [
            "/api/users",
            "/api/products",
            "/api/orders"
        ]

        for endpoint in required_functions:
            response = app.client.get(endpoint)
            assert response.status_code != 404, f"{endpoint} not implemented"

    def test_functional_correctness(self, app):
        """Test functions produce correct results"""
        # Test calculation correctness
        response = app.client.post("/api/calculate", json={"a": 2, "b": 3})
        assert response.json()["result"] == 5

    # 2. Performance Efficiency Tests
    def test_time_behaviour(self, app):
        """Test response time meets SLA"""
        import time

        start = time.time()
        response = app.client.get("/api/products")
        duration = time.time() - start

        assert duration < 2.0, f"Response too slow: {duration}s"
        assert response.status_code == 200

    def test_resource_utilization(self, app):
        """Test resource usage is efficient"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024**2  # MB

        # Perform operations
        for _ in range(100):
            app.client.get("/api/products")

        mem_after = process.memory_info().rss / 1024**2
        mem_delta = mem_after - mem_before

        assert mem_delta < 100, f"Memory leak detected: {mem_delta}MB"

    # 3. Security Tests
    def test_authentication_required(self, app):
        """Test authentication is enforced"""
        protected_endpoints = ["/api/admin", "/api/users/profile"]

        for endpoint in protected_endpoints:
            response = app.client.get(endpoint)  # No auth token
            assert response.status_code == 401

    def test_sql_injection_protection(self, app):
        """Test SQL injection is prevented"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--"
        ]

        for malicious in malicious_inputs:
            response = app.client.get(f"/api/users?name={malicious}")
            # Should not cause error, should be escaped
            assert response.status_code in [200, 400]
            # Should not return all users
            assert len(response.json()) < 100

    # Add more tests for other ISO 25010 characteristics...
```

#### Step 3: Run Quality Tests

```bash
# Run all quality tests
pytest tests/test_my_app_quality.py -v

# Generate coverage report
pytest tests/test_my_app_quality.py --cov=your_app --cov-report=html

# Run specific characteristic tests
pytest tests/test_my_app_quality.py -k "security"
```

### Quality Checklist Template

```markdown
# ISO 25010 Quality Checklist

## Functional Suitability
- [ ] Functional Completeness - All specified functions implemented
- [ ] Functional Correctness - Functions produce correct results
- [ ] Functional Appropriateness - Functions facilitate tasks

## Performance Efficiency
- [ ] Time Behaviour - Response time < [YOUR_SLA]s
- [ ] Resource Utilization - Memory < [YOUR_LIMIT]MB
- [ ] Capacity - Handles [YOUR_LOAD] concurrent users

## Compatibility
- [ ] Co-existence - Works with other systems
- [ ] Interoperability - Exchanges data correctly

## Usability
- [ ] Appropriateness Recognizability - Purpose is clear
- [ ] Learnability - Easy to learn
- [ ] Operability - Easy to operate
- [ ] User Error Protection - Prevents errors
- [ ] Accessibility - WCAG 2.1 Level AA

## Reliability
- [ ] Maturity - Meets reliability needs
- [ ] Availability - Uptime > 99%
- [ ] Fault Tolerance - Operates despite faults
- [ ] Recoverability - Recovers from failures

## Security
- [ ] Confidentiality - Protects information
- [ ] Integrity - Prevents unauthorized modification
- [ ] Non-repudiation - Actions provably occurred
- [ ] Accountability - Actions are traceable
- [ ] Authenticity - Identity is provable

## Maintainability
- [ ] Modularity - Discrete components
- [ ] Reusability - Components are reusable
- [ ] Analysability - Easy to diagnose
- [ ] Modifiability - Easy to modify
- [ ] Testability - Easy to test

## Portability
- [ ] Adaptability - Works in different environments
- [ ] Installability - Easy to install
- [ ] Replaceability - Can replace other systems
```

---

## Accessibility Patterns

### What Is It?

WCAG 2.1 Level AA compliant accessibility patterns for AI interfaces.

### Why Reuse It?

- ✅ Legal compliance (ADA, EN 301 549)
- ✅ Tested with screen readers
- ✅ Complete implementation
- ✅ Rare in AI projects

### Files to Copy

```bash
# Accessibility implementation
apps/app_streamlit_accessible.py  # Full accessible Streamlit app
tests/test_accessibility.py       # Accessibility tests
```

### Accessibility Patterns Library

#### Pattern 1: ARIA Live Regions for Dynamic Content

```python
# For AI streaming responses
import streamlit as st

def create_aria_live_region(region_id: str, politeness: str = "polite"):
    """
    Create ARIA live region for dynamic content updates.

    Args:
        region_id: Unique identifier for the region
        politeness: "polite" (waits for pause) or "assertive" (immediate)
    """
    st.markdown(f'''
        <div id="{region_id}"
             role="status"
             aria-live="{politeness}"
             aria-atomic="true"
             class="sr-accessible">
        </div>
    ''', unsafe_allow_html=True)

# Usage in your app
create_aria_live_region("chat-response", "polite")

# When streaming AI response
st.markdown('''
    <script>
    document.getElementById('chat-response').textContent = "AI is thinking...";
    </script>
''', unsafe_allow_html=True)
```

#### Pattern 2: Keyboard Navigation

```python
def create_keyboard_accessible_button(
    label: str,
    action_id: str,
    accesskey: str = None
):
    """
    Create button with full keyboard support.

    Args:
        label: Button label
        action_id: Unique ID for the button
        accesskey: Optional keyboard shortcut (e.g., "s" for Alt+S)
    """
    accesskey_attr = f'accesskey="{accesskey}"' if accesskey else ''

    st.markdown(f'''
        <button id="{action_id}"
                class="accessible-button"
                {accesskey_attr}
                tabindex="0"
                role="button"
                aria-label="{label}">
            {label}
            {f'<span class="accesskey-hint">(Alt+{accesskey})</span>' if accesskey else ''}
        </button>
    ''', unsafe_allow_html=True)

# Usage
create_keyboard_accessible_button("Send Message", "send-btn", "s")
```

#### Pattern 3: High Contrast Mode

```python
def apply_high_contrast_mode():
    """Apply high contrast styles for visibility"""
    st.markdown('''
        <style>
        .high-contrast {
            background: #000 !important;
            color: #fff !important;
        }

        .high-contrast button {
            background: #fff !important;
            color: #000 !important;
            border: 3px solid #fff !important;
        }

        .high-contrast input {
            background: #000 !important;
            color: #fff !important;
            border: 3px solid #fff !important;
        }

        /* Ensure 7:1 contrast ratio */
        .high-contrast a {
            color: #4da6ff !important;  /* Light blue on black */
        }
        </style>
    ''', unsafe_allow_html=True)

# Usage
if st.sidebar.checkbox("High Contrast Mode"):
    apply_high_contrast_mode()
```

#### Pattern 4: Screen Reader Announcements

```python
def announce_to_screen_reader(message: str, priority: str = "polite"):
    """
    Announce message to screen readers without visual display.

    Args:
        message: Message to announce
        priority: "polite" or "assertive"
    """
    st.markdown(f'''
        <div role="status"
             aria-live="{priority}"
             aria-atomic="true"
             class="sr-only">
            {message}
        </div>

        <style>
        .sr-only {{
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0,0,0,0);
            white-space: nowrap;
            border-width: 0;
        }}
        </style>
    ''', unsafe_allow_html=True)

# Usage
announce_to_screen_reader("Your message was sent successfully")
```

#### Pattern 5: Focus Management

```python
def set_focus(element_id: str):
    """Set focus to specific element (for keyboard navigation)"""
    st.markdown(f'''
        <script>
        (function() {{
            const element = document.getElementById('{element_id}');
            if (element) {{
                element.focus();
                // Also move visual viewport to element
                element.scrollIntoView({{
                    behavior: 'smooth',
                    block: 'center'
                }});
            }}
        }})();
        </script>
    ''', unsafe_allow_html=True)

# Usage after form submission
set_focus("message-input")
```

### Complete Accessible Form Example

```python
def create_accessible_chat_interface():
    """Complete accessible chat interface"""

    st.markdown('<h1 id="main-heading" tabindex="-1">AI Chat Assistant</h1>',
                unsafe_allow_html=True)

    # Skip to main content link
    st.markdown('''
        <a href="#chat-input" class="skip-link">
            Skip to chat input
        </a>
        <style>
        .skip-link {
            position: absolute;
            top: -40px;
            left: 0;
            background: #000;
            color: #fff;
            padding: 8px;
            z-index: 100;
        }
        .skip-link:focus {
            top: 0;
        }
        </style>
    ''', unsafe_allow_html=True)

    # Accessible input with label
    st.markdown('''
        <label for="chat-input" class="input-label">
            Your message (required)
        </label>
        <input id="chat-input"
               type="text"
               aria-required="true"
               aria-describedby="input-hint"
               placeholder="Type your message..."
               class="chat-input">
        <div id="input-hint" class="hint-text">
            Press Enter to send, Shift+Enter for new line
        </div>
    ''', unsafe_allow_html=True)

    # Accessible send button
    st.markdown('''
        <button id="send-button"
                type="button"
                aria-label="Send message"
                accesskey="s">
            Send <span class="accesskey-hint">(Alt+S)</span>
        </button>
    ''', unsafe_allow_html=True)

    # ARIA live region for responses
    st.markdown('''
        <div id="chat-response"
             role="log"
             aria-live="polite"
             aria-relevant="additions"
             aria-label="Chat messages">
        </div>
    ''', unsafe_allow_html=True)

    # Status announcements
    announce_to_screen_reader("Chat interface loaded and ready")
```

---

## Security Components

### Component 1: Cryptographic Audit Trail

**File:** `plugins/examples/audit_plugin.py`

```python
# Copy and adapt this for audit logging
from plugins.examples.audit_plugin import AuditPlugin

# Usage in your application
audit = AuditPlugin()
await audit.initialize({"audit_directory": "logs/audit"})

# Log actions
await audit.log_action(
    action="user_login",
    user_id="user123",
    metadata={"ip": "192.168.1.1"}
)

# Verify integrity (detect tampering)
is_valid = audit.verify_integrity()
if not is_valid:
    alert("AUDIT LOG TAMPERING DETECTED!")
```

### Component 2: JWT Authentication

**File:** `plugins/examples/auth_plugin.py`

```python
# Copy and adapt for your authentication needs
from plugins.examples.auth_plugin import AuthenticationPlugin

auth = AuthenticationPlugin()
await auth.initialize({
    "jwt_secret": "your-secret-key",
    "token_expiry_hours": 24
})

# Register user
result = await auth.register_user("username", "password")

# Login
token = await auth.login("username", "password")

# Verify token
user = await auth.verify_token(token)
```

### Component 3: Rate Limiting

**File:** `plugins/examples/rate_limit_plugin.py`

```python
# Copy and adapt for DoS protection
from plugins.examples.rate_limit_plugin import RateLimitPlugin

rate_limiter = RateLimitPlugin()
await rate_limiter.initialize({
    "max_requests_per_minute": 60,
    "max_burst": 10
})

# Use in your API
@app.route("/api/chat")
async def chat(request):
    # Check rate limit
    user_id = get_user_id(request)
    is_allowed = await rate_limiter.check_rate_limit(user_id)

    if not is_allowed:
        return {"error": "Rate limit exceeded"}, 429

    # Process request...
```

---

## Research Tools

### Tool 1: Sensitivity Analysis

**File:** `research/sensitivity_analysis.py`

```python
# Reuse for your AI/ML research
from research.sensitivity_analysis import (
    temperature_sensitivity_analysis,
    PerformanceMetrics
)

# Analyze your model
results = temperature_sensitivity_analysis(
    model="your-model",
    prompt="test prompt",
    temperature_range=(0.0, 2.0),
    steps=20
)

# Results is a pandas DataFrame
print(results.describe())  # Statistical summary
print(results.corr())      # Correlations

# Visualize
import matplotlib.pyplot as plt
plt.plot(results['temperature'], results['response_time'])
plt.xlabel('Temperature')
plt.ylabel('Response Time')
plt.savefig('sensitivity.png')
```

### Tool 2: Cost Analysis

**File:** `demo_multi_model_cost_analysis.py`

```python
# Reuse for cost-benefit analysis
from demo_multi_model_cost_analysis import MultiModelCostAnalyzer

analyzer = MultiModelCostAnalyzer()

# Test models
models = ["model1", "model2", "model3"]
for model in models:
    result = analyzer.process_request(
        model=model,
        prompt="test"
    )

# Generate cost report
report = analyzer.generate_report()
print(report)  # Detailed cost breakdown
```

---

## Documentation Templates

All templates are in `docs/templates/` and ready to use:

### Template 1: Plugin Documentation
**File:** `docs/templates/plugin_template.md`

Copy and fill in for your plugins.

### Template 2: Tutorial
**File:** `docs/templates/tutorial_template.md`

Step-by-step tutorial format.

### Template 3: API Reference
**File:** `docs/templates/api_template.md`

Standard API documentation format.

---

## Code Snippets Library

### Snippet 1: Async Error Handling

```python
async def safe_execute(func, *args, **kwargs):
    """Execute async function with comprehensive error handling"""
    try:
        result = await func(*args, **kwargs)
        return {"success": True, "data": result}
    except ConnectionError as e:
        return {"success": False, "error": f"Connection failed: {e}"}
    except TimeoutError as e:
        return {"success": False, "error": f"Timeout: {e}"}
    except Exception as e:
        logging.exception("Unexpected error")
        return {"success": False, "error": f"Internal error: {e}"}
```

### Snippet 2: Configuration Validation

```python
from typing import Dict, List

def validate_config(config: Dict, required_keys: List[str]) -> List[str]:
    """Validate configuration and return list of errors"""
    errors = []

    # Check required keys
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required key: {key}")

    # Type validation examples
    if "port" in config and not isinstance(config["port"], int):
        errors.append("Port must be integer")

    if "timeout" in config and config["timeout"] <= 0:
        errors.append("Timeout must be positive")

    return errors
```

### Snippet 3: Retry Logic with Exponential Backoff

```python
import asyncio
import random

async def retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0
):
    """Retry function with exponential backoff"""

    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise  # Last attempt, re-raise

            # Exponential backoff with jitter
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)
            await asyncio.sleep(delay + jitter)

            logging.warning(f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s")
```

---

## Integration Examples

### Example: Adding Plugin System to Flask

```python
from flask import Flask, request
from plugins.plugin_manager import PluginManager

app = Flask(__name__)
plugin_manager = PluginManager()

@app.before_first_request
async def load_plugins():
    await plugin_manager.load_plugins("plugins/")

@app.before_request
async def before_request():
    context = {
        "request": request,
        "path": request.path,
        "method": request.method
    }
    context = await plugin_manager.execute_hook("before_request", context)
    # Store modified context
    request.plugin_context = context

@app.after_request
async def after_request(response):
    context = getattr(request, 'plugin_context', {})
    context["response"] = response
    await plugin_manager.execute_hook("after_request", context)
    return response
```

### Example: Adding Quality Tests to Django

```python
# your_django_app/tests/test_quality.py
from django.test import TestCase
from test_iso25010_compliance import ISO25010TestFramework

class DjangoQualityTests(TestCase, ISO25010TestFramework):
    """ISO 25010 quality tests for Django app"""

    def test_functional_completeness(self):
        """Test all views are accessible"""
        from django.urls import reverse

        required_views = ['home', 'about', 'contact']
        for view_name in required_views:
            url = reverse(view_name)
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 404)

    def test_security_csrf_protection(self):
        """Test CSRF protection is enabled"""
        response = self.client.post('/api/submit/', {})
        # Should require CSRF token
        self.assertEqual(response.status_code, 403)
```

---

## License

All components in this project are released under the **MIT License**.

You are free to:
- ✅ Use commercially
- ✅ Modify
- ✅ Distribute
- ✅ Use privately

See [LICENSE](LICENSE) for full terms.

---

## Support

**Questions about reusing components?**

1. Check this documentation
2. Review example code in `examples/` directory
3. Open a [GitHub Discussion](../../discussions)
4. File an [issue](../../issues) with "question" label

---

## Contributing Back

If you improve a component, consider contributing back:

1. Fork the repository
2. Make your improvements
3. Submit a pull request
4. Help others benefit from your work!

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

**Happy reusing! Build something awesome!** 🚀
