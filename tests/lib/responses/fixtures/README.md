# WebSocket contract scenarios

This is the maintainer index for [websocket_scenarios.json](websocket_scenarios.json)
and the behavior tests that cannot be represented as static messages. A fixture can
describe an event, but cannot prove what happens when a sender is interrupted,
a reader is slow, or a real HTTP upgrade combines client and connection headers.
Use the index to check extensions against those behaviors before changing a public API.

The JSON fixture is version 1. Keep its existing IDs and expected message order
unchanged. At the public revisions below, all five copies have SHA-256
`464c5151691cd393166a3078b66e372e6136c85b45396536cedbca23437edd46`.
Equal bytes prove common input, not that every runtime handled it correctly.

| Fixture ID | Assertion to preserve |
| --- | --- |
| `completed_then_completed` | Ordered complete messages; a completed turn leaves the socket reusable. |
| `failed_then_completed` | A failed response is a terminal response, not a transport close. |
| `incomplete_then_completed` | An incomplete response ends its turn and preserves its status. |
| `nested_error_then_completed` | An API error remains observable; the next turn can complete. |
| `unknown_event_and_fields` | Unknown event types and fields stay observable alongside typed events. |
| `premature_close_1000` | A clean socket close before a terminal is not a successful response. |
| `premature_close_1011` | An error close is a transport failure, not a fabricated terminal. |
| `malformed_json` | Invalid JSON is observable as failure without being passed off as a typed event. |

## Runtime scenarios

These semantic IDs identify behavior, not new JSON cases. Their test references
are executable Python selectors; sync/async and other variants are supplied by
pytest. Run them from the repository root in the normal contributor environment:

```sh
uv run --locked --all-extras pytest -q -n 0 tests/lib/responses/test_websocket_contract.py \
  tests/lib/responses/test_websocket_auth.py::test_handshake_honors_prepared_url_query_and_headers \
  tests/lib/responses/test_websocket_session.py::test_custom_upgrade_headers_preserve_auth_and_connection_precedence \
  tests/lib/responses/test_websocket_session.py::test_raw_receive_preserves_text_utf8_and_binary_bytes \
  tests/lib/responses/test_websocket_session.py::test_wait_cancellation_does_not_lose_event_or_close_other_lane \
  tests/lib/responses/test_websocket_session.py::test_queue_overflow_is_explicit_and_stops_reader \
  tests/lib/responses/test_websocket_session.py::test_recovery_send_is_rejected_without_reserving_or_queueing \
  tests/lib/responses/test_websocket_session.py::test_uncertain_send_is_not_replayed_after_existing_recovery
```

| Semantic ID | Observable assertion | Python tests in the command above |
| --- | --- | --- |
| `upgrade.custom_headers` | A real upgrade carries SDK, client, and per-connection headers with documented precedence. | `test_handshake_honors_prepared_url_query_and_headers`, `test_custom_upgrade_headers_preserve_auth_and_connection_precedence` |
| `message.complete_ordered` | Complete text/UTF-8/binary data is preserved in receive order. Turn/terminal order remains covered by the eight JSON IDs. | `test_raw_receive_preserves_text_utf8_and_binary_bytes` plus both contract runners |
| `consumer.cancel_cleanup` | Canceling an unassigned receive leaves the event available and other lanes usable. | `test_wait_cancellation_does_not_lose_event_or_close_other_lane` |
| `consumer.slow_explicit_overflow` | A configured bound produces explicit failure, never silent event loss; the profile below specifies what closes. | `test_queue_overflow_is_explicit_and_stops_reader` |
| `send.unattempted_vs_uncertain` | Known pre-write rejection never reserves/replays a create; an uncertain write is never automatically replayed. | `test_recovery_send_is_rejected_without_reserving_or_queueing`, `test_uncertain_send_is_not_replayed_after_existing_recovery` |

These checks use synthetic local peers. They do not certify service persistence,
authorization for sideband sessions, or package availability.

## Extension proof

For each extension, choose **additive** (new opt-in API), **private change**
(existing API and defaults retained) or **redesign** (a public behavior must
change). The proposed classification is an implementation review question, not
an approval or a promise of support. A language owner may choose differently
where that runtime's read/send semantics require it.

