# Browser and mixed Responses tools

`BrowserToolset` turns a supplied driver's methods into Responses function tools.
It does not add a native browser tool type to the Responses API. The model
must support function tools. Screenshots are sent as native `input_image`
parts in `function_call_output`, with an `input_text` state report.
The SDK does not install a browser, access browser profiles, or manage a
driver's session. See [the read-only quickstart](../examples/browser/README_read_only.md)
for a local Playwright reader, or [Fieldwork](../examples/browser-use-demo/README.md)
for an owned reservation form.

## Start with an async driver

Use Python 3.10 or later. Create an environment and install the SDK and
Playwright:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install openai playwright==1.63.0
.venv/bin/python -m playwright install chromium
```

On Linux, if bundled Chromium cannot start with its sandbox enabled, select
a locally installed Chrome before running the quickstart:

```sh
export OPENAI_EXAMPLE_BROWSER_CHANNEL=chrome
```

Leave the variable unset to use Playwright's bundled Chromium. Both choices
keep the browser sandbox enabled.

On Windows, use `.venv\Scripts\python.exe` in place of `.venv/bin/python`.
Set `OPENAI_API_KEY` and `OPENAI_MODEL` in your shell. Use a model available
to your project that supports Responses function tools. Save this as
`reader.py`, then run `.venv/bin/python reader.py`:

```python
import asyncio
import os

from openai import AsyncOpenAI
from openai.lib.browser import (
    AsyncBrowserToolset,
    BrowserError,
    BrowserState,
    TabInput,
)
from openai.lib.responses_tool_runner import AsyncResponsesToolRunner
from playwright.async_api import Page, async_playwright


class Reader:
    def __init__(self, page: Page) -> None:
        self.page = page

    async def state(self) -> BrowserState:
        return {"tabs": [{"id": "one", "url": self.page.url, "title": await self.page.title(), "active": True}]}

    async def get_page_text(self, args: TabInput) -> str:
        if args["tab_id"] not in (None, "one"):
            raise BrowserError("Unknown tab.")
        return await self.page.locator("body").inner_text()


async def main() -> None:
    channel = os.environ.get("OPENAI_EXAMPLE_BROWSER_CHANNEL")
    if channel not in (None, "chrome"):
        raise ValueError("OPENAI_EXAMPLE_BROWSER_CHANNEL must be unset or chrome.")
    async with async_playwright() as playwright, AsyncOpenAI() as client:
        session = await playwright.chromium.launch(
            channel=channel, chromium_sandbox=True, env={"PATH": os.environ["PATH"]}
        )
        try:
            page = await session.new_page()
            await page.set_content("<title>Cafe</title><p>Cafe hours: 08:00-16:00.</p>")
            browser = AsyncBrowserToolset(Reader(page), members=["get_page_text"])
            response = await AsyncResponsesToolRunner(browser=browser).run(
                client,
                {
                    "model": os.environ["OPENAI_MODEL"],
                    "input": "Read the page and tell me when the cafe closes.",
                    "store": False,
                },
                max_steps=3,
            )
            print(response.output_text)
        finally:
            await session.close()


asyncio.run(main())
```

The answer should say that the cafe closes at 16:00. This example sends
current text from a real, isolated browser page. The driver rejects unknown
tabs; it exposes no writes and needs no approval callback. Replace the sample
page with a page your app controls and grant only the reads your task needs.
Keep the isolated session and its cleanup in your application.

The synchronous equivalents are `BrowserToolset` and `ResponsesToolRunner`.
Use synchronous driver methods and callbacks with them. For a custom loop,
send `browser.tools` in a Responses request. Pass each returned browser
function call to `browser.execute(call)`. Async callers await `execute`.

## Driver contract

Create drivers and approval callbacks in trusted application code. Keep executable configuration
separate from untrusted page data, and return page data through the declared driver report fields.

Tab state reports HTTP and HTTPS origins, such as `https://example.com:8443`, without credentials,
paths, queries, or fragments. Legacy state (without observation metadata) preserves `about:blank`
and reports only the scheme for other URLs, such as `data:` or `file:`. Its 2048-byte UTF-8 limit
applies to the reported value, so a long page path does not prevent a state read.
State with observation metadata accepts only HTTP(S) URLs or `about:blank` and displays HTTP(S) origins.
It truncates titles to 1,024 UTF-8 bytes at a character boundary and sets `title_truncated` when needed.
The SDK does not impose a tab-count limit, with or without observation metadata. Individual
drivers may set their own limits. Titles and page content still need your application's privacy policy.

A driver must implement `state() -> BrowserState`. State contains `tabs`
with string `id`, `title`, and `url`, and Boolean `active`. IDs must be
unique. When tabs exist, exactly one must be active. By default, the SDK provides
`browser_list_tabs` from state. It registers only the following named methods
that the driver implements:

