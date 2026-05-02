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


class TestSetLogLevel:
    """Tests for set_log_level and setup_logging."""

    def test_set_log_level_string_debug(self) -> None:
        from openai._utils._logs import set_log_level, logger, httpx_logger

        set_log_level("debug")
        assert logger.level == logging.DEBUG
        assert httpx_logger.level == logging.DEBUG

    def test_set_log_level_string_info(self) -> None:
        from openai._utils._logs import set_log_level, logger, httpx_logger

        set_log_level("info")
        assert logger.level == logging.INFO
        assert httpx_logger.level == logging.INFO

    def test_set_log_level_string_warning(self) -> None:
        from openai._utils._logs import set_log_level, logger, httpx_logger

        set_log_level("warning")
        assert logger.level == logging.WARNING
        assert httpx_logger.level == logging.WARNING

    def test_set_log_level_string_warn(self) -> None:
        from openai._utils._logs import set_log_level, logger, httpx_logger

        set_log_level("warn")
        assert logger.level == logging.WARNING
        assert httpx_logger.level == logging.WARNING

    def test_set_log_level_string_error(self) -> None:
        from openai._utils._logs import set_log_level, logger, httpx_logger

        set_log_level("error")
        assert logger.level == logging.ERROR
        assert httpx_logger.level == logging.ERROR

    def test_set_log_level_string_critical(self) -> None:
        from openai._utils._logs import set_log_level, logger, httpx_logger

        set_log_level("critical")
        assert logger.level == logging.CRITICAL
        assert httpx_logger.level == logging.CRITICAL

    def test_set_log_level_case_insensitive(self) -> None:
        from openai._utils._logs import set_log_level, logger, httpx_logger

        set_log_level("WARNING")
        assert logger.level == logging.WARNING
        assert httpx_logger.level == logging.WARNING

    def test_set_log_level_numeric(self) -> None:
        from openai._utils._logs import set_log_level, logger, httpx_logger

        set_log_level(logging.WARNING)
        assert logger.level == logging.WARNING
        assert httpx_logger.level == logging.WARNING

    def test_set_log_level_invalid_string_raises(self) -> None:
        from openai._utils._logs import set_log_level

        with pytest.raises(ValueError, match="Invalid log level"):
            set_log_level("not_a_level")

    def test_setup_logging_respects_openai_log_level_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from openai._utils._logs import setup_logging, logger, httpx_logger

        monkeypatch.setenv("OPENAI_LOG_LEVEL", "warning")
        monkeypatch.delenv("OPENAI_LOG", raising=False)
        setup_logging()
        assert logger.level == logging.WARNING
        assert httpx_logger.level == logging.WARNING

    def test_setup_logging_openai_log_level_takes_precedence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from openai._utils._logs import setup_logging, logger, httpx_logger

        monkeypatch.setenv("OPENAI_LOG_LEVEL", "error")
        monkeypatch.setenv("OPENAI_LOG", "debug")
        setup_logging()
        assert logger.level == logging.ERROR
        assert httpx_logger.level == logging.ERROR

    def test_setup_logging_legacy_openai_log_still_works(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from openai._utils._logs import setup_logging, logger, httpx_logger

        monkeypatch.delenv("OPENAI_LOG_LEVEL", raising=False)
        monkeypatch.setenv("OPENAI_LOG", "info")
        setup_logging()
        assert logger.level == logging.INFO
        assert httpx_logger.level == logging.INFO

    def test_setup_logging_legacy_openai_log_warning(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from openai._utils._logs import setup_logging, logger, httpx_logger

        monkeypatch.delenv("OPENAI_LOG_LEVEL", raising=False)
        monkeypatch.setenv("OPENAI_LOG", "warning")
        setup_logging()
        assert logger.level == logging.WARNING
        assert httpx_logger.level == logging.WARNING

    def test_setup_logging_no_env_does_not_set_level(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from openai._utils._logs import setup_logging, logger, httpx_logger

        monkeypatch.delenv("OPENAI_LOG_LEVEL", raising=False)
        monkeypatch.delenv("OPENAI_LOG", raising=False)

        # Save original levels
        orig_logger_level = logger.level
        orig_httpx_level = httpx_logger.level

        setup_logging()

        # Levels should not have changed
        assert logger.level == orig_logger_level
        assert httpx_logger.level == orig_httpx_level

    def test_set_log_level_importable_from_openai(self) -> None:
        import openai

        assert hasattr(openai, "set_log_level")
        assert callable(openai.set_log_level)
