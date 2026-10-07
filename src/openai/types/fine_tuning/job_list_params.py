# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import TypedDict

__all__ = ["JobListParams"]


class JobListParams(TypedDict, total=False):
    after: str
    """Identifier for the last job from the previous pagination request."""

    limit: int
    """Number of fine-tuning jobs to retrieve."""

    metadata: Optional[Dict[str, str]]
    """Optional metadata filter.

    To filter, use the syntax `metadata[k]=v`. Omitting the parameter or passing an
    empty object applies no metadata filter. An empty value, such as `metadata[k]=`,
    filters for that key with an empty string value. To select jobs with null
    metadata, send the literal query string `metadata=null`. Nullable caller types
    do not specify how a client serializes null for a deep-object parameter. Use a
    raw query parameter if the client omits null. Do not combine the two query
    forms.
    """