| Driver method | Typed argument | Result |
| --- | --- | --- |
| `navigate` | `NavigateInput`: url, tab_id | string or None |
| `read_page` | `ReadPageInput`: filter ("all" or "interactive"), tab_id | string, BrowserReadV1 or None |
| `get_page_text` | `TabInput`: tab_id | string, BrowserReadV1 or None |
| `find` | `FindInput`: query, tab_id | string, BrowserReadV1 or None |
| `click`, `hover`, `scroll_to` | `ClickInput`: target, tab_id | string or None |
| `type` | `TypeInput`: target, text, tab_id | string or None |
| `key` | `KeyInput`: keys (list of strings), tab_id | string or None |
| `scroll` | `ScrollInput`: direction, amount, tab_id | string or None |
| `wait_for` | `WaitForInput`: text, timeout_ms, tab_id | string or None |
| `select_option` | `SelectOptionInput`: target, values (list of strings), tab_id | string or None |
| `screenshot` | `TabInput`: tab_id | Responses `input_image` dict |
| `zoom` | `ZoomInput`: tab_id, region | Responses `input_image` dict |
| `new_tab` | `NewTabInput`: url | string or None |
| `switch_tab`, `close_tab` | `TabInput`: tab_id | string or None |

All fields are required in tool calls. Most `tab_id` fields accept null for
the active tab; `switch_tab` and `close_tab` require a string. A null new-tab
URL means a blank page. A screenshot must have at least one nonempty
`image_url` or `file_id` and may specify `detail`. Both sources may be present;
every supplied source must be valid.
Screenshots and zoom images permit only `type`, `image_url`, `file_id`,
`detail`, and the native optional `prompt_cache_breakpoint={"mode": "explicit"}`.
The helper validates and copies the breakpoint before reading final state.
`detail` may be omitted or None, or set to `auto`, `low`, `high`, or `original`.
The optional `zoom` method receives `[left, top, right, bottom]` as four
nonnegative safe integers with positive width and height. The driver checks
viewport bounds and owns cropping. Coordinates after a crop still refer to the
original full screenshot. Zoom is a read; it grants no pointer permission. The
SDK validates and copies its image before calling the final state callback.
Drivers define the meaning and lifetime of target IDs in page reads.
Make IDs stable for the current page and reject stale IDs explicitly.

`scroll_to` requires confirmation. `wait_for` is a read; its text must be
nonempty and at most 256 UTF-8 bytes after whitespace normalization. The
timeout is an integer from 1 through 30000 milliseconds. Every browser driver method,
including `state`, navigation, reads, input, and opt-in methods, may declare
an optional keyword-only `cancelled` parameter. Ordinary function executors may do the same.
The SDK passes the caller's predicate only when a method declares it; existing methods
without that parameter still work. Check it before effects and keep it true after a stop
request. Use it to stop I/O promptly where the underlying library permits.
See [navigation and waits](browser-navigation.md) for the cancellation
contract and owned example.

Pass `members=["read_page", "get_page_text", "screenshot"]` to expose only selected
methods from a full driver. Names must be unique fixed members implemented by that
driver; `list_tabs` needs only `state()`. An empty list exposes no methods. The SDK
copies the selection at construction and keeps its fixed tool order. Confirmation
and URL policy are required only for selected methods. Explicitly disabled calls
raise `BrowserError` before state reads or consent. Omitting `members` preserves
the default behavior, including `list_tabs`. Disabling `list_tabs` does not hide
state returned by other successful operations.

Use `additional_members=["read_page_scoped", "hover_at"]` to add named optional
methods to the defaults this driver actually implements. Those additions must
exist. Do not pass `members` and `additional_members` together. Both selections
keep the fixed SDK order. `DEFAULT_BROWSER_MEMBERS` and `BROWSER_MEMBERS` are
exported immutable tuples of default and all fixed names. They describe the SDK
vocabulary, not a particular driver's capabilities.

For type checking, use `BrowserDriver` for a minimal state-only driver.
`BrowserReadDriver`, `BrowserNavigationDriver`, `BrowserClickDriver`, and
`BrowserScreenshotDriver` add the named capability. Async variants use the
`Async` prefix. Drivers need not inherit them: structural implementations work.
Use an async toolset with async driver methods and sync with sync. The constructor
rejects a known mismatch for a selected method. Unannotated wrappers may be
ambiguous; the SDK checks their result when it executes the method.

## Opt in to scoped reads and pointer input

These fixed members stay off by default, even when a driver implements them.
Use `additional_members` to keep available defaults, or `members` to choose the
complete set. A scoped reader can use `additional_members=["read_page_scoped"]`.
A pointer driver can use `members=["screenshot", "click_at", "drag_path", "hold_keys"]`
and must pass `confirm`.

