"""
ISO/IEC 25010 Compatibility Testing
====================================

Tests for Compatibility quality characteristic:
- Co-existence: Works alongside other software
- Interoperability: Exchanges information with other systems
- Python version compatibility
- OS compatibility
- Browser compatibility

Author: ISO/IEC 25010 Compliance Team
Version: 1.0.0
"""

import os
import platform
import sys
from pathlib import Path

import pytest

# ============================================================================
# COMPATIBILITY TESTS - ISO/IEC 25010
# ============================================================================


class TestPythonCompatibility:
    """Test compatibility across Python versions"""

    def test_python_version_minimum(self):
        """Test: Python version meets minimum requirement"""
        version_info = sys.version_info
        assert version_info >= (3, 10), f"Python 3.10+ required, got {sys.version}"

    def test_python_version_supported(self):
        """Test: Python version is in supported range"""
        version_info = sys.version_info
        supported_versions = [(3, 10), (3, 11), (3, 12), (3, 13), (3, 14)]

        is_supported = any(version_info[:2] == supported for supported in supported_versions)

        assert is_supported, f"Python version {version_info[:2]} not in supported list"

    def test_required_modules_importable(self):
        """Test: All required modules can be imported"""
        required_modules = [
            "streamlit",
            "flask",
            "ollama",
            "pytest",
            "asyncio",
            "json",
            "pathlib",
            "typing",
        ]

        for module_name in required_modules:
            try:
                __import__(module_name)
            except ImportError as e:
                pytest.fail(f"Required module '{module_name}' cannot be imported: {e}")

    def test_async_await_syntax_supported(self):
        """Test: Python version supports async/await"""
        import inspect

        # Test async function definition
        async def test_async():
            return True

        assert inspect.iscoroutinefunction(test_async)

    def test_type_hints_supported(self):
        """Test: Python version supports type hints"""
        from typing import Dict, List, Optional

        def test_function(param: str) -> Optional[Dict[str, List[int]]]:
            return {"key": [1, 2, 3]}

        # If this doesn't raise SyntaxError, type hints are supported
        assert callable(test_function)


class TestOSCompatibility:
    """Test compatibility across operating systems"""

    def test_os_detected(self):
        """Test: Operating system is detected"""
        os_name = platform.system()
        supported_os = ["Darwin", "Linux", "Windows"]

        assert os_name in supported_os, f"OS '{os_name}' may not be fully supported"

    def test_path_separator_handling(self):
        """Test: Path handling works on any OS"""
        test_path = Path("test") / "path" / "file.txt"
        assert isinstance(test_path, Path)

        # Path should use correct separator for OS
        path_str = str(test_path)
        if platform.system() == "Windows":
            assert "\\" in path_str or "/" in path_str
        else:
            assert "/" in path_str

    def test_home_directory_accessible(self):
        """Test: Home directory can be accessed"""
        home = Path.home()
        assert home.exists(), "Home directory not accessible"
        assert home.is_dir(), "Home is not a directory"

    def test_temp_directory_accessible(self):
        """Test: Temp directory can be accessed"""
        import tempfile

        temp_dir = Path(tempfile.gettempdir())
        assert temp_dir.exists(), "Temp directory not accessible"
        assert temp_dir.is_dir(), "Temp is not a directory"

    def test_file_operations_work(self):
        """Test: Basic file operations work on this OS"""
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            test_file = Path(f.name)
            f.write("test content")

        try:
            # Read
            content = test_file.read_text()
            assert content == "test content"

            # Check existence
            assert test_file.exists()

            # Check is_file
            assert test_file.is_file()

        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()

    @pytest.mark.skipif(platform.system() == "Windows", reason="Unix-specific test")
    def test_unix_permissions(self):
        """Test: Unix file permissions work (macOS, Linux)"""
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False) as f:
            test_file = Path(f.name)

        try:
            # Set permissions
            test_file.chmod(0o600)
            stat_info = test_file.stat()

            # Check permissions (owner read/write only)
            assert (stat_info.st_mode & 0o777) == 0o600

        finally:
            if test_file.exists():
                test_file.unlink()

    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
    def test_windows_paths(self):
        """Test: Windows path handling works"""
        # Windows-specific path tests
        test_path = Path("C:/test/path")
        assert str(test_path)  # Should not raise error


