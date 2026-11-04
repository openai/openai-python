# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["EnvironmentTemplateDeleted"]


class EnvironmentTemplateDeleted(BaseModel):
    """A deleted reusable environment template."""

    id: str
    """The ID of the deleted environment template."""

    deleted: bool
    """Whether the environment template was deleted. Always `true`."""

    object: Literal["agent.environment.template.deleted"]
    """The object type. Always `agent.environment.template.deleted`."""
