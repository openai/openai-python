# Python generated-code transition

## Objective and non-negotiable contract

Eliminate handwritten patches in generated-owned files while preserving every existing developer-facing API and behavior. Handwritten runtime code remains a supported part of this SDK. Completion means the generated-owned tree matches a verified generation, with public extension wiring generated from authoritative compiler/configuration facts. Moving code to `lib/` while leaving handwritten imports, methods, or hooks in generated files is only an intermediate step.

No removals or renames of public symbols, new required arguments, narrower input/return types, dependency or Python-floor changes, altered defaults, new payload limits, changed warnings, or changed sync/async behavior are authorized by this transition. Deprecated methods and compatibility import paths remain supported.

## Baseline and measurement

Audited 2026-10-19 at public SDK commit `5589146d738e0c38758e117b8383a02c2e4e2ee7`. This is a fixed baseline, not a claim about future main.

- Public generated snapshot: `12578924cd37047e1bff02ea0e6f90114b363d15`.
- Generation ID: `021e41cf-0817-45e4-a61f-ed6fae979669`.
- Verified generated-content SHA-256: `b5dab72c84981b6bbd1709863e017a16f1902b9aa11cd721143186487fd2787b`.
- **41 mixed files; 6,081 added + 1,287 deleted = 7,368 custom patch lines.**
- Current physical size of these files: **45,486 lines**; pure-generated counterparts: **40,692 lines**.
- 36 mixed Python files under `src/openai/`, one source-tree Markdown reference, one generated test, two reporting scripts, and root `api.md`.
- Repository policy: 10,000 patch lines, leaving 2,632 at this baseline. No budget adjustment is part of the initial implementation.

The existing reporter is authoritative: it compares paths owned by the pure-generated snapshot with their integrated contents, including mode changes. Additions and deletions never cancel. These are diff lines, including comments, blank lines, moved definitions, overloads, and formatting; they are not executable handwritten statements. Current/generated physical lines count all lines, including comments and blanks. Reordering a method can cost both additions and deletions without changing behavior.

The snapshot owns 1,961 paths, including 1,791 under `src/openai/`. Another 203 tracked source-tree files (34,861 physical lines) are outside that snapshot. None has the standard generated-file header. They include intentionally handwritten runtime and helper modules and do not count as mixed files. This boundary must be audited during future generations; do not broaden exclusions, relabel files, edit checkpoints, or change the counter to reduce the result. Existing workflow exclusions remain unchanged.

Machine-readable per-file data: [castiron-transition-inventory.json](castiron-transition-inventory.json).

Reproduce the authoritative report from a trusted checkout, using full commit SHAs:

```sh
python3 -I scripts/castiron/custom_code_report.py report \
  --repo . \
  --base 5589146d738e0c38758e117b8383a02c2e4e2ee7 \
  --head 5589146d738e0c38758e117b8383a02c2e4e2ee7 \
  --public --fetch --require-head-hash \
  --out /tmp/python-custom-code-transition
```

Read `.castiron.stats.yml` at the inspected revision. Validate public snapshot generation metadata, snapshot-branch ancestry, and content hash through the existing reporter. For physical sizes, read each integrated/generated blob and use `len(blob.splitlines())`; do not count the entire SDK diff because it also contains handwritten-only files. Regenerate this inventory after each promoted generation and record before/after measurements in its PR.

## Complete file inventory

`+` and `-` are the remaining customization against the generated snapshot. The table is ordered by patch size.

