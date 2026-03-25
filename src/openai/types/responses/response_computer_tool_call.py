# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .computer_action_list import ComputerActionList

__all__ = [
    "ResponseComputerToolCall",
    "PendingSafetyCheck",
    "Action",
    "ActionClick",
    "ActionDoubleClick",
    "ActionDrag",
    "ActionDragPath",
    "ActionKeypress",
    "ActionMove",
    "ActionScreenshot",
    "ActionScroll",
    "ActionType",
    "ActionWait",
]


class PendingSafetyCheck(BaseModel):
    """A pending safety check for the computer call."""

    id: str
    """The ID of the pending safety check."""

    code: Optional[str] = None
    """The type of the pending safety check."""

    message: Optional[str] = None
    """Details about the pending safety check."""


class ActionClick(BaseModel):
    """A click action."""

    button: Literal["left", "right", "wheel", "back", "forward"]
    """Indicates which mouse button was pressed during the click.

    One of `left`, `right`, `wheel`, `back`, or `forward`.
    """

    type: Literal["click"]
    """Specifies the event type. For a click action, this property is always `click`."""

    x: int
    """The x-coordinate where the click occurred."""

    y: int
    """The y-coordinate where the click occurred."""

    keys: Optional[List[str]] = None
    """The keys being held while clicking."""


class ActionDoubleClick(BaseModel):
    """A double click action."""

    keys: Optional[List[str]] = None
    """The keys being held while double-clicking."""

    type: Literal["double_click"]
    """Specifies the event type.

    For a double click action, this property is always set to `double_click`.
    """

    x: int
    """The x-coordinate where the double click occurred."""

    y: int
    """The y-coordinate where the double click occurred."""


class ActionDragPath(BaseModel):
    """An x/y coordinate pair, e.g. `{ x: 100, y: 200 }`."""

    x: int
    """The x-coordinate."""

    y: int
    """The y-coordinate."""


class ActionDrag(BaseModel):
    """A drag action."""

    path: List[ActionDragPath]
    """An array of coordinates representing the path of the drag action.

    Coordinates will appear as an array of objects, eg

    ```
    [
      { x: 100, y: 200 },
      { x: 200, y: 300 }
    ]
    ```
    """

    type: Literal["drag"]
    """Specifies the event type.

    For a drag action, this property is always set to `drag`.
    """

    keys: Optional[List[str]] = None
    """The keys being held while dragging the mouse."""


class ActionKeypress(BaseModel):
    """A collection of keypresses the model would like to perform."""

    keys: List[str]
    """The combination of keys the model is requesting to be pressed.

    This is an array of strings, each representing a key.
    """

    type: Literal["keypress"]
    """Specifies the event type.

    For a keypress action, this property is always set to `keypress`.
    """


class ActionMove(BaseModel):
    """A mouse move action."""

    type: Literal["move"]
    """Specifies the event type.

    For a move action, this property is always set to `move`.
    """

    x: int
    """The x-coordinate to move to."""

    y: int
    """The y-coordinate to move to."""

    keys: Optional[List[str]] = None
    """The keys being held while moving the mouse."""


class ActionScreenshot(BaseModel):
    """A screenshot action."""

    type: Literal["screenshot"]
    """Specifies the event type.

    For a screenshot action, this property is always set to `screenshot`.
    """


class ActionScroll(BaseModel):
    """A scroll action."""

    scroll_x: int
    """The horizontal scroll distance."""

    scroll_y: int
    """The vertical scroll distance."""

    type: Literal["scroll"]
    """Specifies the event type.

    For a scroll action, this property is always set to `scroll`.
    """

    x: int
    """The x-coordinate where the scroll occurred."""

    y: int
    """The y-coordinate where the scroll occurred."""

    keys: Optional[List[str]] = None
    """The keys being held while scrolling."""


class ActionType(BaseModel):
    """An action to type in text."""

    text: str
    """The text to type."""

    type: Literal["type"]
    """Specifies the event type.

    For a type action, this property is always set to `type`.
    """


class ActionWait(BaseModel):
    """A wait action."""

    type: Literal["wait"]
    """Specifies the event type.

    For a wait action, this property is always set to `wait`.
    """


Action: TypeAlias = Annotated[
    Union[
        ActionClick,
        ActionDoubleClick,
        ActionDrag,
        ActionKeypress,
        ActionMove,
        ActionScreenshot,
        ActionScroll,
        ActionType,
        ActionWait,
    ],
    PropertyInfo(discriminator="type"),
]


class ResponseComputerToolCall(BaseModel):
    """A tool call to a computer use tool.

    See the
    [computer use guide](https://platform.openai.com/docs/guides/tools-computer-use) for more information.
    """

    id: str
    """The unique ID of the computer call."""

    call_id: str
    """An identifier used when responding to the tool call with output."""

    pending_safety_checks: List[PendingSafetyCheck]
    """The pending safety checks for the computer call."""

    status: Literal["in_progress", "completed", "incomplete"]
    """The status of the item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """

    type: Literal["computer_call"]
    """The type of the computer call. Always `computer_call`."""

    action: Optional[Action] = None
    """A click action."""

    actions: Optional[ComputerActionList] = None
    """Flattened batched actions for `computer_use`.

    Each action includes an `type` discriminator and action-specific fields.
    """
