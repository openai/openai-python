# Pointer input in an owned fixture

This optional example handles a small set of native pointer actions on the same
page as the browser driver. Create a disposable page owned by the launcher.
Use it only when the launcher owns the fixture code and can guarantee that it
will not insert and remove private content while an image is being captured.
The checks before and after capture cannot prove what appeared temporarily.
They are not a redaction service for arbitrary sites.

Pass `public_viewports=frozenset({exact_url})` to `open_browser`. The URL must
also appear in `owned_fixture_urls`. The default grants no owned screenshots or
zoom. DOM `public_values` grants never enable pixels. Borrowed browser behavior
is unchanged and cannot create this owned adapter. The driver refuses forms,
editable areas, child frames, canvas, media, shadow roots, custom elements,
private markers, or scans beyond 2,000 elements, including hidden ones.

Capture the original `ElementHandle` from your own fixture construction code,
not from agent input or a browser ref. Call
`await driver.owned_computer(record, cancelled=stop.is_set)`, then pass the
result to `AsyncComputerToolset`. Pass the same persistent cancellation
predicate to any Responses runner. The adapter starts unarmed: issue a native
screenshot-only call before the first gesture. Only that adapter's native
screenshot arms one gesture. Browser screenshot and zoom do not arm it.
A fresh screenshot never adopts a replacement record or document.

Supported actions are move, left/right click, a 2–100 point drag, optional
Shift, and Enter/Escape when a visible enabled `button[role=menuitem]` in the
original record has focus. Other computer actions refuse before dispatch.
Two gestures in the same native call can stop after the first: the SDK takes
the screenshot only at the end. Successful SDK calls can therefore arm the
next gesture. The native API does not echo an image ID; the adapter checks its
locally captured eligible view, not which old chat image the caller used.

Zoom uses `browser_zoom` on the selected driver with
`{"tab_id": null, "region": [left, top, right, bottom]}`. It returns a native
CSS-pixel crop, without upscaling. Subsequent coordinates still use the full
viewport. Its [image return fields](../../docs/browser.md#driver-contract) match
screenshots: `image_url` and `file_id` may both be present, with at least one
nonempty source. The optional `prompt_cache_breakpoint` accepts
`{"mode": "explicit"}` or `None`. To require confirmation, include `zoom` in
`confirm_reads`.

A changed URL, generation, record, viewport, privacy condition, or
PNG makes a pending gesture refuse. After attempted native input, uncertain
release or outcome retires the context before bounded cleanup. No rollback
is implied. Wait for the old run to finish and check its result before a new handoff.

Follow the [browser setup](README.md) to get the released example files and
install the SDK, Playwright, and Chromium. Run from the unpacked release's
root. If you are in `examples`, run `cd ..` first:

```sh
. .venv-browser/bin/activate
python examples/browser/exercise_pointer.py
```

The exercise uses a fixed localhost fixture and no API credentials. It checks
native browser events, business results, supported menus/drag, refused input,
scrolled crops, lost replies, and repeated cancellation. It checks a local,
owned fixture; it does not verify hosted or arbitrary-site compatibility.
