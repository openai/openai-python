# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, TypeAlias

__all__ = ["BetaResponseSteerErrorCode"]

BetaResponseSteerErrorCode: TypeAlias = Union[
    Literal[
        "response_not_found",
        "invalid_input",
        "steering_not_supported",
        "too_many_pending_steers",
        "response_already_completed",
        "response_not_active",
        "successor_creation_failed",
    ],
    str,
]
