from __future__ import annotations

from typing import Callable

from ...._utils import is_mapping
from ....types.beta.beta_response_stream_event import BetaResponseStreamEvent
from ....types.responses.response_stream_event import ResponseStreamEvent


def maybe_response_stream_event_normalizer(cast_to: object) -> Callable[[object], object] | None:
    if cast_to != ResponseStreamEvent and cast_to != BetaResponseStreamEvent:
        return None

    return ResponseStreamEventNormalizer().normalize


class ResponseStreamEventNormalizer:
    def __init__(self) -> None:
        self._function_call_names_by_item_id: dict[str, str] = {}

    def normalize(self, data: object) -> object:
        if not is_mapping(data):
            return data

        event_type = data.get("type")
        if event_type == "response.output_item.added":
            self._remember_function_call_name(data)
        elif event_type == "response.function_call_arguments.done" and "name" not in data:
            return self._with_function_call_name(data)

        return data

    def _remember_function_call_name(self, data: object) -> None:
        if not is_mapping(data):
            return

        item = data.get("item")
        if not is_mapping(item) or item.get("type") != "function_call":
            return

        item_id = item.get("id")
        name = item.get("name")
        if isinstance(item_id, str) and isinstance(name, str):
            self._function_call_names_by_item_id[item_id] = name

    def _with_function_call_name(self, data: object) -> object:
        if not is_mapping(data):
            return data

        item_id = data.get("item_id")
        if not isinstance(item_id, str):
            return data

        name = self._function_call_names_by_item_id.get(item_id)
        if name is None:
            return data

        return {**data, "name": name}
