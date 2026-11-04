# Fieldwork

Book a table in a synthetic local browser. Fieldwork reads the form, asks before
submitting, and verifies both the confirmation and all saved fields. Watch the
actual browser image, take control, type or click, return control to the agent,
or stop. References from an older control phase cannot authorize an action.

Use Python 3.10 or later. From the Python SDK checkout or source archive root,
install this source and the browser dependency:

```sh
python3 -m venv .venv-browser
. .venv-browser/bin/activate
python -m pip install -e . playwright==1.63.0
python -m playwright install chromium
```

On Linux, if bundled Chromium cannot start with its sandbox enabled, use a
locally installed Chrome. Set this before starting the server or local checks:

```sh
export OPENAI_EXAMPLE_BROWSER_CHANNEL=chrome
```

Leave the variable unset to use Playwright's bundled Chromium. Both choices
keep the browser sandbox enabled.

Start the server in the same shell:

```sh
python examples/browser-use-demo/server.py
```

Open the private URL printed in your terminal. Rehearsal uses Decisions to
choose among local scripted actions and makes no model request. For Live mode,
set `OPENAI_API_KEY` and `OPENAI_MODEL` on the server before launch. Live
defaults to Responses; select Decisions to compare the candidate-based runner.
API-specific model names can use `OPENAI_RESPONSES_MODEL` and
`OPENAI_DECISIONS_MODEL`. Live requests can spend API credits.

The one-page `booking.py` adapter trusts only Fieldwork's own reservation
fixture and refuses every other network route. It deliberately exposes only
the three form effects and read tools required here. It is not a driver for
arbitrary sites. See [the BrowserDriver guide](../../docs/browser.md) for the
SDK interface. For a smaller read-only example, see
[the local reader](../browser/README_read_only.md).

Local checks, without a model key:

```sh
python examples/browser-use-demo/exercise.py
python examples/browser-use-demo/exercise_ui.py
```