| Method | Typed argument fields | Result |
| --- | --- | --- |
| `click_at` | `ClickAtInput`: tab_id, x, y, button, click_count, keys | string or None |
| `hover_at` | `HoverAtInput`: tab_id, x, y | string or None |
| `set_checked` | `SetCheckedInput`: tab_id, target, checked (Boolean) | string or None |
| `drag_path` | `DragPathInput`: tab_id, path, keys | string or None |
| `hold_keys` | `HoldKeysInput`: tab_id, keys, duration_ms | string or None |
| `read_page_scoped` | `ReadPageScopedInput`: tab_id, root, depth, filter | `BrowserScopedReadV1` |

All fields are required; `tab_id=None` means the active tab. Extra properties are
rejected, including extra fields on a path point. Coordinates are nonnegative safe
integers in the full CSS viewport. They still use the full viewport after zooming; the
driver checks current bounds. `click_at` takes `left`, `right`, or `middle` as its
`button`, and 1, 2, or 3 as `click_count`. A `drag_path` has 2 through 100 exact
`{"x": x, "y": y}` points. On these methods, `keys` is a unique list of `Control`,
`Alt`, `Meta`, or `Shift` modifiers. An empty list is valid.

`hold_keys` takes 1 through 8 unique nonempty key names of at most 64 UTF-8 bytes each
and `duration_ms` from 1 through 3000. Key names must contain valid Unicode scalar values.
All numbers must be finite safe integers; booleans are rejected. The three mutators require
`confirm` returning exactly `True` before execution. They also receive the per-call
`cancelled` predicate as a keyword argument. This leaves existing method signatures
unchanged. Use synchronous methods and callbacks with `BrowserToolset`; use asynchronous
methods and callbacks with `AsyncBrowserToolset`.

`read_page_scoped` is a read and needs no confirmation. A `None` root discovers visible
sections; a string root is a driver-issued scope ref, never a selector. It must be nonempty,
at most 256 UTF-8 bytes and valid Unicode. `depth` is from 1 through 32; `filter` is
`all` or `interactive`. DOM depth within the selected root has its own counter, separate
from frame and shadow limits.

Return a `BrowserScopedReadV1` dictionary, exported from `openai.lib.browser`. It has
the existing `version`, `text`, `elements`, and `omitted` fields plus `scopes`, a list
of `{"ref": ..., "label": ...}` entries. The SDK imposes no fixed scope count. Each ref
and label must be nonempty, valid Unicode and at most 256 UTF-8 bytes. Scope refs must be
unique and cannot equal any element ref. The whole projected report, including scopes,
has no SDK byte limit. This method rejects string and `None` results. The SDK
copies known fields before the final state callback. The original `BrowserReadV1` report
and its seven action roles remain unchanged.

Scope refs can select a read root, but cannot authorize an element mutation. Give them the
same tab, document, generation and visibility invalidation as element refs. Element actions
must reject scope refs. Keep field privacy and work limits in the driver.

## Opt in to diagnostics, scripts, and file transfers

These four methods also stay off by default. Select each one in `members` and
provide `confirm`, including for diagnostic reads. A driver's implementation alone
does not expose them to the model.

| Method | Required arguments | Result |
| --- | --- | --- |
| `read_diagnostics` | `tab_id`, `source`, `limit` | `BrowserReadV1` with no elements |
| `run_script` | `tab_id`, `source`, `timeout_ms` | Text |
| `upload_file` | `grant_id` | `BrowserFileOutcome` |
| `download_file` | `grant_id` | `BrowserFileOutcome` |

For `read_diagnostics`, choose `console` or `network` as the source and a limit
from 1 through 100. Return a structured read with an empty `elements` array.
The driver must filter private data and bound its history. Do not return raw
headers, cookies, credentials, or unfiltered console messages.

`run_script` takes nonempty source containing valid Unicode and a timeout
from 1 through 30000 milliseconds. The SDK preserves the full source.
Return text containing valid Unicode.
An empty string is valid; a null result is not. The SDK preserves large results.
Scripts run with the page's privileges. Use a fresh session without
credentials, restrict its network access, and retire it if execution becomes
uncertain. Stopping the local waiter does not prove that a page script stopped.

File methods accept only a caller-issued `grant_id`: nonempty, valid Unicode,
and at most 256 UTF-8 bytes. The grant identifies one approved, task-scoped file;
it is not a path or URL. The file owner must get separate file approval. It must recheck expiry and
ownership, enforce size limits, and permit the grant only once. Browser confirmation does not replace this file approval.

Return exactly `version`, `status`, `effect`, and `cleanup`. Set `version` to 1.
`cleanup` is `not_started`, `pending`, or `completed`. The valid status/effect
pairs are:

| `status` | `effect` |
| --- | --- |
| `completed` | `completed` |
| `refused` | `none` |
| `unknown` | `unknown` |
| `interrupted` | `none` or `unknown` |

