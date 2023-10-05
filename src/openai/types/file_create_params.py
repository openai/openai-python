# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .._types import FileTypes

__all__ = ["FileCreateParams"]


class FileCreateParams(TypedDict, total=False):
    file: Required[FileTypes]
    """The file object (not file name) to be uploaded.

    If the `purpose` is set to "fine-tune", the file will be used for fine-tuning.
    """

    purpose: Required[str]
    """The intended purpose of the uploaded file.

    Use "fine-tune" for
    [fine-tuning](https://platform.openai.com/docs/api-reference/fine-tuning). This
    allows us to validate the format of the uploaded file is correct for
    fine-tuning.
    """
