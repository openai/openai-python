# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Literal, cast

import httpx2

from ._types import NotGiven
from ._exceptions import OpenAIError

DataResidency = Literal["global", "us", "eu", "ae"]

_DATA_RESIDENCY_BASE_URLS: dict[DataResidency, str] = {
    "global": "https://api.openai.com/v1",
    "us": "https://us.api.openai.com/v1",
    "eu": "https://eu.api.openai.com/v1",
    "ae": "https://ae.api.openai.com/v1",
}


def resolve_data_residency(
    data_residency: DataResidency | None,
    base_url: str | httpx2.URL | None | NotGiven,
    *,
    provider: object | None = None,
    websocket_base_url: str | httpx2.URL | None = None,
) -> str | httpx2.URL | None:
    """Resolve a named endpoint before inherited or environment options are applied."""
    if data_residency is None:
        return None if isinstance(base_url, NotGiven) else base_url
    if not isinstance(base_url, NotGiven):
        raise ValueError("The `data_residency` and `base_url` arguments are mutually exclusive")
    if websocket_base_url is not None:
        raise ValueError("The `data_residency` and `websocket_base_url` arguments are mutually exclusive")
    if provider is not None:
        raise OpenAIError("The `data_residency` and `provider` arguments are mutually exclusive")
    if not isinstance(cast(object, data_residency), str) or data_residency not in _DATA_RESIDENCY_BASE_URLS:
        raise ValueError("Invalid `data_residency`; expected one of 'global', 'us', 'eu', or 'ae'")
    return _DATA_RESIDENCY_BASE_URLS[data_residency]
