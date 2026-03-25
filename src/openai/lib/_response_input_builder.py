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
        items.append(output_item.model_dump(exclude_unset=True))  # type: ignore[arg-type]
    return items


def validate_response_input(items: Sequence[Union[ResponseInputItemParam, object]]) -> None:
    """Validate that reasoning+message pairs are not orphaned in an input list.

    Walks ``items`` and raises ``ValueError`` when it detects a ``message``-type
    item (role=assistant) that is NOT immediately preceded by a ``reasoning``-type
    item, but where a ``reasoning`` item exists elsewhere in the list — the classic
    orphaning pattern that causes a 400 from the API.

    This validator is a standalone opt-in helper.  The primary recommendation is
    to build the input list with :func:`get_response_input_items` instead of
    filtering ``response.output`` manually.

    Raises:
        ValueError: with a descriptive message that includes the offending item id
            and explains the constraint.

    Example usage::

        from openai.lib import validate_response_input

        validate_response_input(conversation)  # raises ValueError if orphaned
        response = client.responses.create(model="o3", input=conversation)
    """
    has_reasoning = any(_item_type(item) == "reasoning" for item in items)
    if not has_reasoning:
        # No reasoning items at all — nothing to validate.
        return

    for i, item in enumerate(items):
        if _item_type(item) != "message":
            continue
        role = _item_role(item)
        if role != "assistant":
            continue
        # This is an assistant message.  It must be immediately preceded by a
        # reasoning item when reasoning items exist in the list.
        preceded_by_reasoning = i > 0 and _item_type(items[i - 1]) == "reasoning"
        if not preceded_by_reasoning:
            item_id = _item_id(item)
            id_hint = f" (id={item_id!r})" if item_id else ""
            raise ValueError(
                f"Orphaned assistant message{id_hint} detected: a 'message' item with "
                f"role='assistant' must be immediately preceded by its paired 'reasoning' "
                f"item when reasoning items are present in the input. "
                f"The OpenAI Responses API requires that reasoning and the immediately "
                f"following assistant message are always passed together as a consecutive "
                f"pair. Either include the paired reasoning item directly before this "
                f"message, use 'previous_response_id' to let the API manage context, or "
                f"build the input list with get_response_input_items() which preserves "
                f"pairs automatically."
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
