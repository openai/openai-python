from __future__ import annotations

from typing import Any, Dict, Union, Mapping, Callable, Iterable, Awaitable
from typing_extensions import TypeAlias

from ....types.beta.input_content_param import InputContentParam

ToolOutput: TypeAlias = Union[str, Mapping[str, Any], Iterable[InputContentParam], None]
ToolHandler: TypeAlias = Callable[[Dict[str, Any]], ToolOutput]
AsyncToolHandler: TypeAlias = Callable[[Dict[str, Any]], Union[ToolOutput, Awaitable[ToolOutput]]]