The SDK copies and validates this result before asking for final browser state.
Only `completed` sets the tool output's `ok` to true. Other outcomes retain the
structured result with `ok` false, so the runner skips dependent browser calls in
that response. Check the actual file and application state before retrying an
unknown transfer. A file result does not prove that a later form submission or
business action succeeded.

`run_script`, `upload_file`, `download_file`, and diagnostic reads may declare
the same `cancelled` keyword as other browser methods. Python exports `RunScriptInput`,
`ReadDiagnosticsInput`, `BrowserFileInput`, and `BrowserFileOutcome`.

## Return a structured page read

The three read methods may return a `BrowserReadV1` dictionary:

```python
from openai.lib.browser import BrowserReadV1

read: BrowserReadV1 = {
    "version": 1,
    "text": "Dispatch queue",
    "elements": [{"ref": "current-button", "role": "button", "label": "Dispatch BP-1207"}],
    "omitted": ["value"],
}
```

Each element has a unique `ref`, a nonempty label, and one of these roles:
`button`, `textbox`, `combobox`, `checkbox`, `radio`, `slider`, or `listbox`.
Optional `value` and `options: [{"label": ..., "value": ...}]`
contain only data the driver permits the model to see. `get_page_text` must
return an empty `elements` list. The SDK does not parse strings as structured reads.
A `None` result supplies only the updated browser state. Return an empty string
when the read completes with no text.
Checkbox and radio elements may report Boolean `checked`; listbox options
may report Boolean `selected`. The SDK omits those fields on other roles.
See [native browser forms](browser-forms.md) for driver field requirements.

The SDK copies known fields before reading final state. It rejects invalid
reports and stops the run. Unknown fields are omitted without being read.
Refs and labels have a 256-byte limit; values have a 512-byte limit.
The SDK does not limit the number of elements or options, page text size,
or complete report size. Text must contain valid Unicode scalar
values. Omission codes must be unique members of the `BrowserReadV1` type;
use them to report incomplete coverage.

The driver owns visibility, field privacy and ref validity. Size checks do not
make arbitrary page data safe. Limit driver work to the document and fields
your application permits, and report incomplete coverage in `omitted`.
Fieldwork implements only its own fixed reservation page; it does not claim
general browsing, arbitrary DOM filtering, or frame and shadow-root support.

## Confirmation, navigation, and recovery

If a driver implements a method that can change state, construction requires
`confirm(ctx)`. This includes clicks, typing, keyboard actions, scroll,
selection, hover, tab changes, and navigation. Navigation or new-tab methods
also require `url_policy(ctx, url)`. Both callbacks must return exactly
`True` to proceed. Async toolsets require async callbacks.
Both callbacks, including confirmations for `confirm_reads`, may declare an
optional `cancelled` keyword parameter. The helper passes the current
cancellation probe only when the callback declares it, so existing callback
signatures still work. Interactive approvals can check the probe and return
promptly. The toolset remains busy until a running callback returns or raises.
The SDK asks for confirmation before state-changing methods. By default,
read-only methods do not call `confirm`. To protect selected reads, also pass
`confirm_reads=["list_tabs", "get_page_text", "screenshot"]`. Include only reads
registered by this toolset.

With `confirm_reads`, the callback can receive `BrowserReadConfirmContext`.
Its `phase` is `"before_read"` and `state` is None: the SDK has not read a URL,
title, tab list, or page yet. It also contains the original `call_id`, `member`,
and validated `arguments`. Refusal or a policy failure returns fixed text and
no state. A protected read skipped after an earlier failure has the same result;
it never calls the policy or driver.

For other operations, `BrowserConfirmContext` contains `call_id`, `member`,
`arguments`, and a copy of the current `state`. The callback for a toolset with
`confirm_reads` accepts the union of the two context types.
Changes to callback arguments cannot change the dispatched action. The URL
policy checks requested URLs before confirmation. The driver must enforce
which domains a browser can reach. It must handle redirects, links, popups,
subresources, downloads, and credential isolation. Treat page content
as untrusted; do not grant permission merely because the page asks.

`confirm` approves the fixed action arguments. Its `state` is a prior observation, not a lock
on the document or focused control. A page can navigate or change focus while a person decides.
For consent tied to a specific page or control, the driver must check the original target at execution.
Disable `key` and refuse `type` with a `None` target in that flow; both use current focus.
Apply equivalent target binding to other actions that depend on the current browser state.


For an expected, safe-to-share failure, a driver may raise
`BrowserError("Element no longer exists.")`. Choose that message yourself;
do not pass exception text or page contents into `BrowserError`. Other
driver exceptions produce a fixed error message. Invalid state reports stop
the run instead of sending a possibly inconsistent state to the model.
A recoverable browser failure returns `ok: false` and current state. The
runner returns a skipped output for later browser calls in that response.
It still executes unrelated registered functions and can recover next turn.

