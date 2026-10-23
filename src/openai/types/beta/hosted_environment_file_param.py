# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = ["HostedEnvironmentFileParam", "HostedEnvironmentFileParamFileID", "HostedEnvironmentFileParamInline"]


class HostedEnvironmentFileParamFileID(TypedDict, total=False):
    """A file previously uploaded through the OpenAI Files API."""

    file_id: Required[str]
    """The ID of the uploaded file."""

    path: Required[str]
    """The absolute destination path inside `/workspace`."""

    type: Required[Literal["file_id"]]
    """The type of the object. Always `file_id`."""


class HostedEnvironmentFileParamInline(TypedDict, total=False):
    """A file supplied directly as standard-base64 data."""

    data: Required[str]
    """The standard-base64-encoded file contents."""

    path: Required[str]
    """The absolute destination path inside `/workspace`."""

    type: Required[Literal["inline"]]
    """The type of the object. Always `inline`."""


HostedEnvironmentFileParam: TypeAlias = Union[HostedEnvironmentFileParamFileID, HostedEnvironmentFileParamInline]