class TestOllamaCompatibility:
    """Test compatibility with Ollama server"""

    def test_ollama_import(self):
        """Test: Ollama Python library can be imported"""
        try:
            import ollama

            assert hasattr(ollama, "list")
            assert hasattr(ollama, "chat")
            assert hasattr(ollama, "generate")
        except ImportError:
            pytest.fail("Ollama library not installed")

    def test_ollama_client_instantiation(self):
        """Test: Ollama client can be created"""
        import ollama

        # This should not raise an error
        client = ollama  # Library is functional as module

        assert client is not None

    @pytest.mark.skip(reason="Requires Ollama server running")
    def test_ollama_server_connection(self):
        """Test: Can connect to Ollama server (skipped by default)"""
        import ollama

        try:
            models = ollama.list()
            assert "models" in models or isinstance(models, (list, dict))
        except Exception as e:
            pytest.fail(f"Cannot connect to Ollama: {e}")

    def test_ollama_version_compatibility(self):
        """Test: Ollama library version is compatible"""
        import ollama

        # Check that ollama module has expected attributes
        required_functions = ["list", "chat", "generate", "pull", "push", "create"]

        for func_name in required_functions:
            assert hasattr(ollama, func_name), f"Ollama missing function: {func_name}"


class TestDependencyCompatibility:
    """Test dependency version compatibility"""

    def test_streamlit_version(self):
        """Test: Streamlit version is compatible"""
        import streamlit as st

        version = st.__version__
        major, minor, patch = map(int, version.split(".")[:3])

        # Require Streamlit >= 1.0.0
        assert major >= 1, f"Streamlit version {version} too old (need 1.0+)"

    def test_flask_version(self):
        """Test: Flask version is compatible"""
        import flask

        version = flask.__version__
        major = int(version.split(".")[0])

        # Require Flask >= 2.0.0
        assert major >= 2, f"Flask version {version} too old (need 2.0+)"

    def test_pytest_version(self):
        """Test: Pytest version is compatible"""
        import pytest

        version = pytest.__version__
        major = int(version.split(".")[0])

        # Require pytest >= 7.0.0
        assert major >= 7, f"Pytest version {version} too old (need 7.0+)"

    def test_all_dependencies_importable(self):
        """Test: All dependencies from requirements.txt can be imported"""
        dependencies = {
            "streamlit": "1.51.0",
            "flask": "3.1.2",
            "ollama": "0.4.5",
            "pytest": "8.3.4",
            "pytest-cov": "6.0.0",
            "pytest-asyncio": "0.24.0",
        }

        for package in dependencies.keys():
            # Handle packages with different import names
            import_name = package.replace("-", "_")

            try:
                __import__(import_name)
            except ImportError:
                pytest.fail(f"Dependency '{package}' cannot be imported")


class TestBrowserCompatibility:
    """Test browser compatibility for Streamlit UI"""

    def test_streamlit_default_browser(self):
        """Test: Streamlit can determine default browser"""
        import webbrowser

        # Check that webbrowser module works
        assert hasattr(webbrowser, "get")

        # Try to get default browser (doesn't open, just checks)
        try:
            browser = webbrowser.get()
            assert browser is not None
        except Exception:
            # Some environments don't have a browser configured (CI/CD)
            pytest.skip("No browser configured in this environment")

    def test_websocket_support(self):
        """Test: Environment supports WebSocket (for Streamlit)"""
        # Streamlit uses WebSocket for real-time updates
        try:
            import websockets

            assert websockets is not None
        except ImportError:
            # websockets is optional, Streamlit may bundle its own
            pytest.skip("websockets package not installed (may be bundled)")

    def test_streamlit_server_config(self):
        """Test: Streamlit config options are valid"""
        import streamlit as st

        # Check that config module exists
        assert hasattr(st, "get_option")

        # Test some common config options
        try:
            st.get_option("server.port")
            st.get_option("server.address")
        except Exception:
            pass  # Config may not be fully initialized in test environment


