# File generated for OpenEval dataset import/export support.

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict

__all__ = ["OpenEvalItem", "from_openeval", "to_openeval"]


class OpenEvalMessage(TypedDict, total=False):
    role: str
    content: str


class OpenEvalItem(TypedDict, total=False):
    id: Optional[str]
    input: List[OpenEvalMessage]
    expected_output: Optional[str]
    metadata: Optional[Dict[str, Any]]


def from_openeval(item: OpenEvalItem) -> Dict[str, Any]:
    """
    Convert an OpenEval dataset item into OpenAI Chat Completion messages format.
    """
    messages: List[Dict[str, Any]] = []
    for msg in item.get("input", []):
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", ""),
        })

    result: Dict[str, Any] = {"messages": messages}
    if item.get("id"):
        result["id"] = item["id"]
    if item.get("expected_output"):
        result["expected_output"] = item["expected_output"]
    if item.get("metadata"):
        result["metadata"] = item["metadata"]
    return result


def to_openeval(
    messages: List[Dict[str, Any]],
    id: Optional[str] = None,
    expected_output: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> OpenEvalItem:
    """
    Export OpenAI Chat Completion messages and metadata into OpenEval dataset item format.
    """
    input_messages: List[OpenEvalMessage] = [
        {"role": str(msg.get("role", "user")), "content": str(msg.get("content", ""))}
        for msg in messages
    ]
    item: OpenEvalItem = {"input": input_messages}
    if id is not None:
        item["id"] = id
    if expected_output is not None:
        item["expected_output"] = expected_output
    if metadata is not None:
        item["metadata"] = metadata
    return item
