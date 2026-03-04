from __future__ import annotations

import os
import logging
from typing import Any, Mapping
from typing_extensions import override

from ._utils import is_dict

logger: logging.Logger = logging.getLogger("openai")
httpx_logger: logging.Logger = logging.getLogger("httpx")


SENSITIVE_HEADERS = {"api-key", "authorization"}


def redact_sensitive_headers(headers: Mapping[str, Any]) -> dict[str, Any]:
    return {
        k: (v if str(k).lower() not in SENSITIVE_HEADERS else "<redacted>")
        for k, v in headers.items()
    }


def _basic_config() -> None:
    # e.g. [2023-10-05 14:12:26 - openai._base_client:818 - DEBUG] HTTP Request: POST http://127.0.0.1:4010/foo/bar "200 OK"
    logging.basicConfig(
        format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def setup_logging() -> None:
    env = os.environ.get("OPENAI_LOG")
    if env == "debug":
        _basic_config()
        logger.setLevel(logging.DEBUG)
        httpx_logger.setLevel(logging.DEBUG)
    elif env == "info":
        _basic_config()
        logger.setLevel(logging.INFO)
        httpx_logger.setLevel(logging.INFO)


class SensitiveHeadersFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        if is_dict(record.args) and "headers" in record.args and is_dict(record.args["headers"]):
            record.args["headers"] = redact_sensitive_headers({**record.args["headers"]})
        return True
