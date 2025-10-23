# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RealtimeMcphttpErrorParam"]


class RealtimeMcphttpErrorParam(TypedDict, total=False):
    code: Required[int]

    message: Required[str]

    type: Required[Literal["http_error"]]
