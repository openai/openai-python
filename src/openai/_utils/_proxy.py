from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Iterable, cast
from typing_extensions import ClassVar

T = TypeVar("T")


class LazyProxy(Generic[T], ABC):
    """Implements data methods to pretend that an instance is another instance.

    This includes forwarding attribute access and othe methods.
    """

    should_cache: ClassVar[bool] = False

    def __init__(self) -> None:
        self.__proxied: T | None = None

    def __getattr__(self, attr: str) -> object:
        return getattr(self.__get_proxied__(), attr)

    def __repr__(self) -> str:
        return repr(self.__get_proxied__())

    def __str__(self) -> str:
        return str(self.__get_proxied__())

    def __dir__(self) -> Iterable[str]:
        return self.__get_proxied__().__dir__()

    @property  # type: ignore
    def __class__(self) -> type:
        return self.__get_proxied__().__class__

    def __get_proxied__(self) -> T:
        if not self.should_cache:
            return self.__load__()

        proxied = self.__proxied
        if proxied is not None:
            return proxied

        self.__proxied = proxied = self.__load__()
        return proxied

    def __set_proxied__(self, value: T) -> None:
        self.__proxied = value

    def __as_proxied__(self) -> T:
        """Helper method that returns the current proxy, typed as the loaded object"""
        return cast(T, self)

    @abstractmethod
    def __load__(self) -> T:
        ...
