# Borrow a Daytona desktop for computer actions

This optional async example adapts an already-started Daytona desktop to
`AsyncComputerToolset`. It checks one active display and supports a limited set
of pointer and keyboard actions. It never creates, starts or stops a sandbox.

Download **Source code (zip)** from the
[Python SDK release page](https://github.com/openai/openai-python/releases/latest).
Unpack it and open its root folder in your terminal. If you are in
`examples`, run `cd ..` first. Use Python 3.10 or later and install the
SDK and optional Daytona package in a separate environment:

```sh
python3 -m venv .venv-daytona
.venv-daytona/bin/python -m pip install --upgrade openai 'daytona==0.220.0' 'Pillow==12.3.0'
.venv-daytona/bin/python examples/computer-daytona/exercise.py
```

Use your configured registry. The optional package is not an SDK dependency.
The exercise passes on Python 3.10. It calls installed Daytona async classes
through a mocked toolbox transport. It checks actions, refusals, screenshots,
and display changes through the OpenAI helper. It creates no sandbox and sends no provider or model request.

To run the repository's strict optional adapter check, first use the repository
tool versions from `CONTRIBUTING.md`:

```sh
PYRIGHT_PROJECT=scripts/pyrightconfig.daytona-example.json \
  scripts/run-pyright --pythonpath .venv-daytona/bin/python
```

## Use an async desktop your application already owns

In code next to `adapter.py`, pass the running sandbox's `computer_use`,
an OpenAI client, model, prompt, async approval callbacks and Stop predicate.
Approve the initial screenshot before starting the run.

```python
from adapter import DaytonaComputer
from openai import AsyncComputerToolset


async def run_desktop(
    computer_use, client, model, prompt, approve_initial_screenshot, approve_action, cancelled
):
    if cancelled():
        raise RuntimeError("Stopped.")
    driver = await DaytonaComputer.from_started_desktop(computer_use)
    if cancelled() or await approve_initial_screenshot(cancelled=cancelled) is not True:
        raise RuntimeError("Initial screenshot declined or stopped.")
    if cancelled():
        raise RuntimeError("Stopped.")
    image = await driver.screenshot(cancelled=cancelled)
    if cancelled():
        raise RuntimeError("Stopped.")
    return await AsyncComputerToolset(driver).run(
        client,
        {
            "model": model,
            "tools": [{"type": "computer"}],
            "input": [{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": image["image_url"], "detail": "original"},
                ],
            }],
        },
        max_steps=20,
        before_action=approve_action,
        cancelled=cancelled,
    )
```

The initial screenshot callback receives `cancelled` as a keyword argument.
Use it to stop waiting when the user presses Stop. The separate `approve_action`
callback receives each SDK action and can use the same Stop predicate.
Return exactly `True` from either callback only for permitted captures or actions. Forward the
Stop predicate to every tool or runner call. Pending safety checks require a
separate explicit approval callback; the helper refuses them by default. Drain
admitted provider work after Stop or an error before your application releases
the sandbox. Do not replay an uncertain input.

## Supported subset and limits

Capture a full-screen screenshot before pointer input. The adapter requires
exactly one active display at (0, 0), with an integer ID and positive dimensions.
It rechecks those fields before pointer actions. A change retires the adapter,
including keyboard input; create a new adapter and take a fresh screenshot.
A same-size replacement with the same reported ID cannot be detected.

The adapter supports in-bounds left and right clicks, left double-click, move,
exactly two-point drag, text, keypress, screenshot and a one-second wait. Keypress
preserves single characters and accepts ctrl, alt, shift or cmd before the last
key; common arrow and modifier aliases map to Daytona names. All scrolls,
extra buttons, pointer actions with held keys and other drag paths raise before
input. It does not guess a pixel-to-wheel conversion or split a drag.

The PNG check validates the original dimensions, complete image data and checksums.
It cannot prove who produced the pixels. Your application owns the sandbox and its private view, network access,
provider logging and cleanup. The adapter does not revoke other owners' access.
This is mocked provider transport and local conformance only: it provides no
hosted lifecycle, network or privacy proof.

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

The encoded PNG byte budget defaults to `2 * ((8 * width + 1) * height) + 65_536`,
capped at the largest safe integer. This allows twice the largest 16-bit RGBA
scanlines plus 64 KiB for headers and metadata. It is an example memory budget,
not a PNG format limit. A valid image with unusually large metadata may exceed
it. Choose another positive safe integer for `max_screenshot_bytes` when needed:

```python
driver = await DaytonaComputer.from_started_desktop(computer_use, max_screenshot_bytes=128 * 1024 * 1024)
```

The adapter checks the returned base64 length before it allocates the decoded
PNG. Daytona has already returned the provider string at that point, so this
budget does not bound provider-side or transport memory. An over-budget frame
revokes pointer access until the adapter captures a matching frame.