## Mix browser, computer, and ordinary functions

Register a normal function with its Responses function schema and an executor:

```python
from openai.lib.responses_tool_runner import (
    AsyncRegisteredFunction,
    AsyncResponsesToolRunner,
)


async def lookup(args: dict[str, object]) -> str:
    return str(args["reference"])


registered = AsyncRegisteredFunction(
    tool={
        "type": "function",
        "name": "lookup",
        "description": "Look up a reference",
        "parameters": {
            "type": "object",
            "properties": {"reference": {"type": "string"}},
            "required": ["reference"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    execute=lookup,
)
# Pass your existing AsyncComputerToolset and AsyncBrowserToolset:
runner = AsyncResponsesToolRunner(browser=browser, computer=computer, functions=[registered])
```

Executors receive the decoded JSON object. They return a string or a Responses
function-output content list. Function names must be unique and must not
match an enabled browser tool. Names may start with `browser_`. The runner
rejects calls without an executor.

The runner preserves `tool_choice` for every request. It rejects a choice that
always requires a local tool because that run cannot finish. This includes a
specific function or computer choice, `required` when all declared tools are
local, and `allowed_tools` with `mode: "required"` when every allowed tool is
local. Use `auto`, or use `responses.create` for a single forced request.
Required choices that also permit a declared server tool remain supported.

If you already have a Pydantic Responses tool, register its parser and an
explicit typed callback:
```python
from pydantic import BaseModel
from openai import pydantic_responses_function_tool
from openai.lib.responses_tool_runner import AsyncRegisteredFunction


class Lookup(BaseModel):
    reference: str


async def lookup(args: Lookup) -> str:
    return args.reference


registered = AsyncRegisteredFunction.from_tool(
    pydantic_responses_function_tool(Lookup),
    execute=lookup,
)
```
Use the existing SDK Responses Pydantic wrapper, as returned by
`openai.pydantic_responses_function_tool`; `from_tool` validates and parses before
execution. Its sync twin is `RegisteredFunction.from_tool`.
Malformed arguments never call your executor. Typed outputs must be a string
or a valid Responses function-output content list.

`params.tools` also accepts web search, file search, code interpreter, image
generation, and MCP declarations, or one computer declaration for a registered
driver. The runner retains completed server results in native history. A failed,
unfinished, undeclared, or mismatched server result stops further local effects.
When any server tool is declared, local calls wait until the full response arrives
even with `eager=True`. This protects against a failure arriving later in the stream.
For sparse or out-of-order stream indices, the runner defers any suffix after
the first gap until the completed response confirms the output order. Already
executed prefix calls retain their receipts if the stream fails.
At that boundary, `supply_outputs` can replace an unattempted ordinary function
that allows overrides, even without an explicit early-execution policy.

This runner needs stored responses to continue after image generation.
The runner rejects `store=False` with `image_generation` before sending a request or running a function.
Set `store=True` when storage is appropriate, or use `client.responses.create` for a single stateless request.
The runner never enables storage for you.

MCP approval uses `approve_mcp(request)` on `run` or `iterate`. Return exactly
True or False; the async runner awaits the callback. The runner retains the
original request ID and pairs it with your answer. Later MCP calls must match
the approved server, name, and arguments. A missing callback never grants access.
The SDK does not accept an approval result invented by the model.
When an MCP tool is admitted, the ledger also saves a pending checkpoint before each request.
Requests that declare MCP tools disable automatic SDK retries, with or without a ledger.
If transport fails or the response is lost, inspect the MCP server before starting a new run;
that checkpoint cannot resume, since the server may already have applied an effect.
Saved MCP declarations omit authorization and custom headers and replace server URLs with SHA-256
fingerprints. Native requests still use the original URL. Put credentials that must rotate in
authorization or headers. Changing a URL path or an unrecognized query value changes its identity
and requires a new run. Checkpoints containing raw MCP URLs cannot resume.
Other checkpoint inputs and outputs remain private application data.
Saved Code Interpreter declarations keep credential names and domains but clear
their secret values. Supply current values in the tool configuration when resuming.

Supply `approve_mcp` when initial input or a saved ledger contains approved MCP requests.
Before the first save or API request, the runner asks again for each approval that has no completed
matching MCP call. This applies with or without a ledger or context budget. It keeps completed calls
and earlier refusals unchanged. If fresh approval is needed, a missing callback stops the run.

Approval is required by default. The runner enforces `always`, `never`, and unambiguous
tool-name approval filters from the captured request. A call that requires approval must
reference a matching prior approved request before local work can continue.
An empty `always: {}` or `never: {}` filter applies to every tool. Read-only
filters and ambiguous filter combinations remain API policies because the response does
not contain enough information to verify them.