| File | Current lines | Generated lines | + | - | Patch | Track |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `src/openai/resources/beta/threads/runs/runs.py` | 3,161 | 2,052 | 1,290 | 181 | 1,471 | T4 |
| `src/openai/resources/responses/responses.py` | 5,141 | 4,295 | 920 | 74 | 994 | T5 |
| `src/openai/resources/audio/transcriptions.py` | 1,089 | 1,403 | 287 | 601 | 888 | T3 |
| `src/openai/_client.py` | 2,401 | 1,702 | 759 | 60 | 819 | T2 |
| `src/openai/resources/chat/completions/completions.py` | 3,456 | 2,854 | 603 | 1 | 604 | T6 |
| `src/openai/resources/beta/threads/threads.py` | 2,009 | 1,626 | 390 | 7 | 397 | T4 |
| `src/openai/resources/vector_stores/file_batches.py` | 867 | 628 | 242 | 3 | 245 | T7 |
| `src/openai/resources/uploads/uploads.py` | 765 | 544 | 221 | 0 | 221 | T8 |
| `src/openai/resources/vector_stores/files.py` | 1,032 | 813 | 220 | 1 | 221 | T7 |
| `src/openai/__init__.py` | 505 | 321 | 185 | 1 | 186 | T2 |
| `src/openai/resources/videos.py` | 1,457 | 1,306 | 153 | 2 | 155 | T10 |
| `api.md` | 2,074 | 1,963 | 119 | 8 | 127 | T16 |
| `src/openai/resources/beta/agents/environments/files.py` | 596 | 473 | 125 | 2 | 127 | T9 |
| `src/openai/resources/beta/agents/sessions/sessions.py` | 1,304 | 1,202 | 113 | 11 | 124 | T9 |
| `src/openai/resources/audio/translations.py` | 374 | 409 | 40 | 75 | 115 | T3 |
| `src/openai/resources/beta/responses/responses.py` | 5,535 | 5,535 | 55 | 55 | 110 | T5 |
| `src/openai/resources/webhooks/webhooks.py` | 1,146 | 1,061 | 89 | 4 | 93 | T12 |
| `tests/api_resources/test_videos.py` | 939 | 919 | 54 | 34 | 88 | T10 |
| `src/openai/resources/webhooks/__init__.py` | 42 | 73 | 24 | 55 | 79 | T12 |
| `src/openai/resources/embeddings.py` | 263 | 257 | 27 | 21 | 48 | T13 |
| `src/openai/resources/live/forks.py` | 1,416 | 1,419 | 15 | 18 | 33 | T11 |
| `src/openai/resources/live/sideband.py` | 1,393 | 1,396 | 15 | 18 | 33 | T11 |
| `src/openai/resources/files.py` | 826 | 800 | 26 | 0 | 26 | T14 |
| `src/openai/resources/beta/beta.py` | 269 | 248 | 21 | 0 | 21 | T15 |
| `src/openai/resources/realtime/api.md` | 149 | 169 | 0 | 20 | 20 | T16 |
| `src/openai/resources/realtime/translations/translations.py` | 1,112 | 1,096 | 18 | 2 | 20 | T11 |
| `src/openai/resources/live/live.py` | 1,613 | 1,608 | 11 | 6 | 17 | T11 |
| `src/openai/resources/realtime/realtime.py` | 1,630 | 1,624 | 9 | 3 | 12 | T11 |
| `src/openai/types/decision_input_image_param.py` | 47 | 37 | 11 | 1 | 12 | T1 |
| `src/openai/types/decision_input_text_param.py` | 33 | 23 | 11 | 1 | 12 | T1 |
| `scripts/castiron/custom_code_budget.py` | 737 | 737 | 5 | 5 | 10 | T0 |
| `src/openai/resources/beta/agents/sessions/artifacts.py` | 561 | 551 | 10 | 0 | 10 | T9 |
| `scripts/castiron/test_custom_code_report.py` | 460 | 467 | 0 | 7 | 7 | T0 |
| `src/openai/types/webhooks/__init__.py` | 73 | 71 | 3 | 1 | 4 | T1 |
| `src/openai/types/webhooks/unwrap_webhook_event.py` | 74 | 74 | 2 | 2 | 4 | T1 |
| `src/openai/types/responses/tool.py` | 398 | 399 | 1 | 2 | 3 | T1 |
| `src/openai/types/responses/tool_param.py` | 398 | 395 | 3 | 0 | 3 | T1 |
| `src/openai/types/webhooks/live_call_incoming_webhook_event.py` | 71 | 70 | 2 | 1 | 3 | T1 |
| `src/openai/types/fine_tuning/fine_tuning_job_integration.py` | 5 | 7 | 0 | 2 | 2 | T1 |
| `src/openai/types/realtime/conversation_item_input_audio_transcription_delta_event.py` | 40 | 40 | 1 | 1 | 2 | T1 |
| `src/openai/types/realtime/realtime_error_event.py` | 25 | 25 | 1 | 1 | 2 | T1 |
| **Total** | **45,486** | **40,692** | **6,081** | **1,287** | **7,368** | |

## Work tracks and dependencies

Track totals partition the entire inventory; proposed reductions are upper bounds until a verified regeneration proves that every patch in the relevant files has disappeared.

