# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, cast

from ._types import Body, Omit, NotGiven, FileTypes, RequestFiles
from ._utils._json import openapi_dumps


def encode_multipart(
    body: object,
    extra_body: Body | None,
    encodings: Mapping[str, tuple[str, bool]],
    raw_body_field: str | None = None,
    existing_files: RequestFiles | None = None,
) -> tuple[dict[str, object] | None, RequestFiles | None, bytes | None, str]:
    """Prepare explicitly encoded form fields without flattening their JSON contents."""
    if not isinstance(body, Mapping):
        raise TypeError("Multipart request body must be a mapping")
    if extra_body is not None and not isinstance(extra_body, Mapping):
        raise TypeError("Multipart extra_body must be a mapping")
    original = cast(Mapping[str, object], body)
    overrides = cast(Mapping[str, object], extra_body or {})
    merged = {key: value for key, value in {**original, **overrides}.items() if not isinstance(value, (Omit, NotGiven))}
    # A raw request alternative is safe only when there is no other payload to lose.
    # Explicit null remains a JSON part; only an omitted field selects the raw body.
    if not existing_files and raw_body_field is not None and set(merged) == {raw_body_field}:
        value = merged[raw_body_field]
        if not isinstance(value, str):
            raise TypeError("Raw multipart alternative must be a string")
        return None, None, value.encode("utf-8"), encodings[raw_body_field][0]

    files: list[tuple[str, FileTypes]] = list(
        existing_files.items() if isinstance(existing_files, Mapping) else (existing_files or [])
    )
    for name, (content_type, as_json) in encodings.items():
        if name not in merged:
            continue
        value = merged.pop(name)
        if as_json:
            data = openapi_dumps(value)
        else:
            if not isinstance(value, str):
                raise TypeError(f"Multipart field {name!r} must be a string")
            data = value.encode("utf-8")
        files.append((name, (None, data, content_type)))
    return merged or None, files, None, "multipart/form-data"
