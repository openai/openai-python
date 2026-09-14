from __future__ import annotations

import array
import base64
from typing import cast

from ..._types import Omit, NotGiven
from ..._utils import is_given
from ..._extras import numpy as np, has_numpy
from ...types.create_embedding_response import CreateEmbeddingResponse


def parse_embedding_response(
    obj: CreateEmbeddingResponse, *, encoding_format: str | Omit | NotGiven
) -> CreateEmbeddingResponse:
    if is_given(encoding_format):
        # don't modify the response object if a user explicitly asked for a format
        return obj

    if not obj.data:
        raise ValueError("No embedding data received")

    if not any(isinstance(embedding.embedding, str) for embedding in obj.data):
        return obj

    use_numpy = has_numpy()
    for embedding in obj.data:
        data = cast(object, embedding.embedding)
        if not isinstance(data, str):
            continue
        if not use_numpy:
            # use array for base64 optimisation
            embedding.embedding = array.array("f", base64.b64decode(data)).tolist()
        else:
            embedding.embedding = np.frombuffer(  # type: ignore[no-untyped-call]
                base64.b64decode(data), dtype="float32"
            ).tolist()

    return obj
