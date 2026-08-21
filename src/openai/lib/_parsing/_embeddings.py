from __future__ import annotations

import sys
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

    for embedding in obj.data:
        data = cast(object, embedding.embedding)
        if not isinstance(data, str):
            continue
        decoded = base64.b64decode(data)
        if not has_numpy():
            # use array for base64 optimisation
            floats = array.array("f", decoded)
            if sys.byteorder == "big":
                floats.byteswap()
            embedding.embedding = floats.tolist()
        else:
            embedding.embedding = np.frombuffer(  # type: ignore[no-untyped-call]
                decoded, dtype="<f4"
            ).tolist()

    return obj
