from __future__ import annotations

from typing import Any, Literal, get_args, get_origin, get_type_hints

from openai._compat import PYDANTIC_V1
from openai.types.responses.response import Response
from openai.resources.responses.responses import Responses, AsyncResponses
from openai.types.chat.completion_create_params import CompletionCreateParamsBase
from openai.resources.chat.completions.completions import Completions, AsyncCompletions
from openai.types.responses.response_create_params import ResponseCreateParamsBase
from openai.types.responses.responses_client_event import ResponsesClientEvent
from openai.types.responses.responses_client_event_param import ResponsesClientEventParam


def _literal_values(annotation: Any) -> tuple[str, ...]:
    for arg in get_args(annotation):
        if get_origin(arg) is Literal:
            return get_args(arg)

    raise AssertionError(f"Expected an optional Literal annotation, got {annotation!r}")


def _response_model_annotation(model: Any) -> Any:
    if PYDANTIC_V1:
        return model.__fields__["prompt_cache_retention"].outer_type_

    return model.model_fields["prompt_cache_retention"].annotation


def test_prompt_cache_retention_literals_use_underscore() -> None:
    annotations = {
        "CompletionCreateParamsBase": get_type_hints(CompletionCreateParamsBase, include_extras=True)[
            "prompt_cache_retention"
        ],
        "ResponseCreateParamsBase": get_type_hints(ResponseCreateParamsBase, include_extras=True)[
            "prompt_cache_retention"
        ],
        "Response": _response_model_annotation(Response),
        "ResponsesClientEvent": _response_model_annotation(ResponsesClientEvent),
        "ResponsesClientEventParam": get_type_hints(ResponsesClientEventParam, include_extras=True)[
            "prompt_cache_retention"
        ],
    }

    for name, annotation in annotations.items():
        assert _literal_values(annotation) == ("in_memory", "24h"), name


def test_prompt_cache_retention_resource_annotations_use_underscore() -> None:
    annotations = {
        "Completions.create": get_type_hints(Completions.create, include_extras=True)["prompt_cache_retention"],
        "AsyncCompletions.create": get_type_hints(AsyncCompletions.create, include_extras=True)["prompt_cache_retention"],
        "Responses.create": get_type_hints(Responses.create, include_extras=True)["prompt_cache_retention"],
        "AsyncResponses.create": get_type_hints(AsyncResponses.create, include_extras=True)["prompt_cache_retention"],
    }

    for name, annotation in annotations.items():
        assert _literal_values(annotation) == ("in_memory", "24h"), name
