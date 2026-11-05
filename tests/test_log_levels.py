from __future__ import annotations

import logging

import pytest

from openai._utils._logs import setup_logging


@pytest.mark.parametrize(
    ("setting", "expected_level"),
    [
        ("debug", logging.DEBUG),
        ("info", logging.INFO),
        ("warning", logging.WARNING),
        ("error", logging.ERROR),
        ("critical", logging.CRITICAL),
    ],
)
def test_openai_log_sets_standard_log_level(
    setting: str,
    expected_level: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    logger = logging.getLogger("openai")
    original_level = logger.level

    try:
        monkeypatch.setenv("OPENAI_LOG", setting)
        setup_logging()
        assert logger.level == expected_level
    finally:
        logger.setLevel(original_level)
