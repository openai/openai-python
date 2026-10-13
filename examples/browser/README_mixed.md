# A receipt across the host browser and isolated editor

For installed Chrome on Linux, see [Choose a local browser](README.md#choose-a-local-browser).

This optional example uses Responses with structured browser tools, one
approved local function, and native computer actions. It supports one fixed
receipt, rather than general file transfers.

Follow the [browser setup](README.md) to download the released example files,
install the SDK and Playwright, and get Chromium. Run the commands below from
the unpacked release's root. If you are in `examples`, run `cd ..` first,
then activate the browser environment:

```sh
. .venv-browser/bin/activate
```

No guest is needed for the browser and file checks:

```sh
python examples/browser/exercise_mixed.py
```

That exercise uses the real guarded local browser and receipt HTTP request.
Its Responses client and native input are simulated. It never calls
an external API and cannot verify a saved guest file. For a real guest, first
follow the [desktop guest setup](../computer-desktop/guest/README.md). Then
pass the absolute path of the private runtime you built:

```sh
python -m pip install Pillow==12.3.0
python examples/browser/exercise_mixed.py --runtime-dir /absolute/private/runtime
```

Use `--handoff` to check Take/Return, including a held browser action,
pending receipt approval, expired grant, snapshots and the original 20-request
limit. Without `--runtime-dir`, the browser and HTTP receipt are real and
guest input is simulated. This can never verify a saved guest file. With
the runtime, the handoff exercise also checks the actual editor, saved file,
guest browser and human completion at zero remaining requests.

For a live Responses run, set OPENAI_API_KEY and OPENAI_MODEL in the caller's
environment and explicitly opt in:

```sh
python examples/browser/run_mixed.py --live --runtime-dir /absolute/private/runtime
```

The task has two different workspaces. Browser tools control a fresh host
Chromium context called Dispatch receipts. Only the native computer screenshot
shows the Linux guest; use its editor on the right and leave its other browser
untouched. The program asks before starting, before the host action, before
fetching and showing the approved public text to the model, and before native
editor input. Type `no` at a prompt, `stop`, or press Ctrl+C to stop. A Stop never rolls
back an earlier Route or admitted transfer.

To take control, type `take` even while an approval is open. Wait for
`Human owns both workspaces`. Until that message, the original agent's
entire desktop lease may still be settling and human input is refused. The
same host browser and guest stay open. The terminal accepts one human command
at a time:

- `view` writes two current private PNGs and prints their local paths. Open
  them to see the host and guest. A snapshot shows the moment it was taken;
  type `view` again after changing either workspace.
- `host route` uses only the original checked Route control.
- `host receipt` requests the fixed receipt and disclosure approval.
- `guest click X Y` clicks in the editor half; `guest select-all`,
  `guest type` and `guest save` enter only the approved public receipt.
- `return` removes the PNGs, drains human work, checks the original browser
  and receipt, and resumes only if they remain eligible. Type `stop` at any
  time to terminate and remove the PNGs.

Each resumed agent phase reads the current host and guest. It asks again
before guest input. A confirmed Route, transfer or disclosure remains a
completed fact: no replay, second fetch, or recreated expired grant is
allowed. A transfer that finished before disclosure still needs new approval
to disclose. If the human completed the task, the program verifies it without
another model request. All phases share the original 20-request allowance.
The SDK's complete ledger checkpoints stay in the original private area only
until each complete lease settles. The final proof contains phase-prefixed
IDs and counts, never ledger history or screenshots.

Three owners prove the outcome. The checked host Route must match its server
record. The download must complete with consent to disclose its trusted text.
The guest must match the saved file and show no guest-browser effect.
Neither the model's answer nor a simulated screenshot can pass the real file
check. Refused, stopped, unknown and unverified runs stay visibly incomplete.
The output shows outcomes and call IDs, not file bodies, screenshots, grants,
paths or credentials.

Only the fixed synthetic receipt is supported. Its download stays quarantined;
the function returns the separately trusted public text only after digest and
size verification. The model cannot select another file, URL, header or path.
Native input is limited to required editor gestures, select-all/save and the
exact approved text. These fixture rules do not create a general OS file policy
or an OS network firewall for the host browser. The guest has no network adapter
or host file share. A failed drain, unknown transfer or lost original control
ends this example visibly; it cannot grant human access to a still-running lease.
