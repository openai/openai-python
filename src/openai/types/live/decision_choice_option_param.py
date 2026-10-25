# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, TypedDict

__all__ = ["DecisionChoiceOptionParam"]


class DecisionChoiceOptionParam(TypedDict, total=False):
    value: Required[Union[str, bool]]

    description: str
