# Responses WebSocket sessions

`ResponsesWebSocketSession` and `AsyncResponsesWebSocketSession` add routed
lanes and final-response collection to an existing `client.responses.connect()`
connection. The existing connection API and its defaults are unchanged. Install
the `openai[realtime]` extra to use WebSockets.

```python
from openai import AsyncOpenAI
from openai.lib.responses_websocket import (
    AsyncResponsesWebSocketSession,
    ResponsesWebSocketLimits,
)

# Choose budgets for your application's expected responses.
limits = ResponsesWebSocketLimits(
    max_lanes=8,  # Includes the default lane and closed reservations until reconnect.
    max_events_per_lane=128,
    max_events=512,
    max_bytes_per_lane=16 * 1024 * 1024,
    max_bytes=32 * 1024 * 1024,
    max_response_bytes=None,  # Default: no cumulative response accumulation cap.
)

async def run():
    async with AsyncOpenAI() as client:
        async with client.responses.connect(websocket_connection_options={"max_size": None}) as connection:
            async with AsyncResponsesWebSocketSession(connection, limits=limits) as session:
                lane = session.lane("conversation")
                await lane.send({
                    "type": "response.create",
                    "model": "gpt-4o-mini",
                    "input": "Say hello.",
                })
                response = await lane.get_final_response()
                return response
```

The session owns the connection's read side and lifetime. Its one reader uses the
connection's raw receive, event parsing, and recovery methods. While the session
is active, receive through its lanes instead of calling the connection's `recv`,
iterator, or `dispatch_events`.
Direct sends through the connection can bypass lane ownership; send through the
lane when using these helpers. Closing the session closes the connection.

Register each named lane before sending. For `response.create`, `lane.send` adds
its `stream_id` and rejects conflicting routing metadata. Steering commands keep
their original fields and route through `previous_response_id`. The lane ID is independent of
`previous_response_id`, which you can supply explicitly for continuation. Consume
one response's terminal event before sending the next create on that lane.
Different lanes can run concurrently; use one consumer per lane. The default
lane (`session.default`) receives events without a registered routing ID,
including unknown events and connection-level errors. Observe it when using
named lanes so these events and errors are not left unread.

`lane.recv()` preserves typed events and unknown fields. `get_final_response()`
consumes remaining events and returns the terminal `Response`, including `failed`
and `incomplete` results. Finalized output items fill an omitted terminal output
through the existing Responses accumulator. Text deltas remain available through
`recv`; final response collection does not require SSE-only item setup events.
No tool is executed automatically. A nested protocol error raises
`ResponsesWebSocketError`, whose `event` is the original event; the exception
message does not include request or response data.

A repeated `get_final_response()` returns the cached result unless the reader
has observed a newer `response.created` on that lane, in which case it consumes
the next response. It does not wait for a hypothetical future successor. Use
`recv()` to observe that boundary when coordinating steering; accepted steering
alone does not prove that a successor has started.

For incremental text and tool-input snapshots, opt in with a separate helper
fed by the events you already receive:

```python
from openai.lib.responses_websocket import ResponsesWebSocketAccumulator

accumulator = ResponsesWebSocketAccumulator()
expected_stream_id = "conversation"  # Same ID passed to session.lane(); None for session.default.
while True:
    event = await lane.recv()  # Use lane.recv(timeout=...) in a sync session.
    # Original event fields, including unknown variants/fields, remain available.
    # Inspect events in memory before filtering. Never log raw events: they can
    # contain customer data, tool arguments, credentials, or error details.
    if getattr(event, "stream_id", None) != expected_stream_id:
        continue
    accumulator.add_event(event)
    event_type = event.type
    if event.type == "response.output_text.delta":
        pass  # Update the application's UI with event.delta (provisional).
    elif event.type == "response.output_item.done":
        pass  # Replace the provisional item at event.output_index with event.item.
    elif isinstance(event_type, str) and event_type in {"response.completed", "response.failed", "response.incomplete"}:
        snapshot = accumulator.snapshot()  # One full projection of all items.
        response = accumulator.get_final_response()
        break
accumulator.reset()  # Does not close the lane or connection.
```

Use one helper per lane and reset it before the next turn. The default lane
also receives raw events for unregistered or detached lanes. Observe those
events before filtering, then feed only the response you are collecting.
The same check applies when consuming directly from a connection.

