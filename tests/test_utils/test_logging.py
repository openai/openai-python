import logging
from typing import Any, Dict, cast

import pytest

from openai._utils import SensitiveHeadersFilter


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
