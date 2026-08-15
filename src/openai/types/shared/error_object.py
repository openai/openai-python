# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional, Union

from ..._models import BaseModel

__all__ = ["ErrorObject"]


class ErrorObject(BaseModel):
    code: Optional[Union[str, int]] = None

    message: str

    param: Optional[str] = None

    type: str
