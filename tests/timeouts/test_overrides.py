from __future__ import annotations

import os

import httpx
import pytest

from openai import OpenAI
from openai._models import FinalRequestOptions
from openai._base_client import DEFAULT_TIMEOUT


base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


def test_per_request_timeout_overrides_default(client: OpenAI) -> None:
    # default timeout applied when none provided per-request
    request = client._build_request(FinalRequestOptions(method="get", url="/foo"))
    timeout = httpx.Timeout(**request.extensions["timeout"])  # type: ignore[arg-type]
    assert timeout == DEFAULT_TIMEOUT

    # per-request timeout overrides the default
    request = client._build_request(
        FinalRequestOptions(method="get", url="/foo", timeout=httpx.Timeout(100.0))
    )
    timeout = httpx.Timeout(**request.extensions["timeout"])  # type: ignore[arg-type]
    assert timeout == httpx.Timeout(100.0)