Use a trusted OpenAI client. Custom client hooks and transports can change requests
and retry behavior after the helper validates its inputs; your application owns those changes.
For Responses and Decisions runs, a fixed caller-supplied idempotency key applies to the first request. Later turns get fresh keys; HTTP retries of one request retain its key.
Supply trusted per-run request options too. Native options can change request data
after validation. Ledger runs accept a narrower set of options.

A registered computer defaults
to `{"type": "computer"}`. Computer calls go through
`ComputerToolset.execute`, with its required pending-safety-check approval;
pass `approve_safety_checks` and `before_action` to the runner as needed.
These callbacks may accept an optional keyword-only `cancelled` parameter,
just like computer driver methods. The helper passes the effective cancellation
probe only when the callback declares it. Existing one-argument callbacks still
work: `approve_safety_checks(call)` and `before_action(action)`. Interactive
approvals can check the probe and settle promptly. The toolset stays busy until
the callback returns or raises, and it performs no further actions after a
reported cancellation. Sync and async toolsets behave the same way.

Computer approval covers the action's fixed arguments. It does not freeze the
screen or focus while a person decides. If consent must apply to a particular
target, the driver must bind the action to that target or reject it after a
state change. Run computer actions in an isolated environment with limited
network access.

Computer-only loops with `ComputerToolset.run` or `AsyncComputerToolset.run` also accept Responses
`context_management` compaction. The helper replays the opaque compaction item before continuing.
This differs from the mixed runner's local `context_budget` option.

## Streaming and interrupted actions

`runner.run(client, params, stream=True, on_event=callback)` reports existing
SDK Responses stream events. By default, it waits for a completed response.
It validates all call names and IDs before dispatch. `eager=True` starts a call
when its completed output-item event arrives. Eager execution reduces delay,
but an action may finish before a later stream failure or unknown call.
Enable eager execution only when a completed item may run before the runner validates the full response. If
a later event changes or removes that item, the runner stops and keeps its execution record. It
cannot undo the action. Leave eager execution off, or use an empty policy for early execution, if all
actions must wait for the complete response to pass validation.
The runner never repeats a completed output item. It closes the response
stream on success, exception, or cancellation.

Set `cancelled` to a synchronous predicate checked before and after dispatch
and between stream events. Keep it true after requesting a stop. An already
awaited callback must settle before the runner can check that predicate again.
Async task cancellation propagates as `ToolRunnerCancelledError`, an
`asyncio.CancelledError` with the same call ID fields as `ToolRunnerError`,
when user callbacks let the cancellation exception escape. Catch it inside the
task that calls the runner to inspect receipts. Python's `asyncio.Task` can wrap
a cancellation subclass in plain `CancelledError` when another task awaits it.
A callback can
catch and suppress task cancellation. Such callbacks must also use the
persistent `cancelled` predicate to prevent effects after they return.
`max_steps` counts Responses requests. If the last request still calls a
local tool, the runner stops before that action.
`ToolRunnerError.attempted_call_ids` includes an action that may have changed
state before throwing. `completed_call_ids` means the SDK built an output;
it can include a refused or skipped browser action. Inspect both before
deciding to retry. The runner never retries application actions.
The error message identifies fixed SDK validation failures, such as an incomplete
response or mismatched stream output. Errors from API calls, drivers, parsers and
checkpoint storage keep a generic message.

Browser and computer toolsets and both runners expose synchronous `close()`,
including their async variants. It stops new calls and returns
`{"status": "draining"}` if a call is active, otherwise `{"status": "closed"}`.
Await or otherwise finish the active call before cleaning up your driver.
The helper never closes a caller-owned driver. Calls on the same active helper
fail as busy instead of interleaving actions; separate driver sessions can use
separate helpers. Repeated async cancellation still drains started independent
functions before returning.

Pass `on_diagnostic=callback` to a runner or toolset to receive
`ToolDiagnostic` events. The callback is synchronous in both Python variants
and must return None. Schedule any async logging yourself. Callback failures
cannot change action approval or results. An event contains `api`, `stage`,
`reason`, `duration_ms`, `call_id`, `member`, and `usage`. It excludes raw
arguments, page text, URL, screenshots, credentials, and exception text.
Usage contains native token counts when supplied by a parsed response;
otherwise it is None. Decisions emits the selected candidate ID before dispatch,
so an action failure still leaves a useful trace. Treat caller-chosen IDs as
potentially sensitive in exported logs.

Use explicit input history. `previous_response_id`, `conversation`,
`background`, and `params.stream` are rejected; choose streaming on
`run()`. Request options can be applied with `client.with_options(...)`.

## Choose which tools can run early

Set `early_execution` when constructing the runner to limit execution before
full response inspection:

