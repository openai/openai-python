import inspect
from contextlib import contextmanager
from functools import partial, update_wrapper, wraps
from types import TracebackType
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    NewType,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
    overload,
)

import httpx2 as httpx

from .mocks import Mocker
from .models import (
    AllMockedAssertionError,
    CallList,
    PassThrough,
    ResolvedRoute,
    Route,
    RouteList,
    SideEffectError,
)
from .patterns import Pattern, merge_patterns, parse_url_patterns
from .types import DefaultType, ResolvedResponseTypes, RouteResultTypes, URLPatternTypes

Default = NewType("Default", object)
DEFAULT = Default(...)


class Router:
    def __init__(
        self,
        *,
        assert_all_called: bool = True,
        assert_all_mocked: bool = True,
        base_url: Optional[str] = None,
    ) -> None:
        self._assert_all_called = assert_all_called
        self._assert_all_mocked = assert_all_mocked
        self._bases = parse_url_patterns(base_url, exact=False)

        self.routes = RouteList()
        self.calls = CallList()

        self._snapshots: List[Tuple] = []
        self.snapshot()

    def clear(self) -> None:
        """
        Clears all routes. May be rolled back to snapshot state.
        """
        self.routes.clear()

    def snapshot(self) -> None:
        """
        Snapshots current routes and calls state.
        """
        # Snapshot current routes and calls
        routes = RouteList(self.routes)
        calls = CallList(self.calls)
        self._snapshots.append((routes, calls))

        # Snapshot each route state
        for route in routes:
            route.snapshot()

    def rollback(self) -> None:
        """
        Rollbacks routes, and optionally calls, to snapshot state.
        """
        if not self._snapshots:
            return

        # Revert added routes and calls to last snapshot
        routes, calls = self._snapshots.pop()
        self.routes[:] = routes
        self.calls[:] = calls

        # Revert each route state to last snapshot
        for route in self.routes:
            route.rollback()

    def reset(self) -> None:
        """
        Resets call stats.
        """
        self.calls.clear()
        for route in self.routes:
            route.reset()

    def assert_all_called(self) -> None:
        not_called_routes = [route for route in self.routes if not route.called]
        assert not_called_routes == [], "RESPX: some routes were not called!"

    def __getitem__(self, name: str) -> Route:
        return self.routes[name]

    @overload
    def pop(self, name: str) -> Route:
        ...  # pragma: nocover

    @overload
    def pop(self, name: str, default: DefaultType) -> Union[Route, DefaultType]:
        ...  # pragma: nocover

    def pop(self, name, default=...):
        """
        Removes a route by name and returns it.

        Raises KeyError when `default` not provided and name is not found.
        """
        try:
            return self.routes.pop(name)
        except KeyError as ex:
            if default is ...:
                raise ex
            return default

    def route(
        self, *patterns: Pattern, name: Optional[str] = None, **lookups: Any
    ) -> Route:
        route = Route(*patterns, **lookups)
        return self.add(route, name=name)

    def add(self, route: Route, *, name: Optional[str] = None) -> Route:
        """
        Adds a route with optionally given name,
        replacing any existing route with same name or pattern.
        """
        if not isinstance(route, Route):
            raise ValueError(
                f"Invalid route {route!r}, please use respx.route(...).mock(...)"
            )

        route._pattern = merge_patterns(route.pattern, **self._bases)
        route = self.routes.add(route, name=name)
        return route

    def request(
        self,
        method: str,
        url: Optional[URLPatternTypes] = None,
        *,
        name: Optional[str] = None,
        **lookups: Any,
    ) -> Route:
        if lookups:
            # Validate that lookups doesn't contain method or url
            pattern_keys = {p.split("__", 1)[0] for p in lookups.keys()}
            if "method" in pattern_keys:
                raise TypeError("Got multiple values for pattern 'method'")
            elif url and "url" in pattern_keys:
                raise TypeError("Got multiple values for pattern 'url'")

        return self.route(method=method, url=url, name=name, **lookups)

    def get(
        self,
        url: Optional[URLPatternTypes] = None,
        *,
        name: Optional[str] = None,
        **lookups: Any,
    ) -> Route:
        return self.request(method="GET", url=url, name=name, **lookups)

    def post(
        self,
        url: Optional[URLPatternTypes] = None,
        *,
        name: Optional[str] = None,
        **lookups: Any,
    ) -> Route:
        return self.request(method="POST", url=url, name=name, **lookups)

    def put(
        self,
        url: Optional[URLPatternTypes] = None,
        *,
        name: Optional[str] = None,
        **lookups: Any,
    ) -> Route:
        return self.request(method="PUT", url=url, name=name, **lookups)

    def patch(
        self,
        url: Optional[URLPatternTypes] = None,
        *,
        name: Optional[str] = None,
        **lookups: Any,
    ) -> Route:
        return self.request(method="PATCH", url=url, name=name, **lookups)

    def delete(
        self,
        url: Optional[URLPatternTypes] = None,
        *,
        name: Optional[str] = None,
        **lookups: Any,
    ) -> Route:
        return self.request(method="DELETE", url=url, name=name, **lookups)

    def head(
        self,
        url: Optional[URLPatternTypes] = None,
        *,
        name: Optional[str] = None,
        **lookups: Any,
    ) -> Route:
        return self.request(method="HEAD", url=url, name=name, **lookups)

    def options(
        self,
        url: Optional[URLPatternTypes] = None,
        *,
        name: Optional[str] = None,
        **lookups: Any,
    ) -> Route:
        return self.request(method="OPTIONS", url=url, name=name, **lookups)

    def record(
        self,
        request: httpx.Request,
        *,
        response: Optional[httpx.Response] = None,
        route: Optional[Route] = None,
    ) -> None:
        call = self.calls.record(request, response)
        if route:
            route.calls.append(call)

    @contextmanager
    def resolver(self, request: httpx.Request) -> Generator[ResolvedRoute, None, None]:
        resolved = ResolvedRoute()

        try:
            yield resolved

            if resolved.route is None:
                # Assert we always get a route match, if check is enabled
                if self._assert_all_mocked:
                    raise AllMockedAssertionError(f"RESPX: {request!r} not mocked!")

                # Auto mock a successful empty response
                resolved.response = httpx.Response(200)

            elif resolved.response == request:
                # Pass-through request
                raise PassThrough(
                    f"Request marked to pass through: {request!r}",
                    request=request,
                    origin=resolved.route,
                )

            else:
                # Mocked response
                assert isinstance(resolved.response, httpx.Response)

        except SideEffectError as error:
            self.record(request, response=None, route=error.route)
            raise error.origin from error
        except PassThrough:
            self.record(request, response=None, route=resolved.route)
            raise
        else:
            self.record(request, response=resolved.response, route=resolved.route)

    def resolve(self, request: httpx.Request) -> ResolvedRoute:
        with self.resolver(request) as resolved:
            for route in self.routes:
                prospect = route.match(request)
                if prospect is not None:
                    resolved.route = route
                    resolved.response = cast(ResolvedResponseTypes, prospect)
                    break

        if resolved.response and isinstance(resolved.response.stream, httpx.ByteStream):
            resolved.response.read()  # Pre-read stream

        return resolved

    async def aresolve(self, request: httpx.Request) -> ResolvedRoute:
        with self.resolver(request) as resolved:
            for route in self.routes:
                prospect: RouteResultTypes = route.match(request)

                # Await async side effect and wrap any exception
                if inspect.isawaitable(prospect):
                    try:
                        prospect = await prospect
                    except Exception as error:
                        raise SideEffectError(route, origin=error) from error

                if prospect is not None:
                    resolved.route = route
                    resolved.response = cast(ResolvedResponseTypes, prospect)
                    break

        if resolved.response and isinstance(resolved.response.stream, httpx.ByteStream):
            await resolved.response.aread()  # Pre-read stream

        return resolved

    def handler(self, request: httpx.Request) -> httpx.Response:
        resolved = self.resolve(request)
        assert isinstance(resolved.response, httpx.Response)
        return resolved.response

    async def async_handler(self, request: httpx.Request) -> httpx.Response:
        resolved = await self.aresolve(request)
        assert isinstance(resolved.response, httpx.Response)
        return resolved.response


