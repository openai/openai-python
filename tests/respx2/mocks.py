import inspect
from abc import ABC
from types import MappingProxyType
from typing import TYPE_CHECKING, ClassVar, Dict, List, Type
from unittest import mock

import httpcore2 as httpcore
import httpx2 as httpx

from tests.respx2.patterns import parse_url

from .models import AllMockedAssertionError, PassThrough
from .transports import TryTransport

if TYPE_CHECKING:
    from .router import Router  # pragma: nocover

__all__ = ["Mocker", "HTTPCoreMocker"]


class Mocker(ABC):
    _patches: ClassVar[List[mock._patch]]
    name: ClassVar[str]
    routers: ClassVar[List["Router"]]
    targets: ClassVar[List[str]]
    target_methods: ClassVar[List[str]]

    # Automatically register all the subclasses in this dict
    __registry: ClassVar[Dict[str, Type["Mocker"]]] = {}
    registry = MappingProxyType(__registry)

    def __init_subclass__(cls) -> None:
        if not getattr(cls, "name", None) or ABC in cls.__bases__:
            return

        if cls.name in cls.__registry:
            raise TypeError(
                "Subclasses of Mocker must define a unique name. "
                f"{cls.name!r} is already defined as {cls.__registry[cls.name]!r}"
            )

        cls.routers = []
        cls._patches = []
        cls.__registry[cls.name] = cls

    @classmethod
    def register(cls, router: "Router") -> None:
        cls.routers.append(router)

    @classmethod
    def unregister(cls, router: "Router") -> bool:
        if router in cls.routers:
            cls.routers.remove(router)
            return True
        return False

    @classmethod
    def add_targets(cls, *targets: str) -> None:
        targets = tuple(filter(lambda t: t not in cls.targets, targets))
        if targets:
            cls.targets.extend(targets)
            cls.restart()

    @classmethod
    def remove_targets(cls, *targets: str) -> None:
        targets = tuple(filter(lambda t: t in cls.targets, targets))
        if targets:
            for target in targets:
                cls.targets.remove(target)
            cls.restart()

    @classmethod
    def start(cls) -> None:
        # Ensure we only patch once!
        if cls._patches:
            return

        # Start patching target transports
        for target in cls.targets:
            for method in cls.target_methods:
                try:
                    spec = f"{target}.{method}"
                    patch = mock.patch(spec, spec=True, new_callable=cls.mock)
                    patch.start()
                    cls._patches.append(patch)
                except AttributeError:
                    pass

    @classmethod
    def stop(cls, force: bool = False) -> None:
        # Ensure we don't stop patching when registered transports exists
        if cls.routers and not force:
            return

        # Stop patching HTTPX
        while cls._patches:
            patch = cls._patches.pop()
            patch.stop()

    @classmethod
    def restart(cls) -> None:
        # Only stop and start if started
        if cls._patches:  # pragma: nocover
            cls.stop(force=True)
            cls.start()

    @classmethod
    def handler(cls, httpx_request):
        httpx_response = None
        assertion_error = None
        for router in cls.routers:
            try:
                httpx_response = router.handler(httpx_request)
            except AllMockedAssertionError as error:
                assertion_error = error
                continue
            else:
                break
        if assertion_error and not httpx_response:
            raise assertion_error
        return httpx_response

    @classmethod
    async def async_handler(cls, httpx_request):
        httpx_response = None
        assertion_error = None
        for router in cls.routers:
            try:
                httpx_response = await router.async_handler(httpx_request)
            except AllMockedAssertionError as error:
                assertion_error = error
                continue
            else:
                break
        if assertion_error and not httpx_response:
            raise assertion_error
        return httpx_response

    @classmethod
    def mock(cls, spec):
        raise NotImplementedError()  # pragma: nocover


class HTTPXMocker(Mocker):
    name = "httpx"
    targets = [
        "httpx2._client.Client",
        "httpx2._client.AsyncClient",
    ]
    target_methods = ["_transport_for_url"]

    @classmethod
    def mock(cls, spec):
        def _transport_for_url(self, *args, **kwargs):
            handler = (
                cls.async_handler
                if inspect.iscoroutinefunction(self.request)
                else cls.handler
            )
            mock_transport = httpx.MockTransport(handler)
            pass_through_transport = spec(self, *args, **kwargs)
            transport = TryTransport([mock_transport, pass_through_transport])
            return transport

        return _transport_for_url


