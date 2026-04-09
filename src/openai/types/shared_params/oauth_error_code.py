# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, TypeAlias

__all__ = ["OAuthErrorCode"]

OAuthErrorCode: TypeAlias = Union[Literal["invalid_grant", "invalid_subject_token"], str]