| Track | Scope | Files | Patch lines | Required compiler/input capability | Scheduling |
| --- | --- | ---: | ---: | --- | --- |
| T0 | Restore generated reporting tooling | 2 | 17 | None; restore semantically equivalent local rename and deleted assertions | First SDK PR; independent |
| T1 | Type and import compatibility | 10 | 47 | Typed compatibility declarations, export deduplication, static deprecation; schema documentation fixes | Independent of resource helpers |
| T2 | Client and module entrypoint | 2 | 1,005 | Typed client hooks, provider adapter factories, root lazy-export/module-client declarations | Separate client and root-entrypoint PRs; high compatibility risk |
| T3 | Audio overloads and response formats | 2 | 1,003 | Response-discriminated overloads, runtime selection/parser hooks | Independent; compare existing OpenAI-profile support first |
| T4 | Assistants threads/runs helpers | 2 | 1,868 | Generic delegated helpers, polling, stream managers, legacy method names | After helper declarations; split runs vs threads |
| T5 | Responses helpers and beta class layout | 2 | 1,104 | Generic parse/stream hooks, exact overloads, websocket class partitioning | Split main Responses and beta class layout |
| T6 | Chat parsing and streaming | 1 | 604 | Generic parse/stream declarations and request validation hooks | After shared helper representation |
| T7 | Vector store helpers | 2 | 466 | Generated typed delegates to polling/runtime helpers | Split files vs batches; independent of uploads |
| T8 | Chunked uploads | 1 | 221 | Typed overloads/delegates and handwritten orchestration | Compatibility-test PR first; independent |
| T9 | Hosted Agents helpers | 3 | 261 | Typed delegates, output binding, custom event streams | Files/artifacts independently; sessions later |
| T10 | Video polling and generated tests | 2 | 243 | Generated helper declarations, deprecation-aware test emission | Compatibility coverage first; independent |
| T11 | Live and Realtime websocket contracts | 5 | 115 | Resource-specific queue default facts, constructor policy, translation/calls hooks | Live and Realtime separate compiler PRs |
| T12 | Webhook facade and resource exports | 2 | 172 | Generated verification delegates; exact sync facade and wrapper identity | Maintainer/CODEOWNER review; independent |
| T13 | Embedding decoding hooks | 1 | 48 | Default parameter and post-parser generation facts | Independent; existing runtime remains handwritten |
| T14 | File processing helper | 1 | 26 | Generate exact wait_for_processing delegate | Small initial helper-declaration consumer |
| T15 | Beta compatibility aliases | 1 | 21 | Generated compatibility getters/lazy exports | Independent of helpers; preserve existing warning/decorator behavior |
| T16 | API reference documentation | 2 | 147 | Emit helper signatures and wrapper/type links from the same compiler facts | After each related helper; final docs cleanup |

## Compiler changes

The maintained compiler is `api/castiron` in the OpenAI monorepo; the standalone Castiron repository is archived. Do not implement compiler fixes in that archived checkout. Compiler paths below are design targets, not a claim that all capabilities are absent. Current OpenAI-profile generation already has some helper documentation, audio, native websocket, extended union, and lazy-export support, also present in the pinned snapshot; compare current merged output before adding a second mechanism. Helper-documentation and compatibility-export configuration already lives in `crates/castiron-oas-transform/src/config/{python_helper_docs.rs,python_compatibility.rs}`, with corresponding typed IR and renderer modules. Documentation facts alone do not generate runtime delegates.

### Typed extension declarations and delegates

Extend the compiler model with typed resource helper declarations: method name and placement, parameter/overload sources, generic return types, sync/async mode, delegate target, request preparation/post-parser hooks, specialized stream classes, and raw/streaming-wrapper exposure. Validate these facts and project them into the Python renderer. Use existing configuration/model mechanisms where they fit; do not accept arbitrary code injection, raw SDK-file snapshots, or path-specific source replacement as the extension API.

Generate exact signatures rather than `*args, **kwargs` facades. Derive shared parameters from canonical endpoint facts so future schema changes reach helper methods, overloads, and docs together. Existing tests comparing helper and endpoint signatures are part of the contract. Keep orchestration in the existing handwritten modules where possible: polling/deadlines, file preparation, parsing, streaming accumulation, authentication/provider integration, and upload lifecycle. Generated delegates are the stable boundary.

Concrete implementation areas are `crates/castiron-oas-transform/src/config.rs`, `crates/castiron-ir/src/castiron_facts/resource.rs`, `crates/castiron-compiler/src/sdk_compiler/castiron_facts.rs`, and `crates/castiron-render-python/src/{resources.rs,resources/collect_views_timed.rs,resources/websocket.rs,templates/resource.py.askama}`, plus API-reference/config inputs. Locate and read current modules before each change. Add focused compiler tests and generation-level tests for each capability.

### Client and package integration facts

Replace the remaining local `_client.py` edits through explicit generated hooks and public signature configuration for callable credentials, provider behavior, copy semantics, client construction, request transforms, and response parsing. Keep existing handwritten implementations and preserve subclass override ordering, credentials/headers/environment precedence, transport ownership, and error timing. A wholesale new client architecture is outside this migration.

