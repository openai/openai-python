# Structured browser example

This example uses the SDK's browser function tools and mixed Responses runner.
It reads page elements, fills a synthetic reservation form, calls an ordinary
function, manages tabs, and returns a screenshot as an image. The SDK owns the
model loop. Playwright owns the browser.

Download **Source code (zip)** from the
[Python SDK release page](https://github.com/openai/openai-python/releases/latest)
and unpack it to get the example files. Run the commands below from that
unpacked folder's root. If you arrived here from the guide's `examples`
directory, run `cd ..` first.

Use Python 3.10 or later. Install the SDK and Playwright in a separate
environment. Playwright is an optional example dependency.

```sh
python3 -m venv .venv-browser
.venv-browser/bin/python -m pip install --upgrade openai 'playwright==1.63.0'
.venv-browser/bin/python -m playwright install chromium
```

## Choose a local browser

The local Browser examples use Playwright's bundled Chromium by default.
On Linux, when bundled Chromium cannot start with the host's sandbox, install
Google Chrome through your system's approved package setup. Then set:

```sh
export OPENAI_EXAMPLE_BROWSER_CHANNEL=chrome
```

This selects the installed Google Chrome for the structured Browser example,
read-only reader, inspector, evaluation, resource-desk workflow, and the
Fieldwork dashboard (including its host browser in mixed mode). Each launch
still uses a new disposable profile with the browser sandbox enabled.
The setting accepts only `chrome`; unset it to return to bundled Chromium.
Preflight checks the bundled executable by default. With `chrome`, it checks
the channel selection and reports that availability and sandbox support will
be checked at launch. It does not establish that Chrome is installed.

## Run the example

Set `OPENAI_API_KEY` and `OPENAI_MODEL` in your process environment. Choose a
model available to your account that supports function tools and image inputs.
The example serves only synthetic pages on a temporary loopback port and uses
a fresh Chromium profile. It does not reuse your browser accounts.

```sh
.venv-browser/bin/python examples/browser/run.py
# Stream model events and run completed tool calls after each response:
.venv-browser/bin/python examples/browser/run.py --stream
# Explicit early execution can act before the response finishes:
.venv-browser/bin/python examples/browser/run.py --stream --eager
```

The example asks before each action that changes browser state. `--auto-approve-fixture`
approves those actions within this bundled, disposable fixture. The program verifies the
reservation and tab state independently of the model's answer. A successful
run prints `PASS: browser state confirms the reservation and tab task.`

To exercise the driver and SDK without a key or model request, including stale
references, hidden and password content, redirects, and popups:

```sh
.venv-browser/bin/python examples/browser/exercise.py --screenshot /tmp/browser-exercise.png
```

The driver binds references to observed elements and rejects stale references.
`read_page` and `find` return a V1 object with `version`, `text`, `elements`,
and `omitted`. Reads cap work and retained refs before constructing the report.
They keep visible form labels and bounded select options, but omit passwords,
hidden fields, private controls and executable option values that do not fit.
`find` scans the current page, even as the first call after navigation.
Like `read_page`, it replaces earlier refs. `get_page_text`
still returns a bounded string and preserves refs. Use `read_page` when you
need omission reasons as well as text. References are checked against current
visible label, native control type, enabled state and DOM destination before
use. If these change, read or find again. Arbitrary JavaScript listener changes
are outside this DOM check.

All pages share context-level HTTP interception. The driver blocks unapproved
origins, checks redirect targets before following them, and blocks WebSockets,
service workers, and downloads. These browser controls do not replace a container
or VM with network policy when you run untrusted websites.

Contributors can check all example files under the repository's strict Pyright
settings, using an environment with Playwright installed:

```sh
PYRIGHT_PROJECT=scripts/pyrightconfig.browser-example.json \
  ./scripts/run-pyright --pythonpath .venv-browser/bin/python
```
