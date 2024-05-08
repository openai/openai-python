# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .._types import FileTypes

__all__ = ["FileCreateParams"]


class FileCreateParams(TypedDict, total=False):
    file: Required[FileTypes]
    """The File object (not file name) to be uploaded."""

    purpose: Required[Literal["assistants", "batch", "fine-tune"]]
    """The intended purpose of the uploaded file.

    Use "assistants" for
    [Assistants](https://platform.openai.com/docs/api-reference/assistants) and
    [Messages](https://platform.openai.com/docs/api-reference/messages), "batch" for
    [Batch API](https://platform.openai.com/docs/guides/batch), and "fine-tune" for
    [Fine-tuning](https://platform.openai.com/docs/api-reference/fine-tuning).
    """
