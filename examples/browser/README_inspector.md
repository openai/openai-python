# Check setup and try a driver without an API key

For installed Chrome on Linux, see [Choose a local browser](README.md#choose-a-local-browser).

Run these commands from the SDK source archive. Use Python 3.10 or later.

```sh
python -m pip install -U openai "playwright==1.63.0"
python -m playwright install chromium
python examples/browser/preflight.py
```

The preflight checks the SDK helper, Playwright, and Chromium. It prints each
missing prerequisite and the command to fix it. It does not read API
credentials or start a model run. To check a desktop setup, choose
`--environment desktop-vm` or `--environment desktop-container`. For a
built VM, also pass `--runtime-dir /private/tmp/desktop-$UID`. See the
[desktop guide](../computer-desktop/README.md) for setup instructions.

## Inspect and try calls

List the schemas on a real isolated fixture, or choose the small in-memory
driver:

```sh
python examples/browser/driver_inspector.py
python examples/browser/driver_inspector.py --driver memory
```

A read is private until you approve it. These two calls show the refused and
approved results:

```sh
python examples/browser/driver_inspector.py --member read_page --args '{"tab_id":null,"filter":"all"}'
python examples/browser/driver_inspector.py --member read_page --args '{"tab_id":null,"filter":"all"}' --approve
```

Set a checkbox on the local form. `--ref-label` reads the current page.
It requires one matching label and uses its fresh SDK reference for this call:

```sh
python examples/browser/driver_inspector.py --member set_checked --ref-label Ready --args '{"tab_id":null,"checked":true}' --approve
```

`--stop` aborts before dispatch. The inspector invokes `AsyncBrowserToolset.execute`
for every call, including its reads. Disabled methods, malformed inputs,
missing consent, and Stop still apply. It runs on fixed local fixtures, never
on your browser profile.

Run the shared driver checks and the coordinate exercise:

```sh
python examples/browser/driver_inspector.py --exercise
python examples/browser/exercise_coordinates.py --report /tmp/browser-coordinates.html
```

The report path must be new. Open the file to compare each original screenshot
with its supplied image size. The exercise maps a point to current browser CSS coordinates. It uses that
point to hover and click the real local canvas.
It covers equal size, twice the size, and different horizontal and vertical
scales. It also checks refused, stopped, and stale actions.

For your own partial driver, import `check_partial_driver` from
`driver_inspector.py` and call it on an isolated driver implementing
`state` and `read_page`. The example checks the same contract on an
in-memory driver and Playwright. Extend it with your own fixture checks
before giving your driver more capabilities. The inspector is example code,
not an additional production driver interface.
