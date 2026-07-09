import os
import logging
from typing_extensions import override

from ._utils import is_dict

logger: logging.Logger = logging.getLogger("openai")
httpx_logger: logging.Logger = logging.getLogger("httpx")


SENSITIVE_HEADERS = {"api-key", "authorization", "x-amz-security-token"}


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
        # Case 1: headers passed as a dict in record.args (structured logging)
        if is_dict(record.args) and "headers" in record.args and is_dict(record.args["headers"]):
            headers = record.args["headers"] = {**record.args["headers"]}
            for header in headers:
                if str(header).lower() in SENSITIVE_HEADERS:
                    headers[header] = "<redacted>"

        # Case 2: headers already interpolated into the log message string
        # (e.g. httpx debug output: "headers={'authorization': 'Bearer sk-...'}")
        import re
        msg = record.getMessage()
        for header in SENSITIVE_HEADERS:
            # Match header: 'value' or header: "value" in the formatted message
            pattern = rf"(?i)({re.escape(header)}['"]?\s*:\s*['"]?)([^'"\s,}}]+)"
            redacted = re.sub(pattern, r"\1<redacted>", msg)
            if redacted != msg:
                record.msg = redacted
                record.args = ()
                break

        return True
