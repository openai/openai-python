# Scoped reads and guarded pointer input

These optional examples use a disposable local browser and fixed pages. They make no API
requests and need no API key or model. The scoped exercise chooses between repeated
sections with the same control labels. The pointer exercise checks clicks, a modifier drag,
and a timed key hold on one launcher-owned canvas.

Download and unpack **Source code (zip)** from the
[Python SDK release page](https://github.com/openai/openai-python/releases/latest).
Keep the `examples` folders together. From the unpacked `examples` directory:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade openai playwright==1.63.0
.venv/bin/python -m playwright install chromium
.venv/bin/python browser/exercise_scoped.py
.venv/bin/python browser/exercise_capabilities.py
```

These commands use a macOS or Linux shell. On Windows, replace `.venv/bin/python` with
`.venv\Scripts\python.exe`.

The scoped result reports `picked: "south"`, bounded depth, privacy, stale-ref refusals, and
unchanged legacy behavior. The pointer exercise prints `PASS` lines after checking actual
events and state: trusted right, middle and double clicks; modifier drag; timed hold and
released keys; rejection of a replaced canvas; and retirement of only the cancelled owner.

## Scoped reads in this driver

The driver exposes `read_page_scoped` only when `open_browser` has `owned_fixture_urls`.
Select it explicitly, for example with
`members=["read_page", "read_page_scoped", "click"]`, and provide `confirm` for `click`.
A `None` root discovers named main-document `section`, `article`, `nav`, or
`role="region"` elements. The example reads names from direct `aria-label` attributes.
Child frames report `unsupported_root`; it does not issue scope refs inside frames.

Use a returned scope ref for another `read_page_scoped` call. If you need to click, choose
an element ref from that result. A scope ref itself cannot authorize a click. Hidden,
replaced, renamed, stale and cross-tab refs fail. The scan retains privacy and total work
limits; `depth` separately bounds DOM traversal within the selected root.

## Guarded pointer factory

Create the page in your launcher and keep the original element handles for its record and
any secret-free canvases you created. Call
`await driver.owned_browser(record, cancelled=stop.is_set, canvases=canvases)`.
The persistent `cancelled` predicate is required. The optional list of canvases must come
from fixture construction, never from model refs or a page-supplied selection. Replacing
an allowed canvas does not transfer permission.

The returned driver supplies `state()`, `screenshot`, `click_at`, `drag_path`, and
`hold_keys`. Pass it to `AsyncBrowserToolset` with
`members=["screenshot", "click_at", "drag_path", "hold_keys"]` and `confirm`. The three
actions stay hidden when `members` is omitted.

Capture a screenshot through this pointer driver before **each** gesture. The screenshot
grants one gesture against the checked current view. Coordinates remain full-viewport CSS
pixels after zooming. The factory reuses the existing public-pixel, record, bounds, and
gesture checks. Held keys must be released when the operation ends; if cancellation or
failure prevents safe release, the driver retires its owning context. Other contexts remain
separate.

The default screenshot and native pointer paths still deny canvases. These browser methods
do not add native computer actions that the existing adapter refuses. The launcher must
guarantee that the fixed fixture never presents secrets, including during capture. These
checks cannot redact arbitrary sites. The DOM checks cannot inspect
closed shadow roots. Grant public pixels only for templates you control throughout the run,
including any components they create. See the
[SDK browser contract](../../docs/browser.md#opt-in-to-scoped-reads-and-pointer-input)
for argument bounds and result types.

## Diagnose or script the local fixture

From the SDK `examples` directory, run:

```sh
.venv/bin/python browser/exercise_sensitive.py
```

This uses a real local browser and makes no model requests. The optional factory
`await create_sensitive_driver(context, url, diagnostics=True, scripts=True)` requires an empty context
and an exact local fixture URL. Enable only the methods your task needs, then
select `read_diagnostics` or `run_script` in the SDK helper and supply confirmation.

Diagnostics report bounded console levels and network status, without message
contents or request URLs. The script exercise changes an SVG shape and reads a
synthetic value. It also checks blocked network access, stale refs, cancellation,
and retirement after a timeout. Scripts have the page's privileges; this example
is limited to a fresh, secret-free fixture and does not make arbitrary code safe.
