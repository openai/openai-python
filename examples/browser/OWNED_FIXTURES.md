# Owned fixture reference checks

This optional async Python example has two modes. `open_browser(url)` keeps
the generic Playwright actions and legacy state. To use bounded V1 state and
stronger references, pass `owned_fixture_urls=frozenset({...})`. Supply the
exact installed HTTP(S) URLs for the fixture pages and required endpoints.
`open_browser` creates and delegates its own disposable context.

Use the URL's canonical browser spelling in every fixture declaration: a lowercase host,
an explicit path (`/` for the root), no default port, no dot path segments, and no fragment.
For example, use `https://fixture.example/`, not `https://FIXTURE.example:443`.
Noncanonical declarations are rejected. Use the same exact URL in `owned_fixture_urls`,
`public_values`, and `public_viewports`; the driver does not rewrite these permission keys.

Create one driver and one SDK toolset for each context. The launcher must
serialize admitted work through that owner and drain it before handing the
page to a person. A ref binds to the observed element and remains reusable
while its identity matches. It is not a single-use permission or a way to
coordinate two independent toolsets. A failed or cancelled navigation after
browser dispatch retires the driver; owned mode also closes its disposable
context. Validate a fresh task before starting again.

Run the local proof with the optional Playwright environment:
```sh
python examples/browser/exercise_owned.py
```
It starts its own fixture server and makes no API calls. It checks the
independent server-side effect history, not only a success string.

Run `python examples/browser/exercise_network.py` for local request checks.
Select `--case basic`, `redirects`, `origin`, `chain`, or `popup` to inspect
one boundary. These checks start disposable local servers and make no API calls.

Run `python examples/browser/exercise_navigation.py` for history, target scroll
and visible wait checks in real Chromium. It tests stale and recycled refs,
same-document URL refusal, field consent across pages, and cancellation. See
[the navigation guide](../../docs/browser-navigation.md) for exact arguments
and supported boundaries.

`open_browser` guards requests in both modes. It allows direct approved URLs
and refuses every HTTP 301, 302, 303, 307 or 308 before fetching a target.
Even an approved target is refused. A 304 remains an ordinary response.
No redirected request is retried. A POST could already have acted; the
launcher must reconcile that effect. An allowed redirect is unsupported,
not a URL-policy refusal.

The guard buffers each allowed HTTP response to reject redirects before they are followed. It supports finite responses and has no separate 30-second fetch timeout. Action timeouts and session cancellation still apply. Open-ended response streams require network enforcement outside this guard.

A denied popup may leave Chromium's error document open. Owned state,
reads and close through the driver refuse that document, even if its ID is
known to the launcher. The SDK cannot get a usable starting state. The
owning launcher must close the blocked Playwright page or the whole context;
this is not agent or SDK recovery.

Service workers and WebSockets are blocked. These browser request guards
do not establish OS, WebRTC, DNS, host-process or provider egress isolation.

Only use the owned mode with fixtures whose consequential handlers capture
the immutable record shown to the user. The included `owned-fixture.html`
does this when it installs a record. Unsupported controls have no usable
ref. Hover, key and generic scroll are omitted in this mode; type requires a ref.
Owned `scroll_to` requires an observed ref and clears refs after scrolling.
General sites, trusted pointer actions, arbitrary callbacks and custom
editors are outside this contract. It is not a general network sandbox.

Ref actions use one synchronous DOM evaluation on the originally captured
handle. A current record/role/label, enabled/writable target, and visible
unobscured center must still match. Exact-installed child frames must have
an accessible, untransformed path through each parent frame's hit test.
Click uses DOM activation, text and single-select use a native value setter
and one input event. No focus, key, hover, scroll, automatic wait or retry is
hidden in that boundary. Required form validation is inspected without
dispatching an invalid event.

Any lost or malformed reply after evaluation may have begun retires the
owned driver before waiting for context closure. Reads, new tabs and new
actions fail even if close stalls or fails. A separate explicitly started
run is the only way to obtain a new driver. Only an explicit pre-action
refusal proves zero effects.

The driver cannot observe an SDK cancellation after it already returned its
checked result. The launcher still has to drain admitted work, revoke refs
with `invalidate_references()` before and after handoff, and reconcile
uncertain caller results. A cancellation alone never transfers page control.

V1 state returns a fixed safe fixture title rather than the page title.
Events omit URLs, dialog text and download names; they retain the newest 32
notices without consumption by reads. URL display is an origin, never the
navigation authorization value.

Owned `read_page`, `find`, and `get_page_text` return a V1 read object:
`{version, text, elements, omitted}`. Elements contain an opaque ref, native
role and visible label. Labels use at most eight visible same-root
`aria-labelledby` sources, then `aria-label`, visible native labels, rendered
text, then placeholder. Hidden text and embedded field values are excluded.
Visible business labels such as `Dispatch BP-1207` stay searchable; raw DOM
identity and private binding attributes are never part of the report.

Current field values are denied by default. The owner can opt in exact
installed document, private record, and field tuples when opening its context:

```python
async with open_browser(
    fixture_url,
    owned_fixture_urls=installed_urls,
    public_values=frozenset({(fixture_url, "case_a", "guest")}),
) as driver:
    report = await driver.read_page({"tab_id": None, "filter": "all"})
```

`data-browser-field` identifies a field; the page cannot grant permission by
setting it. `data-browser-private` on any visible ancestor, or a password,
file or hidden input, overrides every declaration. The fixture's input and
select use keys `guest` and `team`. `rich-child.html` uses `queue`.
The declaration does not cover another URL or recycled record.

One read visits at most 2000 DOM nodes, including hidden siblings, lookups
and slots, 16 frames, and eight frame or open-shadow boundaries. It returns
at most 16 KiB of text, 100 elements, 32 options each, and 64 KiB of UTF-8
JSON. `omitted` explains limits and exclusions. `find` filters visible labels
before counting targets. `get_page_text` never returns refs or revokes the
current ones.

Exact installed cross-origin frames can contribute query-filtered text
prefixed `Read only: remote frame`. The driver checks each iframe's center
through real handles in the parent realm and excludes covered or transformed
paths. These summaries have no refs: a check in one realm cannot authorize an
atomic action in another. Open shadow roots and assigned light children are
supported. `unsupported_root` remains a conservative coverage warning because
an absent `shadowRoot` cannot prove that no closed root exists. This is a
bounded fixture name rule, not an arbitrary-site accessible-name implementation.
# Native form fields

The owned example also supports visible native textarea, date, range,
checkbox, radio and multiple select fields. Use the existing `type`, `click`
and `select_option` members with current refs. See
[`docs/browser-forms.md`](../../docs/browser-forms.md) for values, events and
limits. The same exact `public_values` tuple is required to reveal any
current value, checked state, available options or selected options.
Page markup never grants that permission.

The existing 100-tab observation limit applies to live owned tabs at
registration. Closing a tab frees a slot. A 101st live tab retires the driver
and closes only its disposable owned context; it cannot close a caller's
borrowed browser.
