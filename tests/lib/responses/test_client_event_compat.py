from types import ModuleType

import pytest

from openai.types.responses import responses_client_event as event, responses_client_event_param as param


@pytest.mark.parametrize("module", [event, param])
@pytest.mark.parametrize(
    "name",
    [
        "ContextManagement",
        "Conversation",
        "Moderation",
        "ModerationPolicy",
        "ModerationPolicyInput",
        "ModerationPolicyOutput",
        "PromptCacheOptions",
        "StreamOptions",
        "ToolChoice",
        "ToolChoiceSpecificProgrammaticToolCallingParam",
    ],
)
def test_legacy_helper_exports(module: ModuleType, name: str) -> None:
    assert name in module.__all__
    assert getattr(module, name) is getattr(module, f"ResponseCreate{name}")


def test_legacy_model_helpers() -> None:
    context: event.ContextManagement = event.ContextManagement(type="compaction", compact_threshold=1000)
    conversation: event.Conversation = "conv_test"
    tool_choice: event.ToolChoice = event.ToolChoiceSpecificProgrammaticToolCallingParam(
        type="programmatic_tool_calling"
    )
    response = event.ResponseCreate(
        type="response.create",
        context_management=[context],
        conversation=conversation,
        moderation=event.Moderation(
            model="omni-moderation-latest",
            policy=event.ModerationPolicy(
                input=event.ModerationPolicyInput(mode="score"),
                output=event.ModerationPolicyOutput(mode="block"),
            ),
        ),
        prompt_cache_options=event.PromptCacheOptions(mode="explicit"),
        stream_options=event.StreamOptions(include_obfuscation=False),
        tool_choice=tool_choice,
    )
    assert response.context_management == [context]
    assert response.to_dict(exclude_unset=True)["moderation"] == {
        "model": "omni-moderation-latest",
        "policy": {"input": {"mode": "score"}, "output": {"mode": "block"}},
    }


def test_legacy_param_helpers() -> None:
    context: param.ContextManagement = {"type": "compaction", "compact_threshold": 1000}
    conversation: param.Conversation = "conv_test"
    tool_choice: param.ToolChoice = param.ToolChoiceSpecificProgrammaticToolCallingParam(
        type="programmatic_tool_calling"
    )
    response: param.ResponseCreate = {
        "type": "response.create",
        "context_management": [context],
        "conversation": conversation,
        "moderation": param.Moderation(
            model="omni-moderation-latest",
            policy=param.ModerationPolicy(
                input=param.ModerationPolicyInput(mode="score"),
                output=param.ModerationPolicyOutput(mode="block"),
            ),
        ),
        "prompt_cache_options": param.PromptCacheOptions(mode="explicit"),
        "stream_options": param.StreamOptions(include_obfuscation=False),
        "tool_choice": tool_choice,
    }
    assert response["context_management"] == [context]
    assert response["moderation"] == {
        "model": "omni-moderation-latest",
        "policy": {"input": {"mode": "score"}, "output": {"mode": "block"}},
    }
