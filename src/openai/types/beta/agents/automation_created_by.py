# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ...._utils import PropertyInfo
from ...._models import BaseModel

__all__ = ["AutomationCreatedBy", "AutomationCreatedByResourceDeveloper", "AutomationCreatedByResourceAgent"]


class AutomationCreatedByResourceDeveloper(BaseModel):
    type: Literal["developer"]
    """The type of the object. Always `developer`."""


class AutomationCreatedByResourceAgent(BaseModel):
    session_id: str
    """The creator session, which is also the automation's target."""

    tool_call_id: str
    """The tool call that created the automation."""

    type: Literal["agent"]
    """The type of the object. Always `agent`."""


AutomationCreatedBy: TypeAlias = Annotated[
    Union[AutomationCreatedByResourceDeveloper, AutomationCreatedByResourceAgent], PropertyInfo(discriminator="type")
]
