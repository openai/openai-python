# File generated for OpenEval dataset import/export support.

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Union, Optional, cast
from typing_extensions import Required, TypedDict

__all__ = ["OpenEvalItem", "OpenEvalGrader", "from_openeval", "to_openeval"]


class OpenEvalMessage(TypedDict, total=False):
    role: str
    content: str


class OpenEvalGrader(TypedDict, total=False):
    """Inline grader object -- see spec/schemas/grader.json. Most callers
    will instead pass a bare grader-id string in OpenEvalItem['graders']."""

    id: Required[str]
    type: Required[str]
    name: str
    description: str
    weight: float
    params: Dict[str, Any]


class OpenEvalItem(TypedDict, total=False):
    # id and graders are REQUIRED by spec/schemas/testcase.json
    # ("required": ["id", "input", "graders"]) -- not optional.
    id: Required[str]
    input: Required[Union[str, List[str]]]
    graders: Required[List[Union[str, OpenEvalGrader]]]
    expected_output: Optional[str]
    metadata: Optional[Dict[str, Any]]


def from_openeval(item: OpenEvalItem) -> Dict[str, Any]:
    """
    Convert a spec-valid OpenEval TestCase into OpenAI Chat Completion
    messages format.

    ``item["input"]`` is a string or an array of strings per the EvalPort
    TestCase schema, not an array of {role, content} objects -- that chat
    shape is OpenAI's own native format, produced by to_openeval() below,
    not something to_openeval()'s *caller* is expected to hand you.

    If this item carries the original chat messages this adapter itself
    exported (see to_openeval()), they're restored losslessly from
    ``metadata["openeval"]["openai_messages"]``. Otherwise -- e.g. a hand-authored
    TestCase, or one from a different tool -- every input string is
    reconstructed as a single "user" message, the same fallback every other
    adapter in the EvalPort ecosystem uses for a grader/tool type it doesn't
    recognize.
    """
    metadata: Dict[str, Any] = {}
    raw_metadata = item.get("metadata")
    if isinstance(raw_metadata, dict):
        metadata = {str(k): v for k, v in cast(Dict[Any, Any], raw_metadata).items()}

    raw_saved_messages: Any = None
    raw_openeval_meta = metadata.get("openeval")
    if isinstance(raw_openeval_meta, dict) and "openai_messages" in raw_openeval_meta:
        raw_saved_messages = raw_openeval_meta.get("openai_messages")
    else:
        raw_openai_meta = metadata.get("openai")
        if isinstance(raw_openai_meta, dict) and "messages" in raw_openai_meta:
            raw_saved_messages = raw_openai_meta.get("messages")
        elif "_openai_messages" in metadata:
            raw_saved_messages = metadata.get("_openai_messages")

    if isinstance(raw_saved_messages, list):
        messages: List[Dict[str, Any]] = []
        for m in cast(List[Any], raw_saved_messages):
            if isinstance(m, dict):
                messages.append({str(k): v for k, v in cast(Dict[Any, Any], m).items()})
            else:
                messages.append({"role": "user", "content": str(m)})
    else:
        raw_input = item.get("input", "")
        input_strings = [raw_input] if isinstance(raw_input, str) else list(raw_input)
        messages = [{"role": "user", "content": s} for s in input_strings]

    result: Dict[str, Any] = {"messages": messages}
    for k, v in item.items():
        if k not in ("input", "graders", "metadata", "id", "expected_output"):
            result[k] = v
    if "id" in item and item["id"]:
        result["id"] = item["id"]
    expected_output = item.get("expected_output")
    if expected_output is not None:
        result["expected_output"] = expected_output
    if metadata:
        result["metadata"] = metadata
    return result


def to_openeval(
    messages: List[Dict[str, Any]],
    graders: List[Union[str, OpenEvalGrader]],
    id: Optional[str] = None,
    expected_output: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> OpenEvalItem:
    """
    Export OpenAI Chat Completion messages into a spec-valid OpenEval
    TestCase (spec/schemas/testcase.json).

    Args:
        messages: OpenAI chat messages ({role, content} dicts). Must be non-empty.
        graders: REQUIRED -- TestCase.graders must have >=1 entry per spec.
            Pass grader-id strings (referencing graders already defined on
            the enclosing Suite) or inline grader objects. Must be non-empty.
        id: TestCase.id is required by spec; if omitted, a uuid4 is
            generated so the output always validates.
        expected_output: Target reference output for the test case (if any).
        metadata: Optional metadata dictionary.

    ``input`` is built as one string per message ("{role}: {content}"),
    satisfying the schema's string-or-array-of-strings requirement. The
    *original* messages are additionally preserved verbatim under
    metadata["openeval"]["openai_messages"] so from_openeval() can reconstruct the
    exact role/content structure on import instead of collapsing everything
    to "user" turns -- "openeval.*" being the spec-reserved namespace in the
    EvalPort ecosystem.
    """
    if not messages:
        raise ValueError("messages must contain at least one message")
    if not graders:
        raise ValueError("graders must contain at least one grader")

    input_strings: List[str] = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if isinstance(content, str):
            input_strings.append(f"{role}: {content}")
        else:
            input_strings.append(f"{role}: {content!s}")

    merged_metadata: Dict[str, Any] = {}
    if metadata is not None:
        merged_metadata = {str(k): v for k, v in metadata.items()}

    formatted_messages = [{str(k): v for k, v in m.items()} for m in messages]
    raw_openeval_meta = merged_metadata.get("openeval")
    openeval_dict = dict(raw_openeval_meta) if isinstance(raw_openeval_meta, dict) else {}
    openeval_dict["openai_messages"] = formatted_messages
    merged_metadata["openeval"] = openeval_dict

    item: OpenEvalItem = {
        "id": id or str(uuid.uuid4()),
        "input": input_strings if len(input_strings) != 1 else input_strings[0],
        "graders": graders,
        "metadata": merged_metadata,
    }
    if expected_output is not None:
        item["expected_output"] = expected_output
    return item
