# OpenAI Python API Library

[![PyPI version](https://img.shields.io/pypi/v/openai.svg)](https://pypi.org/project/openai/)

The OpenAI Python library provides convenient access to the `0`[OpenAI REST API](#rest-api) from any `0`[Python](#python) 3.7+ application. The `0`[library](#library) includes type definitions for all request `0`[params](#parameters) and response fields, and offers both synchronous and `0`[asynchronous](#asynchronous) clients powered by `0`[httpx](#http).

It is generated from our `0`[OpenAPI](#openapi) specification with `0`[Stainless](#stainless).

📘 **Explanation:** The OpenAI Python library is like a toolbox that makes it easy to use OpenAI's AI models in your Python programs. Imagine you have a smart robot assistant that can help you with various tasks like answering questions or generating text. This library helps you communicate with that robot using a set of rules (API) over the internet.

<details>
<summary><b>Table of Contents</b></summary>

- [Documentation](#documentation)
- [Installation](#installation)
- [Usage](#usage)
- [Polling Helpers](#polling-helpers)
- [Bulk Upload Helpers](#bulk-upload-helpers)
- [Streaming Helpers](#streaming-helpers)
- [Async Usage](#async-usage)
- [Streaming Responses](#streaming-responses)
- [Module-Level Client](#module-level-client)
- [Using Types](#using-types)
- [Pagination](#pagination)
- [Nested Params](#nested-params)
- [File Uploads](#file-uploads)
- [Handling Errors](#handling-errors)
- [Retries](#retries)
- [Timeouts](#timeouts)
- [Advanced](#advanced)
- [Microsoft Azure OpenAI](#microsoft-azure-openai)
- [Requirements](#requirements)
- [Versioning](#versioning)
- [Quick Definitions](#quick-definitions)

</details>

## Documentation

The `0`[REST API](#rest-api) documentation can be found on [platform.openai.com](https://platform.openai.com/docs). The full API of this `0`[library](#library) can be found in [api.md](api.md).

📘 **Explanation:** The OpenAI documentation is like a user manual for this system. It has all the instructions and information you need to use OpenAI's AI models in your Python programs. Think of it as a detailed guide that shows you how to communicate with your smart robot assistant.

## Installation

> [!IMPORTANT] The [SDK](#sdk) was rewritten in v1, which was released November 6th 2023. See the [v1 migration guide](https://github.com/openai/openai-python/discussions/742), which includes scripts to automatically update your code.

```sh
# install from PyPI
pip install openai
```

🚀 **Explanation:** To use this library, you need to install it first. This is like installing a new app on your phone, but for Python. Imagine you are adding a new tool to your toolbox so you can use it in your programming projects. The command `pip install openai` is like telling your computer to go to the Python app store (PyPI) and download the OpenAI tool for you.

## Usage

The full API of this library can be found in [api.md](api.md).

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-3.5-turbo",
)
```

💡 **Explanation:** Here's how you use the library to talk to the AI models. Think of this like having a conversation with your smart robot assistant. You set up the connection, ask it to say something, and then it responds. Let's break it down:

1. First, you import the necessary tools (`os` and `OpenAI`).
2. Then, you create a "client" - think of this as establishing a phone line to the AI.
3. You send a message to the AI, just like texting a friend.
4. The AI processes your message and sends back a response.

This code sets up the AI client and asks it to say "This is a test." It's like teaching a parrot to repeat a phrase!

## Polling Helpers

When interacting with the API some actions such as starting a `0`[Run](#run) and adding files to vector stores are `0`[asynchronous](#asynchronous) and take time to complete. The SDK includes helper functions which will poll the status until it reaches a terminal state and then return the resulting object. If an API method results in an action that could benefit from polling there will be a corresponding version of the method ending in '_and_poll'.

For instance to create a Run and poll until it reaches a terminal state you can run:

```python
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
)
```

⏳ **Explanation:** Some actions take time to complete, like starting a process or uploading files. Polling helpers keep checking until these actions are done. Imagine you are baking a cake and you keep checking the oven until the cake is ready. In this case, you're starting a task (like asking the AI to do some work) and then waiting until it's finished before moving on. The `create_and_poll` function does this waiting for you automatically, so you don't have to keep checking manually.

## Bulk Upload Helpers

When creating and interacting with vector stores, you can use polling helpers to monitor the status of operations. For convenience, we also provide a bulk upload helper to allow you to simultaneously upload several files at once.

```python
sample_files = [Path("sample-paper.pdf"), ...]

batch = await client.vector_stores.file_batches.upload_and_poll(
    store.id,
    files=sample_files,
)
```

📤 **Explanation:** You can upload multiple files at once and check their status. This is like sending a bunch of letters at the post office and waiting to see when they are all delivered. In programming terms, you're sending multiple files to the AI system at the same time, which can save a lot of time compared to uploading them one by one. The `upload_and_poll` function takes care of sending all the files and waiting until they're all properly received and processed.

## Streaming Helpers

The SDK also includes helpers to process streams and handle incoming events.

```python
with client.beta.threads.runs.stream(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Please address the user as Jane Doe. The user has a premium account.",
) as stream:
    for event in stream:
        if event.type == "thread.message.delta" and event.data.delta.content:
            print(event.data.delta.content[0].text)
```

🔄 **Explanation:** You can stream responses from the AI, which means you get parts of the response as they come in, instead of waiting for the whole thing. It's like watching a YouTube video as it loads rather than waiting for the entire video to download first. In this code:

1. You start a "stream" of information from the AI.
2. You give some instructions to the AI (like how to address the user).
3. As the AI generates its response, you get pieces of it one at a time.
4. You can process or display these pieces as they arrive, making the interaction feel more real-time and responsive.

This is particularly useful for long responses or when you want to show progress to the user while the AI is thinking.

## Async Usage

Simply import `AsyncOpenAI` instead of `OpenAI` and use `await` with each API call:

```python
import os
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

async def main() -> None:
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
        model="gpt-3.5-turbo",
    )

asyncio.run(main())
```

🔄 **Explanation:** You can use the library with `0`[asynchronous](#asynchronous) code, which lets your program do other things while waiting for the AI to respond. It's like cooking several dishes at once instead of one after the other. Here's what's happening:

1. You import a special version of the OpenAI client that works asynchronously.
2. You define a function (`main()`) that uses `await` to talk to the AI.
3. This allows your program to do other tasks while it's waiting for the AI's response.
4. Finally, you run this async function using `asyncio.run(main())`.

This is particularly useful in applications that need to handle multiple tasks simultaneously, like web servers or interactive applications.

## Streaming Responses

We provide support for streaming responses using `0`[Server Side Events (SSE)](#sse).

```python
from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True,
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")
```

🔄 **Explanation:** Streaming responses allow you to get and process the AI's reply piece by piece, as it's being generated. It's like reading a book as it's being written, page by page, instead of waiting for the entire book to be finished. This code:

1. Sets up a streaming connection to the AI.
2. Asks the AI to say "this is a test".
3. As the AI generates its response, it sends back small "chunks" of text.
4. The code prints out each chunk as it arrives, creating a smooth, flowing output.

This is great for creating more responsive and interactive applications, especially when dealing with longer AI responses.

## Module-Level Client

> [!IMPORTANT]
> We highly recommend instantiating client instances instead of relying on the global client.

We also expose a global client instance that is accessible in a similar fashion to versions prior to v1.

```python
import openai

# optional; defaults to `os.environ['OPENAI_API_KEY']`
openai.api_key = '...'

# all client options can be configured just like the `OpenAI` instantiation counterpart
openai.base_url = "https://..."
openai.default_headers = {"x-foo": "true"}

completion = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.choices[0].message.content)
```

🔧 **Explanation:** This section talks about a global client, which is like having a universal remote that works for all your devices. However, just like a universal remote might not have all the special features for each specific device, using a global client isn't always the best choice for complex programs. Here's what's happening:

1. You set up a global OpenAI client that can be used anywhere in your code.
2. You can configure various options for this client, like the API key and default settings.
3. You can then use this client to interact with the AI, like asking it how to list files in a directory.

While this method is simple and can be useful for quick experiments or small scripts, for larger projects, it's better to create specific client instances for different parts of your program. This gives you more control and makes your code easier to manage and test.

## Using Types

Nested request parameters are `0`[TypedDicts](#typeddict). Responses are [Pydantic models](https://docs.pydantic.dev) which also provide helper methods for things like:

- Serializing back into `0`[JSON](#json), `model.to_json()`
- Converting to a dictionary, `model.to_dict()`

```python
from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Can you generate an example json object describing a fruit?",
        }
    ],
    model="gpt-3.5-turbo-1106",
    response_format={"type": "json_object"},
)
```

🛠️ **Explanation:** The library uses typed requests and responses, which means it can help you catch mistakes while you write your code. Think of it as having a spell-checker for your programming instructions. Here's what this means:

1. When you send requests to the AI, you use special Python dictionaries (`0`[TypedDicts](#typeddict)) that help ensure you're providing the right kind of information.
2. When you get responses back, they come as Pydantic models, which are like smart containers for data.
3. These models have helpful methods, like turning the data back into JSON or into a regular Python dictionary.

In the example, we're asking the AI to create a `0`[JSON object](#json-object) describing a fruit. The library ensures we're formatting our request correctly and helps us work with the response easily. This type system acts like a safety net, catching potential errors before they cause problems in your program.

## Pagination

List methods in the OpenAI API are paginated.

This library provides auto-paginating iterators with each list response, so you do not have to request successive pages manually:

```python
import openai

client = OpenAI()

all_jobs = []
# Automatically fetches more pages as needed.
for job in client.fine_tuning.jobs.list(
    limit=20,
):
    # Do something with job here
    all_jobs.append(job)
print(all_jobs)
```

📄 **Explanation:** Some API responses are too large to send all at once, so they are split into pages. The library can automatically handle fetching these pages for you. It's like getting a long book in several smaller, manageable volumes instead of one big, heavy book. Here's how it works:

1. You start a request to list something, like jobs for fine-tuning AI models.
2. You set a limit (in this case, 20) for how many items you want per page.
3. The library automatically fetches new pages as you go through the list.
4. You can process each item (job) as it comes in, without worrying about the pagination.

This makes it much easier to work with large amounts of data, as you don't have to manually keep track of which page you're on or when to request the next page. The library handles all of that for you behind the scenes.

## Nested Params

Nested `0`[parameters](#parameters) are dictionaries, typed using `0`[TypedDict](#typeddict). Some parameters are nested dictionaries, which you can pass as dictionaries in your requests. For example:

```python
from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Can you generate an example json object describing a fruit?",
        }
    ],
    model="gpt-3.5-turbo-1106",
    response_format={"type": "json_object"},
)

```

```
📂 **Explanation:** Nested parameters allow you to organize complex information in a structured way, like having folders inside folders on your computer. Here's what's happening in this code:

1. We create an OpenAI 0[client](#client)</span> to communicate with the AI.
2. We use the 0[chat.completions.create](#chat-completions-create)</span> method to generate a response.
3. The `messages` parameter is a list containing a dictionary. This dictionary has two nested key-value pairs: "role" and "content".
4. We specify the AI model to use with the `model` parameter.
5. The 0[response_format](#response-format)</span> parameter is another nested dictionary, telling the AI to respond with a 0[JSON object](#json-object)</span>.

This nested structure allows us to provide detailed and organized instructions to the AI. In this case, we're asking it to generate a 0[JSON](#json)</span> object describing a fruit. The use of 0[TypedDict](#typeddict)</span> helps ensure that we're formatting these nested parameters correctly, reducing the chance of errors in our code.

## File Uploads

Request parameters that correspond to file uploads can be passed as `bytes`, a [`PathLike`](https://docs.python.org/3/library/os.html#os.PathLike) instance or a tuple of `(filename, contents, media type)`.
```

📁 **Explanation:** You can upload files directly to the API, which can be used for things like fine-tuning models. It's like uploading a document to a website so that the site can use the information in the document. In this example:

1. We import the `Path` class to work with file paths easily.
2. We create an OpenAI client.
3. We use the `files.create` method to upload a file.
4. We specify the file path and its purpose (in this case, for fine-tuning a model).

This is useful when you need to provide large amounts of data to the AI, such as training data for customizing models.

## Handling Errors

When the library is unable to connect to the API (for example, due to network connection problems or a timeout), a subclass of `openai.APIConnectionError` is raised.

When the API returns a non-success status code (that is, 4xx or 5xx response), a subclass of `openai.APIStatusError` is raised, containing `status_code` and `response` properties.

All errors inherit from `openai.APIError`.

```python
import openai
from openai import OpenAI

client = OpenAI()

try:
    client.fine_tuning.jobs.create(
        model="gpt-3.5-turbo",
        training_file="file-abc123",
    )
except openai.APIConnectionError as e:
    print("The server could not be reached")
    print(e.__cause__)  # an underlying Exception, likely raised within httpx.
except openai.RateLimitError as e:
    print("A 429 status code was received; we should back off a bit.")
except openai.APIStatusError as e:
    print("Another non-200-range status code was received")
    print(e.status_code)
    print(e.response)
```

⚠️ **Explanation:** The library provides error handling for different types of errors that can occur while interacting with the API. It's like having a plan for what to do if something goes wrong while you're working on a project. Here's what's happening:

1. We set up a try-except block to catch different types of errors.
2. We attempt to create a fine-tuning job.
3. If there's a connection error, we catch it and print a message.
4. If we hit a rate limit (too many requests), we catch that specific error.
5. For any other API errors, we catch them and print details about the error.

This error handling helps you write more robust code that can gracefully handle problems when they occur, rather than crashing unexpectedly.

## Retries

Certain errors are automatically retried 2 times by default, with a short exponential backoff. Connection errors (for example, due to a network connectivity problem), 408 Request Timeout, 409 Conflict, 429 Rate Limit, and >=500 Internal errors are all retried by default.

You can use the `max_retries` option to configure or disable retry settings:

```python
from openai import OpenAI

# Configure the default for all requests:
client = OpenAI(
    # default is 2
    max_retries=0,
)

# Or, configure per-request:
client.with_options(max_retries=5).chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "How can I get the name of the current day in Node.js?",
        }
    ],
    model="gpt-3.5-turbo",
)
```

🔁 **Explanation:** Some errors are automatically retried by the library. You can configure how many times to retry or disable retries. It's like trying to reconnect your WiFi if it drops the first time. Here's what this code does:

1. We can set a default number of retries for all requests when creating the client.
2. We can also set the number of retries for a specific request using `with_options()`.
3. If an error occurs that's eligible for retry, the library will automatically try again up to the specified number of times.

This feature helps make your application more resilient to temporary network issues or server problems.

## Timeouts

By default requests time out after 10 minutes. You can configure this with a `timeout` option, which accepts a float or an [`httpx.Timeout`](https://www.python-httpx.org/advanced/#fine-tuning-the-configuration) object:

```python
from openai import OpenAI

# Configure the default for all requests:
client = OpenAI(
    # 20 seconds (default is 10 minutes)
    timeout=20.0,
)

# Override per-request:
client.with_options(timeout=5.0).chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "How can I list all files in a directory using Python?",
        }
    ],
    model="gpt-3.5-turbo",
)
```

⏲️ **Explanation:** You can set how long to wait for a response before timing out. It's like setting a timer for how long you'll wait for a friend before leaving. Here's what's happening:

1. We can set a default timeout for all requests when creating the client.
2. We can also set a timeout for a specific request using `with_options()`.
3. If the API doesn't respond within the specified time, the request will be cancelled and an error will be raised.

This helps prevent your application from hanging indefinitely if there's a problem with the API or network.

## Advanced

### Logging

We use the standard library [`logging`](https://docs.python.org/3/library/logging.html) module.

You can enable logging by setting the environment variable `OPENAI_LOG` to `debug`.

```shell
$ export OPENAI_LOG=debug
```

📜 **Explanation:** Logging helps you see what's happening behind the scenes in your application. It's like having a detective's notebook that records everything that happens. By setting the `OPENAI_LOG` environment variable to `debug`, you're telling the library to write detailed information about its operations, which can be very helpful for troubleshooting problems.

## Microsoft Azure OpenAI

To use this library with [Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/overview), use the `AzureOpenAI` class instead of the `OpenAI` class.

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2023-07-01-preview",
    azure_endpoint="https://example-endpoint.openai.azure.com",
)

completion = client.chat.completions.create(
    model="deployment-name",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)

print(completion.to_json())
```

🔧 **Explanation:** If you are using OpenAI through Microsoft Azure, you need to use the AzureOpenAI class. It's like using a different key to unlock the same door. Here's what's happening:

1. We import the `AzureOpenAI` class instead of the regular `OpenAI` class.
2. We create a client with Azure-specific parameters like `api_version` and `azure_endpoint`.
3. We can then use this client to interact with the AI in the same way as before.

This allows you to use OpenAI's capabilities through Microsoft's Azure cloud platform, which might be preferred for certain business or integration reasons.

## Requirements

Python 3.7 or higher.

💻 **Explanation:** You need Python 3.7 or higher to use this library. It's like needing a specific version of an app to use certain features. Make sure your Python version is up to date before trying to use this library.

## Versioning

This package generally follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions, though certain backwards-incompatible changes may be released as minor versions:

1. Changes that only affect static types, without breaking runtime behavior.
2. Changes to library internals which are technically public but not intended or documented for external use. _(Please open a GitHub issue to let us know if you are relying on such internals)_.
3. Changes that we do not expect to impact the vast majority of users in practice.

We take backwards-compatibility seriously and work hard to ensure you can rely on a smooth upgrade experience.

We are keen for your feedback; please open an [issue](https://www.github.com/openai/openai-python/issues) with questions, bugs, or suggestions.

🔄 **Explanation:** The library follows versioning rules to ensure backward compatibility. It's like updating an app on your phone to get new features without breaking the old ones. The developers try to make sure that when they release new versions:

1. Your existing code will still work (backwards-compatibility).
2. You know what to expect from each update (following SemVer conventions).
3. You have a way to give feedback or report problems (through GitHub issues).

This helps you keep your projects up-to-date while minimizing the risk of unexpected breaks in your code.

## Quick Definitions

- `<span id="rest-api">`**REST API**: A way for computer systems to communicate over the internet using standard HTTP methods. [Learn more](https://en.wikipedia.org/wiki/Representational_state_transfer)
- `<span id="python">`**Python**: A popular programming language known for its simplicity and readability. [Learn more](https://www.python.org/)
- `<span id="library">`**Library**: A collection of pre-written code that programmers can use to simplify their work. [Learn more](https://en.wikipedia.org/wiki/Library_(computing))
- `<span id="parameters">`**Parameters**: Values passed to a function or method to specify how it should operate. [Learn more](https://docs.python.org/3/glossary.html#term-parameter)
- `<span id="asynchronous">`**Asynchronous**: A way of programming that allows multiple operations to happen at the same time without waiting for each other to complete. [Learn more](https://docs.python.org/3/library/asyncio.html)
- `<span id="http">`**HTTP**: The protocol used for transmitting data over the internet. [Learn more](https://developer.mozilla.org/en-US/docs/Web/HTTP)
- `<span id="openapi">`**OpenAPI**: A specification for machine-readable interface files for describing, producing, consuming, and visualizing RESTful web services. [Learn more](https://www.openapis.org/)
- `<span id="stainless">`**Stainless**: A tool for generating API clients from OpenAPI specifications. [Learn more](https://stainlessapi.com/)
- `<span id="sdk">`**SDK**: Software Development Kit, a set of tools for creating software applications. [Learn more](https://en.wikipedia.org/wiki/Software_development_kit)
- `<span id="run">`**Run**: In the context of OpenAI, a Run is an execution of an Assistant on a Thread. [Learn more](https://platform.openai.com/docs/api-reference/runs)
- `<span id="sse">`**SSE (Server-Sent Events)**: A technology that allows a web page to get updates from a server automatically. [Learn more](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- `<span id="typeddict">`**TypedDict**: A type hint class in Python used to define dictionaries with a fixed set of keys, each with a specified type. [Learn more](https://docs.python.org/3/library/typing.html#typing.TypedDict)
- `<span id="json">`**JSON**: JavaScript Object Notation, a lightweight data interchange format. [Learn more](https://www.json.org/json-en.html)
- `<span id="json-object">`**JSON object**: A data structure in JSON format, consisting of key-value pairs. [Learn more](https://www.json.org/json-en.html)
- `<span id="client">`**Client**: An object or library that provides an interface to interact with a service or API. [Learn more](https://en.wikipedia.org/wiki/Client_(computing))
- `<span id="chat-completions-create">`**chat.completions.create**: A method in the OpenAI API used to generate chat completions. [Learn more](https://platform.openai.com/docs/api-reference/chat/create)
- `<span id="response-format">`**response_format**: A parameter used to specify the desired format of the API response. [Learn more](https://platform.openai.com/docs/api-reference/chat/create#chat/create-response_format)
