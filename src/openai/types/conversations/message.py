# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .text_content import TextContent
from .refusal_content import RefusalContent
from .input_file_content import InputFileContent
from .input_text_content import InputTextContent
from .input_image_content import InputImageContent
from .output_text_content import OutputTextContent
from .summary_text_content import SummaryTextContent
from .computer_screenshot_content import ComputerScreenshotContent

__all__ = ["Message", "Content"]

Content: TypeAlias = Annotated[
    Union[
        InputTextContent,
        OutputTextContent,
        TextContent,
        SummaryTextContent,
        RefusalContent,
        InputImageContent,
        ComputerScreenshotContent,
        InputFileContent,
    ],
    PropertyInfo(discriminator="type"),
]


class Message(BaseModel):
    id: str
    """The unique ID of the message."""

    content: List[Content]
    """The content of the message"""

    role: Literal["unknown", "user", "assistant", "system", "critic", "discriminator", "developer", "tool"]
    """The role of the message.

    One of `unknown`, `user`, `assistant`, `system`, `critic`, `discriminator`,
    `developer`, or `tool`.
    """

    status: Literal["in_progress", "completed", "incomplete"]
    """The status of item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """

    type: Literal["message"]
    """The type of the message. Always set to `message`."""
