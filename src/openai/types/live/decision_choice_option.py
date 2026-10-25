# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union, Optional

from pydantic import StrictStr, StrictBool

from ..._models import BaseModel

__all__ = ["DecisionChoiceOption"]


class DecisionChoiceOption(BaseModel):
    value: Union[StrictStr, StrictBool]

    description: Optional[str] = None
