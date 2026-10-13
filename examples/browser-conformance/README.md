# Installed browser helper conformance

This probe calls the public browser, computer, and Responses
runner entrypoints in an **installed** wheel. It uses synthetic data and an
in-process HTTP transport; it needs no API credential or browser dependency.
Each case asserts effects and replayed output, then writes a JSON receipt.

Run with an existing clean virtual environment that has the wheel installed.
Provide absolute paths to that environment, the wheel, this source checkout, and
the commit whose three helper sources match that package:

```sh
/path/to/consumer-env/bin/python -I -B \
  /path/to/checkout/examples/browser-conformance/consumer.py \
  --consumer /path/to/consumer-env \
  --archive /path/to/openai.whl \
  --source /path/to/checkout \
  --package-head 'FULL_COMMIT_SHA' > python-wheel.json
```

Both sync and async lanes run. Isolated Python must load `openai` from
`site-packages` within the supplied environment. The probe compares installed
helper hashes to the wheel, current source files, and the specified commit. It
exits nonzero on mismatch or any failed case. The receipt records these paths,
hashes, current source HEAD, the verified helper-source commit and every case ID.
It does not prove that all wheel files came from that commit. This verifies a
wheel only; it does not test source-distribution installation.

`vectors.json` is byte-identical to the Node SDK's conformance catalog.
It supplies member calls, invalid states and arguments, strict consent values,
entry policies and mixed tool wire items. `boundary_ids` names the shared checks
whose getter/callback mechanics are language-specific. The three normal mixed
modes and two interruption modes use each language's own synthetic transport.

Missing required policies reject at construction before any observation or action.
Removing a required policy after registration returns a controlled refusal with
harmless before/after state observations and no action. The other checks cover
snapshots across getters/awaits, refusal, cancellation, error redaction, and replay
of reasoning, browser images, ordinary function and native computer outputs.

These receipts verify the supplied installed wheel and runtime only. They do
not establish hosted CI, live API, real-browser, provider or competitor parity.

The 14 `ledger:*` cases also run through installed public Responses helpers
in both synchronous and asynchronous lanes. They check write-before-dispatch,
thrown/nested and partially returned effects, recorder failures (including a
lost acknowledgement), refusal of unresolved browser or eager calls, and
explicit generator `close()` / `aclose()`. A successful boundary case resumes
with original call IDs and multimodal output exactly once plus a fresh caller
observation, then rejects a stale revision in the caller's own save callback.
Native history, registration, per-request retry isolation and the saved
request budget are checked before more effects or HTTP. The recorder here is
an in-memory fixture. These cases do not prove durable storage, cross-process
locking, exactly-once provider effects, or semantic freshness of the caller
observation. Those guarantees require the caller's environment.

The seven `rich-read:*` cases check typed reports from read_page, find and
get_page_text: known-field projection, a final-state mutation, fatal malformed
output, large reports, text-only refs, and unchanged legacy JSON strings. The
six `selective:*` cases check mixed SSE order, result replacement after server-tool deferral, explicit empty vs omitted or
None timing policy, ordinary and native tools both named computer, pending
ledger refusal and changed completion. Only eligible pending ordinary output
can be supplied; previous effects are retained on failure.

The seven `budget:*` cases send native HTTP and SSE through the public runner.
They bound replay bytes and images, preserve the full ledger and require the
runner's own dropped-ID receipt even after the policy edits its snapshot.
Protected safety and latest screenshots, invalid choices, old-ID replay and
remaining request lifetime on fresh resume are checked before further effects.
The sync case cancels inside its policy callback; the async case holds that
callback and uses the persistent cancelled predicate before releasing it.

Each receipt lists the case IDs for its sync or async lane. These checks validate
SDK boundaries with synthetic drivers. They do not prove DOM privacy, remote
action identity or durable recording. Callbacks that suppress Python task
cancellation still need the runner's persistent `cancelled` predicate; these
cases do not claim to interrupt arbitrary user code.
