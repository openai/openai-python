# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..._types import SequenceNotStr

__all__ = [
    "BetaFileSearchToolParam",
    "Filters",
    "FiltersComparisonFilter",
    "FiltersCompoundFilter",
    "FiltersCompoundFilterFilter",
    "FiltersCompoundFilterFilterComparisonFilter",
    "RankingOptions",
    "RankingOptionsHybridSearch",
]


class FiltersComparisonFilter(TypedDict, total=False):
    """
    A filter used to compare a specified attribute key to a given value using a defined comparison operation.
    """

    key: Required[str]
    """The key to compare against the value."""

    type: Required[Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin"]]
    """
    Specifies the comparison operator: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`,
    `nin`.

    - `eq`: equals
    - `ne`: not equal
    - `gt`: greater than
    - `gte`: greater than or equal
    - `lt`: less than
    - `lte`: less than or equal
    - `in`: in
    - `nin`: not in
    """

    value: Required[Union[str, float, bool, SequenceNotStr[Union[str, float]]]]
    """
    The value to compare against the attribute key; supports string, number, or
    boolean types.
    """


class FiltersCompoundFilterFilterComparisonFilter(TypedDict, total=False):
    """
    A filter used to compare a specified attribute key to a given value using a defined comparison operation.
    """

    key: Required[str]
    """The key to compare against the value."""

    type: Required[Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin"]]
    """
    Specifies the comparison operator: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`,
    `nin`.

    - `eq`: equals
    - `ne`: not equal
    - `gt`: greater than
    - `gte`: greater than or equal
    - `lt`: less than
    - `lte`: less than or equal
    - `in`: in
    - `nin`: not in
    """

    value: Required[Union[str, float, bool, SequenceNotStr[Union[str, float]]]]
    """
    The value to compare against the attribute key; supports string, number, or
    boolean types.
    """


FiltersCompoundFilterFilter: TypeAlias = Union[FiltersCompoundFilterFilterComparisonFilter, object]


class FiltersCompoundFilter(TypedDict, total=False):
    """Combine multiple filters using `and` or `or`."""

    filters: Required[Iterable[FiltersCompoundFilterFilter]]
    """Array of filters to combine.

    Items can be `ComparisonFilter` or `CompoundFilter`.
    """

    type: Required[Literal["and", "or"]]
    """Type of operation: `and` or `or`."""


Filters: TypeAlias = Union[FiltersComparisonFilter, FiltersCompoundFilter]


class RankingOptionsHybridSearch(TypedDict, total=False):
    """
    Weights that control how reciprocal rank fusion balances semantic embedding matches versus sparse keyword matches when hybrid search is enabled.
    """

    embedding_weight: Required[float]
    """The weight of the embedding in the reciprocal ranking fusion."""

    text_weight: Required[float]
    """The weight of the text in the reciprocal ranking fusion."""


class RankingOptions(TypedDict, total=False):
    """Ranking options for search."""

    hybrid_search: RankingOptionsHybridSearch
    """
    Weights that control how reciprocal rank fusion balances semantic embedding
    matches versus sparse keyword matches when hybrid search is enabled.
    """

    ranker: Literal["auto", "default-2024-11-15"]
    """The ranker to use for the file search."""

    score_threshold: float
    """The score threshold for the file search, a number between 0 and 1.

    Numbers closer to 1 will attempt to return only the most relevant results, but
    may return fewer results.
    """


class BetaFileSearchToolParam(TypedDict, total=False):
    """A tool that searches for relevant content from uploaded files.

    Learn more about the [file search tool](https://platform.openai.com/docs/guides/tools-file-search).
    """

    type: Required[Literal["file_search"]]
    """The type of the file search tool. Always `file_search`."""

    vector_store_ids: Required[SequenceNotStr[str]]
    """The IDs of the vector stores to search."""

    filters: Optional[Filters]
    """A filter to apply."""

    max_num_results: int
    """The maximum number of results to return.

    This number should be between 1 and 50 inclusive.
    """

    ranking_options: RankingOptions
    """Ranking options for search."""
