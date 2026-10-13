# Screenshot-based browser use

This example runs the Responses computer tool in a fresh, single-page Chromium profile.
It sends native computer actions to Playwright and returns screenshots to the SDK.
It uses no browser DOM tools, tab-state API, or partner-specific driver API.

Use Python 3.10 or later and import the helper with
`from openai import AsyncComputerToolset`. From the repository root, install the SDK and Playwright
in an isolated environment. Playwright is a separate example dependency, not an
SDK dependency. The official package is published by Microsoft at
[Playwright on PyPI](https://pypi.org/project/playwright/).

```sh
python -m venv .venv-computer
.venv-computer/bin/python -m pip install -e . --index-url https://pypi.org/simple
.venv-computer/bin/python -m pip install playwright==1.63.0 --index-url https://pypi.org/simple
.venv-computer/bin/python -m playwright install chromium
```

Playwright downloads Chromium from its official distribution. The example uses
a temporary profile and does not reuse your existing browser profile.

Run the included page with a model that supports the Responses computer tool and
an `OPENAI_API_KEY` from your environment:

```sh
.venv-computer/bin/python examples/computer/run.py --model YOUR_COMPUTER_MODEL
```

The default opens the bundled local fixture and blocks every outgoing page
request, including requests to other localhost ports. To open a site, allow its
origin explicitly. Each allowed origin includes its scheme, host, and port; paths
are not separate permissions. The driver refuses HTTP redirects, even within
an allowed origin. Open the approved destination URL directly instead.

```sh
.venv-computer/bin/python examples/computer/run.py \
  --model YOUR_COMPUTER_MODEL --url http://127.0.0.1:8080/ \
  --allow-origin http://127.0.0.1:8080 'Describe this page'
```

Use a throwaway site or sandbox you own. Keep credentials outside the browser,
since the agent can see and act on anything on its screen. This driver blocks
service workers and WebSockets and refuses unmatched intercepted HTTP requests.
Playwright routing is not a complete network sandbox; enforce deployment-level
egress policy before permitting untrusted websites.

The program asks before each state-changing action and each pending API safety
check. Only the literal return value `True` allows the action or check; closing
or refusing stops the run. Read-only screenshot and wait actions are allowed.
Approval covers the fixed action arguments. It does not freeze the screen or
focus. A driver must bind the target or reject a stale action when consent
depends on a particular target.
The helper supports exactly one `computer` (or `computer_use_preview`) tool.
It does not support other tools, streaming, background responses,
`previous_response_id`, or `conversation`. It replays the full input history.
It validates the inputs you pass to `run`. Your OpenAI client is trusted: custom
client hooks or transports can change requests after that validation. Your
application is responsible for those changes.

`AsyncComputerToolset(driver).run(client, params, ...)` owns the Responses loop,
up to `max_steps` calls to `responses.create`, including the final response.
Client retry settings still apply to each call. If your application already has a loop, use
`await AsyncComputerToolset(driver).execute(call, ...)`; it accepts the same
`approve_safety_checks` and `before_action` callbacks and returns a
`computer_call_output`. The caller owns browser cleanup in both cases. An
unsupported action, invalid coordinate, excessive scroll, or refusal stops before
later actions run. Pointer modifier keys and drag buttons are released even on errors.

Use synchronous driver methods with `ComputerToolset` and `async def` methods
with `AsyncComputerToolset`. The helper rejects known mismatches when you create
it. Preserve decorator metadata or return annotations when wrapping methods.
Opaque wrappers are checked when called, so their own code can run before the
helper detects a mismatch.

## Exercise without an API key

This smoke run sends scripted model responses through the real SDK HTTP client and
drives the real included page in headless Chromium. It verifies the greeting and
returned PNG. It does not call a model or external API.

```sh
.venv-computer/bin/python examples/computer/exercise.py
# Optional evidence from this scripted run:
.venv-computer/bin/python examples/computer/exercise.py --screenshot /tmp/computer-exercise.png
```

Contributors can type-check all three example files with the repository's strict
Pyright settings and the example environment above. Set up the repository's
Node tooling as described in [CONTRIBUTING.md](../../CONTRIBUTING.md) first:

```sh
PYRIGHT_PROJECT=scripts/pyrightconfig.computer-example.json \
  ./scripts/run-pyright --pythonpath .venv-computer/bin/python
```
