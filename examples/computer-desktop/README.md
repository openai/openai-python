# Optional isolated desktop

Use this example when a task needs a browser and a native editor on the same
screen. The SDK dispatches native computer actions. This example owns a
fresh, private Linux guest running Chromium and Mousepad. It never opens your
personal desktop or browser profile.

This example needs an Apple-silicon Mac. Download **Source code (zip)** from
the [Python SDK release page](https://github.com/openai/openai-python/releases/latest)
and unpack it. Open that folder's root in your terminal. If you are in
`examples`, run `cd ..` first. Use Python 3.10 or later and install the
SDK in a separate environment:

```sh
python3 -m venv .venv-desktop
. .venv-desktop/bin/activate
python -m pip install --upgrade openai Pillow==12.3.0
```

Install trusted vfkit and xorriso executables on PATH as described in the
[guest prerequisites](guest/README.md#before-the-first-run). From the SDK
source root, set up the private guest, then exercise it:

```sh
python examples/computer-desktop/guest/setup.py --runtime-dir /private/tmp/desktop-$UID
python examples/computer-desktop/exercise.py --runtime-dir /private/tmp/desktop-$UID
```

Setup downloads and verifies the fixed Debian media and builds the guest.
It checks a completed runtime before returning without another download or
build. The [guest instructions](guest/README.md) cover offline media, binary
overrides, failure recovery and runtime ownership.

It needs no API key. Each sync and async run starts a new guest and captures
a 1024 x 768 PNG. It tests repeated pointer movement and nonzero scrolling,
then clicks the browser fixture and saves text in Mousepad. Each run checks
the exact fixture effect and saved file without returning their contents.
Separate checks confirm that denied approvals send no input. They also
confirm that Stop completes during a held approval and blocks later calls.

## Optional API run

After the no-key exercise passes, set `OPENAI_API_KEY` and `OPENAI_MODEL` in
the host environment. Use a model that supports the computer tool. Then run:

```sh
python examples/computer-desktop/run.py --live --runtime-dir /private/tmp/desktop-$UID
```

This command uses the Responses API and can spend API credits. It asks you
to approve the fixed local task, then asks again if the API requests a safety
decision. The model must route the browser ticket and save the exact receipt
in the editor. The final result checks both changes independently.
Credentials stay in the host SDK client. Ctrl-C stops the owned guest.

## Use the desktop owner

`verify()` observes the current fixed records and leaves the desktop usable.
Before reporting a matching result as final, call `seal()` and check its
returned records again: a save may have changed them since the earlier check.
Sealing stops the guest browser and editor and drains the fixture writer.
The last frame captured before shutdown stays available for reference.
Use the returned records to verify the final result. Further input is refused.
Start a new desktop for any more work. Stop still removes the sealed guest.

Use `Desktop(runtime_dir)` with a trusted `pathlib.Path`. Call
`desktop.operation(lambda tools: tools.execute(call, ...))` around a complete
sync operation, including approval callbacks. For async code, pass a callback
to `await desktop.operation_async(work)`; it receives an
`AsyncComputerToolset`. Keep approvals in the application. Call
`desktop.stop()` in `finally` (or `await asyncio.to_thread(desktop.stop)`).
Stop blocks new calls and drains an admitted operation for up to five seconds.
It then removes only that instance's created process and run directory.
An uncertain input also retires the instance; it is never retried.
Check `desktop.uncertain_effects` when an input receipt is lost. A known denial
stays distinct from an uncertain effect. A confirmed result also stays
confirmed when Stop prevents you from using it.

The guest has no NIC, host-mounted filesystem, personal profile or API
credential. A private socket forwards only one validated action to the guest
per request. Runtime actions cannot choose a shell command, host path, guest
image, endpoint or environment. Chromium keeps its normal sandbox.

The fixture limits each action:

- Points must fit the screenshot.
- Typed text can contain at most 2,000 Unicode characters.
- Drags use 2 to 100 points; key combinations use at most five entries.
- Scrolling allows at most 2,048 pixels per axis.
- PNGs fit 4 MiB. The transport accepts 4 KiB action replies or 6 MiB screenshot replies.

A guest receives 4 CPUs and 4 GiB of RAM. Those values do not promise host
RSS or process limits. Unsupported keys, points and actions fail before input.

These examples support the tested host, guest and fixed task.
The installed SDK does not include the VM. Hosted providers, other apps,
other operating systems and other guest releases need separate validation.
A failed setup or exercise is a failed run. The earlier Docker profile could
not start Chromium's normal sandbox and is not a fallback.