```python
runner = AsyncResponsesToolRunner(
    browser=browser,
    functions=[registered],
    early_execution={"functions": ["browser_get_page_text"], "computer": False},
)
response = await runner.run(client, params, stream=True, eager=True)
```

Use registered function wire names, including exposed `browser_` names. The
separate `computer` Boolean selects the native computer dispatcher; an ordinary
function named `computer` remains a function. Unknown or duplicate names and
invalid policies fail at construction. The runner copies the selection, so later
caller mutations do not change it.

The policy applies only with both `stream` and `eager` enabled. Omitting it or
passing None keeps blanket eager execution. An empty dictionary defers every
local tool. The first deferred tool holds all later items in their original order,
including tools selected for early execution. `run()` advances automatically.
With `iterate()`, inspect the completed turn before advancing. Closing the iterator
at that boundary executes no deferred tools and sends no next request.

For each already-allowed early call, pass `before_early_call(call)` to
`run()` or `iterate()`. Return `"execute"` or `"defer"`. The async runner
awaits this callback. It receives a copy; editing arguments or IDs cannot change
the action. The hook cannot enable a name outside `early_execution`. A deferral
holds the remaining suffix until complete inspection. Server tools always force
that complete-response boundary before any local effect.

Declare `independent=True` only for ordinary registered functions that share
no mutable state and need no ordering with one another. Set `max_concurrent_calls`
on `run()` or `iterate()` to a positive integer (default 2). At each full
window the runner waits for every admitted call, records their outputs in
original order, and only then reads more stream events. A limit of 1 runs
these calls sequentially. This limit applies only to opted-in independent
eager calls without a ledger. In a local-only eager
run without a ledger, these functions can overlap. A browser call, computer
call, dependent function, deferral, or completed turn waits for all started
functions. The runner writes outputs in original call order and reports every
completed sibling after a failure. With a ledger it runs serially to preserve
admission and receipt order. Both `from_tool` variants accept `independent`.
Defaults remain serial.

The policy changes timing, not permission. Browser confirmation and native
safety/action checks still run before each effect. Earlier effects can survive
a later refusal or stream failure. Supplied outputs can replace only unattempted
ordinary functions that explicitly allow overrides, never browser or native
computer calls. A saved proposal with deferred work is not a resumable completed
boundary. The synchronous runner follows the same rules.

## Bound the native input sent on each request

Pass `context_budget` to `run()` or `iterate()`. A ledger is optional.

Every save receives a detached, complete checkpoint, including saves before and after local
effects. The application owns its storage limit and retention policy. Large batches or long histories
can cause quadratic cumulative copying and storage work as each snapshot grows.
`context_budget` limits the next API input; it does not bound ledger storage
or that snapshot work.

An interrupted pending checkpoint contains the last saved prefix. It can omit later text and unattempted proposals; it never authorizes replay. Before and after an effect, the saved checkpoint includes the full observed prefix and execution records.

The same whole-pair and pending-effect rules apply to in-memory runs:

```python
from openai.lib.responses_tool_runner import ContextBudgetDecision, ContextBudgetSnapshot


def select_completed_results(snapshot: ContextBudgetSnapshot) -> ContextBudgetDecision:
    return {
        "drop_call_ids": snapshot["eligible_call_ids"],
        "summary": "Older tool outputs remain in the application's full ledger.",
    }


response = await runner.run(
    client,
    params,
    context_budget={
        "max_input_bytes": 240_000,
        "max_input_images": 3,
        "keep_recent_screenshots": 1,
        "compact": select_completed_results,
    },
)
```

The runner measures the input array as compact UTF-8 JSON. It counts
`input_image` blocks in messages and function outputs, plus each native computer
screenshot. Images count even when specified by file ID or remote URL. The
runner does not fetch remote content. These limits cover input bytes and images,
not tokens, decoded image size, the entire HTTP body, ledger size or spending.

Before sending a request that would exceed a limit, the runner calls your policy
once. It first checks that all earlier tool calls are complete. The snapshot is
a copy: changing it cannot alter the runner's history. Choose IDs from
`eligible_call_ids`. The SDK removes each selected call and its matched output
from this request. All other items keep their original order.

The SDK always keeps messages, reasoning, the latest registered browser state,
and the latest native computer pair. It also keeps computer calls with safety
checks and the requested number of recent screenshots (default 1). Ordinary
function images still count against the image limit; they do not qualify as
screenshots from the registered browser.

The SDK adds a receipt with each omitted call ID, its tool kind and, for a
function, its name. Your optional summary appears in a separate user message.
Both messages count against the byte limit. They cannot grant approval or prove
that an external action succeeded. The runner keeps full history and receipts
in memory and rejects a dropped call ID if it appears again. With a ledger,
all 14 fields also retain that original full history. It cannot detect the same real-world action described under a new ID.