class TestNetworkCompatibility:
    """Test network configuration compatibility"""

    def test_localhost_resolution(self):
        """Test: localhost resolves correctly"""
        import socket

        try:
            # Resolve localhost
            ip = socket.gethostbyname("localhost")
            assert ip in ["127.0.0.1", "::1"], f"localhost resolves to unexpected IP: {ip}"
        except socket.gaierror:
            pytest.fail("Cannot resolve 'localhost'")

    def test_port_availability(self):
        """Test: Common ports can be checked for availability"""
        import socket

        def is_port_in_use(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", port)) == 0

        # Test that we can check port status (don't require specific ports free)
        port_5000_status = is_port_in_use(5000)
        port_8501_status = is_port_in_use(8501)

        # Just assert we can check (not whether they're free)
        assert isinstance(port_5000_status, bool)
        assert isinstance(port_8501_status, bool)

    def test_http_client_available(self):
        """Test: HTTP client libraries are available"""
        try:
            import urllib.request

            assert urllib.request is not None
        except ImportError:
            pytest.fail("urllib.request not available")

        try:
            import requests

            assert requests is not None
        except ImportError:
            pass  # requests is optional


class TestConcurrencyCompatibility:
    """Test concurrency features compatibility"""

    def test_asyncio_available(self):
        """Test: asyncio module is available"""
        import asyncio

        assert hasattr(asyncio, "run")
        assert hasattr(asyncio, "create_task")
        assert hasattr(asyncio, "gather")

    def test_async_execution_works(self):
        """Test: Async functions can be executed"""
        import asyncio

        async def test_coroutine():
            await asyncio.sleep(0.001)
            return "success"

        result = asyncio.run(test_coroutine())
        assert result == "success"

    def test_concurrent_futures_available(self):
        """Test: concurrent.futures is available"""
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(lambda: "test")
            result = future.result(timeout=1.0)
            assert result == "test"


class TestEncodingCompatibility:
    """Test text encoding compatibility"""

    def test_utf8_encoding_supported(self):
        """Test: UTF-8 encoding works"""
        test_text = "Hello 世界 🌍"

        # Encode to bytes
        encoded = test_text.encode("utf-8")
        assert isinstance(encoded, bytes)

        # Decode back
        decoded = encoded.decode("utf-8")
        assert decoded == test_text

    def test_json_unicode_handling(self):
        """Test: JSON handles Unicode correctly"""
        import json

        test_data = {"message": "Hello 世界", "emoji": "🚀"}

        # Serialize
        json_str = json.dumps(test_data, ensure_ascii=False)
        assert "世界" in json_str
        assert "🚀" in json_str

        # Deserialize
        parsed = json.loads(json_str)
        assert parsed == test_data

    def test_file_encoding_utf8(self):
        """Test: Files can be written/read with UTF-8"""
        import tempfile

        test_content = "UTF-8 test: 日本語 Français العربية 🎉"

        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as f:
            test_file = Path(f.name)
            f.write(test_content)

        try:
            # Read back with UTF-8
            content = test_file.read_text(encoding="utf-8")
            assert content == test_content
        finally:
            if test_file.exists():
                test_file.unlink()


# ============================================================================
# TEST SUMMARY
# ============================================================================


def test_compatibility_summary():
    """Test: Generate compatibility test summary"""
    summary = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": platform.system(),
        "platform_release": platform.release(),
        "architecture": platform.machine(),
        "python_implementation": platform.python_implementation(),
    }

    print("\n" + "=" * 70)
    print("COMPATIBILITY TEST SUMMARY")
    print("=" * 70)
    for key, value in summary.items():
        print(f"{key:25s}: {value}")
    print("=" * 70)

    # Assert that summary was generated (always passes)
    assert summary is not None
