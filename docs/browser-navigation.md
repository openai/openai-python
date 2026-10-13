# History, targeted scrolling and waits

These private browser helpers use ordinary Responses function tools. A driver
can implement two extra optional members:

- `scroll_to(action: ClickInput)` scrolls toward an observed target ref. It
  requires the same `confirm` callback as click.
- `wait_for(action: WaitForInput, *, cancelled)` waits for visible text. It is
  a read and does not need confirmation or URL policy. The optional keyword
  is the same persistent cancellation predicate passed to toolset execution.
  Every browser method may declare this optional keyword-only parameter.
  The toolset passes it when the method accepts it; existing signatures remain valid.

The async driver methods return awaitables. For sync or async drivers, pass
`members=["navigate", "scroll_to", "wait_for"]` to advertise only those tools.
Omitted or unimplemented members are never a fallback. Pass
`{text, timeout_ms, tab_id}` to `wait_for`. Normalize whitespace in the text;
the result must be nonempty and at most 256 UTF-8 bytes. Set the timeout to
an integer from 1 to 30000. Results include the usual checked state. A timeout
is a controlled failure. Later actions in that batch follow existing runner rules.

## Optional owned Playwright example

`examples/browser/browser_driver.py` implements history through
`navigate({"url": "back" | "forward" | "reload", "tab_id": ...})`.
The SDK sends that exact argument to URL policy, then requires confirmation.
Approving `back` approves a history operation, not a known destination URL.
Direct URL rules and all old action arguments remain unchanged.

Owned history needs a fresh, private, empty context with installed fixture
pages. It cannot be enabled on a borrowed browser with existing history.
History attempts clear refs even for a no-entry result. Read again afterward.
Network requests still require the exact installed URL and reject all redirects.
Same-document history may make no request. The driver checks the final page URL
before returning state, text, or images. BFCache restores and foreign
pre-existing history are unsupported. A final check cannot undo prior script.

The owned example scrolls only to a previously observed ref. It checks the
saved record and frame, performs one immediate scroll, then clears refs.
It never moves the pointer, focuses the target, or retries a locator. This does
not discover unseen virtual rows. A target outside view must have a real
scrollable container with a visible client area. Viewport-only clipping or a
covered, positioned, or transformed path that cannot be proved safe is refused.
The old generic `scroll` still uses CSS
pixel deltas, capped at 3072; it does not use wheel notches.

The owned wait searches the existing bounded `get_page_text` report.
It issues no refs and follows that read's existing field-privacy rules. It checks
cancellation, tab and document identity between reads. Reaching the condition
returns `Visible condition met.`; expiry returns a fixed error without the
search text. The deadline bounds cooperative reads and pauses. A hung browser
thread may delay a read. Drain the work or revoke its context before handing
control to a human. This is not a total workflow or spending limit.

Generic mode does not advertise either new member: its legacy text and refs
do not provide these owned guarantees.
