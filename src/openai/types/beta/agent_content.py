# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .output_text import OutputText

__all__ = ["AgentContent", "EncryptedContentResource"]


class EncryptedContentResource(BaseModel):
    """Encrypted content exchanged between agents."""

    encrypted_content: str
    """The encrypted content payload."""

    type: Literal["encrypted_content"]
    """The content type. Always `encrypted_content`."""


AgentContent: TypeAlias = Annotated[Union[OutputText, EncryptedContentResource], PropertyInfo(discriminator="type")]
