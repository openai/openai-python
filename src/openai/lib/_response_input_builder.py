from __future__ import annotations

from typing import List, Union, Sequence

from ..types.responses.response import Response
from ..types.responses.response_input_item_param import ResponseInputItemParam


def get_response_input_items(response: Response) -> List[ResponseInputItemParam]:
    """Extract output items from a Response to use as input for the next turn.

    Iterates ``response.output`` in order and returns all items converted to
    ``ResponseInputItemParam`` dicts, preserving the required reasoning+message
    consecutive pairing.

    The Responses API requires that any ``reasoning`` item and the immediately
    following ``message`` (assistant) item are always passed together as a
    consecutive pair when building the ``input`` for the next turn.  Filtering
    out reasoning items (or re-ordering them) causes a 400 error from the API.

    SDK-only fields (e.g. ``parsed`` from ``ParsedResponseOutputText``) are
    excluded so the returned dicts conform to ``ResponseInputItemParam``.

    Example usage::

        from openai.lib import get_response_input_items

        conversation: list = []
        for user_msg in turns:
            conversation.append({"role": "user", "content": user_msg})
            response = client.responses.create(
                model="o3",
                input=conversation,
                reasoning={"effort": "high"},
            )
            # Preserves reasoning+message pairs automatically:
            conversation.extend(get_response_input_items(response))
    """
    items: List[ResponseInputItemParam] = []
    for output_item in response.output:
        data = output_item.model_dump(
            exclude_unset=True,
            exclude=getattr(output_item, "__api_exclude__", None),
        )
        # Strip SDK-only fields from nested content items
        # (e.g. ParsedResponseOutputText.parsed is not part of the API schema)
        for content_item in data.get("content", []):
            if isinstance(content_item, dict):
                content_item.pop("parsed", None)
        items.append(data)  # type: ignore[arg-type]
    return items


def validate_response_input(items: Sequence[Union[ResponseInputItemParam, object]]) -> None:
    """Validate that reasoning+message pairs are intact in an input list.

    Walks ``items`` and raises ``ValueError`` when it detects a ``reasoning``-type
    item that is NOT immediately followed by a ``message``-type item with
    role=assistant — the classic broken-pair pattern that causes a 400 from the
    API.

    Standalone assistant messages (those not part of a reasoning pair) are allowed
    and will not trigger a validation error.

    This validator is a standalone opt-in helper.  The primary recommendation is
    to build the input list with :func:`get_response_input_items` instead of
    filtering ``response.output`` manually.

    Raises:
        ValueError: with a descriptive message that includes the offending item id
            and explains the constraint.

    Example usage::

        from openai.lib import validate_response_input

        validate_response_input(conversation)  # raises ValueError if broken pair
        response = client.responses.create(model="o3", input=conversation)
    """
    for i, item in enumerate(items):
        if _item_type(item) != "reasoning":
            continue
        # Each reasoning item must be immediately followed by an assistant message.
        next_idx = i + 1
        if next_idx < len(items):
            next_item = items[next_idx]
            if _item_type(next_item) == "message" and _item_role(next_item) == "assistant":
                continue
        item_id = _item_id(item)
        id_hint = f" (id={item_id!r})" if item_id else ""
        raise ValueError(
            f"Orphaned reasoning item{id_hint} detected: a 'reasoning' item "
            f"must be immediately followed by its paired 'message' item with "
            f"role='assistant'. The OpenAI Responses API requires that reasoning "
            f"and the immediately following assistant message are always passed "
            f"together as a consecutive pair. Either include the paired assistant "
            f"message directly after this reasoning item, or remove the reasoning "
            f"item. Use get_response_input_items() to build input lists that "
            f"preserve pairs automatically."
        )


def _item_type(item: object) -> str:
    if isinstance(item, dict):
        return str(item.get("type", ""))
    return str(getattr(item, "type", ""))


def _item_role(item: object) -> str:
    if isinstance(item, dict):
        return str(item.get("role", ""))
    return str(getattr(item, "role", ""))


def _item_id(item: object) -> str:
    if isinstance(item, dict):
        return str(item.get("id", ""))
    return str(getattr(item, "id", ""))
