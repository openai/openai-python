# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing import Union

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Embedding"]


class Embedding(BaseModel):
    embedding: Union[List[float], str]
    """The embedding vector, which can be either:
    - a list of floats (if encoding_format is "float")
    - a base64 encoded string (if encoding_format is "base64").

    The length of the vector depends on the model as listed in the
    [embedding guide](https://platform.openai.com/docs/guides/embeddings).
    """

    index: int
    """The index of the embedding in the list of embeddings."""

    object: Literal["embedding"]
    """The object type, which is always "embedding"."""
