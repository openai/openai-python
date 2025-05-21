# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = ["ResponseCodeInterpreterToolCallParam", "Result", "ResultLogs", "ResultFiles", "ResultFilesFile"]


class ResultLogs(TypedDict, total=False):
    logs: Required[str]
    """The logs of the code interpreter tool call."""

    type: Required[Literal["logs"]]
    """The type of the code interpreter text output. Always `logs`."""


class ResultFilesFile(TypedDict, total=False):
    file_id: Required[str]
    """The ID of the file."""

    mime_type: Required[str]
    """The MIME type of the file."""


class ResultFiles(TypedDict, total=False):
    files: Required[Iterable[ResultFilesFile]]

    type: Required[Literal["files"]]
    """The type of the code interpreter file output. Always `files`."""


Result: TypeAlias = Union[ResultLogs, ResultFiles]


class ResponseCodeInterpreterToolCallParam(TypedDict, total=False):
    id: Required[str]
    """The unique ID of the code interpreter tool call."""

    code: Required[str]
    """The code to run."""

    results: Required[Iterable[Result]]
    """The results of the code interpreter tool call."""

    status: Required[Literal["in_progress", "interpreting", "completed"]]
    """The status of the code interpreter tool call."""

    type: Required[Literal["code_interpreter_call"]]
    """The type of the code interpreter tool call. Always `code_interpreter_call`."""

    container_id: str
    """The ID of the container used to run the code."""