Generate root entrypoint exports/lazy exports, module-client routing, and provider adapter factory wiring from explicit facts. Retain Azure/Bedrock auto-selection/ambiguity rules, cached module attributes and mutation precedence, deferred imports, historical exceptions and transport names, and symbol identity. Tests must compare both direct class clients and the module-level client.

### Compatibility types and websocket policies

Model explicit compatibility classes, union extensions, export deduplication, class-level static deprecation, and internal deprecation suppression. Preserve distinct historical classes even when structurally identical. Fix schema documentation mistakes in schema inputs. For Live, emit the SDK queue constant/default and direct-constructor queue policy from resource facts under the OpenAI profile; do not change unrelated websocket resources. For Realtime, preserve required translation model/query forwarding, explicit caller receive limits, `max_size=None` defaults, and specialized calls-resource construction.

Intentional output changes belong under `CodegenProfile::OpenAI`. Preserve `StainlessParity` fixture behavior and never rewrite existing Stainless fixtures, provenance, or expected archives. Test both profiles.

## Track-specific contracts and acceptance criteria

### T0 — reporting restoration (17 lines, two files)

The budget-checker delta is a local variable rename (`policy` to `policy_sha`); restoring the generated spelling must leave policy selection/evaluation identical. The reporter test delta deletes assertions, including explicit workflow-exclusion/inclusion checks; restore those assertions, including existing duplicates, rather than changing the generated baseline. Run the entire offline custom-code unit suite. Acceptance: both files byte-identical to the current verified snapshot and 39 mixed files / 7,351 patch lines if this is the only baseline change. This reduces customization without modifying policy, counting, or exclusions.

### T1 — compatibility types (47 lines, ten files)

- `decision_input_image_param.py` and `decision_input_text_param.py` each define a historical `PromptCacheBreakpoint` TypedDict. Preserve separate classes and their `__module__`; aliasing the shared generated class breaks `tests/test_decision_prompt_cache.py`.
- `responses/tool_param.py` exposes `ParseableToolParam = Union[ToolParam, ChatCompletionFunctionToolParam]`; preserve static imports and both tool shapes. Deduplicate the extra `WebSearchTool` import in `tool.py` while preserving explicit re-export and `__all__` behavior.
- `fine_tuning_job_integration.py` removes `__all__`; restoring the generated restriction would narrow current wildcard imports, including `FineTuningJobWandbIntegrationObject`. Preserve those exports.
- Preserve `LiveCallIncomingWebhookEvent` static deprecation with `category=None`, legacy discriminator parsing, and internal import suppression. Do not introduce runtime warnings or remove its union branch.
- Preserve the two Realtime schema doc corrections in authoritative input: authored `RealtimeServerEventError` (implementers) and `RealtimeServerEventConversationItemInputAudioTranscriptionDelta` (configuring). These are documentation-only changes; do not modify the Beta schema or unrelated grammar.

Acceptance: import/identity/wildcard-export assertions and type-checking fixtures pass; type files match regenerated output without alias substitutions that alter identities.

### T2 — client and root module (1,005 lines, two files)

Preserve synchronous/asynchronous callable key providers; eager credential checking and the module-client bypass; workload identity/X.509/provider authentication behavior; credential/environment isolation; safe retry and 401 replay behavior; data residency/base URLs; `.copy`/`.with_options`; case-insensitive headers and `Omit`; transport defaults and ownership. Preserve Azure/Bedrock routing, ambiguous-provider errors, root lazy exports, old API exceptions, and public transport aliases. Split client and entrypoint implementations.

Verify `tests/test_client.py`, `tests/test_module_client.py`, `tests/test_lazy_imports.py`, and relevant provider/auth/copy tests. Add targeted parity cases for uncovered signatures/identities before moving hooks. Security-sensitive changes require SDK CODEOWNER and compiler maintainer review. Do not publish vulnerability details as part of cleanup.

### T3 — audio (1,003 lines, two files)

Generate overloads and response-class selection from response-format/stream facts. Preserve transcription JSON/verbose JSON/diarized JSON model classes, translation JSON/verbose JSON classes, text/SRT/VTT strings, streaming event types, and default model behavior for omitted/legacy `None`. Unknown values retain historical warning and fallback behavior. Preserve compatibility helpers/logger names. Most deleted lines are overload or layout churn, not code safe to discard.

Verify `tests/lib/test_audio.py`, `tests/lib/test_audio_response_format.py`, generated sync/async resource cases, and static overload selection. The pinned generated snapshot already contains response-format overloads and parser selection. The retained patch replaces overload groups/signatures/doc placement and preserves parser aliases, logging and a legacy `_get_response_format_type` shim. Extend compatibility generation around the existing feature rather than adding another response-format engine. Reuse `crates/castiron-oas-transform/src/config/python_response_format.rs`, `crates/castiron-compiler/src/sdk_compiler/castiron_facts/python_response_format.rs`, and `crates/castiron-render-python/src/resources/response_format.rs`; preserve the existing SDK parser in `lib/_parsing/_audio.py`.

