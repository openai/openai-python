# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["FileSearchToolParam", "FileSearch"]


class FileSearch(TypedDict, total=False):
    max_num_results: int
    """The maximum number of results the file search tool should output.

    The default is 20 for `gpt-4*` models and 5 for `gpt-3.5-turbo`. This number
    should be between 1 and 50 inclusive.

    Note that the file search tool may output fewer than `max_num_results` results.
    See the
    [file search tool documentation](https://platform.openai.com/docs/assistants/tools/file-search/number-of-chunks-returned)
    for more information.
    """


class FileSearchToolParam(TypedDict, total=False):
    type: Required[Literal["file_search"]]
    """The type of tool being defined: `file_search`"""

    file_search: FileSearch
    """Overrides for the file search tool."""
