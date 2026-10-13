# Use the browser driver with a managed session

This example creates a Browserbase session, connects over CDP, and gives
your callback a restricted browser driver. You can also supply a Playwright
Browser that your application already owns. Both paths create and close their
own context.

## Run the local exercise

Download **Source code (zip)** from the
[Python SDK release page](https://github.com/openai/openai-python/releases/latest).
Unpack it and open its root folder in your terminal. If you are in
`examples`, run `cd ..` first. Use Python 3.10 or later and install the
SDK and optional packages in a separate environment:

```sh
python3 -m venv .venv-browser
. .venv-browser/bin/activate
python -m pip install --upgrade openai 'browserbase==1.20.0' 'playwright==1.63.0'
python -m playwright install chromium
python examples/browser/exercise_browserbase.py
```

Use your configured package registry. If Playwright 1.63.0 already has its
Chromium installed, skip the browser install command. The exercise starts a
new, private profile with Chromium's sandbox enabled. It uses an HTTPX mock
transport for provider responses and sends no model requests. On success, the
command exits with status 0 and each JSON case reports `"pass": true`. The final
summary gives the number of passing cases and `"apiRequests": 0`.

## Pass a driver to a Responses run

Place application code next to this example. Supply your already-configured
AsyncBrowserbase and AsyncOpenAI clients, Playwright's `chromium`, response
parameters, and application policies. The example does not close those clients.

```python
from openai.lib.browser import AsyncBrowserToolset
from openai.lib.responses_tool_runner import AsyncResponsesToolRunner
from browserbase_session import with_browserbase_session, with_borrowed_browser


async def run_owned(provider, chromium, client, params, config, confirm, url_policy, receipts, cancelled):
    async def work(driver, stopped):
        browser = AsyncBrowserToolset(driver, confirm=confirm, url_policy=url_policy)
        return await AsyncResponsesToolRunner(browser=browser).run(client, params, cancelled=stopped)

    return await with_browserbase_session(
        provider, chromium, config, work, on_cleanup=receipts.append, cancelled=cancelled
    )


async def run_borrowed(connected_browser, client, params, config, confirm, url_policy, receipts, cancelled):
    async def work(driver, stopped):
        browser = AsyncBrowserToolset(driver, confirm=confirm, url_policy=url_policy)
        return await AsyncResponsesToolRunner(browser=browser).run(client, params, cancelled=stopped)

    return await with_borrowed_browser(
        connected_browser, config, work, on_cleanup=receipts.append, cancelled=cancelled
    )
```

For an owned session, pass
`{"project_id": project_id, "allowed_origins": ["https://your-application.example"]}`.
Use exact HTTP or HTTPS origins without paths or trailing slashes. Borrowed
mode needs only `{"allowed_origins": allowed_origins}` and never closes the
caller's Browser. Both async policies must return exactly `True` to permit an
action. Reads and screenshots can disclose page content, so give the driver
access only to suitable pages.

For human consent tied to a specific page or control, use original refs checked at execution.
Disable `key` and refuse `type` with a `None` target; both use current focus.
The prior state is not a document lock. See the [approval contract](../../docs/browser.md#confirmation-navigation-and-recovery).

## Retain the task when you stop

`on_cleanup(handle)` is required on both entry points. The application must
store this private handle synchronously, without throwing or starting more
work. The scope calls it once, after admitted work and initial cleanup finish,
even when an exception or task cancellation changes form through a shield or
gather. If the callback fails, delivery cannot be guaranteed.

During setup, Stop interrupts the wait for context creation and route
installation. Pending setup remains owned through cleanup.

Retain the scope task itself. On Stop, cancel that task and then await it before
using the receipt:

```python
import asyncio
from browserbase_session import with_browserbase_session


async def stop_owned(provider, chromium, config, work, wait_for_stop):
    receipts = []
    scope = asyncio.create_task(
        with_browserbase_session(provider, chromium, config, work, on_cleanup=receipts.append)
    )
    await wait_for_stop()
    scope.cancel()
    try:
        await scope
    except asyncio.CancelledError:
        pass
    if receipts:
        cleanup = await receipts[0].retry()
        return cleanup["status"]
```

Cancelling only an outer `asyncio.shield(scope)` does not stop the scope and
does not imply a receipt exists. Keep and join the original task. Once your
callback starts, the scope waits for it to finish before closing its context.

In `work`, pass the supplied `stopped` predicate as `cancelled=stopped` to
every `AsyncResponsesToolRunner.run()`, `AsyncResponsesToolRunner.iterate()`,
and `AsyncBrowserToolset.execute()` call. Those helpers reject new work after
Stop when they receive that predicate. The scope cannot prevent direct driver
calls that ignore Stop. Your callback must await all browser work and must not
use the driver after it returns.

On success the scope returns `{"result": result, "status": status, "cleanup": handle}`.
Directly awaited failures also offer `error.cleanup`. Use `on_cleanup` as
the authoritative receipt across task wrappers. Never send that handle to a
model or put it in logs. Concurrent `retry()` calls share one attempt.
Owned cleanup validates the saved ID and project before requesting release and
reading back the status. Each attempt has a deadline and at most three reads.
It never retries a create without a verified result. Borrowed cleanup closes
only its new context. Status `complete`, `pending`, or `unverified` reports
cleanup observations, not task success, billing, or erasure.

The driver advertises 15 generic members. It does not enable file transfers,
arbitrary downloads, rich fixture grants, or desktop control. Context routing
and blocked service workers are not a provider firewall. The launcher owns its
pre-import environment, headers, provider logging, and HTTP client. The
example cannot redact logs a supplied client already wrote. The local exercise
does not prove hosted access, remote context support, release, or cost.

## What the generic driver can protect

Use this driver only on pages your application has approved for model access.
A page controls its own scripts and DOM. The read filters omit common private
controls; they cannot make a hostile signed-in page safe. Screenshots can show
anything visible. Do not rely on DOM markers as a security boundary against
the page that creates them.

For HTTP(S) tabs, this driver's borrowed and owned state reports only the
origin. It omits paths, queries, fragments, and URL credentials. Borrowed
state keeps `about:blank` as-is and reports only the scheme for other URLs.
The borrowed URL projection must fit 2,048 UTF-8 bytes. The separate 16 KiB
text and 64 KiB report budgets apply to page reads. Page titles and visible
content may still be sensitive, so limit access to suitable pages.

`find` filters matches before its 100-result limit, but it keeps the same
bounded scan and report budgets as `read_page`. A `report_limit` or
`work_limit` omission means later controls may still match. An empty result
with either omission does not mean that the page has no match.

The configured provider client supplies the CDP connection endpoint. Trust it
as part of the connection setup, keep endpoints out of logs and model input,
and configure network access in the environment. A browser navigation policy
does not restrict where the application opens its CDP connection.
 This trust includes HTTP discovery and WebSocket redirects followed by Playwright. A connection to a compromised provider requires separate host-network isolation; checking only the initial URL would not enforce that boundary.