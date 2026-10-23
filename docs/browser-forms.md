# Browser form fields

A BrowserDriver may implement `type` for literal field replacement,
`click` for a current control reference, and `select_option` for option
values. The SDK asks the registered confirmation callback before each change;
the driver determines which native controls it supports.

Structured reads can report `checkbox`, `radio`, `slider` and `listbox`,
as well as `button`, `textbox` and `combobox`. Checkbox and radio elements
may include Boolean `checked`; listbox options may include Boolean
`selected`. Values remain strings. The SDK validates and copies known
fields; it does not impose a fixed count limit on returned controls or options.

Drivers own field privacy and reference identity. Do not expose password,
file or private values merely because a browser supplies them. Validate a
complete select request before changing a field. Check disabled/read-only
state and reject references invalidated while an operator decided. After an
uncertain toggle, inspect or retire the session instead of retrying it.

The [Fieldwork example](../examples/browser-use-demo/README.md) implements
only its owned reservation form's text, select and submit controls.
