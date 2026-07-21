# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
import sys
import logging
from typing import TYPE_CHECKING, Iterator, AsyncIterator

import httpx
import pytest
from pytest_asyncio import is_async_test

from openai import OpenAI, AsyncOpenAI, DefaultHttpx2Client, DefaultAioHttpClient, DefaultAsyncHttpx2Client
from openai._utils import is_dict

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest  # pyright: ignore[reportPrivateImportUsage]

pytest.register_assert_rewrite("tests.utils")

logging.getLogger("openai").setLevel(logging.DEBUG)


# automatically add `pytest.mark.asyncio()` to all of our async tests
# so we don't have to add that boilerplate everywhere
def pytest_collection_modifyitems(items: list[pytest.Function]) -> None:
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)

    # RESPX only intercepts HTTPX, so it cannot mock requests made by aiohttp or HTTPX2.
    for item in items:
        if "respx_mock" not in item.fixturenames:
            continue

        if test_http_client == "httpx2" and {"client", "async_client"}.intersection(item.fixturenames):
            item.add_marker(pytest.mark.skip(reason="HTTPX2 client is not compatible with respx_mock"))
            continue

        if "async_client" not in item.fixturenames:
            continue

        if not hasattr(item, "callspec"):
            continue

        async_client_param = item.callspec.params.get("async_client")
        if is_dict(async_client_param) and async_client_param.get("http_client") == "aiohttp":
            item.add_marker(pytest.mark.skip(reason="aiohttp client is not compatible with respx_mock"))


base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
test_http_client = os.environ.get("OPENAI_TEST_HTTP_CLIENT", "httpx")

api_key = "My API Key"
admin_api_key = "My Admin API Key"


@pytest.fixture(scope="session")
def client(request: FixtureRequest) -> Iterator[OpenAI]:
    strict = getattr(request, "param", True)
    if not isinstance(strict, bool):
        raise TypeError(f"Unexpected fixture parameter type {type(strict)}, expected {bool}")

    http_client = DefaultHttpx2Client() if test_http_client == "httpx2" else None

    with OpenAI(
        base_url=base_url,
        api_key=api_key,
        admin_api_key=admin_api_key,
        _strict_response_validation=strict,
        http_client=http_client,
    ) as client:
        yield client


@pytest.fixture(scope="session")
async def async_client(request: FixtureRequest) -> AsyncIterator[AsyncOpenAI]:
    param = getattr(request, "param", True)

    # defaults
    strict = True
    http_client: None | httpx.AsyncClient = None

    if isinstance(param, bool):
        strict = param
    elif is_dict(param):
        strict = param.get("strict", True)
        assert isinstance(strict, bool)

        http_client_type = param.get("http_client", "httpx")
        if http_client_type == "aiohttp":
            if sys.version_info < (3, 10):
                pytest.skip("the aiohttp client requires Python 3.10 or later")

            http_client = DefaultAioHttpClient()
    else:
        raise TypeError(f"Unexpected fixture parameter type {type(param)}, expected bool or dict")

    if http_client is None and test_http_client == "httpx2":
        http_client = DefaultAsyncHttpx2Client()

    async with AsyncOpenAI(
        base_url=base_url,
        api_key=api_key,
        admin_api_key=admin_api_key,
        _strict_response_validation=strict,
        http_client=http_client,
    ) as client:
        yield client