If a required policy is missing, invalid, or still produces input above the
limits, the runner stops. It saves no new request admission, sends no HTTP
request and executes no more tools. Pending work, refusal and uncertain effects
cannot be compacted. Closing an iterator never calls the policy.

A sync callback must return its decision directly. The async runner also accepts
an awaitable. Use the persistent `cancelled` predicate for reliable cancellation.
A callback that suppresses Python task cancellation must settle before the
runner can drain.

The budget applies only to that invocation. Supply it again on ledger resume;
omitting it keeps existing full-history behavior. The original ledger
`max_steps`/`consumed_requests` limits still apply. Auto truncation and nonempty
`context_management` are incompatible; in budget mode unspecified truncation
becomes `disabled`. Budget mode requires plain native request data, including
a built-in list or string for `input`, and rejects custom containers before
reading them. None/omission preserves current behavior without a budget.

Without `context_budget`, the runner also accepts native Responses `context_management`
compaction. It checks the required item fields and replays the encrypted content unchanged,
including when resuming a saved run. Do not combine the two modes.

When paused on a non-final `ResponsesRunnerTurn`, call
`turn.append_user_text("Focus on the current tab.")` before advancing.
The runner adds the text as an ordinary user message after that turn's tools
and receipts finish. It accepts nonempty text only. JSON-looking text remains
user text; it cannot supply an approval or tool result. The budget and total
step count continue. Closed, stale, and final turns reject new text.

## Selecting guarded actions with Decisions

When your application can enumerate every available action itself, use
`DecisionsToolRunner` or `AsyncDecisionsToolRunner`. Decisions selects from
your descriptions. It does not generate browser calls, return computer safety
checks, or authorize an action. Provide only actions your application may
perform. Enforce URL and approval policies in the executors before effects.

Each request receives only the observation you supply. Include earlier page content needed for
the choice, such as rules read in another tab. Bound that saved text and keep it separate from
current element references. Refresh references before executing an action.

For a task with several steps, include the last completed action and bounded page text from before it.
Capture that text from the same validated read used to create the action. Save it only after the
tool reports success, and reset it for a new task. Keep browser handles inside the executor and
use separate choice IDs. If a tool refuses or fails, stop the executor with an error.
The Fieldwork demo uses a local rehearsal and independently checks the saved reservation.

```python
from openai import AsyncOpenAI
from openai.lib.decisions_tool_runner import (
    AsyncDecisionCandidate,
    AsyncDecisionsToolRunner,
    DecisionObservation,
)


async def complete(model: str, task: str, page) -> str:
    async def observe() -> DecisionObservation:
        return await page.locator("body").inner_text()

    async def candidates(observation: DecisionObservation) -> list[AsyncDecisionCandidate]:
        async def mark_reviewed() -> None:
            # Check the current page URL and request permission here when needed.
            await page.get_by_role("button", name="Mark reviewed").click()

        return [
            {"id": "review", "description": "Mark the document reviewed", "execute": mark_reviewed},
            {"id": "done", "description": "The document is already reviewed", "done": True},
        ]

    async def verify(observation: DecisionObservation) -> bool:
        return await page.get_by_text("Review recorded", exact=True).is_visible()

    async with AsyncOpenAI() as client:
        result = await AsyncDecisionsToolRunner(
            observe=observe,
            candidates=candidates,
            verify=verify,
        ).run(client, {"model": model, "input": task}, max_steps=8)
    return result["status"]
```

`observe` returns text or the generated Decisions iterable of `input_text`
and inline `input_image` parts. External image URLs and file IDs are not
supported. The runner owns a snapshot before passing observations to callbacks.
Each step uses only the task and current observation, without replaying tool
history. Candidates need unique IDs and descriptions. Exactly one must have
`done: True` and no executor. All other candidates need callable executors.
One done-only item ends locally without an API request; otherwise there must
be 2–255 candidates.

Only `verify` returning exactly `True` on a fresh observation produces
`status="verified"`. With no verifier, done produces `"unverified"`.
A model refusal produces `"refused"`. After failed verification, another
choice is possible while requests remain. Failed done-only verification stops
immediately.
`max_steps` counts actual Decisions requests. An action selected on the final
request does not run.

The result carries native `decisions`, `attempted_candidate_ids`, and
`completed_candidate_ids`. A `DecisionsToolRunnerError` or async
`DecisionsToolRunnerCancelledError` carries the ID evidence and a fixed
`reason`. If an executor changes state and then fails, its ID is attempted,
not completed. Inspect these fields before deciding whether to retry.
Use `cancelled` for cooperative cancellation and `client.with_options(...)`
for request options. Run parameters are `model`, the task string `input`,
and optional `safety_identifier`; Responses flags and streaming are rejected.
Decisions access or model errors never fall back to Responses automatically.

## Hosted environments

See [provider connections](browser-providers.md) for browser and desktop
driver integration and ownership rules.
