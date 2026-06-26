import os
import pytest
from unittest.mock import patch

from openai._utils._utils import sanitize_proxy_env_vars


@pytest.fixture(autouse=True)
def clean_proxy_env():
    """Save and restore proxy env vars around each test."""
    proxy_vars = (
        "HTTP_PROXY", "http_proxy",
        "HTTPS_PROXY", "https_proxy",
        "ALL_PROXY", "all_proxy",
        "NO_PROXY", "no_proxy",
    )
    saved = {var: os.environ.get(var) for var in proxy_vars}
    yield
    for var, val in saved.items():
        if val is None:
            os.environ.pop(var, None)
        else:
            os.environ[var] = val


def test_sanitize_proxy_env_vars_no_newlines():
    os.environ["NO_PROXY"] = "localhost,192.168.1.1"
    sanitize_proxy_env_vars()
    assert os.environ["NO_PROXY"] == "localhost,192.168.1.1"


def test_sanitize_proxy_env_vars_with_newline():
    os.environ["NO_PROXY"] = "localhost\n192.168.1.1"
    sanitize_proxy_env_vars()
    assert os.environ["NO_PROXY"] == "localhost,192.168.1.1"


def test_sanitize_proxy_env_vars_with_crlf():
    os.environ["NO_PROXY"] = "localhost\r\n192.168.1.1"
    sanitize_proxy_env_vars()
    assert os.environ["NO_PROXY"] == "localhost,192.168.1.1"


def test_sanitize_proxy_env_vars_with_multiple_newlines():
    os.environ["NO_PROXY"] = "localhost\n192.168.1.1\n10.0.0.1"
    sanitize_proxy_env_vars()
    assert os.environ["NO_PROXY"] == "localhost,192.168.1.1,10.0.0.1"


def test_sanitize_proxy_env_vars_with_whitespace():
    os.environ["NO_PROXY"] = " localhost \n 192.168.1.1 "
    sanitize_proxy_env_vars()
    assert os.environ["NO_PROXY"] == "localhost,192.168.1.1"


def test_sanitize_proxy_env_vars_with_empty_entries():
    os.environ["NO_PROXY"] = "localhost\n\n192.168.1.1"
    sanitize_proxy_env_vars()
    assert os.environ["NO_PROXY"] == "localhost,192.168.1.1"


def test_sanitize_proxy_env_vars_all_proxy_vars():
    os.environ["HTTP_PROXY"] = "http://proxy:8080\n"
    os.environ["HTTPS_PROXY"] = "https://proxy:8443\n"
    os.environ["NO_PROXY"] = "localhost\n192.168.1.1"
    
    sanitize_proxy_env_vars()
    
    assert os.environ["HTTP_PROXY"] == "http://proxy:8080"
    assert os.environ["HTTPS_PROXY"] == "https://proxy:8443"
    assert os.environ["NO_PROXY"] == "localhost,192.168.1.1"


def test_sanitize_proxy_env_vars_empty_value():
    os.environ["NO_PROXY"] = ""
    sanitize_proxy_env_vars()
    assert os.environ["NO_PROXY"] == ""


def test_sanitize_proxy_env_vars_not_set():
    os.environ.pop("NO_PROXY", None)
    sanitize_proxy_env_vars()
    assert "NO_PROXY" not in os.environ


def test_sanitize_proxy_env_vars_preserves_commas():
    os.environ["NO_PROXY"] = "localhost,192.168.1.1\n10.0.0.1"
    sanitize_proxy_env_vars()
    assert os.environ["NO_PROXY"] == "localhost,192.168.1.1,10.0.0.1"


def test_openai_client_with_newline_in_no_proxy():
    """Integration test: creating an OpenAI client with newlines in NO_PROXY should not raise."""
    import httpx
    from openai._base_client import _DefaultHttpxClient

    os.environ["NO_PROXY"] = "localhost\n192.168.1.1"
    
    client = _DefaultHttpxClient()
    assert client is not None
    client.close()
