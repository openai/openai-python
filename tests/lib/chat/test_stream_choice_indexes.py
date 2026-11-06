from __future__ import annotations

from openai.types.chat import ChatCompletionChunk
from openai.lib.streaming.chat import ChatCompletionStreamState
from openai.types.chat.chat_completion_chunk import Choice, ChoiceDelta


def _chunk(*, index: int, content: str, role: str | None = None) -> ChatCompletionChunk:
    return ChatCompletionChunk.construct(
        id="chatcmpl-test",
        object="chat.completion.chunk",
        created=0,
        model="gpt-test",
        choices=[
            Choice.construct(
                index=index,
                finish_reason=None,
                logprobs=None,
                delta=ChoiceDelta.construct(content=content, role=role),
            )
        ],
    )


def test_stream_choices_can_arrive_out_of_index_order() -> None:
    state = ChatCompletionStreamState()

    list(state.handle_chunk(_chunk(index=1, content="one", role="assistant")))
    list(state.handle_chunk(_chunk(index=0, content="zero", role="assistant")))
    events = list(state.handle_chunk(_chunk(index=1, content=" continued")))

    snapshot = state.current_completion_snapshot
    assert [(choice.index, choice.message.content) for choice in snapshot.choices] == [
        (0, "zero"),
        (1, "one continued"),
    ]

    content_delta = next(event for event in events if event.type == "content.delta")
    assert content_delta.snapshot == "one continued"
