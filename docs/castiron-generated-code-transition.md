# Python generated-code transition

## Objective and non-negotiable contract

Eliminate handwritten patches in generated-owned files while preserving every existing developer-facing API and behavior. Handwritten runtime code remains a supported part of this SDK. Completion means the generated-owned tree matches a verified generation, with public extension wiring generated from authoritative compiler/configuration facts. Moving code to `lib/` while leaving handwritten imports, methods, or hooks in generated files is only an intermediate step.

No removals or renames of public symbols, new required arguments, narrower input/return types, dependency or Python-floor changes, altered defaults, new payload limits, changed warnings, or changed sync/async behavior are authorized by this transition. Deprecated methods and compatibility import paths remain supported.

## Current public baseline and measured final candidate — 2026-10-22

The released baseline `cfa0a79b6395bb0561b28879122a9f90a87cdada` (3.37.0) contains **41 mixed files / 7,409 custom patch lines** (4,890 additions and 2,519 deletions), spanning **39,960 physical lines**. Its public generated checkpoint is `992b9cbba312b4bf10128b9f1d36112b48340363`.

Candidate `b53d11fd9a9b337a6d7a3412f256dff64ea4d684`, generated from merged compiler `84f592da365c50862876c4dd63cef35eff88c45d`, measures **0 mixed files / 0 custom patch lines** against authentic checkpoint `f028b1b011d31cf0cd8a1939e83bf7ec5d2b8762`. Generation `592b2cad-c398-46a9-9df6-7858c09f3b65` has verified hash `2e485073ea1166bc85b3b8c04a512d221b82ef5c490801250ffc209d6292e201`. All **1,980 generated manifest entries** match checkpoint and candidate hashes and modes. All 41 formerly mixed files match generation; their measured combined physical size is **40,213 lines**, including comments and blanks. The strict report records 41 customizations removed and 31 generated baselines changed.