| Extension | Observable constraint and existing evidence | Proposed scope; remaining work |
| --- | --- | --- |
| Translation finish/drain | Closing input must leave one reader delivering trailing audio/transcript events until a valid `session.closed`. [Node](https://github.com/openai/openai-node/blob/d0616b81c9a0d9cdf924903e5f1e364957e3c7e9/tests/lib/realtime/translations.test.ts): `sends typed and raw envelopes, closes once, and delivers all trailing events before finishing`; [Java](https://github.com/openai/openai-java/blob/aeae12de892a159626efd7e74e2594e1cdcee248/openai-java-client-okhttp/src/test/kotlin/com/openai/client/okhttp/TranslationConnectionTest.kt): `canceledReceiveAndSingleReaderWorkWhileFinishDoesNotStealEitherEvent`; [Ruby](https://github.com/openai/openai-ruby/blob/b3706d84fbb68e700bb726559fba0da0393de567/test/openai/realtime/translation_connection_test.rb): `test_translation_drains_final_output_after_the_close_command`. | Additive endpoint API with private admission/drain lifecycle. Python/Go have no Translation transport at the public revisions below; do not label them verified from another SDK's tests. |
| Live open vs ready, primary/sideband/fork | An open socket is not a ready session; each role sends only the correct startup command. [Python roles](../../live/test_websocket_roles.py): `test_live_role_startup_and_routing` (all roles, sync/async). | Additive role entrypoints and private readiness guards; never apply Responses recovery to Live audio/tools. Real hosted storage and sideband eligibility require a separate live check. Go Live is not present in the pinned public Go tree. |
| Responses lanes | `stream_id` routes delivery; `previous_response_id` selects history. They must stay independent. [Python session](../test_websocket_session.py): `test_interleaved_lanes_default_unknown_and_detach`. | Private routing under the existing APIs. Do not change how each profile invalidates or retains lanes on reconnect. |
| Physical socket replacement | Refresh the handshake through the endpoint's client path, without replaying uncertain writes or inventing application state. [Python session](../test_websocket_session.py): `test_detached_lane_is_released_after_reconnect` and the two send scenarios above. | Private connection replacement within the endpoint's existing opt-in recovery policy. Explicit application state restoration stays the caller's job. |
| Non-owning helper observation | Callers still see raw events; disposing a helper affects only its state/timers, not other observers or the connection. [Python roles](../../live/test_websocket_roles.py): `test_disposed_grouper_leaves_dispatcher_other_observers_and_socket_usable`; [Python accumulator](../test_websocket_accumulator.py): `test_default_lane_foreign_events_can_be_inspected_without_feeding_the_projection`. | Additive opt-in helpers. A collecting lane/session may own a read side; a caller-fed accumulator never does. |

Run the Python extension selectors with the same pytest command, substituting:

```sh
uv run --locked --all-extras pytest -q -n 0 \
  tests/lib/live/test_websocket_roles.py::test_live_role_startup_and_routing \
  tests/lib/live/test_websocket_roles.py::test_disposed_grouper_leaves_dispatcher_other_observers_and_socket_usable \
  tests/lib/responses/test_websocket_session.py::test_interleaved_lanes_default_unknown_and_detach \
  tests/lib/responses/test_websocket_session.py::test_detached_lane_is_released_after_reconnect \
  tests/lib/responses/test_websocket_accumulator.py::test_default_lane_foreign_events_can_be_inspected_without_feeding_the_projection
```

## Native profiles: preserve these differences

These pinned public sources record the APIs the tests must exercise. A shared
scenario asserts a semantic outcome; it must not impose one SDK's queue limit,
cancellation behavior, or send-completion meaning on another. Scope is the
Responses adapter shown, not every WebSocket endpoint or HTTP transport.

| SDK and source | Entrypoint, send meaning, runtime/provider scope | Limits, cancellation, compatibility |
| --- | --- | --- |
| [Python](https://github.com/openai/openai-python/blob/68b173a24fa9ebfc6b84694a39a0dd0f9a1e6087/src/openai/lib/responses_websocket/README.md) | `client.responses.connect()`; opt-in `ResponsesWebSocketSession` / async form, `lane.send()`. Sync and async `websockets` via `openai[realtime]`; HTTP-only auth is rejected before dialing. Sending is not API completion. | Caller chooses positive lane/event/byte budgets. Queue overflow closes the owned socket; collection overflow preserves raw events/other lanes. Collection uncapped by default. Canceled receive/final wait keeps queued events and accumulated state. Existing raw API unchanged. |
| [TypeScript](https://github.com/openai/openai-node/blob/d0616b81c9a0d9cdf924903e5f1e364957e3c7e9/docs/responses-websocket-session.md) | `ResponsesWS` with optional Node `ws` and agent; opt-in `ResponsesWebSocketSession`, `lane.create()` after open. Connection listeners keep seeing raw events. Send acceptance is not API completion. Do not infer browser custom-header support from Node. | Required session budgets; lane overflow fails that lane, session exhaustion fails/drains largest backlog. Canceled receive keeps events; canceled final collection after consumption detaches the lane. Reconnect invalidates old lanes. Original low-level sends keep their existing behavior. |
| [Go](https://github.com/openai/openai-go/blob/d7fd0c65cc247957d5b247ad42283fc8e4061868/responses/responses_websocket.go) | `client.Responses.Connect(ctx, options)`, `Send` / `Create` do one local write; `DeliveryError.MayHaveBeenSent` marks uncertainty. The configured HTTP upgrade transport must expose a writable upgraded stream. Opening context bounds opening only. | [Options](https://github.com/openai/openai-go/blob/d7fd0c65cc247957d5b247ad42283fc8e4061868/packages/websocket/connection.go): message/events/bytes unlimited at zero; 16 pending sends, 64 named IDs, 5s close by default. Receive context cancels only that wait. `Reconnect`/`Recover` returns a fresh connection; re-register lanes. |
| [Java](https://github.com/openai/openai-java/blob/aeae12de892a159626efd7e74e2594e1cdcee248/docs/responses-websocket.md) | Blocking/async `client.responses().connect()`, `lane.send()` means accepted for writing. OkHttp disables redirects and connection-failure retries; an opening HTTP 503 with `Retry-After: 0` may retry once, before any command is sent. HTTP-only clients report unsupported. Azure unified routing only. | 64 named lanes/1 pending send; configurable receive bounds, native 16 MiB outgoing limit. Overflow fails connection. Unassigned future receive can cancel; assigned event cannot. Explicit reconnect retains open lanes. Closing connection does not shut down the shared client executor. |
| [Ruby](https://github.com/openai/openai-ruby/blob/b3706d84fbb68e700bb726559fba0da0393de567/lib/openai/helpers/responses_websocket/README.md) | `client.responses.connect`; opt-in `OpenAI::Responses::Session.open` / `lane.send_event`. Async is optional and loaded on demand; operations belong to owning Ruby thread. Send completion is not response completion. | Required lane/event/byte and response budgets. Queue overflow closes owned transport; collection overflow preserves raw events. Canceling receive/final wait retains queued state. Explicit recovery creates new lanes and invokes caller restoration; old handles fail. No change to low-level defaults. |

Public input locations at those revisions: [Node](https://github.com/openai/openai-node/blob/d0616b81c9a0d9cdf924903e5f1e364957e3c7e9/tests/lib/responses/fixtures/websocket_scenarios.json),
[Go](https://github.com/openai/openai-go/blob/d7fd0c65cc247957d5b247ad42283fc8e4061868/internal/websockettest/testdata/scenarios.json),
[Java](https://github.com/openai/openai-java/blob/aeae12de892a159626efd7e74e2594e1cdcee248/openai-java-client-okhttp/src/test/resources/responses-websocket/scenarios.json),
and [Ruby](https://github.com/openai/openai-ruby/blob/b3706d84fbb68e700bb726559fba0da0393de567/test/openai/responses_websocket/fixtures/websocket_scenarios.json).
For an actual runtime certification, use that repository's contributor commands
and record the tested commit and result. Do not substitute this map or matching
fixtures for another SDK's run.
