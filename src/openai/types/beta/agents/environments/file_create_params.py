# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = ["FileCreateParams", "HostedEnvironmentFileParamFileID", "HostedEnvironmentFileParamInline"]


class HostedEnvironmentFileParamFileID(TypedDict, total=False):
    file_id: Required[str]
    """The ID of the uploaded file."""

    path: Required[str]
    """The absolute destination path inside `/workspace`."""

    type: Required[Literal["file_id"]]
    """The type of the object. Always `file_id`."""


class HostedEnvironmentFileParamInline(TypedDict, total=False):
    data: Required[str]
    """The standard-base64-encoded file contents."""

    path: Required[str]
    """The absolute destination path inside `/workspace`."""

    type: Required[Literal["inline"]]
    """The type of the object. Always `inline`."""


FileCreateParams: TypeAlias = Union[HostedEnvironmentFileParamFileID, HostedEnvironmentFileParamInline]
