# Native browser forms (private helper)

Use the existing `BrowserToolset` members with an owned-fixture driver.
Each change still requires the current `confirm` callback. These helpers
are unreleased; the example has local Chromium coverage only.

| Native field | Existing member | Input |
| --- | --- | --- |
| Text input or textarea | `type` | Literal replacement in `text` |
| Date input | `type` | Exact native date such as `2031-02-03`; empty clears unless required |
| Range input | `type` | Native numeric text within min, max and step, such as `40` |
| Checkbox or radio | `click` | Current target ref |
| Single select | `select_option` | Exactly one unambiguous option value |
| Multiple select | `select_option` | Complete selected set; `[]` clears it |

A checkbox click toggles the observed state. Read before deciding to click
and read again afterward. A radio click selects its option; clicking an
already selected radio need not emit another change. Do not retry a toggle
after an uncertain result. Inspect or retire that run first.

The driver refuses invalid date/range values instead of silently rounding,
clamping or interpreting a localized date. It validates the whole select
request before touching any option. Missing/duplicate values, disabled
optgroups and hidden/private options that would be selected or cleared all
refuse before effects. Radio group validation covers the complete same-root,
same-form named group, including external form-associated inputs. Unnamed
radios are independent. Groups crossing another owned record or unsupported
fields refuse before the click.

Bounded V1 reads can use four additional roles: `checkbox`, `radio`,
`slider` and `listbox`. Checkbox/radio elements can contain `checked`.
Options on a listbox can contain `selected`. Values for slider/date/text
remain strings. Existing element, option, ref, label and value limits apply.
Page text and complete reports have no fixed byte limit. Original button, textbox and combobox roles continue to discard
unknown checked/selected fields. Only the launcher's immutable exact
`(document URL, record ID, field ID)` entry grants disclosure of field state;
a read permission is separate from permission to change a target. Text-only
reads do not expose field state.

Text replacement emits input. Explicit date, range and select replacement
emit input then change. Native checkbox/radio clicks use the browser's native
event behavior. These are browser events, not a claim of trusted hardware
input. If an input handler replaces the logical target before change, the
driver retires the context without sending change to the replacement.

The driver retains exact document/ref, disabled, read-only, visibility,
same-origin frame and supported open-shadow-root checks. Private, hidden,
password/file, unsupported custom controls and remote action refs remain
unsupported. Owned focus-only typing, key presses, hover and auto-wait are
not enabled. Generic borrowed Playwright contexts keep their existing behavior
and do not inherit these owned-fixture guarantees.
