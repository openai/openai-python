# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ...._utils import PropertyInfo
from ...._models import BaseModel
from ..input_content import InputContent
from .automation_environment import AutomationEnvironment
from .automation_agent_config import AutomationAgentConfig

__all__ = [
    "AutomationTarget",
    "AutomationTargetResourceNewSession",
    "AutomationTargetResourceNewSessionInput",
    "AutomationTargetResourceExistingSession",
]


class AutomationTargetResourceNewSessionInput(BaseModel):
    """A user message recorded in a session."""

    content: List[InputContent]
    """The content of the message."""

    role: Literal["user"]
    """The role of the message author. Always `user`."""

    type: Literal["message"]
    """The type of the input item. Always `message`."""


class AutomationTargetResourceNewSession(BaseModel):
    agent: Optional[AutomationAgentConfig] = None
    """The inline agent configuration, or null when agent_id is configured."""

    agent_id: Optional[str] = None
    """The saved agent reference, or null when an inline agent is configured."""

    environment: AutomationEnvironment
    """Configuration or references used to select the execution environment."""

    input: List[AutomationTargetResourceNewSessionInput]
    """Initial input delivered to each new session."""

    metadata: Dict[str, str]
    """Metadata attached to each new session."""

    type: Literal["new_session"]
    """The type of the object. Always `new_session`."""

    vault_ids: List[str]
    """Vaults made available to each new session."""


class AutomationTargetResourceExistingSession(BaseModel):
    instructions: str
    """Saved instructions delivered as an automation notification."""

    session_id: str
    """The session receiving each invocation."""

    type: Literal["existing_session"]
    """The type of the object. Always `existing_session`."""


AutomationTarget: TypeAlias = Annotated[
    Union[AutomationTargetResourceNewSession, AutomationTargetResourceExistingSession],
    PropertyInfo(discriminator="type"),
]
