# Use a standalone browser-use browser

This example owns a standalone browser through the optional
`browser-use-sdk==3.4.2` client. It opens one CDP connection and passes a fresh,
restricted browser context to your callback. The callback can use
`AsyncBrowserToolset` and the ordinary `AsyncResponsesToolRunner`.

## Run the local exercise

Download **Source code (zip)** from the
[Python SDK release page](https://github.com/openai/openai-python/releases/latest).
Unpack it and open its root folder in your terminal. If you are in
`examples`, run `cd ..` first. Use Python 3.10 or later and install the
SDK and optional dependencies in a separate environment:

```sh
python3 -m venv .venv-browser
. .venv-browser/bin/activate
python -m pip install --upgrade openai 'browser-use-sdk==3.4.2' 'playwright==1.63.0'
python -m playwright install chromium
python examples/browser/exercise_browser_use.py
```

If Playwright 1.63.0 already has Chromium installed, skip the browser install
command. The exercise creates a new private profile with Chromium's sandbox
enabled. A loopback server supplies synthetic provider HTTP responses. The
exercise sends no model requests and uses no provider account. Success prints
25 passing cases.

## Run a task in an owned browser

Place application code next to this example. Supply your configured OpenAI
client, response parameters, a trusted provider key and base URL, and your
application's approval policies. The scope creates and closes its own provider
client; it does not close your OpenAI client.

```python
from openai.lib.browser import AsyncBrowserToolset
from openai.lib.responses_tool_runner import AsyncResponsesToolRunner
from browser_use_session import with_standalone_browser


async def run_owned(chromium, client, params, provider_key, provider_base_url,
                    allowed_origins, confirm, url_policy, receipts, cancelled):
    async def work(driver, stopped):
        browser = AsyncBrowserToolset(driver, confirm=confirm, url_policy=url_policy)
        return await AsyncResponsesToolRunner(browser=browser).run(
            client, params, cancelled=stopped
        )

    return await with_standalone_browser(
        chromium, allowed_origins, work,
        api_key=provider_key,
        base_url=provider_base_url,
        on_cleanup=receipts.append,
        cancelled=cancelled,
    )
```

Pass a list of exact HTTP or HTTPS origins, without paths or trailing slashes.
The owner snapshots this list at admission before creating a provider client.
Changes to the caller's list while create or connect is pending cannot expand
the approved origins. Both async policies must return exactly `True` before a
change or navigation proceeds. Reads and screenshots can disclose content, so
grant only pages appropriate for the task.

Use the lightweight provider SDK only. The browser-use agent's BrowserSession
attaches browser-wide observers which can modify other contexts. This example
does not support simultaneous use of that live agent. If your application
already owns a Playwright Browser, see
[the borrowed-browser example](README_browserbase.md#pass-a-driver-to-a-responses-run).
It requires no browser-use provider session and closes only its new context.

## Stop and cleanup

`on_cleanup(handle)` is required. Store the private handle synchronously without
throwing or starting more work. The scope calls it once after admitted setup,
the entire callback, and initial cleanup have finished, including after task
cancellation. If the callback throws or returns an awaitable, delivery cannot
be guaranteed. If a Task is cancelled before the scope starts, it admits no
work and delivers no handle.

Keep the scope task itself. On Stop, cancel that task and join it:

```python
import asyncio
from browser_use_session import with_standalone_browser


async def stop_owned(chromium, allowed_origins, work, provider_key, provider_base_url,
                     wait_for_stop):
    receipts = []
    scope = asyncio.create_task(with_standalone_browser(
        chromium, allowed_origins, work,
        api_key=provider_key, base_url=provider_base_url,
        on_cleanup=receipts.append,
    ))
    await wait_for_stop()
    scope.cancel()
    try:
        await scope
    except asyncio.CancelledError:
        pass
    if receipts:
        return (await receipts[0].retry())["status"]
```

Cancelling only an outer `asyncio.shield(scope)` does not stop the owned scope
or imply that a receipt exists. Direct results and directly awaited exceptions
also contain a cleanup handle. Use `on_cleanup` across Task, gather, and shield,
which can transform cancellation exceptions. Never log or send this handle to
a model or put it in tool output.

Your `work` callback must pass its supplied `stopped` predicate to every
runner `run()`, runner `iterate()`, or toolset `execute()` call as
`cancelled=stopped`. Those helpers then refuse later work after Stop. The scope
cannot forcibly revoke direct driver calls that ignore Stop. Await all browser
work and stop using the driver before your callback returns.

The owner creates one standalone browser with zero client retries, a one-minute
provider timeout, no proxy, and recording disabled. It saves the parsed UUID
and requires the same ID, active status, and an explicitly returned
`agentSessionId=None` before CDP. A missing field remains unverified.
After drain, it closes its own fresh context and CDP connection, checks the
same ID and standalone status again, requests Stop, and reads back stopped.
Concurrent cleanup retries share one attempt on the saved ID.

Cleanup returns `complete`, `pending`, or `unverified`. An uncertain create,
wrong ID, or agent-owned response cannot authorize Stop. The owner never lists,
guesses an ID, or repeats create. HTTP or local close failures report
`pending`. HTTPX's 2.5-second timeout limits inactivity; it is not a deadline
for the whole operation.

The generic driver exposes 15 members. Its guarded context blocks service
workers and downloads, but context routing is not a provider or OS firewall.
The application controls its environment and logging before importing provider
packages. The example sanitizes its own errors. The local exercise does not
prove hosted access, remote isolation, provider permissions, release, or cost.

The configured provider and base URL are trusted connection setup. Their CDP
endpoint may differ from the API host. Keep that endpoint private and enforce
connection policies in your application or network environment. For page and
URL disclosure limits, see the generic borrowed-browser guide. This trust includes HTTP discovery and WebSocket redirects followed by Playwright. A connection to a compromised provider requires separate host-network isolation; checking only the initial URL would not enforce that boundary.

Each cleanup attempt bounds its local close wait. A pending local close cannot
block the provider identity check and Stop after application work has drained.
Cleanup reports complete only after both local close and matching provider Stop
are confirmed; retries wait for the same pending close.
