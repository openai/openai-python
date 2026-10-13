# Use an E2B desktop with computer tools

This optional example connects the SDK's computer tools to your running E2B
desktop. It supports left and right clicks, left
double-clicks, mouse movement, text, key chords, screenshots, and a one-second
wait. It does not create or stop a sandbox.

## Run the local exercise

Download **Source code (zip)** from the
[Python SDK release page](https://github.com/openai/openai-python/releases/latest).
Unpack it and open its root folder in your terminal. If you are in
`examples`, run `cd ..` first. Use Python 3.10 or later and install the SDK
and optional E2B packages in a separate environment:

```sh
python3 -m venv .venv-e2b
.venv-e2b/bin/python -m pip install --upgrade openai 'e2b-desktop==2.6.0' 'e2b==2.52.0' 'Pillow==12.3.0'
.venv-e2b/bin/python examples/computer-e2b/exercise.py
```

The exercise calls the installed E2B input methods with controlled command and
file services. It checks the commands and SDK tool outputs, sends no provider
or model requests, and does not start a desktop. The Python provider is
synchronous, so this example uses the synchronous OpenAI runner.

## Add the driver to your application

Supply your running desktop, OpenAI client, model name, prompt, and approval
callbacks. The `cancelled` callback must report whether the user has pressed Stop.
Keep the desktop private to this run. Send its first screenshot with the prompt
so the model can see where to act. Put this code next to `adapter.py`.

```python
from openai import ComputerToolset
from openai.lib.responses_tool_runner import ResponsesToolRunner
from adapter import E2BComputer


def run_desktop(
    desktop, client, model, prompt, approve_initial_screenshot, approve_action, cancelled
):
    if cancelled():
        raise InterruptedError("Run stopped.")
    driver = E2BComputer.from_started_desktop(desktop)
    try:
        if cancelled():
            raise InterruptedError("Run stopped.")
        if approve_initial_screenshot(cancelled=cancelled) is not True:
            raise RuntimeError("Initial screenshot declined.")
        if cancelled():
            raise InterruptedError("Run stopped.")
        image = driver.screenshot(cancelled=cancelled)
        if cancelled():
            raise InterruptedError("Run stopped.")
        params = {"model": model, "input": [{"role": "user", "content": [
            {"type": "input_text", "text": prompt},
            {"type": "input_image", "image_url": image["image_url"], "detail": "original"},
        ]}]}
        return ResponsesToolRunner(computer=ComputerToolset(driver)).run(
            client, params, max_steps=20,
            before_action=approve_action, cancelled=cancelled,
        )
    finally:
        driver.close()
```

The initial screenshot callback receives `cancelled` as a keyword argument.
Use it to stop waiting for approval when the user presses Stop. The separate
`approve_action` callback receives each SDK action; it can use the same
`cancelled` callback while waiting.
Return exactly `True` from either callback only when your application permits
the capture or action. Forward Stop to every runner or tool execution.
Await an admitted operation before cleanup. Stop does not undo a remote action
or guarantee that a pending provider call ends. Do not share the driver with
other tasks or use it after closing it.

The driver removes only its own temporary screenshot files. As data arrives, it
checks the PNG header against the original dimensions and configured pixel budget.
It checks each chunk against the encoded byte budget before retaining it, then
validates and decodes the complete PNG. Size application memory for both the
encoded image and its decoded pixels.
It returns the image only after removal succeeds. A failed provider operation or changed
desktop retires the driver. If cleanup fails, keep the driver and call `close()`
again after the active operation ends. Never replay an uncertain input action.
Your application still owns sandbox release, network restrictions, provider
timeouts, private viewing, and any provider logging.

## Limits

Drag, pixel scrolling, extra mouse buttons, and held mouse modifiers raise an
error before input. The provider's drag method cannot guarantee release after
failure, and wheel steps do not establish pixel distance. A model can request
these actions, so handle the failed run instead of silently approximating them.

Key chords accept the named modifiers, common navigation keys, F1 through F12,
and single ASCII letters or digits. Names are case-insensitive; use text input
for letter case. Text must be valid Unicode without NUL and fit in 4096 UTF-8
bytes. One provider write preserves characters across its usual chunk boundary.

The local exercise does not prove hosted access, remote display identity,
desktop exclusivity, sandbox release, or network isolation. Matching dimensions
cannot detect every same-size display replacement. Those checks need a real,
private provider run before this example can claim hosted support.

Contributors can check the driver with the repository's strict Pyright settings:

```sh
PYRIGHT_PROJECT=scripts/pyrightconfig.e2b-example.json \
  ./scripts/run-pyright --pythonpath .venv-e2b/bin/python
```

The exercise uses controlled provider test doubles and is checked by running it.

## Screenshot limits

The adapter accepts non-interlaced PNG screenshots only. Its default pixel budget
is 33,177,600 pixels, the area of a 7680 by 4320 display. It rejects a larger
display before capturing a screenshot. To change the budget, set `max_screenshot_pixels` as a factory keyword argument.
Use a positive integer and choose a value your application can afford to decode.
Raising the pixel budget does not enable interlaced PNGs. Providers that return
interlaced PNGs are unsupported by this example.

The pixel budget limits image dimensions, not total process memory. PNG bit depth,
compressed input and decoder buffers also use memory. The existing complete-image
and checksum checks still apply. This setting does not override limits enforced
by the image decoder.

The encoded byte budget defaults to `2 * ((8 * width + 1) * height) + 65_536`,
using the actual desktop dimensions and capped at `2**53 - 1`. This allows twice
the raw 16-bit RGBA scanline size plus 64 KiB for encoding overhead. It is this
example's memory budget, not a PNG format limit. A valid image with unusually
large metadata may exceed it. Set `max_screenshot_bytes` to choose another budget:

```python
driver = E2BComputer.from_started_desktop(desktop, max_screenshot_bytes=128 * 1024 * 1024)
```

Use a positive safe integer. Omit it or pass `None` to use the derived budget.
The adapter checks each chunk before adding it to the image buffer. An
over-budget stream is closed, its temporary file is removed, and the driver
retires. The caller still owns the overall time limit through the `cancelled`
callback. A transport read timeout does not limit total transfer time.
