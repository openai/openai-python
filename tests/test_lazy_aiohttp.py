from __future__ import annotations

import os
import sys
import subprocess
from typing import TYPE_CHECKING
from pathlib import Path
from typing_extensions import assert_type

import httpx2
import pytest

import openai
from openai import DefaultAioHttpClient

if TYPE_CHECKING:
    assert_type(DefaultAioHttpClient(trust_env=False), httpx2.AsyncClient)


def run_python(source: str) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(openai.__file__).parents[1])
    result = subprocess.run([sys.executable, "-c", source], env=env, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr


def test_default_client_does_not_load_aiohttp() -> None:
    run_python(
        """
import asyncio
import sys
import openai
from openai import AsyncOpenAI, DefaultAioHttpClient
from openai._base_client import DefaultAioHttpClient as CanonicalClient
assert DefaultAioHttpClient is CanonicalClient
assert isinstance(DefaultAioHttpClient, type)
client = AsyncOpenAI(api_key="synthetic")
asyncio.run(client.close())
assert "aiohttp" not in sys.modules
assert "openai._vendor.httpx_aiohttp.transport" not in sys.modules
"""
    )


def test_missing_extra_is_reported_only_when_constructing_client() -> None:
    run_python(
        """
import importlib.abc
import sys
class MissingAioHttp(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "aiohttp" or fullname.startswith("aiohttp."):
            raise ModuleNotFoundError("synthetic missing aiohttp", name=fullname)
sys.meta_path.insert(0, MissingAioHttp())
from openai import DefaultAioHttpClient
import httpx2
assert isinstance(DefaultAioHttpClient, type)
assert DefaultAioHttpClient.__name__ == "_MissingAioHttpClient"
assert DefaultAioHttpClient.__bases__ == (httpx2.AsyncClient,)
import typing
assert typing.get_type_hints(DefaultAioHttpClient.__init__) == {"_kwargs": typing.Any, "return": type(None)}
for _ in range(2):
    try:
        DefaultAioHttpClient(trust_env=False)
    except RuntimeError as exc:
        assert str(exc) == "To use the aiohttp client you must have installed the package with the `aiohttp` extra"
    else:
        raise AssertionError("Expected the missing-extra error")
"""
    )


def test_explicit_client_preserves_identity_defaults_and_subclasses() -> None:
    pytest.importorskip("aiohttp")
    run_python(
        """
import asyncio
import inspect
import sys
import httpx2
from openai import DefaultAioHttpClient
from openai._base_client import DefaultAioHttpClient as CanonicalClient
from openai._constants import DEFAULT_TIMEOUT, DEFAULT_CONNECTION_LIMITS
assert "aiohttp" not in sys.modules
class CustomClient(DefaultAioHttpClient):
    marker = "custom"
client = CustomClient(trust_env=False)
from openai._vendor.httpx_aiohttp import Httpx2AiohttpClient, AiohttpTransport
from openai._vendor.httpx_aiohttp.transport import AiohttpTransport as CanonicalTransport
assert DefaultAioHttpClient is CanonicalClient
import typing
assert typing.get_type_hints(DefaultAioHttpClient.__init__) == {"kwargs": typing.Any, "return": type(None)}
assert issubclass(CustomClient, DefaultAioHttpClient)
assert isinstance(client, Httpx2AiohttpClient)
assert isinstance(client, httpx2.AsyncClient)
assert isinstance(client._transport, CanonicalTransport)
assert client._transport.limits is DEFAULT_CONNECTION_LIMITS
assert AiohttpTransport is CanonicalTransport
assert client.marker == "custom"
assert client.timeout == DEFAULT_TIMEOUT
assert client.follow_redirects is True
assert inspect.signature(DefaultAioHttpClient).parameters.keys() == {"kwargs"}
asyncio.run(client.aclose())
transport = httpx2.MockTransport(lambda request: httpx2.Response(200))
client = DefaultAioHttpClient(transport=transport, timeout=17, follow_redirects=False, trust_env=False)
assert client._transport is transport
assert client.timeout == httpx2.Timeout(17)
assert client.follow_redirects is False
asyncio.run(client.aclose())
"""
    )


def test_first_concurrent_construction_uses_one_transport_class() -> None:
    pytest.importorskip("aiohttp")
    run_python(
        """
import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from openai import DefaultAioHttpClient
barrier = Barrier(8)
def construct(_):
    barrier.wait(timeout=30)
    client = DefaultAioHttpClient(trust_env=False)
    result = (type(client), type(client._transport))
    asyncio.run(client.aclose())
    return result
with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(construct, range(8)))
from openai._vendor.httpx_aiohttp import AiohttpTransport
assert all(client is DefaultAioHttpClient and transport is AiohttpTransport for client, transport in results)
"""
    )


def test_vendor_transport_remains_discoverable() -> None:
    pytest.importorskip("aiohttp")
    run_python(
        """
import sys
import openai._vendor.httpx_aiohttp as vendor
assert "AiohttpTransport" in dir(vendor)
assert "aiohttp" not in sys.modules
namespace = {}
exec("from openai._vendor.httpx_aiohttp import *", namespace)
from openai._vendor.httpx_aiohttp.transport import AiohttpTransport
assert vendor.AiohttpTransport is AiohttpTransport
assert namespace["AiohttpTransport"] is AiohttpTransport
"""
    )


def test_broken_extra_preserves_default_client_and_construction_error() -> None:
    run_python(
        """
import asyncio
import importlib.abc
import importlib.util
import sys
class BrokenLoader(importlib.abc.Loader):
    def create_module(self, spec):
        return None
    def exec_module(self, module):
        raise ImportError("synthetic broken optional dependency")
class BrokenAioHttp(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "aiohttp":
            return importlib.util.spec_from_loader(fullname, BrokenLoader(), is_package=True)
sys.meta_path.insert(0, BrokenAioHttp())
from openai import AsyncOpenAI, DefaultAioHttpClient
client = AsyncOpenAI(api_key="synthetic")
asyncio.run(client.close())
assert "aiohttp" not in sys.modules
original = DefaultAioHttpClient
for _ in range(2):
    try:
        DefaultAioHttpClient(trust_env=False)
    except RuntimeError as exc:
        assert str(exc) == "To use the aiohttp client you must have installed the package with the `aiohttp` extra"
    else:
        raise AssertionError("Expected the broken-extra error")
    from openai import DefaultAioHttpClient
    assert DefaultAioHttpClient is original
"""
    )


def test_injected_module_without_spec_keeps_default_client_available() -> None:
    run_python(
        """
import asyncio
import sys
import types
sys.modules["aiohttp"] = types.ModuleType("aiohttp")
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key="synthetic")
asyncio.run(client.close())
"""
    )


def test_preloaded_aiohttp_without_spec_keeps_explicit_client_available() -> None:
    pytest.importorskip("aiohttp")
    run_python(
        """
import asyncio
import aiohttp
import httpx2
aiohttp.__spec__ = None
from openai import DefaultAioHttpClient
client = DefaultAioHttpClient(trust_env=False)
from openai._vendor.httpx_aiohttp import AiohttpTransport
assert isinstance(client, httpx2.AsyncClient)
assert isinstance(client._transport, AiohttpTransport)
asyncio.run(client.aclose())
"""
    )


def test_none_import_sentinel_preserves_missing_extra_class() -> None:
    run_python(
        """
import sys
import httpx2
sys.modules["aiohttp"] = None
from openai import DefaultAioHttpClient
assert DefaultAioHttpClient.__name__ == "_MissingAioHttpClient"
assert DefaultAioHttpClient.__bases__ == (httpx2.AsyncClient,)
try:
    DefaultAioHttpClient()
except RuntimeError as exc:
    assert str(exc) == "To use the aiohttp client you must have installed the package with the `aiohttp` extra"
else:
    raise AssertionError("Expected missing-extra error")
"""
    )
