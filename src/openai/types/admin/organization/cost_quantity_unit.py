# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, TypeAlias

__all__ = ["CostQuantityUnit"]

CostQuantityUnit: TypeAlias = Union[
    str,
    Literal[
        "tokens",
        "1000_tokens",
        "duration_seconds",
        "duration_minutes",
        "duration_hours",
        "gibibyte_hours",
        "images",
        "characters",
    ],
]