Snapshots are immutable and contain selected text, function arguments, and custom tool input,
grouped by output/content index and item ID. They never execute tools. Done
events replace provisional fields. Full item replacements discard old fields;
a changed nonempty item ID starts fresh at its index. A supplied response
output list overrides the projected items, including an explicit empty list;
omitted or null output retains only the helper's earlier projections.

`detailed_snapshot()` returns a separate mutable view when you need the fields
beyond selected text and tool inputs. It contains `stream_id`, `response_id`,
`terminal_type`, `response` and `output`. `response` is the last observed
lifecycle response metadata (excluding `output`), or `None` if none arrived.
`output` is a list of `{"output_index": index, "item": metadata, "content": rows}`.
Each content row is `{"content_index": index, "part": observed_fields}`. The
part's `annotations`, when present as a list, use
`{"annotation_index": index, "annotation": observed_fields}` rows. Indices may
be sparse; list position is not the API index.
For a message that has no projected content, the row's `content` is omitted,
null or empty according to what was actually received.

For example, after collecting an item or terminal as above:

```python
details = accumulator.detailed_snapshot()
for output in details["output"]:
    for content in output.get("content") or []:
        part = content["part"]
        # Fields exist only if received: a WS delta may have no part/item type.
        text = part.get("text")
        citations = part.get("annotations")
        token_scores = part.get("logprobs")
```

Logprobs accumulate with text deltas and a supplied `output_text.done.logprobs`
replaces them, including empty or null values. Content/item/lifecycle replacements
also replace their corresponding annotations and other metadata; text-only done
events do not erase citations. Refusal, tool/MCP and unknown item/part fields are
retained as observed, with unset and null distinct. Unknown standalone events still
pass through unchanged and are not accumulated. Annotation events enrich matching
known items on the accumulator's lane; annotations received before any matching
item/text remain available in the original event and do not start or replace a turn.
A partial field or unknown type
is provisional, not a fabricated validated response or a successful tool result.
You may mutate this returned view without changing the accumulator, events, or
earlier snapshots. The original `snapshot()` remains immutable and hashable.

`snapshot()` materializes the entire current projection and joins retained
fragments. `detailed_snapshot()` also materializes and copies its whole projection.
Both are proportional to the accumulated output, so requesting either after
every delta or completed item repeatedly rebuilds growing prefixes. Use the
original event for progress, including the final item itself on
`response.output_item.done`. Read the full snapshot at a terminal or on explicit
user demand. A per-delta progress display is provisional; done events can shorten or
correct earlier text. A UI can use the received item to replace the item at
`event.output_index`, and use the terminal snapshot for the whole projection.

The helper's `get_final_response()` returns a copy of the exact received server
response, including its original missing/null/empty output, on completed,
failed or incomplete. It never substitutes the projection for that response.
Before a valid terminal it raises; protocol errors retain their original event.
This caller-fed helper owns no socket, reader or timers and can also observe
events from a connection when there is no session.

Cancel an async `recv` or `get_final_response` wait with normal asyncio
cancellation. It leaves queued events and accumulated state available for a later
wait, and does not close the lane or connection. Synchronous waits accept
`timeout=` and likewise preserve data on timeout. `lane.close()` explicitly
detaches that lane and discards its queued events/state without closing the
socket. Future events for a detached named lane go to the default lane for raw
inspection; they do not change its accumulated response or in-flight state. Closing
the default lane opts out of those otherwise unclaimed events.
Every registered ID, including the default lane and unused or closed lanes,
remains reserved against `max_lanes` until the physical socket reconnects.
Terminal responses and errors do not release IDs: accepted steering can start a
successor after a terminal event. Keep the same lane handle open for sequential
responses. Reconnect releases closed reservations; open lanes stay registered on
the replacement socket. Close a lane before reconnecting if you need to recreate
it. After reconnect releases a closed default lane, `session.lane()` (or
`session.lane(None)`) registers a fresh default and updates `session.default`.

Limits apply only to this opt-in session. Event queues are bounded per lane and
across the session; overflow reports `ResponsesWebSocketBufferError` and closes
the owned connection so ordered events are not silently dropped. Queue byte
counts measure received message bytes before parsing, not Python object overhead or
transport decoding memory. Response accumulation is uncapped by default:
omit `max_response_bytes` or set it to `None`. A positive integer opts into a
budget for the cumulative compatible event bytes passed to an accumulator;
exceeding it disables that response's collection, while raw events and other
lanes remain usable. Queue and lane limits still require positive integers.
Choose budgets for large legitimate outputs. These are application budgets,
not protocol limits.
The examples disable the transport's separate 1 MiB message limit with
`websocket_connection_options={"max_size": None}` so large events can reach the
session. If you set a transport limit, choose it separately for the largest
expected individual event; raising session budgets does not raise that limit.