### T4 — Assistants (1,868 lines, two files)

Generate runs create/poll/stream and submit-tool-output helpers, threads create-and-run/poll/stream, and old `create_and_stream` names. Preserve custom handler generic types, deprecated APIs/warnings, sync/async context managers, all endpoint parameters, request options/security, path validation, helper/Beta headers and caller precedence. Polling keeps terminal states including `requires_action`, negotiated server intervals, 1-second fallback, and `stream=False`.

`tests/lib/test_assistants.py` signature synchronization is necessary but insufficient. Add sync/async HTTP and stream-lifecycle contract tests before relocating helper implementations; then split runs and threads changes.

### T5 and T6 — Responses and Chat helpers (1,598 lines plus 110 beta-layout lines)

Generate `.parse`/`.stream` signatures/overloads, generic return types, retrieve streaming variants, helper headers, parser hooks, specialized stream classes, and raw/streaming wrapper exposure. Keep handwritten parsing/accumulation engines. Preserve strict-tool validation, generator materialization, Pydantic models/dataclasses, refusal and finish-reason exceptions, context acquisition/closure, and async manager shapes.

Responses additionally preserves Chat-to-Responses function tool conversion, strict/options/model binding, `text_format` versus `text.format` errors, copied caller configuration, resume-versus-create validation, and `starting_after` semantics. Preserve beta sync/async websocket class placement; its 55 additions/55 deletions are largely layout rather than new feature logic.

Verify `tests/lib/chat/test_completions.py`, `test_completions_streaming.py`, `tests/lib/responses/test_responses.py`, response websocket/session/auth tests, parser/null/input-history cases, and tool-runner tests. Preserve unbounded supported JSON and stream payloads; run large cases sequentially.

### T7 — vector stores (466 lines, two files)

Emit `create_and_poll`, `poll`, `upload`, and `upload_and_poll` delegates. Retain handwritten polling logic in `lib/_vector_stores.py`; isolate batch concurrency separately if needed. For Files helpers, preserve finite nonnegative `max_wait_seconds`, validation before side effects, zero preventing polls, omitted timeout remaining unbounded, deadlines starting after upload/attachment, and bounded sleeps. FileBatches currently has no deadline argument; do not add one during this migration. Across both resources, preserve headers/interval precedence, terminal objects, errors/cancellation, asyncio/trio concurrency, preexisting IDs, and assistants upload purpose.

Verify `tests/lib/test_vector_store_polling.py`, `test_vector_store_file_poll_timeout.py`, `test_vector_store_files.py`, `test_vector_store_file_batches.py`, `tests/test_vector_batch_compat.py`, and signature synchronization.

