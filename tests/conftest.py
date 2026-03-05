# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
import logging
from typing import TYPE_CHECKING, Iterator, AsyncIterator

import httpx
import pytest
from pytest_asyncio import is_async_test

from openai import OpenAI, AsyncOpenAI, DefaultAioHttpClient
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

    # We skip tests that use both the aiohttp client and respx_mock as respx_mock
    # doesn't support custom transports.
    for item in items:
        if "async_client" not in item.fixturenames or "respx_mock" not in item.fixturenames:
            continue

        if not hasattr(item, "callspec"):
            continue

        async_client_param = item.callspec.params.get("async_client")
        if is_dict(async_client_param) and async_client_param.get("http_client") == "aiohttp":
            item.add_marker(pytest.mark.skip(reason="aiohttp client is not compatible with respx_mock"))


base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

api_key = "My API Key"


@pytest.fixture(scope="session")
def client(request: FixtureRequest) -> Iterator[OpenAI]:
    strict = getattr(request, "param", True)
    if not isinstance(strict, bool):
        raise TypeError(f"Unexpected fixture parameter type {type(strict)}, expected {bool}")

    with OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=strict) as client:
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
            http_client = DefaultAioHttpClient()
    else:
        raise TypeError(f"Unexpected fixture parameter type {type(param)}, expected bool or dict")

    async with AsyncOpenAI(
        base_url=base_url, api_key=api_key, _strict_response_validation=strict, http_client=http_client
    ) as client:
        yield client
