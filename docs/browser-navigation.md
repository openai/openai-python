# Browser history, scrolling and waits

Drivers can implement these optional BrowserToolset members:

- `scroll_to(action: ClickInput)` scrolls toward a current target reference.
  It requires the same confirmation callback as click.
- `wait_for(action: WaitForInput, *, cancelled)` waits for visible text.
  It is a read and does not require confirmation unless protected by the
  toolset's read policy. Drivers may declare the optional `cancelled` keyword;
  existing signatures remain valid.

Pass `members=["navigate", "scroll_to", "wait_for"]` to advertise only those
tools. Unimplemented members are not a fallback. `wait_for` accepts `text`,
`timeout_ms` and `tab_id`. Normalized text must be nonempty and at most
256 UTF-8 bytes, and timeout must be an integer from 1 to 30000. A timeout is
a controlled failure; later actions follow the runner's ordinary failure rules.

For history, the SDK passes `back`, `forward` or `reload` as the requested
navigation to URL policy, then confirmation. Approving a history operation
does not approve every possible destination. The driver must enforce its
network policy and invalidate old references when the document changes.

A driver wait should share the same privacy rules as its page reads, check
cancellation and document identity, and report expiry without echoing private
page data. A deadline on a local waiter cannot prove that remote work stopped.
Drain or retire the owned work before handing control to a human.
