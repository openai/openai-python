# File generated to supplement coverage for openai-python PR #3368 (TCP keepalive).
#
# These tests verify that the default sync/async HTTP transports are configured
# with TCP keepalive socket options so that long-lived connections survive NAT
# idle timeouts, while ensuring a caller-supplied client/transport is never
# silently replaced (the ``setdefault`` contract).
from __future__ import annotations

import sys
import socket as socket_module
from typing import Any, List, Tuple

import httpx
import pytest

from openai import OpenAI, AsyncOpenAI
from openai._base_client import (
    DefaultHttpxClient,
    DefaultAsyncHttpxClient,
    _build_keepalive_socket_options,
)

base_url = "http://localhost:4010"
api_key = "My API Key"

SocketOption = Tuple[int, int, int]


def _extract_socket_options(transport: Any) -> List[SocketOption]:
    """Pull the configured ``socket_options`` out of an httpx transport.

    httpx stores the options on the underlying httpcore connection pool, which
    is exposed (privately) as ``transport._pool._socket_options``. We access it
    defensively so a missing attribute fails with a clear assertion rather than
    an opaque ``AttributeError``.
    """
    pool = getattr(transport, "_pool", None)
    assert pool is not None, "transport should expose an underlying connection pool"

    socket_options = getattr(pool, "_socket_options", None)
    assert socket_options is not None, "connection pool should expose _socket_options"

    return list(socket_options)


def _has_option(socket_options: List[SocketOption], level: int, optname: int) -> bool:
    """Return True if an option tuple with the given ``(level, optname)`` exists."""
    return any(opt[0] == level and opt[1] == optname for opt in socket_options)


def _idle_optnames() -> List[int]:
    """Collect the platform-specific "idle time before keepalive" optnames.

    * Linux exposes ``TCP_KEEPIDLE``.
    * macOS exposes ``TCP_KEEPALIVE`` (numerically ``0x10``); some Python builds
      do not export the constant, so fall back to the raw value on darwin.
    """
    optnames: List[int] = []
    if hasattr(socket_module, "TCP_KEEPIDLE"):
        optnames.append(socket_module.TCP_KEEPIDLE)
    if hasattr(socket_module, "TCP_KEEPALIVE"):
        optnames.append(socket_module.TCP_KEEPALIVE)
    if not optnames and sys.platform == "darwin":
        optnames.append(0x10)
    return optnames


class TestOpenAI:
    def test_default_sync_transport_has_tcp_keepalive(self) -> None:
        client = OpenAI(base_url=base_url, api_key=api_key)
        transport = client._client._transport

        assert isinstance(
            transport, httpx.HTTPTransport
        ), "Default sync client should use a concrete httpx.HTTPTransport"

        socket_options = _extract_socket_options(transport)
        assert _has_option(
            socket_options, socket_module.SOL_SOCKET, socket_module.SO_KEEPALIVE
        ), "Default sync transport must enable SO_KEEPALIVE to survive NAT idle timeouts"

    def test_keepalive_includes_keepidle_or_keepalive(self) -> None:
        idle_optnames = _idle_optnames()
        if not idle_optnames:
            pytest.skip("platform exposes no TCP keepidle/keepalive option name")

        socket_options = _build_keepalive_socket_options()
        assert any(
            opt[1] in idle_optnames for opt in socket_options
        ), "Keepalive options must set the idle interval (TCP_KEEPIDLE / TCP_KEEPALIVE)"

    def test_keepalive_includes_keepintvl(self) -> None:
        if not hasattr(socket_module, "TCP_KEEPINTVL"):
            pytest.skip("platform does not support TCP_KEEPINTVL")

        socket_options = _build_keepalive_socket_options()
        assert _has_option(
            socket_options, socket_module.IPPROTO_TCP, socket_module.TCP_KEEPINTVL
        ), "Keepalive options should set the probe interval (TCP_KEEPINTVL) when supported"

    def test_keepalive_includes_keepcnt(self) -> None:
        if not hasattr(socket_module, "TCP_KEEPCNT"):
            pytest.skip("platform does not support TCP_KEEPCNT")

        socket_options = _build_keepalive_socket_options()
        assert _has_option(
            socket_options, socket_module.IPPROTO_TCP, socket_module.TCP_KEEPCNT
        ), "Keepalive options should set the probe count (TCP_KEEPCNT) when supported"

    def test_custom_http_client_transport_not_overridden(self) -> None:
        with httpx.Client() as http_client:
            client = OpenAI(base_url=base_url, api_key=api_key, http_client=http_client)
            assert (
                client._client is http_client
            ), "A caller-supplied http_client must not be replaced"

    def test_custom_transport_kwarg_not_overridden(self) -> None:
        # Passing an explicit transport must win over the keepalive default that
        # DefaultHttpxClient installs via kwargs.setdefault("transport", ...).
        custom_transport = httpx.HTTPTransport()
        http_client = DefaultHttpxClient(transport=custom_transport)

        assert (
            http_client._transport is custom_transport
        ), "An explicit transport= kwarg must not be overridden by the keepalive default"

    def test_build_keepalive_socket_options_returns_valid_list(self) -> None:
        socket_options = _build_keepalive_socket_options()

        assert isinstance(socket_options, list), "helper should return a list"
        assert len(socket_options) >= 1, "helper should return at least SO_KEEPALIVE"

        for opt in socket_options:
            assert isinstance(opt, tuple), f"each option should be a tuple, got {opt!r}"
            assert len(opt) == 3, f"each option should be a (level, optname, value) triple, got {opt!r}"
            assert all(
                isinstance(part, int) for part in opt
            ), f"every element of an option triple should be an int, got {opt!r}"

        assert any(
            opt == (socket_module.SOL_SOCKET, socket_module.SO_KEEPALIVE, 1)
            for opt in socket_options
        ), "helper must always enable SO_KEEPALIVE"


class TestAsyncOpenAI:
    async def test_default_async_transport_has_tcp_keepalive(self) -> None:
        client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        transport = client._client._transport

        assert isinstance(
            transport, httpx.AsyncHTTPTransport
        ), "Default async client should use a concrete httpx.AsyncHTTPTransport"

        socket_options = _extract_socket_options(transport)
        assert _has_option(
            socket_options, socket_module.SOL_SOCKET, socket_module.SO_KEEPALIVE
        ), "Default async transport must enable SO_KEEPALIVE to survive NAT idle timeouts"

    async def test_custom_async_http_client_transport_not_overridden(self) -> None:
        async with httpx.AsyncClient() as http_client:
            client = AsyncOpenAI(base_url=base_url, api_key=api_key, http_client=http_client)
            assert (
                client._client is http_client
            ), "A caller-supplied async http_client must not be replaced"

    async def test_custom_async_transport_kwarg_not_overridden(self) -> None:
        custom_transport = httpx.AsyncHTTPTransport()
        http_client = DefaultAsyncHttpxClient(transport=custom_transport)

        assert (
            http_client._transport is custom_transport
        ), "An explicit transport= kwarg must not be overridden by the keepalive default"
