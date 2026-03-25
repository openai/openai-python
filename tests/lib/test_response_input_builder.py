from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from openai.lib import validate_response_input, get_response_input_items


def _make_reasoning_item(item_id: str = "rs_001") -> Any:
    item = MagicMock()
    item.type = "reasoning"
    item.id = item_id
    item.model_dump.return_value = {"type": "reasoning", "id": item_id, "summary": []}
    return item


def _make_message_item(item_id: str = "msg_001") -> Any:
    item = MagicMock()
    item.type = "message"
    item.role = "assistant"
    item.id = item_id
    item.model_dump.return_value = {"type": "message", "role": "assistant", "id": item_id, "content": []}
    return item


def _make_response(output: list[Any]) -> Any:
    response = MagicMock()
    response.output = output
    return response


# ---------------------------------------------------------------------------
# get_response_input_items
# ---------------------------------------------------------------------------


def test_get_response_input_items_reasoning_and_message() -> None:
    """Returns both reasoning and message items in order."""
    reasoning = _make_reasoning_item("rs_1")
    message = _make_message_item("msg_1")
    response = _make_response([reasoning, message])

    result = get_response_input_items(response)

    assert len(result) == 2
    assert result[0] == {"type": "reasoning", "id": "rs_1", "summary": []}
    assert result[1] == {"type": "message", "role": "assistant", "id": "msg_1", "content": []}


def test_get_response_input_items_message_only() -> None:
    """Returns message items when there are no reasoning items."""
    message = _make_message_item("msg_2")
    response = _make_response([message])

    result = get_response_input_items(response)

    assert len(result) == 1
    assert result[0] == {"type": "message", "role": "assistant", "id": "msg_2", "content": []}


def test_get_response_input_items_empty() -> None:
    """Returns empty list for empty output."""
    response = _make_response([])
    result = get_response_input_items(response)
    assert result == []


# ---------------------------------------------------------------------------
# validate_response_input
# ---------------------------------------------------------------------------


def test_validate_passes_for_consecutive_pair_dicts() -> None:
    """No error when reasoning immediately precedes assistant message (dict form)."""
    items = [
        {"type": "reasoning", "id": "rs_1", "summary": []},
        {"type": "message", "role": "assistant", "id": "msg_1", "content": []},
    ]
    validate_response_input(items)  # should not raise


def test_validate_raises_for_orphaned_message_dicts() -> None:
    """ValueError raised when assistant message is not preceded by reasoning (dict form)."""
    items = [
        {"type": "message", "role": "user", "content": "hello"},
        {"type": "reasoning", "id": "rs_1", "summary": []},
        {"type": "message", "role": "user", "content": "follow-up"},
        {"type": "message", "role": "assistant", "id": "msg_orphan", "content": []},
    ]
    with pytest.raises(ValueError, match="msg_orphan"):
        validate_response_input(items)


def test_validate_raises_error_describes_constraint() -> None:
    """Error message explains the reasoning+message pairing constraint."""
    items = [
        {"type": "reasoning", "id": "rs_1", "summary": []},
        {"type": "message", "role": "user", "content": "hi"},
        {"type": "message", "role": "assistant", "id": "msg_bad", "content": []},
    ]
    with pytest.raises(ValueError, match="consecutive pair"):
        validate_response_input(items)


def test_validate_passes_for_user_only_messages() -> None:
    """No error when there are only user messages and no reasoning items."""
    items = [
        {"type": "message", "role": "user", "content": "hello"},
        {"type": "message", "role": "user", "content": "how are you"},
    ]
    validate_response_input(items)  # should not raise


def test_validate_passes_for_empty_input() -> None:
    """No error for empty input list."""
    validate_response_input([])  # should not raise


def test_validate_passes_with_object_form() -> None:
    """Works with object-form items (not dicts), consecutive pair."""
    reasoning = MagicMock()
    reasoning.type = "reasoning"
    reasoning.id = "rs_obj"

    message = MagicMock()
    message.type = "message"
    message.role = "assistant"
    message.id = "msg_obj"

    validate_response_input([reasoning, message])  # should not raise


def test_validate_raises_with_object_form_orphaned() -> None:
    """Raises ValueError with object-form items when message is orphaned."""
    reasoning = MagicMock()
    reasoning.type = "reasoning"
    reasoning.id = "rs_obj"

    user_msg = MagicMock()
    user_msg.type = "message"
    user_msg.role = "user"

    asst_msg = MagicMock()
    asst_msg.type = "message"
    asst_msg.role = "assistant"
    asst_msg.id = "msg_orphan_obj"

    with pytest.raises(ValueError, match="msg_orphan_obj"):
        validate_response_input([reasoning, user_msg, asst_msg])
