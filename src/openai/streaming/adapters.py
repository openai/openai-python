from typing import Any
from .unified import StreamEvent


class ResponsesEventAdapter:
    @staticmethod
    def adapt(evt: Any) -> StreamEvent:
        t = getattr(evt, "type", None)
        if t == "response.output_text.delta":
            return StreamEvent(
                type="output_text.delta",
                delta=getattr(evt, "delta", None),
                raw=evt,
            )
        if t == "response.completed":
            return StreamEvent(type="response.completed", raw=evt)
        # TODO: map additional event types (tool_call.*, errors, etc.)
        return StreamEvent(type="response.error", raw=evt)


class ChatCompletionsEventAdapter:
    @staticmethod
    def adapt(chunk: Any) -> StreamEvent:
        # Try to extract delta.content from the first choice
        try:
            choice0 = chunk.choices[0]
            delta = getattr(getattr(choice0, "delta", None), "content", None)
            if delta:
                return StreamEvent(
                    type="output_text.delta",
                    delta=delta,
                    raw=chunk,
                )
        except Exception:
            pass
        # TODO: add heuristics for completed and error events
        return StreamEvent(type="response.completed", raw=chunk)
