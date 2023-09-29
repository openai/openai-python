from __future__ import annotations

from typing import TYPE_CHECKING, Any
from typing_extensions import ClassVar

from .._utils import LazyProxy
from ._common import MissingDependencyError, format_instructions

if TYPE_CHECKING:
    import numpy as numpy


NUMPY_INSTRUCTIONS = format_instructions(library="numpy", extra="datalib")


class NumpyProxy(LazyProxy[Any]):
    should_cache: ClassVar[bool] = True

    def __load__(self) -> Any:
        try:
            import numpy
        except ImportError:
            raise MissingDependencyError(NUMPY_INSTRUCTIONS)

        return numpy


if not TYPE_CHECKING:
    numpy = NumpyProxy()
