# Fieldwork browser demo

For installed Chrome on Linux, see [Choose a local browser](../browser/README.md#choose-a-local-browser).

Run six local tasks in a browser with the Python SDK. Fieldwork opens a local
dashboard, a separate temporary Chromium profile and synthetic fixture pages.
It never uses your signed-in browser.

From a Python SDK source archive root, set up the example in Python 3.10 or later:

```sh
python3 -m venv .venv-browser
.venv-browser/bin/python -m pip install openai 'playwright==1.63.0'
.venv-browser/bin/python -m playwright install chromium
.venv-browser/bin/python examples/browser-use-demo/server.py
```

Open the dashboard in a fresh browser profile so previously installed service workers
cannot control it. This is your operator profile, separate from the task browser
the demo creates. The server chooses an available local port; use the private link
printed in your terminal each time. You can still choose a port with `--port` or
`DEMO_PORT`; use a fresh operator profile there too.
Choose **Local rehearsal** to try the Decisions runner with scripted local
answers. This sends no API requests. For live use, set `OPENAI_API_KEY` and
`OPENAI_RESPONSES_MODEL` or `OPENAI_DECISIONS_MODEL` in the shell before
starting the server. `OPENAI_MODEL` can supply either model when its specific
variable is absent. Responses is the default. It uses the Python browser
tools; Decisions chooses from the fixture's current eligible actions.

Support triage, reservations and invoice review compare the final page
with the task. Stock, service and file intake check saved records on the
local server. Changing page text cannot change those records.
A reservation, invoice approval, shipment, service booking or file selection
waits for your approval. File intake also needs your opt-in before Start.
It can select only one generated synthetic file, which expires after 30 seconds.

Open the private link printed by the server in your terminal. It grants control
of this local demo, so do not share it. The page removes the link's token from
the address bar at once; reload requires reopening the private link. Redirected
output shows only the public origin and cannot authorize controls. Other local
users can load the public help page, but cannot view runs or issue controls
without the link. This does not protect against someone with access to your
terminal or the same OS account.

## Choose a starting point

Start with **Book a table** in the dashboard. Use the smaller reader when you want
one file to adapt before adding approvals or desktop control.

| What you want to build | Example to start from | What it teaches |
| --- | --- | --- |
| Read and answer a question | [Local page reader](../browser/README_read_only.md) | A partial driver, allowed navigation and current page evidence |
| Make an approved edit | Book a table | Form inputs, fresh targets, approval and a saved-result check |
| Apply business rules | Invoice review, stock or service | Keep incorrect approved results visible as unverified |
| Transfer a bounded file | [File intake](../browser/README_files.md) | One-use permission, expiry and a checked receipt |
| Combine browser and desktop | [Mixed task](../browser/README_mixed.md) | Separate workspaces, human handoff and one request budget |
| Carry evidence across steps | [Release review](../browser/long-workflow.md) | Prior observations, complete Decisions choices and verification |

## Isolated desktop and mixed workspaces

Before publishing a verified Desktop or Mixed result, the demo stops the guest
browser and editor, drains their fixture writes, and checks the saved records
again. The completed view is a saved frame. Start a new task to make changes.
A change before sealing can still make the final result unverified; that task
has ended too.

On an Apple-silicon Mac, build the fixed guest with the
[desktop setup instructions](../computer-desktop/README.md). Keep the resulting
runtime path and start the dashboard with it:

```sh
export OPENAI_API_KEY="<your API key>"
export OPENAI_RESPONSES_MODEL="<your Responses model>"
.venv-browser/bin/python -m pip install Pillow==12.3.0
.venv-browser/bin/python examples/browser-use-demo/server.py --desktop-runtime /private/tmp/desktop-$UID
```

Choose **Isolated desktop** or **Mixed** in the dashboard. Both need live
Responses and a configured runtime; they do not use a Decisions rehearsal.
The isolated desktop task routes D-2201 in the guest browser and saves the
fixed receipt in the guest editor. It asks before the first input in each
agent phase and before any API safety check.

Mixed keeps the Host dispatch browser separate from the Guest desktop.
Route D-2201 on the Host, approve the one local receipt, then save that exact
text in the editor on the right side of the Guest. The Guest browser on the
left belongs to a different task and must stay untouched. Choose **Host
browser** or **Guest editor** to change the view. The server rejects input
from an older view. Take and Return retain both workspaces in the same task.

The desktop startup can take time. Stop prevents new input, retires the guest
it created and waits for admitted work to finish before allowing another run.
It never removes another task's guest. If control cannot transfer within five
seconds, Fieldwork closes the workspace instead of admitting overlapping input.

With an already-built runtime, check both native dashboard flows locally:

```sh
.venv-browser/bin/python examples/browser-use-demo/exercise_desktop.py --runtime-dir /private/tmp/desktop-$UID
.venv-browser/bin/python examples/browser-use-demo/exercise_mixed.py --runtime-dir /private/tmp/desktop-$UID
```

These two checks use the real local VM and a controlled Responses transport.
They need no API key. They verify actual guest records and saved-file state.

**Take control** waits for the agent's current work to finish before it enables manual input.
**Return control** observes the current page before the agent continues. An
approval from an earlier page or control phase cannot execute. **Stop** closes
the current workspace. File intake offers View and Stop only; it does not let
manual input open a file picker. Saved checkpoints are view only.

If the demo cannot stop pending browser or desktop work safely, it closes that
workspace. Manual control stays unavailable. Wait for cleanup to finish, then
start a new task.

## Inspect usage and failures

Open **Usage and diagnostics** in the dashboard. Token counts come from actual
SDK responses. A failed or incomplete request may have no usage; the summary
shows how many attempts are missing instead of estimating them. API time,
measured browser action time and operator approval wait appear separately.
An unavailable duration stays unrecorded. These values do not establish a
speed or cost advantage over another API.

The normal JSON export keeps only fixed status fields, numeric usage and timing.
It omits page text, action arguments, screenshots, raw errors and private file paths.

For a local investigation on macOS or Linux, start the server with
`--diagnostics`. Open **Usage and diagnostics → Open saved trace viewer**.
Choose a run and select an event in its timeline. Saved frames show the actual
isolated browser or desktop at a checkpoint. This separate viewer has no live
input or approval controls.

```sh
.venv-browser/bin/python examples/browser-use-demo/server.py --diagnostics
```

The server prints a private directory and its capture ID. To view the same
recordings after restarting, pass that exact ID (not the path):

```sh
.venv-browser/bin/python examples/browser-use-demo/server.py --diagnostics-reopen openai-browser-diagnostics-REPLACE_WITH_PRINTED_ID
```

This choice opens only that demo-owned capture. The viewer also reads older
text-only recordings and reports "No saved frames." It reports incomplete
recordings and omitted events or images, rather than filling in missing data.
A resumed capture can record more runs up to the same total limit.

Captures use a 0700 directory and 0600 files. They retain text observations,
Decisions choices, action results, verification and SDK events. They never
record API headers. Images come only from the owned synthetic workspace at an
actual checkpoint. At most 12 frames are saved per run, 1 MiB per frame, and
8 MiB of images per run; a frame beyond those limits is omitted. Text is
limited to 1 MiB per run. The capture accepts at most 16 runs, for a maximum
of 144 MiB across text and images. This first-frames policy keeps earlier
evidence even when later frames must be omitted. No capture content or file
path appears in a normal JSON export.

Captures remain private files on your computer until you delete that directory.
Inspect any synthetic page values before sharing. To check capture and redaction
without a browser or key, run `.venv-browser/bin/python examples/browser-use-demo/exercise_diagnostics.py`.

## Inspect a tool manually

1. Start a browser task, such as **Review an invoice queue**, in local rehearsal.
2. When the agent requests approval, choose **Take control**. Wait for the human
   controls to appear.
3. Open **Manual browser tool inspector** and select **Load current tools**.
4. Select `browser_read_page`, consent to this one call, and run it. Inspect the
   result for current element references.
5. Choose a tool and fill its generated fields. Consent again to each call.
   A sensitive action still shows the normal Approve or Refuse card. Stop ends
   pending calls and revokes further input.
6. Choose **Return control** when you want the agent to continue.

Manual calls pass through the same SDK toolset, task validation and current
reference checks as agent calls. They work only on the current owned browser
page after takeover. Stale, refused and stopped requests cannot authorize
later work. File-intake and desktop tasks keep their existing manual controls;
this browser inspector does not bypass those task restrictions. Saved
checkpoints and the saved trace viewer never accept tool input.

## Maintainer regression checks

These checks target separate failure cases. You do not need to run all of them to try or adapt the example. To check the example with a reviewed SDK installed in the environment:

```sh
.venv-browser/bin/python examples/browser-use-demo/exercise.py
.venv-browser/bin/python examples/browser-use-demo/exercise_wire.py
.venv-browser/bin/python examples/browser-use-demo/exercise_ui.py
```

These checks run real Chromium with the installed Python SDK. The first checks
all six rehearsals and local receipts. The second supplies controlled local
HTTP Responses and Decisions answers and checks Stop and takeover timeouts.
The third drives the actual dashboard. None needs an API key or a vendor account.

The HTML, fixture templates and private `tasks.json` match the Node example.
Contributors who change them should update both SDK source archives and run:

```sh
python3 examples/browser-use-demo/check_shared.py /path/to/openai-node
```

The server does not expose `tasks.json` as an HTTP asset.
