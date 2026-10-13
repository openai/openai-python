# Resource desk: one task across three apps

For installed Chrome on Linux, see [Choose a local browser](../browser/README.md#choose-a-local-browser).

Start in Postbox, choose the requested job, compare rooms in Roomboard, and send its confirmation in Dispatch. All three apps run locally. A saved booking and a saved outgoing message must both match the request. If the agent reserves a room that is too small or expensive, the run remains unverified. The app keeps that choice so you can inspect the mistake. In Rooms, **Revise booking** removes the selected local booking and its local confirmation record, with approval, so you can compare rooms and try again. It does not undo a real email or external booking.

The default API is Responses. Decisions uses the same browser controls with a fresh list of every available button and a Done choice on each turn. It receives the visible page and previous action results, including failures. Choosing Done early does not pass verification. A failed check appears in the next Decisions observation without revealing the correct room.

## Start here

Use Python 3.10 or later. The CLI terminal runner supports macOS and Linux. On other platforms, use `open_workflow` with your own asynchronous approval callback. From the SDK's `examples` directory, install OpenAI and the optional browser dependency:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install openai playwright==1.63.0
.venv/bin/python -m playwright install chromium
.venv/bin/python browser-workflow/run.py --mode serve
```

If your system blocks the default browser cache, set `PLAYWRIGHT_BROWSERS_PATH` to a writable directory before both installation and launch.

Open the address printed in your terminal. You can click through the apps without a key. Press Ctrl+C to close the local server.

Next, check both workflows through a real browser without calling any API:

```sh
.venv/bin/python browser-workflow/exercise.py
.venv/bin/python browser-workflow/exercise_runners.py
.venv/bin/python browser-workflow/exercise_recovery.py storage
.venv/bin/python browser-workflow/exercise_recovery.py startup
```

All commands should print PASS. The first checks saved results, refusal, Stop, and stale references. The second runs Responses and Decisions against a local mock transport. It does not test model quality.

## Run with your API key

Set `OPENAI_API_KEY` and `OPENAI_MODEL` in your shell to a key and model available to your project. Then run:

```sh
.venv/bin/python browser-workflow/run.py --headed
.venv/bin/python browser-workflow/run.py --headed --api decisions --fixture B
```

The program shows the current label of a button before a click. Enter `y` to allow an action. Any other answer stops the run. Ctrl+C also stops it. Each run owns a new disposable browser profile. It never sends SDK credentials to Chromium. Navigation stays within the three workflow pages for the selected fixture. The browser can load their installed assets. There is no automatic replay of an action after refusal or Stop.

The last line is JSON, for example `{"status":"verified"}`. Other outcomes are `unverified`, `refused`, `failed` or `stopped`. Failed or stopped runs exit with a nonzero code. A completed run can remain unverified, so batch scripts must check the JSON status too.

Use `--receipt /absolute/new-file.json` to save a private local record. It includes request counts, observed action or selection IDs, and the cleanup outcome. Booking and correspondence values come from the last completed saved-record check; after Stop, they may be absent. It may include names and addresses from your data. The file must not exist, has owner-only permissions and a 1 MiB limit. The default console result contains only status. The record never includes API keys, model names or raw HTTP errors.

Private receipts require POSIX file permissions. On Windows, omit `--receipt`; the workflow refuses that option before opening a workspace.

## Change the exercise

Use `--data /absolute/fixtures.json --fixture C` with your own synthetic records. Copy `assets/fixtures.json` as a starting point. Each top-level ID needs:

- `requestId`: the exact ID of one request. The UI, prompt, and verifier use this value.
- `task`: instructions for the selected request, without repeating its ID.
- `requests`: objects with `id`, `name`, `recipient`, `time`, `people`, `equipment`, and `budget`.
- `slots`: objects with `id`, `room`, `time`, `capacity`, an `equipment` string array, and `price`.

Use nonempty strings for text fields and unique IDs within each list. Fixture IDs cannot contain unpaired Unicode surrogates because each fixture has its own URL. Request and slot IDs also cannot contain NUL or carriage return; these do not round-trip through the pages unchanged. Line feeds, valid Unicode, and quotes are supported. People and capacity must be positive whole numbers. Budget and price must be finite, nonnegative numbers. Amounts and quantities must not exceed 9,007,199,254,740,991, so Python and the browser keep the same value. A slot's equipment must be an array of nonempty strings. Invalid data fails at startup with the field name, before a browser opens.

The task selects the cheapest slot that satisfies time, capacity, equipment and budget. No expected room ID belongs in the fixture or candidate generator. Use `.test` email addresses. New data does not require changes to the runner. This is also the seam for independently authored future tests.

## Use different apps

This example only verifies its own data stores. It cannot verify an arbitrary URL. To adapt it, make these four explicit changes in `workflow.py`:

1. Replace `serve`, `page_urls`, and `urls` in `open_workflow` with the exact pages and resources you own. Keep navigation in `url_policy` limited to `page_urls`. Allow the pages and their required assets through `driver.guard`. Use the ordinary Playwright driver for apps you did not install as owned fixtures. Never opt a borrowed browser into owned fixture mode.
2. Replace the confirmation callback with your product policy. Show the person the intended effect before booking, sending, or changing a record. Refusal and Stop must still prevent later actions.
3. Replace `stored` and `verify` with read-only checks against each app's authoritative records. Require the room and recipient to match across both records. A model's final message does not prove a booking.
4. Review what Decisions can choose in the new apps. Supply every permitted choice from the current visible state and meaningful prior results. If the next steps cannot be enumerated safely, use Responses.

Use test accounts and disposable data when you adapt the example. These changes are application policy and result checks, not a new browser driver.