The connection's existing opt-in reconnection policy still applies. Reconnecting
does not restore server-side response state. Lane sends reject while reconnecting,
before starting a response, so wait for recovery and restore application state.
Lane sends do not enqueue a
delivery-uncertain write for replay; handle that failure explicitly in your
application. A request whose delivery is uncertain remains in flight until its
terminal event arrives or you detach its lane. When recovery loses that state,
use a fresh ID, or close the lane and reconnect before recreating it, then
explicitly restore the application state.
Existing low-level connection sends retain their existing semantics.

## Continuation and service state

The [WebSocket mode guide](https://developers.openai.com/api/docs/guides/websocket-mode)
defines the server contract. Every new turn sends `response.create`; omit the
HTTP-only `stream` and `background` fields.

- **Warmup:** construct a `ResponseCreate` event from
  `openai.types.responses.responses_client_event` with `generate=False`, using
  its existing extra-field support. Send it through `lane.send()` and collect
  its terminal response with `lane.get_final_response()` (await both in async
  code). Use that response's ID as `previous_response_id` on a later create
  with new input. Warmup prepares state without generating model output.
- **Tools:** after the response completes, execute the application's tool and
  send its `function_call_output` with the original `call_id`, the completed
  response's ID, and only new input items. See
  [the tool-turn example](../../../../examples/responses/websocket.py).
- **Forks:** send the source response's ID on a different lane. With
  `store=False` or ZDR, wait for the fork lane's `response.in_progress` before
  advancing the source lane. Consume lane events with `recv()` to observe this
  barrier, handling errors and premature close while waiting.
- **Automatic compaction:** with `context_management` configured for compaction,
  continue using the latest response ID and only new input items.
- **Standalone compaction:** `client.responses.compact(...)` returns a compacted
  input window, not a response ID for continuation. Send its complete `output`
  as input to a new WebSocket chain, omitting or nulling `previous_response_id`.
  Do not prune items from the compacted output.

The server keeps recent response state in a connection-local cache. With
`store=True`, an older response may be loaded from persisted state. With
`store=False` or ZDR, an uncached ID produces `previous_response_not_found`.
A same-lane continuation returning a 4xx or 5xx evicts its referenced cached
parent; an errored cross-lane fork preserves the shared parent for the source
lane. Do not blindly retry the same parent after a cache miss. Restore the full
retained input and output history as a new chain when needed, including tool
and reasoning items rather than only displayed text. Request
`reasoning.encrypted_content` when retaining reasoning-model output for replay.

## Lanes, limits and connection lifetime

Named stream IDs contain 1–256 ASCII letters, digits, underscores, hyphens or periods;
the helper validates this exact string before reserving an ID. Other types and an
empty string are invalid. Omit the ID for the default lane. Reusing an open lane does
not select conversation history: supply `previous_response_id` explicitly.
The server executes requests on each lane FIFO without overlap, and may
interleave events from different lanes. Named-lane terminals and request errors
echo the ID; default-lane events omit it.

The service allows 16 active responses and queues additional creates. It accepts
32 distinct named IDs per connection; the default lane does not count. These
are separate from the helper's application budgets. Detaching a local lane does
not reset the server's distinct-ID count.

Connections last up to 60 minutes. Plan rotation at completed-turn boundaries.
Reconnecting loses every lane's connection-local cache: use persisted IDs when
available or restore full context explicitly. Handle `previous_response_not_found`,
`invalid_stream_id`, `websocket_stream_limit_reached`, and
`websocket_connection_limit_reached` through the original error event. Observe
the default lane for connection-scoped errors as well as each named lane.

Steering is a separate command: send only `type`, `previous_response_id` and
`input`, without `stream_id`. Accepted steering is not yet committed; the
successor's `response.created` is the commit point. If `response.steer.pending`
requires tool output or approval, fill its `required_input` stubs and send one
create on the parent's lane with that parent ID. Reuse saved results rather
than rerunning tools or resending already accepted steering input.

For the synchronous form, see `examples/responses_websocket.py`.
