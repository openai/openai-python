# Connect a browser or desktop

A provider supplies an environment. Your application keeps the OpenAI client,
approval policy and result checks. Configure the provider's network and
recording settings before handing its driver to a toolset. SDK navigation
policy does not control provider billing, retention, redirects or recordings.

## BrowserDriver

Implement `state()` and only the browser methods your application needs.
Wrap them in `BrowserToolset`, or implement async methods and use
`AsyncBrowserToolset`. Pass `members` to expose a smaller set of tools.
Mutating methods require `confirm`; navigation also requires `url_policy`.
Use current tab/document references and recheck them after approval. The
complete input and output contract is in [Browser tools](browser.md).

## ComputerDriver

Implement `screenshot()` and the input methods needed by your application
(such as `click`, `move`, `type`, `keypress`, and `scroll`).
Screenshots must be valid images whose dimensions match the display used for
input coordinates. Use `ComputerToolset` for synchronous methods or
`AsyncComputerToolset` for asynchronous methods, and pass a confirmation
callback. Keep safety decisions and task-level approvals in your application.
Inspect the result before retrying an uncertain effect. For a native local
example, see [the isolated desktop](../examples/computer-desktop/README.md).

For either protocol, give each task a fresh isolated environment when possible.
For borrowed resources, agree who owns cleanup and what may remain afterward;
close only what your application created. Await started work before releasing
it. A cancelled waiter does not prove that a remote action stopped. Keep
provider credentials on the server, and bound screenshots before decoding them.

No provider package or hosted account is required by the SDK. The SDK does not
include a vendor connection adapter or make claims about hosted account access.
Use Responses for open-ended tasks, or Decisions when the application supplies
all eligible choices and their arguments.
