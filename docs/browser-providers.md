# Connect a hosted browser or desktop

Keep the OpenAI client, driver policies, and result checks in your application.
A provider supplies the browser or desktop. Its client does not replace the
OpenAI SDK or decide whether an action is approved.

## Choose an adapter

| Provider    | Environment                 | Ownership                                                                                                             | Example                                                                         |
| ----------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Browserbase | Browser over CDP            | Create a session, or borrow a browser. Close only the session and context the example creates.                        | [Setup and local exercise](../examples/browser/README_browserbase.md) |
| Browser Use | Standalone browser over CDP | Create a standalone browser and close its owned context. Sharing an active Browser Use engine session is unsupported. | [Setup and local exercise](../examples/browser/README_browser_use.md) |
| Daytona     | Existing desktop            | Borrow a running sandbox. Leave the sandbox running after the task.                                                   | [Setup and local exercise](../examples/computer-daytona/README.md)              |
| E2B         | Existing desktop            | Borrow a running sandbox. Remove the example's screenshot files and leave the sandbox running.                        | [Setup and local exercise](../examples/computer-e2b/README.md)                  |

Each linked guide contains the package versions, imports, connection code,
and a local exercise. Those exercises use synthetic provider responses and
test the adapter without starting a hosted session.

## Keep the connection boundary clear

Before giving a driver to the runner, configure the provider's network access
and session recording for your application. Keep provider credentials on the
server. A navigation policy in the SDK does not control the provider's network,
recordings, billing, or retention.

Use a fresh, isolated environment for each task. For borrowed environments,
confirm who owns cleanup and what may remain after the task. Await all started
work before releasing the environment. A stopped waiter does not prove that a
remote action stopped.

Check these parts of your connection:

- The screenshot and its dimensions describe the same display used by input actions.
- A browser action reaches the named tab and uses a current reference.
- The driver reports failures and uncertain outcomes instead of claiming success.
- Cleanup closes only owned resources and reports when release is unverified.
- File transfers have explicit approval and limits. A remote path is not a local file.

The browser adapters expose a smaller set of operations than the complete
browser helper. They do not automatically add file-transfer grants or desktop
control. The desktop adapters do not provide DOM references or browser tabs.

## Keep the same task logic

Pass the resulting driver to `BrowserToolset` or `ComputerToolset`, then keep
your normal approval callbacks and saved-result checks. Start with Responses
for open-ended tasks. Use Decisions only when your application can provide
the complete choices and arguments.

For the runner contract, see [browser tools](browser.md) and
[computer tools](../examples/computer/README.md). The provider-specific guide owns connection
details; the SDK guide owns tool dispatch. Successful local adapter tests
do not establish hosted account access or task success.