This is measured candidate evidence, **not public delivery**. [PR #4157](https://github.com/openai/openai-python/pull/4157) and subsequent authored default activation remain pending. Python ownership, exclusions, budget and counting definitions are unchanged. The Go ratchet remains inactive for Python.

Canonical documentation now retains all ten supported Videos/Assistants helper listings, including streaming returns, using typed helper metadata and correct relative links. The shared policy checker now evaluates effective next-policy changes and checker rollback when deciding authorization; it retains policy-only updates and required review protections. These generated checker changes do not change the Python policy bytes or ceiling.

Full SDK lint passed Ruff, Pyright, Mypy (2,064 files) and import checks. Focused runtime validation passed **337 tests with 2 skips**; both are expected creation-stream API-shape cases because those streams do not expose `until_done`. Follow-up drain and creation getter/iteration cases are exercised; the skips are not missing-dependency or environment failures. Merged-source reporting validation passed **220 tests with one existing compiler-contract skip**. The actual merged compiler passed **190 transform and 823 renderer tests**, and all **1,966 raw Python outputs** match the reviewed render. Hosted CI, required review, public delivery and default activation remain pending.

The released API status-error message fix and Agents result-schema warning fix are preserved exactly in all four changed files. The earlier released model/union-parsing fix, all five 3.37.0 release files and the two Decisions constructor/union declaration files also retain exact bytes and modes. Previous c551, b77 and e45 audit evidence remains historical; its validation is not substituted for this candidate's checks.

### Current baseline and candidate per-file inventory

Physical lines include comments and blanks. Added/deleted columns measure the
full canonical-to-integrated patch at each immutable commit, not PR attribution.

| File | Public physical | Public added | Public deleted | Candidate physical | Candidate patch |
| --- | ---: | ---: | ---: | ---: | ---: |
| `api.md` | 2094 | 126 | 8 | 2000 | 0 |
| `scripts/castiron/CUSTOM_CODE.md` | 217 | 0 | 40 | 279 | 0 |
| `scripts/castiron/custom_code_budget.py` | 702 | 1 | 4 | 769 | 0 |
| `scripts/castiron/custom_code_policy.py` | 481 | 1 | 4 | 530 | 0 |
| `scripts/castiron/custom_code_report.py` | 1250 | 19 | 254 | 1485 | 0 |
| `scripts/castiron/fixtures/github_publisher.cjs` | 69 | 10 | 63 | 122 | 0 |
| `scripts/castiron/test_custom_code_policy.py` | 587 | 0 | 4 | 720 | 0 |
| `scripts/castiron/test_custom_code_publication.py` | 873 | 4 | 600 | 1469 | 0 |
| `scripts/castiron/test_custom_code_report.py` | 1084 | 0 | 489 | 1573 | 0 |
| `src/openai/__init__.py` | 505 | 185 | 1 | 470 | 0 |
| `src/openai/_client.py` | 2440 | 759 | 60 | 1912 | 0 |
| `src/openai/resources/audio/transcriptions.py` | 1089 | 149 | 453 | 1061 | 0 |
| `src/openai/resources/audio/translations.py` | 374 | 21 | 46 | 360 | 0 |
| `src/openai/resources/beta/agents/environments/files.py` | 604 | 6 | 6 | 604 | 0 |
| `src/openai/resources/beta/agents/sessions/artifacts.py` | 573 | 2 | 2 | 573 | 0 |
| `src/openai/resources/beta/agents/sessions/sessions.py` | 1304 | 113 | 11 | 1271 | 0 |
| `src/openai/resources/beta/responses/responses.py` | 5575 | 55 | 55 | 5575 | 0 |
| `src/openai/resources/beta/threads/runs/runs.py` | 3161 | 1290 | 181 | 2889 | 0 |
| `src/openai/resources/beta/threads/threads.py` | 2009 | 390 | 7 | 1951 | 0 |
| `src/openai/resources/chat/completions/completions.py` | 3456 | 603 | 1 | 3363 | 0 |
| `src/openai/resources/conversations/api.md` | 42 | 1 | 0 | 41 | 0 |
| `src/openai/resources/embeddings.py` | 263 | 27 | 21 | 264 | 0 |
| `src/openai/resources/realtime/api.md` | 149 | 0 | 15 | 164 | 0 |
| `src/openai/resources/realtime/realtime.py` | 1660 | 9 | 3 | 1660 | 0 |
| `src/openai/resources/realtime/translations/translations.py` | 1152 | 34 | 18 | 1152 | 0 |
| `src/openai/resources/responses/api.md` | 208 | 2 | 0 | 208 | 0 |
| `src/openai/resources/responses/responses.py` | 5181 | 920 | 74 | 4866 | 0 |
| `src/openai/resources/uploads/uploads.py` | 652 | 6 | 28 | 674 | 0 |
| `src/openai/resources/webhooks/__init__.py` | 42 | 24 | 55 | 43 | 0 |
| `src/openai/resources/webhooks/webhooks.py` | 1146 | 89 | 4 | 1146 | 0 |
| `src/openai/types/__init__.py` | 157 | 4 | 1 | 157 | 0 |
| `src/openai/types/decision_input_image_param.py` | 47 | 11 | 1 | 47 | 0 |
| `src/openai/types/decision_input_message_param.py` | 95 | 6 | 1 | 95 | 0 |
| `src/openai/types/decision_input_text_param.py` | 33 | 11 | 1 | 33 | 0 |
| `src/openai/types/fine_tuning/fine_tuning_job_integration.py` | 5 | 0 | 2 | 5 | 0 |
| `src/openai/types/realtime/conversation_item_input_audio_transcription_delta_event.py` | 40 | 1 | 1 | 40 | 0 |
| `src/openai/types/realtime/realtime_error_event.py` | 25 | 1 | 1 | 25 | 0 |
| `src/openai/types/responses/tool_param.py` | 398 | 3 | 0 | 399 | 0 |
| `src/openai/types/webhooks/__init__.py` | 73 | 3 | 1 | 73 | 0 |
| `src/openai/types/webhooks/live_call_incoming_webhook_event.py` | 71 | 2 | 1 | 71 | 0 |
| `src/openai/types/webhooks/unwrap_webhook_event.py` | 74 | 2 | 2 | 74 | 0 |

### Current transition mechanisms — all 41 baseline files

This mapping covers the current cfa baseline exactly once per file. It replaces no
historical milestone: the older 27-file track table remains a dated snapshot.
All 41 files match generation in measured b53, including both released Decisions compatibility declarations. Merged compiler build, canonical regeneration and zero-patch verification are complete. Public delivery and authored default activation remain pending.

| Area and files | Compiler change and retained behavior |
| --- | --- |
| **Shared reporting and policy templates**<br>`scripts/castiron/CUSTOM_CODE.md`<br>`scripts/castiron/custom_code_budget.py`<br>`scripts/castiron/custom_code_policy.py`<br>`scripts/castiron/custom_code_report.py`<br>`scripts/castiron/fixtures/github_publisher.cjs`<br>`scripts/castiron/test_custom_code_policy.py`<br>`scripts/castiron/test_custom_code_publication.py`<br>`scripts/castiron/test_custom_code_report.py` | Regenerate the shared documentation, reporter, policy, publisher fixture and regression tests from canonical templates. Template fixes preserve pagination, large identifier handling, setup calls and strict typing. The shared Go ratchet remains opt-in; Python ownership, exclusions and budget are unchanged. Updated shared next-policy selection compares effective policy and checker ancestry; policy-only updates and required authorization remain enforced. Python policy bytes, ceiling, ownership and counting are unchanged. |
| **Client and package declarations**<br>`src/openai/_client.py`<br>`src/openai/__init__.py` | Typed client/package metadata generates signatures, imports, defaults, exports and delegation to handwritten authentication and module-runtime code. Explicit import scopes, binding validation and native member placement preserve original-module state, subclass dispatch, monkeypatching and sync/async behavior. |
| **Parsing and request facades**<br>`src/openai/resources/audio/transcriptions.py`<br>`src/openai/resources/audio/translations.py`<br>`src/openai/resources/chat/completions/completions.py`<br>`src/openai/resources/responses/responses.py` | Typed helper signatures, overloads, request context, parser bindings and stream factories generate public facades. Existing handwritten parsing and request implementations retain sentinel handling, payload construction, stream lifecycle and response types; generated wrappers do not duplicate that runtime logic. |
| **Assistants and Sessions facades**<br>`src/openai/resources/beta/threads/runs/runs.py`<br>`src/openai/resources/beta/threads/threads.py`<br>`src/openai/resources/beta/agents/sessions/sessions.py` | Typed resource helpers, positional request options, method ordering and deprecation metadata generate the existing public entry points. Handwritten Assistants and Sessions implementations retain polling, streaming, warning timing, tool dispatch and cleanup semantics. |
| **Previously released upload and file helpers**<br>`src/openai/resources/beta/agents/environments/files.py`<br>`src/openai/resources/beta/agents/sessions/artifacts.py`<br>`src/openai/resources/uploads/uploads.py` | Retain released helper and upload bindings in the composed configuration and regenerate their facades. Existing handwritten implementations continue to own file processing and uploads, including synchronous factories on async resources, subclass hooks, lazy defaults/logger timing and payload limits. |
| **Embedding parsing**<br>`src/openai/resources/embeddings.py` | The typed runtime hook delegates embedding response handling to the existing handwritten parser while retaining request defaults, encoding behavior and response transformation semantics. |
| **Realtime and legacy response connections**<br>`src/openai/resources/realtime/realtime.py`<br>`src/openai/resources/realtime/translations/translations.py`<br>`src/openai/resources/beta/responses/responses.py` | Typed WebSocket runtime bindings and event-method ordering generate connection facades. Existing transport code retains query composition, client properties, older-runtime fallback and sync/async behavior; the managed Beta projection keeps its released declaration order. |
| **Webhook runtime and compatibility exports**<br>`src/openai/resources/webhooks/__init__.py`<br>`src/openai/resources/webhooks/webhooks.py`<br>`src/openai/types/webhooks/__init__.py`<br>`src/openai/types/webhooks/live_call_incoming_webhook_event.py`<br>`src/openai/types/webhooks/unwrap_webhook_event.py` | Typed runtime bindings, package exports, compatibility aliases and deprecation annotations generate the wrappers and imports. Existing webhook verification remains handwritten; event import paths and deprecated class names remain available without changing verification behavior. |
| **Existing compatibility type declarations**<br>`src/openai/types/decision_input_image_param.py`<br>`src/openai/types/decision_input_text_param.py`<br>`src/openai/types/fine_tuning/fine_tuning_job_integration.py`<br>`src/openai/types/responses/tool_param.py` | Typed compatibility declarations retain PromptCacheBreakpoint, the established fine-tuning module export shape and ParseableToolParam union membership. Generate these declarations directly rather than preserving handwritten additions in generated type modules. |
| **Newly released Decisions constructor and union**<br>`src/openai/types/decision_input_message_param.py`<br>`src/openai/types/__init__.py` | Merged typed legacy TypedDict/union capability emits the released callable DecisionInputMessageParam subclass and separate DecisionInputMessageUnionParam export. Both generated modules are byte-identical to released public files; the two historical c551 residual patches are eliminated in b53. |
| **API documentation**<br>`api.md`<br>`src/openai/resources/conversations/api.md`<br>`src/openai/resources/realtime/api.md`<br>`src/openai/resources/responses/api.md` | Canonical documentation rendering combines typed helper signatures, compatibility facts and external-resource references with the released schema. Regeneration removes stale generated documentation edits while retaining the public helper and resource documentation surface. Merged rendering restores all ten supported Videos/Assistants helper listings directly from typed signatures, deduplicates existing entries and resolves standalone relative links. |
| **Realtime schema descriptions**<br>`src/openai/types/realtime/conversation_item_input_audio_transcription_delta_event.py`<br>`src/openai/types/realtime/realtime_error_event.py` | Propagate the authoritative schema wording through ordinary model rendering, eliminating stale description edits without changing fields, event types or runtime behavior. |

### Remaining delivery and activation sequence

1. Apply verified transition documentation, refresh final-head evidence and finish current-head hosted CI and normal required reviews.
2. Complete normal public promotion, recheck released main and use the protected public merge workflow.
3. Verify the public merge and post-merge CI before marking delivered true.
4. After verified public runtime delivery, activate authored defaults with additive composition, retained opt-ins/imports and Beta generator guards.

### Historical c551 audit against fa9 (before the e8 rebase)

The current measured public baseline is `e8a0fd28bbdc1699c97ff0f602b1af3dd378382d`:
**41 mixed files / 7,409 custom patch lines** (4,890 additions and 2,519 deletions),
containing **39,960 physical lines**. Its authentic public generated checkpoint is
`992b9cbba312b4bf10128b9f1d36112b48340363`, generation
`8e0b46e2-9f31-4393-9a7e-2be585d07efb`, with 1,980 manifest entries.
The strict public reporter verified recorded checkpoint hash and ancestry.
The earlier 27-file / 6,186-line audit at `7db9d884` remains historical; its counts
must not be used as the current public baseline after the newly released Decisions
and reporting changes.

[Release #4154](https://github.com/openai/openai-python/pull/4154) advanced public main
from fa9 to e8 with version 3.37.0 and its changelog only. The five changed files are
`.release-please-manifest.json`, `CHANGELOG.md`, `pyproject.toml`,
`src/openai/_version.py` and `uv.lock`; dependency resolution is unchanged.
Stats, API/config checkpoint and generated manifest are byte-identical. A fresh
strict public report confirms every mixed-file byte hash and all debt counts are
unchanged. The next ordinary rebase must retain these five released files; their
exact hashes and modes are recorded in the inventory.

The candidate below was measured against fa9 and has **not** been regenerated
against e8. Its prior checks do not verify the future release-baseline rebase.

The intermediate candidate `c5519111ba3b907ba226175f2401ec8b18c18fad` has
**2 mixed files / 12 custom patch lines** (10 additions and 2 deletions).
Its generated checkpoint is `da5d06c76d64ed28f1ec415c924323d16900cadc`, generation
`9c4bdbf4-d266-4211-a6ce-6e39bbee056d`, hash
`5dce7cd552b6d28818b7660de7c735877fd738f233f253a34f602cf8939a537b`.
All 1,980 generated manifest hashes/modes are authentic; 1,978 integrated entries
match. Thirty-nine formerly mixed files now match generation. These are candidate
measurements, **not a delivered reduction or a final zero result**. Public delivery
through [PR #4157](https://github.com/openai/openai-python/pull/4157) and subsequent
default configuration activation remain pending.

The residual files are `src/openai/types/decision_input_message_param.py` (6 added,
1 deleted) and `src/openai/types/__init__.py` (4 added, 1 deleted). They preserve the
released callable `DecisionInputMessageParam` TypedDict subclass and separate
`DecisionInputMessageUnionParam` export. Canonical typed compiler support must
retain both contracts; deleting these patches without equivalent generated output
would be a compatibility regression.

Local full SDK lint passed: Mypy checked 2,064 source files, and Pyright, Ruff and
import checks passed. The focused runtime suite passed 166 tests in 2.41 seconds.
These checks apply to c551; the future regenerated candidate requires fresh checks.
A 37-file released-content preservation ledger records 34 byte-identical files;
the three differences are generation stats, `api.md` and the generated manifest. Released
Decisions behavior and workflow updates remain retained; no test or policy bypass
is implied by regenerated manifest changes.


The following snapshots retain historical measurements, not current delivery claims.

## Historical 7db baseline and e320 candidate snapshot

[Public #4155](https://github.com/openai/openai-python/pull/4155) merged as
`7db9d884c33b0d5ef252e9a4b6e7ae0bbd217e5b`; its [post-merge CI](https://github.com/openai/openai-python/actions/runs/39730902045) passed.
The measured pre-transition baseline at that commit is **27 mixed files / 6,186 custom patch lines**
(4,979 additions and 1,207 deletions). These files contain 32,760 physical lines
versus 28,988 generated lines. This historical baseline and its per-file inventory
are retained for comparison with the consolidated transition.

The compiler capabilities are merged in Delta 2593695, following the merged helper/request foundation in Delta 2593282.

The measured private candidate at `e320019182d287cb7470500ab6a69bb95bd5ce54`
has an authoritative checkpoint report of **0 mixed files / 0 custom patch
lines**, removing all 27 remaining customizations. The generated checkpoint is
`9293fea304d8c31dc1b24e3d9970db82752819ff`; the custom patch is empty and all
1,972 generated manifest entries match. These are immutable candidate measurements
that precede public delivery through [PR #4157](https://github.com/openai/openai-python/pull/4157).

Normal regeneration from merged compiler `babbc1ed17987d1c6017b20236058550a2e37cec`
completed without conflicts, producing generation `489447d0-e0d6-455f-a82b-f7c6d8c41bbd`
and checkpoint content hash `5f1421c905f7f97582e04beddc7179ec77da6a8a69cf59656f2ed282e9345d49`.
The reporting-test fixes merged in Delta 2594557,
Delta 2594802 and
Delta 2595513.
The last removes two unused assignments while preserving their setup calls.
The compiler also adds `CreateChatCompletionRequestMessageParam`: it is the same
runtime union object as the existing `ChatCompletionMessageParam`, with identical
six members and ordering. Existing methods and type definitions remain unchanged
from the preceding candidate.

Full SDK lint passed, including Mypy over 2,056 files and Pyright. The focused
reporting/publication suite ran 102 tests in 68.186 seconds: 101 passed and one
existing compiler-contract test was skipped. Public delivery requires current-head
CI, review and protected merging; default configuration activation follows it.

### Measured candidate file inventory

These are physical lines, including comments and blanks, at candidate `e3200191`.
Every listed file is byte- and mode-identical to its authentic generated checkpoint.

| Former mixed file | Released patch lines | Candidate physical lines | Candidate patch lines |
| --- | ---: | ---: | ---: |
| `src/openai/resources/beta/threads/runs/runs.py` | 1,471 | 2,889 | 0 |
| `src/openai/resources/responses/responses.py` | 994 | 4,866 | 0 |
| `src/openai/resources/audio/transcriptions.py` | 888 | 1,061 | 0 |
| `src/openai/_client.py` | 819 | 1,912 | 0 |
| `src/openai/resources/chat/completions/completions.py` | 604 | 3,363 | 0 |
| `src/openai/resources/beta/threads/threads.py` | 397 | 1,951 | 0 |
| `src/openai/__init__.py` | 186 | 470 | 0 |
| `api.md` | 127 | 1,978 | 0 |
| `src/openai/resources/beta/agents/sessions/sessions.py` | 124 | 1,271 | 0 |
| `src/openai/resources/audio/translations.py` | 115 | 360 | 0 |
| `src/openai/resources/beta/responses/responses.py` | 110 | 5,575 | 0 |
| `src/openai/resources/webhooks/webhooks.py` | 93 | 1,146 | 0 |
| `src/openai/resources/webhooks/__init__.py` | 79 | 43 | 0 |
| `src/openai/resources/realtime/translations/translations.py` | 52 | 1,152 | 0 |
| `src/openai/resources/embeddings.py` | 48 | 264 | 0 |
| `src/openai/resources/realtime/api.md` | 20 | 164 | 0 |
| `src/openai/resources/realtime/realtime.py` | 12 | 1,660 | 0 |
| `src/openai/types/decision_input_image_param.py` | 12 | 47 | 0 |
| `src/openai/types/decision_input_text_param.py` | 12 | 33 | 0 |
| `src/openai/types/webhooks/__init__.py` | 4 | 73 | 0 |
| `src/openai/types/webhooks/unwrap_webhook_event.py` | 4 | 74 | 0 |
| `src/openai/types/responses/tool.py` | 3 | 398 | 0 |
| `src/openai/types/responses/tool_param.py` | 3 | 399 | 0 |
| `src/openai/types/webhooks/live_call_incoming_webhook_event.py` | 3 | 71 | 0 |
| `src/openai/types/fine_tuning/fine_tuning_job_integration.py` | 2 | 5 | 0 |
| `src/openai/types/realtime/conversation_item_input_audio_transcription_delta_event.py` | 2 | 40 | 0 |
| `src/openai/types/realtime/realtime_error_event.py` | 2 | 25 | 0 |

The 27 files total 31,290 physical lines. Strict manifest coverage is 1,972 entries;
the legacy reporter counts 1,971 paths because it excludes workflows and includes
the manifest itself. These are different ownership measurements, not conflicting
file counts. The nine handwritten runtime modules remain outside generated ownership.

The remaining work ships in **one consolidated SDK PR**. Compiler prerequisites
can be reviewed and merged independently. The parallel implementation lanes are:

| Area | Tracks | Mixed files | Patch lines | Compiler capability and handwritten boundary |
| --- | --- | ---: | ---: | --- |
| Client and package | T2 | 2 | 1,005 | Typed client/package declarations delegate lifecycle and routing behavior to handwritten runtime modules; preserve original-module state and lexical superclass dispatch. |
| Parsing and request hooks | T3, T5, T6, T13 | 6 | 2,759 | Typed helper signatures, overloads, factories, request context and stream classes; parsing and request behavior stay handwritten. |
| Assistants and Sessions | T4, T9 | 3 | 1,992 | Generated polling/streaming facades preserve method order, deprecation decorators and positional request options; existing helper bodies move to handwritten modules. |
| Types, transports and docs | T1, T11, T12, T16 | 16 | 430 | Typed compatibility declarations, import bindings, transport options and documentation references; existing security/transport implementations stay intact. |

Completion sequence:

1. Merge compiler capabilities through ordinary review and green CI, preserving
   unchanged output for configurations that do not opt in.
2. Build from merged compiler source. Preserve all 15 released migration settings
   and use authenticated authored configuration on a feature branch for the final
   SDK generation. Configuration composition must preserve loaded values and
   ordinary parser/source limits. Default activation follows runtime delivery.
3. Generate every facade, integrate handwritten runtime files, and run the normal
   formatter. Preserve signatures, overloads, raw docs, declaration order, exports,
   defaults, subclass/monkeypatch behavior, sync/async semantics and warnings.
4. Run relevant SDK behavior/security/streaming suites and both type checkers.
   Run the unchanged authoritative ownership/patch reporter against authentic
   checkpoints; require **zero mixed files and zero custom patch lines**, without
   changing ownership, exclusions or budgets. Record final per-file physical lines.
5. Request reviews for each required PR/Delta in #sdk-reviews, address all findings,
   pass current-head CI and protected merging, then verify public post-merge CI.

The implementation previews and compiler tests are development evidence. They do
not establish an additional delivered reduction; the final report and public
merge remain required. Machine-readable history and this plan are retained in
`docs/castiron-transition-inventory.json`.

### Prepared handwritten runtime boundary

The consolidated preview adds eight handwritten runtime modules and updates the
existing embeddings parser. They contain **3,427 physical lines** including blanks
and comments; this is implementation retained in handwritten ownership, not code
removed or a delivered mixed-file reduction. Refresh these counts after normal
final generation.

| Handwritten module | Physical lines | Change |
| --- | ---: | --- |
| `src/openai/lib/_assistants_runs.py` | 768 | New |
| `src/openai/lib/_assistants_threads.py` | 287 | New |
| `src/openai/lib/_chat_completion_resources.py` | 490 | New |
| `src/openai/lib/_client_auth.py` | 977 | New |
| `src/openai/lib/_module_runtime.py` | 120 | New |
| `src/openai/lib/_parsing/_embeddings.py` | 60 | Updated |
| `src/openai/lib/_request_context.py` | 13 | New |
| `src/openai/lib/_response_resources.py` | 643 | New |
| `src/openai/lib/beta/agents/_create.py` | 69 | New |

## Delivered integration — uploads, aliases and Live defaults

[#4152](https://github.com/openai/openai-python/pull/4152) merged through the normal public queue on 2026-10-22 as `a29dc3947aeccecc2e85d8fbad4d7c03b8af13e9`. This delivered **48 → 32 mixed files** and **9,173 → 6,845 custom patch lines**, a net reduction of **2,328**. Private #315 is closed as completed; its generation checkpoints are retained. The 16 files below match generation byte for byte and account for 1,838 previous patch lines; generated-baseline changes explain the difference from the net reduction.

| File now matching generation | Integrated = generated lines | Previous patch |
| --- | ---: | ---: |
| `scripts/castiron/custom_code_budget.py` | 702 | 61 |
| `scripts/castiron/custom_code_report.py` | 1250 | 206 |
| `scripts/castiron/fixtures/github_publisher.cjs` | 69 | 7 |
| `scripts/castiron/test_custom_code_budget.py` | 773 | 70 |
| `scripts/castiron/test_custom_code_github.py` | 978 | 31 |
| `scripts/castiron/test_custom_code_publication.py` | 873 | 27 |
| `scripts/castiron/test_custom_code_report.py` | 1084 | 621 |
| `src/openai/resources/beta/agents/environments/files.py` | 604 | 127 |
| `src/openai/resources/beta/agents/sessions/artifacts.py` | 573 | 10 |
| `src/openai/resources/beta/beta.py` | 266 | 21 |
| `src/openai/resources/live/forks.py` | 1460 | 141 |
| `src/openai/resources/live/live.py` | 1649 | 125 |
| `src/openai/resources/live/sideband.py` | 1427 | 159 |
| `src/openai/resources/uploads/uploads.py` | 652 | 221 |
| `src/openai/types/__init__.py` | 150 | 1 |
| `tests/api_resources/admin/organization/projects/test_api_keys.py` | 442 | 10 |

The released integration preserves upload factories, subclass dispatch, lazy defaults and logging, aliases, Live queue defaults, and current/older-runtime WebSocket behavior. Its validation included 1,606 runtime/client/security tests with 16 skips, 158 reporting tests with one skip, full lint/type checks and independent checkpoint/contract review. All review feedback was addressed before normal protected merge. [Main post-merge CI](https://github.com/openai/openai-python/actions/runs/39727147208) passed. Historical private-candidate evidence is retained under `delivered_integrations` in the JSON.

## Historical published baseline before polling — 2026-10-22

Released commit `a29dc3947aeccecc2e85d8fbad4d7c03b8af13e9` contains **32 mixed files; 5,632 additions + 1,213 deletions = 6,845 custom patch lines**, with **37,881 integrated versus 33,462 generated physical lines**. The public generated snapshot is `75ba2ba983afb0a8823fae82670c5323c0ee9908`, generation `9fa1f60f-3df4-4d35-8b22-19dbbb6c80fb`, content hash `f71f5997995e620542e459fbe3a23789b2fbacf139d5d0c805e79c456abd2f49`. The unchanged reporter verified real public checkpoint ancestry and the recorded hash with `--public --fetch --require-head-hash`; run from a clone whose origin is the public SDK, using this released SHA for both base and head to reproduce the inventory.

The snapshot owns 1,970 paths, including 1,797 source paths. Another 205 source paths / 35,731 physical lines remain outside generated ownership. The polling integration retained this ownership, the existing exclusions and the 10,000-line budget. Physical lines include comments and blanks; patch additions plus deletions are not a count of executable statements. The original October 19 audit below remains historical; `published_audit_history` retains this baseline and the previous 48-file audit; the historical audit records retain the later 27-file polling release; `current_audit` now records fa9.

### Historical per-file inventory before polling

| File | Integrated lines | Generated lines | Added | Deleted | Patch | Track |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `src/openai/resources/beta/threads/runs/runs.py` | 3161 | 2052 | 1290 | 181 | 1471 | T4 |
| `src/openai/resources/responses/responses.py` | 5181 | 4335 | 920 | 74 | 994 | T5 |
| `src/openai/resources/audio/transcriptions.py` | 1089 | 1403 | 287 | 601 | 888 | T3 |
| `src/openai/_client.py` | 2440 | 1741 | 759 | 60 | 819 | T2 |
| `src/openai/resources/chat/completions/completions.py` | 3456 | 2854 | 603 | 1 | 604 | T6 |
| `src/openai/resources/beta/threads/threads.py` | 2009 | 1626 | 390 | 7 | 397 | T4 |
| `src/openai/resources/vector_stores/file_batches.py` | 867 | 628 | 242 | 3 | 245 | T7 |
| `src/openai/resources/vector_stores/files.py` | 1032 | 813 | 220 | 1 | 221 | T7 |
| `src/openai/__init__.py` | 505 | 321 | 185 | 1 | 186 | T2 |
| `src/openai/resources/videos.py` | 1457 | 1306 | 153 | 2 | 155 | T10 |
| `api.md` | 2090 | 1979 | 119 | 8 | 127 | T16 |
| `src/openai/resources/beta/agents/sessions/sessions.py` | 1304 | 1202 | 113 | 11 | 124 | T9 |
| `src/openai/resources/audio/translations.py` | 374 | 409 | 40 | 75 | 115 | T3 |
| `src/openai/resources/beta/responses/responses.py` | 5575 | 5575 | 55 | 55 | 110 | T5 |
| `src/openai/resources/webhooks/webhooks.py` | 1146 | 1061 | 89 | 4 | 93 | T12 |
| `src/openai/resources/webhooks/__init__.py` | 42 | 73 | 24 | 55 | 79 | T12 |
| `src/openai/resources/realtime/translations/translations.py` | 1152 | 1136 | 34 | 18 | 52 | T11 |
| `src/openai/resources/embeddings.py` | 263 | 257 | 27 | 21 | 48 | T13 |
| `src/openai/resources/files.py` | 826 | 800 | 26 | 0 | 26 | T14 |
| `src/openai/resources/realtime/api.md` | 149 | 169 | 0 | 20 | 20 | T16 |
| `src/openai/resources/realtime/realtime.py` | 1660 | 1654 | 9 | 3 | 12 | T11 |
| `src/openai/types/decision_input_image_param.py` | 47 | 37 | 11 | 1 | 12 | T1 |
| `src/openai/types/decision_input_text_param.py` | 33 | 23 | 11 | 1 | 12 | T1 |
| `tests/api_resources/test_videos.py` | 939 | 927 | 12 | 0 | 12 | T10 |
| `src/openai/types/webhooks/__init__.py` | 73 | 71 | 3 | 1 | 4 | T1 |
| `src/openai/types/webhooks/unwrap_webhook_event.py` | 74 | 74 | 2 | 2 | 4 | T1 |
| `src/openai/types/responses/tool.py` | 398 | 399 | 1 | 2 | 3 | T1 |
| `src/openai/types/responses/tool_param.py` | 398 | 395 | 3 | 0 | 3 | T1 |
| `src/openai/types/webhooks/live_call_incoming_webhook_event.py` | 71 | 70 | 2 | 1 | 3 | T1 |
| `src/openai/types/fine_tuning/fine_tuning_job_integration.py` | 5 | 7 | 0 | 2 | 2 | T1 |
| `src/openai/types/realtime/conversation_item_input_audio_transcription_delta_event.py` | 40 | 40 | 1 | 1 | 2 | T1 |
| `src/openai/types/realtime/realtime_error_event.py` | 25 | 25 | 1 | 1 | 2 | T1 |

## Delivered polling integration — 2026-10-22

[Public #4155](https://github.com/openai/openai-python/pull/4155) delivered **32 → 27 mixed files** and **6,845 → 6,186 custom patch lines**, a further **659** reduction. Private #326 is closed as completed; its private checkpoint evidence below is retained. The 27 remaining files contain 4,979 additions + 1,207 deletions and 32,760 integrated versus 28,988 generated physical lines.

Evaluated code: `aaa793c62214fa0c1541581aff6b4235fe5b9d24`. Normal generation used merged compiler `6959b4685e426934700ebb40c159e382714c8542`, pure checkpoint `7e3f90acf16f400505edeff5eb14ebb11981975a`, configuration checkpoint `db11a1a29f20f388bf6443d8bf5666e492f94777`, generation `18a47a5c-822b-47f7-9e5e-afd9c57dc6f6`, and content hash `d0c03ec7e35a1c576cfc7197aa8a3bd4e2b5e240ad90621c86437967444e3ef8`. The unchanged reporter (SHA-256 `6b7cfda1f85426daaa2e4f6186e2d1b20ac638dadaa54be8142ecec89fefd880`) verifies the authentic private checkpoint ancestry and recorded hash.

Exactly seven authored polling configuration settings are added to the released configuration: Files retrieve; vector-store Files create/retrieve; vector-store FileBatches create/retrieve; and Videos create/retrieve. All eight predecessor settings remain intact. Removing these seven settings and collapsing the five endpoint-only shorthand maps reproduces the complete predecessor configuration. Raw and transformed API specifications, dependency files, release metadata, handwritten runtimes, client/translation code, ownership, exclusions and budgets remain unchanged.

The five files below now match the pure checkpoint exactly. Their 659 prior patch lines account for the full reduction; every remaining patch is unchanged.

| File now matching generation | Integrated = generated lines | Previous patch |
| --- | ---: | ---: |
| `src/openai/resources/files.py` | 826 | 26 |
| `src/openai/resources/vector_stores/file_batches.py` | 776 | 245 |
| `src/openai/resources/vector_stores/files.py` | 987 | 221 |
| `src/openai/resources/videos.py` | 1444 | 155 |
| `tests/api_resources/test_videos.py` | 939 | 12 |

Validation: **303 polling/runtime compatibility tests passed** across synchronous, asynchronous and Trio behavior; the normal lint script passed Ruff, Pyright (zero errors), Mypy (2,047 files) and import verification. All **112 public facade contracts** and **16 runtime exports** are retained. Independent review verified that the ten delegate runtime bodies match released method bodies after receiver/validator-alias normalization, every argument is forwarded unchanged, and all other method bodies (including video polling) remain unchanged. Deadlines, validation-before-side-effects, cancellation, upload ownership, concurrency, headers, deprecation warnings and terminal-state behavior remain covered.

Local dependency freshness checks fail on both the unchanged released predecessor and this candidate under the managed registry. Local checks use the exact committed dependency set installed with `uv sync --frozen --all-extras` and no re-resolution; registry security settings and lockfiles are retained. The public promotion subsequently passed its required reviews/checks and normal queue; post-merge CI passed. The independent audit did not replace those gates.

### Remaining released inventory

| File | Integrated lines | Generated lines | Added | Deleted | Patch | Track |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `src/openai/resources/beta/threads/runs/runs.py` | 3161 | 2052 | 1290 | 181 | 1471 | T4 |
| `src/openai/resources/responses/responses.py` | 5181 | 4335 | 920 | 74 | 994 | T5 |
| `src/openai/resources/audio/transcriptions.py` | 1089 | 1403 | 287 | 601 | 888 | T3 |
| `src/openai/_client.py` | 2440 | 1741 | 759 | 60 | 819 | T2 |
| `src/openai/resources/chat/completions/completions.py` | 3456 | 2854 | 603 | 1 | 604 | T6 |
| `src/openai/resources/beta/threads/threads.py` | 2009 | 1626 | 390 | 7 | 397 | T4 |
| `src/openai/__init__.py` | 505 | 321 | 185 | 1 | 186 | T2 |
| `api.md` | 2090 | 1979 | 119 | 8 | 127 | T16 |
| `src/openai/resources/beta/agents/sessions/sessions.py` | 1304 | 1202 | 113 | 11 | 124 | T9 |
| `src/openai/resources/audio/translations.py` | 374 | 409 | 40 | 75 | 115 | T3 |
| `src/openai/resources/beta/responses/responses.py` | 5575 | 5575 | 55 | 55 | 110 | T5 |
| `src/openai/resources/webhooks/webhooks.py` | 1146 | 1061 | 89 | 4 | 93 | T12 |
| `src/openai/resources/webhooks/__init__.py` | 42 | 73 | 24 | 55 | 79 | T12 |
| `src/openai/resources/realtime/translations/translations.py` | 1152 | 1136 | 34 | 18 | 52 | T11 |
| `src/openai/resources/embeddings.py` | 263 | 257 | 27 | 21 | 48 | T13 |
| `src/openai/resources/realtime/api.md` | 149 | 169 | 0 | 20 | 20 | T16 |
| `src/openai/resources/realtime/realtime.py` | 1660 | 1654 | 9 | 3 | 12 | T11 |
| `src/openai/types/decision_input_image_param.py` | 47 | 37 | 11 | 1 | 12 | T1 |
| `src/openai/types/decision_input_text_param.py` | 33 | 23 | 11 | 1 | 12 | T1 |
| `src/openai/types/webhooks/__init__.py` | 73 | 71 | 3 | 1 | 4 | T1 |
| `src/openai/types/webhooks/unwrap_webhook_event.py` | 74 | 74 | 2 | 2 | 4 | T1 |
| `src/openai/types/responses/tool.py` | 398 | 399 | 1 | 2 | 3 | T1 |
| `src/openai/types/responses/tool_param.py` | 398 | 395 | 3 | 0 | 3 | T1 |
| `src/openai/types/webhooks/live_call_incoming_webhook_event.py` | 71 | 70 | 2 | 1 | 3 | T1 |
| `src/openai/types/fine_tuning/fine_tuning_job_integration.py` | 5 | 7 | 0 | 2 | 2 | T1 |
| `src/openai/types/realtime/conversation_item_input_audio_transcription_delta_event.py` | 40 | 40 | 1 | 1 | 2 | T1 |
| `src/openai/types/realtime/realtime_error_event.py` | 25 | 25 | 1 | 1 | 2 | T1 |

Historical private-candidate evidence is retained under `delivered_integrations`; the public release is recorded under `current_audit` in [castiron-transition-inventory.json](castiron-transition-inventory.json). Reproduce the historical private evaluation from an internal SDK checkout containing that commit:

```sh
python3 -I scripts/castiron/custom_code_report.py report \
  --repo . \
  --base a29dc3947aeccecc2e85d8fbad4d7c03b8af13e9 \
  --head aaa793c62214fa0c1541581aff6b4235fe5b9d24 \
  --fetch --require-head-hash \
  --out /tmp/python-polling-candidate-report
```

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

Read `.castiron.stats.yml` at the inspected revision. Validate public snapshot generation metadata, snapshot-branch ancestry, and content hash through the existing reporter. For physical sizes, read each integrated/generated blob and use `len(blob.splitlines())`; do not count the entire SDK diff because it also contains handwritten-only files. Refresh `current_audit` after each promoted generation and record before/after measurements in its PR.

## Historical merged progress — 2026-10-19

[#4113](https://github.com/openai/openai-python/pull/4113) merged on 2026-10-19 at `9d12b565554c08bcee6287c0d8f671b8c97ed911`, verified on `origin/main`. Both reporting files matched the pinned generated snapshot byte for byte at that merge; it changed only those files. Conductor separately verified all post-merge push checks successful on this merge commit, including [run 39315896992](https://github.com/openai/openai-python/actions/runs/39315896992).

The post-merge report verifies **39 mixed files; 6,076 additions + 1,275 deletions = 7,351 patch lines**. This is a merged reduction of two files and 17 patch lines. The remaining mixed files contain 44,289 integrated lines versus 39,488 generated lines; all 39 customized blobs are unchanged from the original audit. The generated snapshot, generation ID and content hash remain unchanged. At that revision, the 10,000-line budget had 2,649 lines of headroom; no budget change is included.

The original inventory below remains the fixed 41-file audit at `5589146d`; the JSON inventory adds a separate `merged_progress` record rather than overwriting its baseline totals or per-file sizes. No compiler-dependent SDK reduction is claimed until its source has merged and its verified generation lands.

Local verification used the exact reporter source from main `9d12b565` (SHA-256 `157ed30ac9d54d20fe5f7e625dc8ee5958beb91cc7e30aaa97cfba8fb3e06e21`). Its duplex Git batch I/O stalled in this environment, so a local adapter supplied the same object-ID input through a temporary stdin file for `git cat-file --batch`. Source, returned Git bytes, snapshot ancestry/hash validation and counting logic were unchanged. This is local I/O-adapted evidence; trusted hosted CI remains authoritative.

Reproduce with the existing reporter using `--base 5589146d738e0c38758e117b8383a02c2e4e2ee7 --head 9d12b565554c08bcee6287c0d8f671b8c97ed911 --public --fetch --require-head-hash` and the same repository/output arguments shown above.

[#4114](https://github.com/openai/openai-python/pull/4114) also merged as `6a52987f2da5c3bc9b700a7094c0cf14fe7e78dc`, verified on main. It adds only the two handwritten plan/inventory documents, leaving the generated-owned tree and measured counts unchanged. Conductor separately verified post-merge push CI, CodeQL and release checks successful on that merge commit, including [run 39316813847](https://github.com/openai/openai-python/actions/runs/39316813847).

The confirmed T0 merge immediately started two independent successors: T10 handwritten video polling compatibility coverage and T15 compiler generation of the existing Beta resource aliases. Neither waits for the pending upload-test PR. Review requests and updates belong in root `#sdk-reviews` posts, deduplicated against existing requests.

## Complete file inventory (fixed baseline)

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
| T4 | Assistants threads/runs helpers | 2 | 1,868 | Generic delegated helpers, polling, stream managers, legacy method names | After helper declarations; batch the family, splitting if review complexity requires |
| T5 | Responses helpers and beta class layout | 2 | 1,104 | Generic parse/stream hooks, exact overloads, websocket class partitioning | Split main Responses and beta class layout |
| T6 | Chat parsing and streaming | 1 | 604 | Generic parse/stream declarations and request validation hooks | After shared helper representation |
| T7 | Vector store helpers | 2 | 466 | Generated typed delegates to polling/runtime helpers | Group files and batches with compatible polling consumers |
| T8 | Chunked uploads | 1 | 221 | Typed overloads/delegates and handwritten orchestration | Compatibility-test PR first; independent |
| T9 | Hosted Agents helpers | 3 | 261 | Typed delegates, output binding, custom event streams | Group files/artifacts with compatible upload work; sessions later |
| T10 | Video polling and generated tests | 2 | 243 | Generated helper declarations, deprecation-aware test emission | Compatibility coverage first; independent |
| T11 | Live and Realtime websocket contracts | 5 | 115 | Resource-specific queue default facts, constructor policy, translation/calls hooks | Preserve submitted Live work; batch compatible remaining WebSocket changes |
| T12 | Webhook facade and resource exports | 2 | 172 | Generated verification delegates; exact sync facade and wrapper identity | Maintainer/CODEOWNER review; independent |
| T13 | Embedding decoding hooks | 1 | 48 | Default parameter and post-parser generation facts | Independent; existing runtime remains handwritten |
| T14 | File processing helper | 1 | 26 | Generate exact wait_for_processing delegate | Small initial helper-declaration consumer |
| T15 | Beta compatibility aliases | 1 | 21 | Generated compatibility getters/lazy exports | Independent of helpers; preserve existing warning/decorator behavior |
| T16 | API reference documentation | 2 | 147 | Emit helper signatures and wrapper/type links from the same compiler facts | After each related helper; final docs cleanup |

## Compiler changes

The maintained compiler is `api/castiron` in the OpenAI monorepo; the standalone Castiron repository is archived. Do not implement compiler fixes in that archived checkout. Compiler paths below are design targets, not a claim that all capabilities are absent. Current OpenAI-profile generation already has some helper documentation, audio, native websocket, extended union, and lazy-export support, also present in the pinned snapshot; compare current merged output before adding a second mechanism. Helper-documentation and compatibility-export configuration already lives in `crates/castiron-oas-transform/src/config/{python_helper_docs.rs,python_compatibility.rs}`, with corresponding typed IR and renderer modules. Documentation facts alone do not generate runtime delegates.

### Typed extension declarations and delegates

Extend the compiler model with typed resource helper declarations: method name and placement, parameter/overload sources, generic return types, sync/async mode, delegate target, request preparation/post-parser hooks, specialized stream classes, and raw/streaming-wrapper exposure. Validate these facts and project them into the Python renderer. Use existing configuration/model mechanisms where they fit; do not accept arbitrary code injection, raw SDK-file snapshots, or path-specific source replacement as the extension API. Retained sync and async signatures must declare every local used by the typed request payload, path, validators and preparation hooks; reject omissions before emitting code. Resolve imports through exact generated or explicitly declared module/symbol pairs, deduplicate only proven re-exports, and check collisions against the globals actually emitted, including typed logger bindings.

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

`tests/lib/test_assistants.py` signature synchronization is necessary but insufficient. Include sync/async HTTP and stream-lifecycle contract tests before relocating helper implementations. Batch the runs/threads helper family when reviewable; split by contract or review complexity when needed.

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

### Batch size and publication policy

The user prefers larger, cohesive PRs to reduce review and merge overhead. The default unit is a complete shared capability with its related resource consumers. Aim for a few hundred authored lines, roughly 300–800 when the work fits naturally; this is a guide, not a new line limit. Exact generated output can be larger when per-file measurements and compatibility evidence make it reviewable.

Include focused contract/security tests, typing fixtures, relevant API-reference changes, and ledger updates with the implementation or SDK regeneration. Existing coverage PRs and submitted compiler Deltas remain valid prerequisites; preserve their current review progress. Future work should normally cover a related family instead of publishing one method, one resource, or one status update per PR.

| Next batch | Scope and boundary |
| --- | --- |
| Polling helpers | T14 Files, T10 Videos and T7 vector-store files/batches: extend the shared typed helper capability across compatible consumers, then regenerate and verify the family together. Preserve each resource's distinct deadlines, options, warnings and terminal-state behavior. |
| Upload helpers | T8 chunked uploads and T9 Hosted Agents files/artifacts: group compatible declarations, extraction and lifecycle coverage. Every affected SDK PR still needs explicit SDK CODEOWNER approval and applicable focused sync/async security regressions. Sessions keep their separate streaming/output contracts. |
| Compatibility and exports | T1 type/import compatibility and T15 Beta aliases: collect related ready compatibility output in a reviewed generation, preserving identities, wildcard exports, static typing and warning behavior. |
| WebSockets | T11 Live and Realtime: batch related constructor/queue/transport policy work where the compiler boundary fits; preserve resource-specific defaults and contracts. |
| Parsing and streaming | T3, T5, T6 and T13: implement shared typed hooks with complete consumer families and their tests; retain focused review boundaries for the richer audio, Chat and Responses contracts. |
| Webhooks, client and Assistants | Deliver each coherent facade/client/helper family with its full compatibility and security coverage. T16 reference changes accompany the corresponding generated features. |

Reconcile and reuse existing branches/Deltas before starting a batch. Implement independent families in parallel. Publish a coherent ready family while unrelated work is blocked; sibling reviews must not stall all progress. A compiler capability and its dependent SDK regeneration remain separate repository changes, and compiler source must merge before SDK output is promoted. Budget adjustments remain separate ratchet-only PRs. Larger batches do not relax zero-breaking-change, provenance, CODEOWNER, compliance, security, test or protected-merge gates.

### Dependency order

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

The user authorizes implementation, publication of independent PRs/Deltas, and automatic reactions to Conductor updates without repeated permission prompts. Current coordinating chat: `codex://threads/01a15fb8-0aab-7b52-9dc3-a7622ac190a8`; historical implementation chat: `codex://threads/6ad66292-b06c-8191-b9f2-baafa5fb801d`. Preserve the historical context when routing successor events. Each event is a wake-up: fetch current head, reviews/threads, CI and merge state before acting. Address actionable feedback, resolve narrow conflicts, rerun appropriate checks, and keep this ledger current. Deduplicate existing review requests.

Use ordinary review/check/queue controls; never approve through a human identity, bypass a gate, weaken CODEOWNERS/counting/fixtures/security, force-push shared work, or promote unmerged compiler output. Required SDK CODEOWNER or compiler maintainer approvals remain real prerequisites. Distinguish approved, queued, and actually merged. Scope follow-up to the PRs/Deltas in this transition, preserve dependencies, and suppress unchanged status.

### Automatic advancement after merges

A confirmed merge must trigger the next eligible work during the same Conductor wake-up, without another user prompt. Advance each dependency independently; do not wait for every PR or Delta in a batch. An approval, green PR checks, or queue enrollment does not count as a merge. First verify the merge commit and its presence on the authoritative target branch.

| Confirmed merge | Required next action |
| --- | --- |
| Reporting cleanup #4113 | Measure actual SDK main against its verified snapshot, record the merged reduction, and choose the next ready track. Keep compiler-dependent work independent of this cleanup. |
| Upload compatibility tests #4112 | Start T8 typed upload delegation and runtime extraction, retaining all merged tests and existing signatures/defaults. Coordinate shared compiler binding work with T14. |
| Transition plan #4114 | Continue the recorded dependency graph; keep the ledger updated in subsequent focused PRs. Merging the plan is not a prerequisite for independent implementation. |
| Live queue compiler change | Verify the merged compiler revision and actual binary provenance, regenerate the affected SDK output, run Live/WebSocket contracts and the authoritative custom-code report, then publish the SDK reduction PR. |
| File-processing delegate compiler change | Verify the merged compiler and binary, reuse/extend its reviewed typed boundary for eligible polling-family consumers, and publish a coherent ready SDK generation after all corresponding compiler inputs merge. Retain all 13 Files contracts plus each additional consumer's focused checks and typing/import coverage. |
| Authored Realtime schema wording change | Regenerate from the merged input through the normal pipeline and publish the two-file documentation reduction, independently of compiler changes. |
| Any SDK reduction PR | Verify the merged behavior and actual remaining patch/file counts; mark the track complete only with evidence, then start the next ready tracks. |

Prefer T9 file/artifact delegates, T7 vector-store helpers, and T8 uploads after the shared typed helper boundary is reviewed and merged; pursue independent T1 compatibility, T11 Realtime, T13 embedding hooks and T15 alias work where their prerequisites permit. Preserve the richer audio, Chat, Responses, Assistants and client contracts before tackling those tracks. Derive readiness from actual reviewed compiler capabilities rather than forcing unrelated helpers into a polling-only abstraction.

On each merge, reconcile existing branches/PRs first to avoid duplicate work, refresh only affected dependencies, run the focused compatibility checks, and publish the next coherent family batches under the publication policy above. Record merge commits, measured reductions, active successors and exact tested heads in the ledger with the related implementation or regeneration; batch routine status updates instead of creating a separate PR for each event. Link successor compiler Deltas to this coordinating chat so Conductor can route their updates here. Parallelize independent file groups in isolated checkouts; serialize changes to shared compiler/configuration mechanisms when needed.

If one successor needs a human review, CI repair, or another merged prerequisite, record that blocker and continue unrelated ready tracks. T7/T8/T9 successors that change file uploads require explicit SDK CODEOWNER approval and focused synchronous/asynchronous security regression coverage as applicable before merge; a predecessor's approval or a green compiler change cannot substitute. Retain all required CODEOWNER, compliance, security, provenance and normal merge gates. Continue until the verified generated-owned tree reaches zero mixed files and zero patch lines; no developer-facing breaking changes are permitted.

## Execution ledger

| Work | State | Evidence / next action |
| --- | --- | --- |
| Baseline audit and plan | Merged; post-merge checks green / complete | [#4114](https://github.com/openai/openai-python/pull/4114), head `7eea9bf1beb552f4db8c456105b6a28bfe9bebe3`, merged as `6a52987f2da5c3bc9b700a7094c0cf14fe7e78dc` on main. Frozen audit: 41 files / 7,368 patch lines at `5589146d`; current merged reduction recorded separately. Explicit current-head human approval and protected merge gates were satisfied. Post-merge push CI, CodeQL and release checks are green on the merge commit, including [run 39316813847](https://github.com/openai/openai-python/actions/runs/39316813847). |
| T0 generated reporting restoration | Original cleanup and renewed restoration merged | Original [#4113](https://github.com/openai/openai-python/pull/4113) remains historical. The renewed canonical reporting restoration is delivered in [#4152](https://github.com/openai/openai-python/pull/4152), merge a29dc394; all seven reporting files listed above match generation. |
| T8 upload helper contract coverage | Merged; successor eligible | [#4112](https://github.com/openai/openai-python/pull/4112) merged on 2026-10-19 as `163a2966140bc0399af7d81e03580d9d907a51df`. Preserve its 16 sync/async contracts in the typed upload-delegation successor. The default 64 MiB boundary remains an additional coverage requirement. This test-only merge does not reduce mixed-file counts or approve a later upload migration. |
| T10 video polling compatibility | Merged; successor eligible | [#4115](https://github.com/openai/openai-python/pull/4115) merged on 2026-10-19 as `969ae2c734a508ebc5e3370c9dc41bd15602a4a4`. Retain all 21 public-entrypoint sync/async contracts and the interval mutation evidence in the polling-family successor. This test-only merge does not reduce mixed-file counts. |
| T15 Beta resource alias generation | Compiler and SDK integration merged | Delta 2566635 merged as 509f49c1. [#4152](https://github.com/openai/openai-python/pull/4152) delivers the generated aliases, removing the 21-line Beta patch while preserving sync/async cached properties and collision guards. |
| T11 Live queue generation | Compiler and SDK integration merged | Delta 2565610 and [#4152](https://github.com/openai/openai-python/pull/4152) deliver generation for Live, forks and sideband, retaining byte limits, direct constructors and caller-owned empty queues. All three files match generation. |
| T1 authored schema documentation | Redundant candidate; merged source already present | Delta 2565621 duplicates the corrections already merged through Delta 1490194, commit `97ba353f886c5248912eb50a516cb1aab2fee4c6`. The duplicate is closed with supersession evidence. The generated/integrated SDK descriptions still differ at the current audit; verify input propagation and regenerate before claiming the two-file/four-line reduction. |
| T7 / T10 / T14 polling family | Compiler, runtime and public integration merged | Delta 2565776 and runtime [#4148](https://github.com/openai/openai-python/pull/4148) are merged. Private #326 applies exactly seven settings on released a29dc394; five files / 659 patch lines clear, 112 contracts and 16 exports remain, and 303 tests pass. [Public #4155](https://github.com/openai/openai-python/pull/4155) merged as `7db9d884`; post-merge CI passed. |
| T8 / T9 upload and agent facades | Compiler, runtime and SDK integration merged | Delta 2568634, runtime [#4146](https://github.com/openai/openai-python/pull/4146) and integration [#4152](https://github.com/openai/openai-python/pull/4152) are merged. Uploads, environment files and session artifacts match generation; synchronous factories on async resources, subclass dispatch, lazy defaults/logger timing, ordering, cleanup and the 64 MiB boundary remain covered. The separate sessions facade still has 124 patch lines. |
| T0 recurring reporting formatting | Canonical source and public integration merged | Deltas 2588691 and 2591310 fix shared-template formatting and preserve the requested unittest import style. [#4152](https://github.com/openai/openai-python/pull/4152) clears seven reporting files / 1,023 prior patch lines. Budget and exclusions are unchanged. |
| T11 client WebSocket query composition | Compiler fixes and public integration merged | Deltas 2589816 and 2590767 are delivered in [#4152](https://github.com/openai/openai-python/pull/4152). Released query semantics, runtime/subclass dispatch, older-runtime fallback, client properties and prepared translations remain verified. Client and translations files still have unrelated custom patches. |
| Earlier stable web-search naming | Superseded; stale candidate closed | Internal #55 closed after confirming merged Delta 2513050 and exact generated/integrated equality of both stable web-search modules on current main. Do not reintroduce its stale generation metadata or historical cross-language naming change. |
| Remaining compatibility imports | Compiler merged; post-merge CI passed | Delta2592476, merge `66acf710bd337b3a9be0b0ad3412d9083e57d9bc`; exact-merge master CI 8915304 passed. |
| Assistants deprecation ordering | Compiler merged | Delta2592631, merge `b0da3235c40a165713cbb742b28d5cbe67cb9e20`; CI and protected validation passed. The response-format overload review finding is fixed. |
| Remaining types/transport/docs bindings | Compiler merged; exact-merge post-CI passed | Delta2592815 merged as `5f5b122cf752c580d70ca3bcd106ffa99c01c799`; current CI, protected validation and exact-merge master CI8917738 passed. The inactive-template whitespace regression is fixed without fixture changes, and the ordinary master conflict is resolved. |
| Shared helper/request hooks | Compiler merged; post-merge CI passed | Delta 2593282 merged as `a7b49aa295d583a377fcea247591b4621efe7a8d`. Current-head CI, protected validation and post-merge CI 8919804 passed. Three unrelated soft failures remain documented; no policies or unrelated code were changed. |
| Client/package declarations | Merged; nine review findings resolved | Delta 2593695, head `4ae71419874d772688a49f0d6efc8279e1e744db`, preserves all 31 upstream package projections. Import/reference resolution, native/class bindings and early/late exports have passing regressions. All 813 renderer tests, library/test Clippy and both immutable parity cases pass; all 1,957 generated files are byte-identical to the validated preview. All nine formal threads are resolved and current-head review approved. Merged as `34e4caadc819f51b8267061485739b6481644593`; protected merge and validation passed. Exact-merge post-merge CI passed. |

The prepared consolidated preview has the following validation. Hosted checks and
review remain required on the published source and final SDK heads.

| Validation | Result and scope |
| --- | --- |
| Compiler | 813 renderer tests and unchanged-policy library/test Clippy pass. All 1,957 preview output files are unchanged; both selected immutable exact/extended parity cases pass on the current source. |
| SDK declarations | 687 contracts preserved: 273 parsing/resource, 168 Assistants/Sessions and 246 client/package. |
| Normal SDK lint | Ruff, Pyright, Mypy across 2,055 source files, and import verification pass. |
| Package build | Local canonical locked build is blocked by managed-registry/lock-source mismatch on unchanged baseline metadata. Final hosted build and wheel checks on Python 3.10/3.14, including isolated legacy HTTPX compatibility, remain required. |
| Client behavior | 605 pass, two skipped; client Mypy also passes. |
| Resource/runtime behavior | 1,796 pass, 15 skipped; the latest three-file Audio/Responses change passes 1,194 affected tests. These runs overlap and must not be added together. |
| Large payloads and transport | 106 pass sequentially, including >32 MiB JSON/structured streaming, >64 MiB SSE, gzip, cleanup and cancellation; fixtures and limits unchanged. The 34 legacy HTTPX cases skip because the optional dependency/lane is absent locally. Hosted legacy compatibility coverage remains required. |
| Structural compatibility | All 14 compatibility module ASTs (79 classes/188 methods) match the release; four transport/security files are byte-identical. |
| Annotation bindings | 424 bindings and seven generic variables accounted for, including bindings checked on their moved runtime owner. |

The ledger reports observed work; projected reductions are not merged reductions. Refresh it with PR/Delta links and exact tested heads as publication completes.

### Initial environment note

The pinned main checkout failed local `uv lock --check` during setup. The same failure occurs in the final preview: the managed package index differs from the registry recorded in the unchanged lockfile, so canonical `uv export --locked` rejects it despite byte-identical released project/lock metadata. The committed dependencies were installed using `uv sync --frozen --all-extras --no-install-project`, without changing project metadata or the lockfile. Record focused test results separately; this local setup result is not a successful locked-policy validation and should not be repaired by an unrelated dependency update in a transition PR.