class AbstractRequestMocker(Mocker):
    @classmethod
    def mock(cls, spec):
        if spec.__name__ not in cls.target_methods:
            # Prevent mocking mock
            return spec

        argspec = inspect.getfullargspec(spec)

        def mock(self, *args, **kwargs):
            kwargs = cls._merge_args_and_kwargs(argspec, args, kwargs)
            request = cls.to_httpx_request(**kwargs)
            request, kwargs = cls.prepare_sync_request(request, **kwargs)
            response = cls._send_sync_request(
                request, target_spec=spec, instance=self, **kwargs
            )
            return response

        async def amock(self, *args, **kwargs):
            kwargs = cls._merge_args_and_kwargs(argspec, args, kwargs)
            request = cls.to_httpx_request(**kwargs)
            request, kwargs = await cls.prepare_async_request(request, **kwargs)
            response = await cls._send_async_request(
                request, target_spec=spec, instance=self, **kwargs
            )
            return response

        return amock if inspect.iscoroutinefunction(spec) else mock

    @classmethod
    def _merge_args_and_kwargs(cls, argspec, args, kwargs):
        arg_names = argspec.args[1:]  # Omit self
        new_kwargs = (
            dict(zip(arg_names[-len(argspec.defaults) :], argspec.defaults))
            if argspec.defaults
            else dict()
        )
        new_kwargs.update(zip(arg_names, args))
        new_kwargs.update(kwargs)
        return new_kwargs

    @classmethod
    def _send_sync_request(cls, httpx_request, *, target_spec, instance, **kwargs):
        try:
            httpx_response = cls.handler(httpx_request)
        except PassThrough:
            response = target_spec(instance, **kwargs)
        else:
            response = cls.from_sync_httpx_response(httpx_response, instance, **kwargs)
        return response

    @classmethod
    async def _send_async_request(
        cls, httpx_request, *, target_spec, instance, **kwargs
    ):
        try:
            httpx_response = await cls.async_handler(httpx_request)
        except PassThrough:
            response = await target_spec(instance, **kwargs)
        else:
            response = await cls.from_async_httpx_response(
                httpx_response, instance, **kwargs
            )
        return response

    @classmethod
    def prepare_sync_request(cls, httpx_request, **kwargs):
        """
        Sync pre-read request body
        """
        httpx_request.read()
        return httpx_request, kwargs

    @classmethod
    async def prepare_async_request(cls, httpx_request, **kwargs):
        """
        Async pre-read request body
        """
        await httpx_request.aread()
        return httpx_request, kwargs

    @classmethod
    def to_httpx_request(cls, **kwargs):
        raise NotImplementedError()  # pragma: nocover

    @classmethod
    def from_sync_httpx_response(cls, httpx_response, target, **kwargs):
        raise NotImplementedError()  # pragma: nocover

    @classmethod
    async def from_async_httpx_response(cls, httpx_response, target, **kwargs):
        raise NotImplementedError()  # pragma: nocover


class HTTPCoreMocker(AbstractRequestMocker):
    name = "httpcore"
    targets = [
        "httpcore2._sync.connection.HTTPConnection",
        "httpcore2._sync.connection_pool.ConnectionPool",
        "httpcore2._sync.http_proxy.HTTPProxy",
        "httpcore2._async.connection.AsyncHTTPConnection",
        "httpcore2._async.connection_pool.AsyncConnectionPool",
        "httpcore2._async.http_proxy.AsyncHTTPProxy",
    ]
    target_methods = ["handle_request", "handle_async_request"]

    @classmethod
    def prepare_sync_request(cls, httpx_request, **kwargs):
        """
        Sync pre-read request body, and update transport request arg.
        """
        httpx_request, kwargs = super().prepare_sync_request(httpx_request, **kwargs)
        kwargs["request"].stream = httpx_request.stream
        return httpx_request, kwargs

    @classmethod
    async def prepare_async_request(cls, httpx_request, **kwargs):
        """
        Async pre-read request body, and update transport request arg.
        """
        httpx_request, kwargs = await super().prepare_async_request(
            httpx_request, **kwargs
        )
        kwargs["request"].stream = httpx_request.stream
        return httpx_request, kwargs

    @classmethod
    def to_httpx_request(cls, **kwargs):
        """
        Create a `HTTPX` request from transport request arg.
        """
        request = kwargs["request"]
        method = (
            request.method.decode("ascii")
            if isinstance(request.method, bytes)
            else request.method
        )
        raw_url = (
            request.url.scheme,
            request.url.host,
            request.url.port,
            request.url.target,
        )
        return httpx.Request(
            method,
            parse_url(raw_url),
            headers=request.headers,
            stream=request.stream,
            extensions=request.extensions,
        )

    @classmethod
    def from_sync_httpx_response(cls, httpx_response, target, **kwargs):
        """
        Create a `httpcore` response from a `HTTPX` response.
        """
        return httpcore.Response(
            status=httpx_response.status_code,
            headers=httpx_response.headers.raw,
            content=httpx_response.stream,
            extensions=httpx_response.extensions,
        )

    @classmethod
    async def from_async_httpx_response(cls, httpx_response, target, **kwargs):
        """
        Create a `httpcore` response from a `HTTPX` response.
        """
        return cls.from_sync_httpx_response(httpx_response, target, **kwargs)


DEFAULT_MOCKER: str = HTTPCoreMocker.name
