from __future__ import annotations

from typing import TYPE_CHECKING, Any
from typing_extensions import override

from .._utils import LazyProxy
from ._common import MissingDependencyError, format_instructions

if TYPE_CHECKING:
    import argcomplete as argcomplete


ARGCOMPLETE_INSTRUCTIONS = format_instructions(library="argcomplete", extra="cli")


class ArgcompleteProxy(LazyProxy[Any]):
    @override
    def __load__(self) -> Any:
        try:
            import argcomplete
        except ImportError as err:
            raise MissingDependencyError(ARGCOMPLETE_INSTRUCTIONS) from err

        return argcomplete


if not TYPE_CHECKING:
    argcomplete = ArgcompleteProxy()


def has_argcomplete() -> bool:
    try:
        import argcomplete  # noqa: F401  # pyright: ignore[reportUnusedImport]
    except ImportError:
        return False

    return True
