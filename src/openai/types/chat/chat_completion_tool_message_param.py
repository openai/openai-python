# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional, Union, Iterable
from typing_extensions import Literal, Required, TypedDict

from .chat_completion_content_part_text_param import ChatCompletionContentPartTextParam

__all__ = ["ChatCompletionToolMessageParam"]


class ChatCompletionToolMessageParam(TypedDict, total=False):
    content: Required[Union[str, Iterable[ChatCompletionContentPartTextParam]]]
    """The contents of the tool message."""

    role: Required[Literal["tool"]]
    """The role of the messages author, in this case `tool`."""

    tool_call_id: Required[str]
    """Tool call that this message is responding to."""

    name: Optional[str]
    """The name of the tool that was called.

    This field is optional and mirrors the `name` field present on other message
    types (e.g. ``ChatCompletionFunctionMessageParam``). Including the tool name
    can improve clarity when multiple tools are used in a single conversation turn,
    and is consistent with OpenAI's own documentation examples for parallel
    function calling.
    """
