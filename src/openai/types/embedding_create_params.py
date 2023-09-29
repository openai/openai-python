# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Literal, Required, TypedDict

__all__ = ["EmbeddingCreateParams"]


class EmbeddingCreateParams(TypedDict, total=False):
    input: Required[Union[str, List[str], List[int], List[List[int]]]]
    """Input text to embed, encoded as a string or array of tokens.

    To embed multiple inputs in a single request, pass an array of strings or array
    of token arrays. Each input must not exceed the max input tokens for the model
    (8191 tokens for `text-embedding-ada-002`) and cannot be an empty string.
    [Example Python code](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
    for counting tokens.
    """

    model: Required[Union[str, Literal["text-embedding-ada-002"]]]
    """ID of the model to use.

    You can use the
    [List models](https://platform.openai.com/docs/api-reference/models/list) API to
    see all of your available models, or see our
    [Model overview](https://platform.openai.com/docs/models/overview) for
    descriptions of them.
    """

    user: str
    """
    A unique identifier representing your end-user, which can help OpenAI to monitor
    and detect abuse.
    [Learn more](https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids).
    """
