# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = [
    "ComputerAction",
    "Click",
    "DoubleClick",
    "Drag",
    "DragPath",
    "Keypress",
    "Move",
    "Screenshot",
    "Scroll",
    "Type",
    "Wait",
]


class Click(BaseModel):
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


class DoubleClick(BaseModel):
    """A double click action."""

    type: Literal["double_click"]
    """Specifies the event type.

    For a double click action, this property is always set to `double_click`.
    """

    x: int
    """The x-coordinate where the double click occurred."""

    y: int
    """The y-coordinate where the double click occurred."""


class DragPath(BaseModel):
    """An x/y coordinate pair, e.g. `{ x: 100, y: 200 }`."""

    x: int
    """The x-coordinate."""

    y: int
    """The y-coordinate."""


class Drag(BaseModel):
    """A drag action."""

    path: List[DragPath]
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


class Keypress(BaseModel):
    """A collection of keypresses the model would like to perform."""

    keys: List[str]
    """The combination of keys the model is requesting to be pressed.

    This is an array of strings, each representing a key.
    """

    type: Literal["keypress"]
    """Specifies the event type.

    For a keypress action, this property is always set to `keypress`.
    """


class Move(BaseModel):
    """A mouse move action."""

    type: Literal["move"]
    """Specifies the event type.

    For a move action, this property is always set to `move`.
    """

    x: int
    """The x-coordinate to move to."""

    y: int
    """The y-coordinate to move to."""


class Screenshot(BaseModel):
    """A screenshot action."""

    type: Literal["screenshot"]
    """Specifies the event type.

    For a screenshot action, this property is always set to `screenshot`.
    """


class Scroll(BaseModel):
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


class Type(BaseModel):
    """An action to type in text."""

    text: str
    """The text to type."""

    type: Literal["type"]
    """Specifies the event type.

    For a type action, this property is always set to `type`.
    """


class Wait(BaseModel):
    """A wait action."""

    type: Literal["wait"]
    """Specifies the event type.

    For a wait action, this property is always set to `wait`.
    """


ComputerAction: TypeAlias = Annotated[
    Union[Click, DoubleClick, Drag, Keypress, Move, Screenshot, Scroll, Type, Wait], PropertyInfo(discriminator="type")
]
