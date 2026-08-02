# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel

__all__ = [
    "BetaFileSearchTool",
    "Filters",
    "FiltersComparisonFilter",
    "FiltersCompoundFilter",
    "FiltersCompoundFilterFilter",
    "FiltersCompoundFilterFilterComparisonFilter",
    "RankingOptions",
    "RankingOptionsHybridSearch",
]


class FiltersComparisonFilter(BaseModel):
    """
    A filter used to compare a specified attribute key to a given value using a defined comparison operation.
    """

    key: str
    """The key to compare against the value."""

    type: Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin"]
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

    value: Union[str, float, bool, List[Union[str, float]]]
    """
    The value to compare against the attribute key; supports string, number, or
    boolean types.
    """


class FiltersCompoundFilterFilterComparisonFilter(BaseModel):
    """
    A filter used to compare a specified attribute key to a given value using a defined comparison operation.
    """

    key: str
    """The key to compare against the value."""

    type: Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin"]
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

    value: Union[str, float, bool, List[Union[str, float]]]
    """
    The value to compare against the attribute key; supports string, number, or
    boolean types.
    """


FiltersCompoundFilterFilter: TypeAlias = Union[FiltersCompoundFilterFilterComparisonFilter, object]


class FiltersCompoundFilter(BaseModel):
    """Combine multiple filters using `and` or `or`."""

    filters: List[FiltersCompoundFilterFilter]
    """Array of filters to combine.

    Items can be `ComparisonFilter` or `CompoundFilter`.
    """

    type: Literal["and", "or"]
    """Type of operation: `and` or `or`."""


Filters: TypeAlias = Union[FiltersComparisonFilter, FiltersCompoundFilter, None]


class RankingOptionsHybridSearch(BaseModel):
    """
    Weights that control how reciprocal rank fusion balances semantic embedding matches versus sparse keyword matches when hybrid search is enabled.
    """

    embedding_weight: float
    """The weight of the embedding in the reciprocal ranking fusion."""

    text_weight: float
    """The weight of the text in the reciprocal ranking fusion."""


class RankingOptions(BaseModel):
    """Ranking options for search."""

    hybrid_search: Optional[RankingOptionsHybridSearch] = None
    """
    Weights that control how reciprocal rank fusion balances semantic embedding
    matches versus sparse keyword matches when hybrid search is enabled.
    """

    ranker: Optional[Literal["auto", "default-2024-11-15"]] = None
    """The ranker to use for the file search."""

    score_threshold: Optional[float] = None
    """The score threshold for the file search, a number between 0 and 1.

    Numbers closer to 1 will attempt to return only the most relevant results, but
    may return fewer results.
    """


class BetaFileSearchTool(BaseModel):
    """A tool that searches for relevant content from uploaded files.

    Learn more about the [file search tool](https://platform.openai.com/docs/guides/tools-file-search).
    """

    type: Literal["file_search"]
    """The type of the file search tool. Always `file_search`."""

    vector_store_ids: List[str]
    """The IDs of the vector stores to search."""

    filters: Optional[Filters] = None
    """A filter to apply."""

    max_num_results: Optional[int] = None
    """The maximum number of results to return.

    This number should be between 1 and 50 inclusive.
    """

    ranking_options: Optional[RankingOptions] = None
    """Ranking options for search."""
