import logging
from typing import Any, Dict, cast

import httpx
import pytest
from respx import MockRouter

from openai import OpenAI
from openai._utils import SensitiveHeadersFilter, redact_sensitive_headers


@pytest.fixture
def logger_with_filter() -> logging.Logger:
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    logger.addFilter(SensitiveHeadersFilter())
    return logger


def test_keys_redacted(logger_with_filter: logging.Logger, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG):
        logger_with_filter.debug(
            "Request options: %s",
            {
                "method": "post",
                "url": "chat/completions",
                "headers": {"api-key": "12345", "Authorization": "Bearer token"},
            },
        )

    log_record = cast(Dict[str, Any], caplog.records[0].args)
    assert log_record["method"] == "post"
    assert log_record["url"] == "chat/completions"
    assert log_record["headers"]["api-key"] == "<redacted>"
    assert log_record["headers"]["Authorization"] == "<redacted>"
    assert (
        caplog.messages[0]
        == "Request options: {'method': 'post', 'url': 'chat/completions', 'headers': {'api-key': '<redacted>', 'Authorization': '<redacted>'}}"
    )


def test_keys_redacted_case_insensitive(logger_with_filter: logging.Logger, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG):
        logger_with_filter.debug(
            "Request options: %s",
            {
                "method": "post",
                "url": "chat/completions",
                "headers": {"Api-key": "12345", "authorization": "Bearer token"},
            },
        )

    log_record = cast(Dict[str, Any], caplog.records[0].args)
    assert log_record["method"] == "post"
    assert log_record["url"] == "chat/completions"
    assert log_record["headers"]["Api-key"] == "<redacted>"
    assert log_record["headers"]["authorization"] == "<redacted>"
    assert (
        caplog.messages[0]
        == "Request options: {'method': 'post', 'url': 'chat/completions', 'headers': {'Api-key': '<redacted>', 'authorization': '<redacted>'}}"
    )


def test_no_headers(logger_with_filter: logging.Logger, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG):
        logger_with_filter.debug(
            "Request options: %s",
            {"method": "post", "url": "chat/completions"},
        )

    log_record = cast(Dict[str, Any], caplog.records[0].args)
    assert log_record["method"] == "post"
    assert log_record["url"] == "chat/completions"
    assert "api-key" not in log_record
    assert "Authorization" not in log_record
    assert caplog.messages[0] == "Request options: {'method': 'post', 'url': 'chat/completions'}"


def test_headers_without_sensitive_info(logger_with_filter: logging.Logger, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG):
        logger_with_filter.debug(
            "Request options: %s",
            {
                "method": "post",
                "url": "chat/completions",
                "headers": {"custom": "value"},
            },
        )

    log_record = cast(Dict[str, Any], caplog.records[0].args)
    assert log_record["method"] == "post"
    assert log_record["url"] == "chat/completions"
    assert log_record["headers"] == {"custom": "value"}
    assert (
        caplog.messages[0]
        == "Request options: {'method': 'post', 'url': 'chat/completions', 'headers': {'custom': 'value'}}"
    )


def test_standard_debug_msg(logger_with_filter: logging.Logger, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG):
        logger_with_filter.debug("Sending HTTP Request: %s %s", "POST", "chat/completions")
    assert caplog.messages[0] == "Sending HTTP Request: POST chat/completions"


def test_response_headers_redaction() -> None:
    """Verify sensitive response headers are redacted by the shared helper."""
    raw_headers = {
        "content-type": "application/json",
        "authorization": "Bearer sk-secret-key",
        "api-key": "my-secret-api-key",
        "x-request-id": "req_abc123",
    }
    filtered = redact_sensitive_headers(raw_headers)
    assert filtered["content-type"] == "application/json"
    assert filtered["authorization"] == "<redacted>"
    assert filtered["api-key"] == "<redacted>"
    assert filtered["x-request-id"] == "req_abc123"


@pytest.mark.respx(base_url="https://api.openai.com/v1")
def test_response_header_redaction_in_client(
    respx_mock: MockRouter,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Integration test: verify _base_client.py redacts sensitive response headers in actual log output."""
    respx_mock.post("/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={"id": "chatcmpl-test", "object": "chat.completion", "choices": [], "created": 0, "model": "gpt-4"},
            headers={"authorization": "Bearer secret", "x-request-id": "req_123"},
        )
    )

    client = OpenAI(api_key="test-key", base_url="https://api.openai.com/v1")

    with caplog.at_level(logging.DEBUG, logger="openai"):
        client.chat.completions.create(messages=[], model="gpt-4")

    response_logs = [r for r in caplog.records if r.getMessage().startswith("HTTP Response:")]
    assert len(response_logs) >= 1, "Expected at least one 'HTTP Response:' log line"
    msg = response_logs[0].getMessage()
    assert "secret" not in msg, "Sensitive header value should be redacted in log output"
    assert "<redacted>" in msg, "Redacted placeholder should appear in log output"