class MockRouter(Router):
    def __init__(
        self,
        *,
        assert_all_called: bool = True,
        assert_all_mocked: bool = True,
        base_url: Optional[str] = None,
        using: Optional[Union[str, Default]] = DEFAULT,
    ) -> None:
        super().__init__(
            assert_all_called=assert_all_called,
            assert_all_mocked=assert_all_mocked,
            base_url=base_url,
        )
        self.Mocker: Optional[Type[Mocker]] = None
        self._using = using

    @overload
    def __call__(
        self,
        func: None = None,
        *,
        assert_all_called: Optional[bool] = None,
        assert_all_mocked: Optional[bool] = None,
        base_url: Optional[str] = None,
        using: Optional[Union[str, Default]] = DEFAULT,
    ) -> "MockRouter":
        ...  # pragma: nocover

    @overload
    def __call__(
        self,
        func: Callable = ...,
        *,
        assert_all_called: Optional[bool] = None,
        assert_all_mocked: Optional[bool] = None,
        base_url: Optional[str] = None,
        using: Optional[Union[str, Default]] = DEFAULT,
    ) -> Callable:
        ...  # pragma: nocover

    def __call__(
        self,
        func: Optional[Callable] = None,
        *,
        assert_all_called: Optional[bool] = None,
        assert_all_mocked: Optional[bool] = None,
        base_url: Optional[str] = None,
        using: Optional[Union[str, Default]] = DEFAULT,
    ) -> Union["MockRouter", Callable]:
        """
        Decorator or Context Manager.

        Use decorator/manager with parentheses for local state, or without parentheses
        for global state, i.e. shared patterns added outside of scope.
        """
        if func is None:
            # Parentheses used, branch out to new nested instance.
            # - Only stage when using local ctx `with respx.mock(...) as respx_mock:`
            # - First stage when using local decorator `@respx.mock(...)`
            #   FYI, global ctx `with respx.mock:` hits __enter__ directly
            settings: Dict[str, Any] = {
                "base_url": base_url,
                "using": using,
            }
            if assert_all_called is not None:
                settings["assert_all_called"] = assert_all_called
            if assert_all_mocked is not None:
                settings["assert_all_mocked"] = assert_all_mocked
            respx_mock = self.__class__(**settings)
            return respx_mock

        # Determine if decorated function needs a `respx_mock` instance
        is_async = inspect.iscoroutinefunction(func)
        argspec = inspect.getfullargspec(func)
        needs_mock_reference = "respx_mock" in argspec.args

        if needs_mock_reference:
            func = partial(func, respx_mock=self)

        # Async Decorator
        async def _async_decorator(*args, **kwargs):
            assert func is not None
            async with self:
                return await func(*args, **kwargs)

        # Sync Decorator
        def _sync_decorator(*args, **kwargs):
            assert func is not None
            with self:
                return func(*args, **kwargs)

        if needs_mock_reference:
            async_decorator = wraps(func)(_async_decorator)
            sync_decorator = wraps(func)(_sync_decorator)
        else:
            async_decorator = update_wrapper(_async_decorator, func)
            sync_decorator = update_wrapper(_sync_decorator, func)

        # Dispatch async/sync decorator, depending on decorated function.
        # - Only stage when using global decorator `@respx.mock`
        # - Second stage when using local decorator `@respx.mock(...)`
        return async_decorator if is_async else sync_decorator

    def __enter__(self) -> "MockRouter":
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        self.stop(quiet=bool(exc_type is not None))

    async def __aenter__(self) -> "MockRouter":
        return self.__enter__()

    async def __aexit__(self, *args: Any) -> None:
        self.__exit__(*args)

    @property
    def using(self) -> Optional[str]:
        from tests.respx2.mocks import DEFAULT_MOCKER

        if self._using is None:
            using = None
        elif self._using is DEFAULT:
            using = DEFAULT_MOCKER
        elif isinstance(self._using, str):
            using = self._using
        else:
            raise ValueError(f"Invalid Router `using` kwarg: {self._using!r}")

        return using

    def start(self) -> None:
        """
        Register transport, snapshot router and start patching.
        """
        self.snapshot()
        self.Mocker = Mocker.registry.get(self.using or "")
        if self.Mocker:
            self.Mocker.register(self)
            self.Mocker.start()

    def stop(self, clear: bool = True, reset: bool = True, quiet: bool = False) -> None:
        """
        Unregister transport and rollback router.
        Stop patching when no registered transports left.
        """
        unregistered = self.Mocker.unregister(self) if self.Mocker else True

        try:
            if unregistered and not quiet and self._assert_all_called:
                self.assert_all_called()
        finally:
            if clear:
                self.rollback()
            if reset:
                self.reset()
            if self.Mocker:
                self.Mocker.stop()