**Merge gate:** Every T7 PR that changes file-upload helpers, including generated delegates and handwritten runtime extractions, requires explicit SDK CODEOWNER approval before merge. Retain and add focused synchronous and asynchronous security regression tests as applicable to the changed upload boundary, including validation before side effects, file ownership/cleanup and cancellation. Preserve credential/header filtering and supported large payloads, following [AGENTS.md](../AGENTS.md#security-requirements-for-coding-agents). Functional tests or compiler approval alone do not satisfy this gate.

### T8 — uploads (221 lines, one file)

Preserve exact `upload_file_chunked` overloads: path/in-memory variants, required filename/bytes for in-memory inputs, inferred path metadata and explicit overrides, 64 MiB default parts, sequential part order, completion part IDs and MD5, handle cleanup on success/failure, and async file I/O. Generate delegates after a handwritten runtime extraction only if it actually simplifies ownership. No new file maximum.

Add focused sync/async mock-transport tests for metadata validation before HTTP calls, multipart content and order, completion, empty inputs, client options, and cleanup before extraction. Existing generated upload smoke tests alone do not cover helper lifecycle.

**Merge gate:** Every T8 file-upload migration PR requires explicit SDK CODEOWNER approval before merge, including generated delegate changes and handwritten runtime extractions. Retain and add focused synchronous and asynchronous security regression tests as applicable: validation before HTTP requests, existing path/file handling, cleanup on failure/cancellation, and credential/header filtering. Use synthetic fixtures and preserve existing large-payload coverage without introducing new limits. The compatibility-test PR does not grant approval to a later migration PR; follow [AGENTS.md](../AGENTS.md#security-requirements-for-coding-agents).

### T9 — Hosted Agents (261 lines, three files)

Generate environment file `prepare`, `prepare_directory`, `upload` and artifact `for_result` delegates with exact signatures. Preserve preflight before side effects, path/symlink safety, ownership of partially uploaded files, cancellation cleanup, async file access, large payloads, ordered artifact selection, and exact-turn scoping.

Sessions additionally needs `output_type`/`tool_handlers` overload parameters, output-schema binding, stream-only handler validation, specialized streams, parser binding and context managers. Preserve subscribe-before-input, idempotency, single-use contexts, typed results, exactly-once dispatch, redaction/cancellation, and exclusion of local output types from serialized bodies. Verify `tests/lib/streaming/agents/`, especially file/artifact/create/output/result/stream contracts.

**Merge gate:** Every T9 PR that changes file-upload helpers requires explicit SDK CODEOWNER approval before merge, including generated delegates and handwritten runtime extractions. Retain and add focused synchronous and asynchronous security regression tests as applicable for preflight/path/symlink safety, partial-upload ownership, cancellation cleanup and sensitive-data/header redaction. Preserve supported large payloads and follow [AGENTS.md](../AGENTS.md#security-requirements-for-coding-agents). Obtain all other security-sensitive reviews required for session/authentication/serialization changes as well.

### T10 — videos (243 lines including generated tests)

Preserve deprecated `create_and_poll`/`poll`, accepted parameters, request options, interval negotiation, queued/in-progress waiting, completed/failed results, unknown-state behavior, and warnings. The generated video tests contain existing deprecation/signature adaptations; derive generated deprecation assertions from method facts, and keep helper contract tests durable outside generated smoke tests. Add focused sync/async polling coverage before changing helper bodies.

### T11 — Live and Realtime (115 lines, five files)

Live defaults use `DEFAULT_LIVE_SEND_QUEUE_MAX_BYTES` (2,097,152 at baseline), including directly constructed connections. Preserve caller-owned empty queues with an explicit `is not None` check. A truthiness fallback changes ownership. Formatting-only URL construction changes should be reconciled only after behavioral parity.

Realtime translations preserve required model arguments, manager storage and query merging, `max_size=None`, and caller-specified websocket options. Main Realtime preserves compatible sync byte receiving and specialized calls-resource classes. Verify `tests/lib/live/test_websocket_roles.py`, `tests/lib/test_realtime_translation.py`, `test_realtime_calls.py`, websocket contract/recovery tests, large audio, explicit receive-limit overrides, reconnect/model propagation, and no accidental command replay.

### T12 — webhooks (172 lines, two files)

Keep verification in `lib/_webhooks.py` and generate exact verifying facades: string/bytes payloads, required headers, secret fallback, tolerance default, error behavior. Async resource verification helpers remain synchronous. Do not restore the pure parser-only unwrap behavior. Preserve the wrapper class identity and `__module__` at `openai.resources.webhooks`, distinct from its internal module class; a simple re-export changes this surface. Verify webhook/signature/endpoint-with-secret tests and legacy event parsing. Compiler maintainer and SDK CODEOWNER review required.

### T13–T16 — small runtime hooks, aliases, and documentation

- Embeddings (48 lines): default to base64 only when `encoding_format` is omitted, preserve explicit formats and post-decoding through `lib/_parsing/_embeddings.py`, plus sync/async type/return behavior. Verify `tests/lib/test_embeddings.py` and generated resource tests.
- Files (26 lines): generate the existing `wait_for_processing` delegate with exact timeout/options/return/error behavior; use as an early helper-declaration consumer.
- Beta aliases (21 lines): preserve old properties and exact existing warning/decorator behavior; generate getters with stable imports. The cached `beta.chat` and `beta.realtime` properties are not themselves deprecated; do not add warnings.
- Documentation (147 lines): derive helper signatures, deprecated compatibility APIs, wrapper exposure and type links from the same facts as code. Reconcile duplicate Safety Alerts content and stale webhook links. Deleted realtime documentation is still part of the inventory; do not silently restore stale or absent APIs.

## Execution order and merge gates

1. Publish this plan/inventory separately from runtime changes. Publish T0 independently and compatibility tests for T8 in parallel.
2. Implement T11 Live facts and T1 compatibility facts independently; compare current merged compiler output for already-supported cases. Small helper declarations for T14 and T9 file/artifact delegates are the next shared boundary.
3. In parallel after their prerequisites, tackle T7 vector stores, T8 uploads, T10 videos, T12 webhooks, T13 embeddings, T15 aliases, and the independent Realtime portion of T11. Each PR states the exact compatibility surface and expected count reduction.
4. Implement T3 audio, T6 Chat, T5 Responses and T9 session hooks, using shared typed helpers/hooks. Split beta websocket class placement separately.
5. Draw down T4 Assistants and T2 client/root integration only with fuller contract coverage. These account for substantial patch size and compatibility risk. T16 documentation follows the relevant generated helper facts.
6. For each compiler change: focused tests + both profile checks + maintained fixture/parity suite; compiler review/merge; regenerate using the merged compiler binary; review isolated SDK output; run compatibility/type/build checks and focused synchronous/asynchronous security regression tests as applicable; obtain required SDK CODEOWNER approval, explicitly including every T7/T8/T9 file-upload migration; then satisfy normal merge gates. Compiler approval, functional tests and earlier PR approvals do not replace CODEOWNER approval on the affected SDK PR. Do not bundle unrelated API schema or dependency updates.
7. After measured reductions land, propose any ceiling decrease in a PR containing only `.castiron-ratchet.json`, with measured usage and headroom. Budget increases require human approval. Strict zero ownership is a separate activation after the SDK really reaches zero; never enable it over remaining patches.

Compiler source changes must be merged to monorepo `master` before an agent promotes their SDK output. Draft generation is allowed for review. An approved but unmerged Delta is not sufficient. Do not hand-update `.castiron.stats.yml`, public snapshot SHAs, manifests, exclusions, or ownership to claim a reduction.

## Verification and completion criteria

For every runtime migration, preserve imports (including compatibility module paths and wildcard exports), `__all__`, class identities/modules, public signatures and overloads, generic return types, sync/async call shape, defaults, sentinel behavior, warnings/errors, request serialization/options, stream lifecycle, and subclass extension behavior. Add targeted baseline contract tests where existing coverage is weak. A smaller diff is insufficient evidence of compatibility.

Run focused sync/async public-entrypoint tests, static type checks, repository lint/build as appropriate, and the existing custom-code unit suite. Run existing high-memory JSON/SSE regression cases sequentially without shrinking fixtures or raising client limits. No dependency or minimum-Python upgrades belong in these PRs. CI evidence must reference the exact current head.

Every file-upload migration, including T7, T8 and T9 generated delegates or handwritten runtime extractions, must retain/add focused synchronous and asynchronous security regression coverage as applicable and obtain explicit SDK CODEOWNER approval before merge. Apply the same repository requirements to all other security-sensitive changes listed in [AGENTS.md](../AGENTS.md#security-requirements-for-coding-agents). Advancing automatically means preparing and validating successor work; merging or promoting it still requires these approvals and tests on the affected PR.

A track is complete only when the compiler change has landed (where needed), the SDK is regenerated from verified merged inputs, its patch is absent in the authoritative report, developer behavior passes, and SDK review/checks are satisfied. Final completion is **zero mixed files and zero custom patch lines**, with legitimate handwritten runtime ownership intact.

## Conductor follow-up policy

The user authorizes implementation, publication of independent PRs/Deltas, and automatic reactions to Conductor updates without repeated permission prompts. Each event is a wake-up: fetch current head, reviews/threads, CI and merge state before acting. Address actionable feedback, resolve narrow conflicts, rerun appropriate checks, and keep this ledger current. Deduplicate existing review requests.

Use ordinary review/check/queue controls; never approve through a human identity, bypass a gate, weaken CODEOWNERS/counting/fixtures/security, force-push shared work, or promote unmerged compiler output. Required SDK CODEOWNER or compiler maintainer approvals remain real prerequisites. Distinguish approved, queued, and actually merged. Scope follow-up to the PRs/Deltas in this transition, preserve dependencies, and suppress unchanged status.

### Automatic advancement after merges

A confirmed merge must trigger the next eligible work during the same Conductor wake-up, without another user prompt. Advance each dependency independently; do not wait for every PR or Delta in a batch. An approval, green PR checks, or queue enrollment does not count as a merge. First verify the merge commit and its presence on the authoritative target branch.

| Confirmed merge | Required next action |
| --- | --- |
| Reporting cleanup #4113 | Measure actual SDK main against its verified snapshot, record the merged reduction, and choose the next ready track. Keep compiler-dependent work independent of this cleanup. |
| Upload compatibility tests #4112 | Start T8 typed upload delegation and runtime extraction, retaining all merged tests and existing signatures/defaults. Coordinate shared compiler binding work with T14. |
| Transition plan #4114 | Continue the recorded dependency graph; keep the ledger updated in subsequent focused PRs. Merging the plan is not a prerequisite for independent implementation. |
| Live queue compiler change | Verify the merged compiler revision and actual binary provenance, regenerate the affected SDK output, run Live/WebSocket contracts and the authoritative custom-code report, then publish the SDK reduction PR. |
| File-processing delegate compiler change | Verify the merged compiler and binary, regenerate the Files resource, rerun the 13 public file-processing contracts and typing/import checks, and publish its SDK reduction PR. Reuse the reviewed typed boundary for the next compatible helper. |
| Authored Realtime schema wording change | Regenerate from the merged input through the normal pipeline and publish the two-file documentation reduction, independently of compiler changes. |
| Any SDK reduction PR | Verify the merged behavior and actual remaining patch/file counts; mark the track complete only with evidence, then start the next ready tracks. |

Prefer T9 file/artifact delegates, T7 vector-store helpers, and T8 uploads after the shared typed helper boundary is reviewed and merged; pursue independent T1 compatibility, T11 Realtime, T13 embedding hooks and T15 alias work where their prerequisites permit. Preserve the richer audio, Chat, Responses, Assistants and client contracts before tackling those tracks. Derive readiness from actual reviewed compiler capabilities rather than forcing unrelated helpers into a polling-only abstraction.

On each merge, reconcile existing branches/PRs first to avoid duplicate work, refresh only affected dependencies, run the focused compatibility checks, and publish the next small PRs/Deltas. Record merge commits, measured reductions, active successors and exact tested heads in the ledger. Link successor compiler Deltas to this coordinating chat so Conductor can route their updates here. Parallelize independent file groups in isolated checkouts; serialize changes to shared compiler/configuration mechanisms when needed.

If one successor needs a human review, CI repair, or another merged prerequisite, record that blocker and continue unrelated ready tracks. T7/T8/T9 successors that change file uploads require explicit SDK CODEOWNER approval and focused synchronous/asynchronous security regression coverage as applicable before merge; a predecessor's approval or a green compiler change cannot substitute. Retain all required CODEOWNER, compliance, security, provenance and normal merge gates. Continue until the verified generated-owned tree reaches zero mixed files and zero patch lines; no developer-facing breaking changes are permitted.

## Execution ledger

| Work | State | Evidence / next action |
| --- | --- | --- |
| Baseline audit and plan | Published with this PR | 41 files / 7,368 patch lines at the pinned baseline; authoritative reporter, content hash, physical counts and track totals verified independently. |
| T0 generated reporting restoration | PR open; review/CI pending | [#4113](https://github.com/openai/openai-python/pull/4113), `886eb8079e65cfc0509fc945c17d7578b3459bfb`; 94 offline tests passed, one compiler-binary contract test skipped (binary unset); generated-byte/AST comparison and assertion mutation passed. Trusted local budget/isolation checks measured 39 files / 7,351 lines. |
| T8 upload helper contract coverage | PR open; review/CI pending | [#4112](https://github.com/openai/openai-python/pull/4112), `0e81c0e88c57cd5939b03779ccb10e6dda717c5b`; 16 sync/async tests, Ruff, targeted mypy and pinned Pyright pass; reversing part IDs failed six tests as expected. Initial CI typing findings repaired; current-head CI pending. Default 64 MiB boundary is not exercised by this slice. |
| T11 Live queue generation | Submitted for compiler review; CI pending | 679 Python renderer unit tests, six generated WebSocket runtime tests, Clippy and Ruff pass; independent review found no blockers. Raw parent comparison verified identical StainlessParity bytes across 21 files and unchanged OpenAI output for unconfigured resources. The complete published patch also passes the repository debug-code guard. Compiler review currently includes an explicit human compliance approval requirement; agents cannot satisfy it through a reviewer identity. Canonical monorepo CI, required reviews and compiler merge remain prerequisites for SDK promotion. |
| T1 authored schema documentation | Submitted for source review | Two authored description fixes; parsed schemas identical outside descriptions, exact intended substitutions and normal YAML/push checks pass. Potential reduction two files / four patch lines after verified regeneration. |
| T14 file-processing delegate | Submitted for compiler review; CI pending | Typed helper binding validated and submitted with normal push hooks enabled. 73 configuration and 679 renderer tests pass; raw parent comparison is byte-identical across 11 files. Generated methods retain AST/signature/doc/module/qualname/defaults/override/await behavior and pass all 13 existing public file-processing tests with the unchanged SDK runtime. Canonical monorepo CI and compiler merge remain required. |

The ledger reports observed work; projected reductions are not merged reductions. Refresh it with PR/Delta links and exact tested heads as publication completes.

### Initial environment note

The pinned main checkout failed local `uv lock --check` during setup. The committed dependencies were installed using `uv sync --frozen --all-extras --no-install-project`, without changing project metadata or the lockfile. Record focused test results separately; this local setup result is not a successful locked-policy validation and should not be repaired by an unrelated dependency update in a transition PR.
