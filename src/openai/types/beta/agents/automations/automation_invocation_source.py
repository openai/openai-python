# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ....._utils import PropertyInfo
from ....._models import BaseModel
from ..automation import Automation

__all__ = [
    "AutomationInvocationSource",
    "AutomationInvocationSourceResourceManual",
    "AutomationInvocationSourceResourceAutomation",
]


class AutomationInvocationSourceResourceManual(BaseModel):
    type: Literal["manual"]
    """The type of the object. Always `manual`."""


class AutomationInvocationSourceResourceAutomation(BaseModel):
    automation: Automation
    """The automation snapshot for this occurrence, excluding confidential values."""

    type: Literal["automation"]
    """The type of the object. Always `automation`."""


AutomationInvocationSource: TypeAlias = Annotated[
    Union[AutomationInvocationSourceResourceManual, AutomationInvocationSourceResourceAutomation],
    PropertyInfo(discriminator="type"),
]
