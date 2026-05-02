import os
import logging
from typing import Union
from typing_extensions import override

from ._utils import is_dict

logger: logging.Logger = logging.getLogger("openai")
httpx_logger: logging.Logger = logging.getLogger("httpx")


SENSITIVE_HEADERS = {"api-key", "authorization"}

_LOG_LEVEL_MAP: dict[str, int] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "warn": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
    "fatal": logging.CRITICAL,
}


def _basic_config() -> None:
    # e.g. [2023-10-05 14:12:26 - openai._base_client:818 - DEBUG] HTTP Request: POST http://127.0.0.1:4010/foo/bar "200 OK"
    logging.basicConfig(
        format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _parse_log_level(value: str) -> int | None:
    """Parse a log level string into a logging level constant.

    Accepts standard level names (case-insensitive) and numeric values.
    Returns None if the value cannot be parsed.
    """
    level = _LOG_LEVEL_MAP.get(value.lower())
    if level is not None:
        return level

    # Try numeric values
    try:
        numeric = int(value)
        if 0 <= numeric <= 100:
            return numeric
    except ValueError:
        pass

    return None


def set_log_level(level: Union[int, str]) -> None:
    """Set the log level for the OpenAI SDK loggers.

    Args:
        level: A log level as a string (e.g. "debug", "info", "warning", "error", "critical")
               or a numeric logging level (e.g. logging.DEBUG, logging.WARNING).
    """
    if isinstance(level, str):
        parsed = _parse_log_level(level)
        if parsed is None:
            raise ValueError(
                f"Invalid log level: {level!r}. "
                f"Expected one of: {', '.join(sorted(_LOG_LEVEL_MAP.keys()))} or a numeric level."
            )
        level = parsed

    _basic_config()
    logger.setLevel(level)
    httpx_logger.setLevel(level)


def setup_logging() -> None:
    # OPENAI_LOG_LEVEL takes precedence over the legacy OPENAI_LOG env var
    env = os.environ.get("OPENAI_LOG_LEVEL") or os.environ.get("OPENAI_LOG")
    if env:
        parsed = _parse_log_level(env)
        if parsed is not None:
            _basic_config()
            logger.setLevel(parsed)
            httpx_logger.setLevel(parsed)


class SensitiveHeadersFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        if is_dict(record.args) and "headers" in record.args and is_dict(record.args["headers"]):
            headers = record.args["headers"] = {**record.args["headers"]}
            for header in headers:
                if str(header).lower() in SENSITIVE_HEADERS:
                    headers[header] = "<redacted>"
        return True
