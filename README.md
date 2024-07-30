# OpenAI Python API library

![PyPI version](https://img.shields.io/pypi/v/openai.svg) ![OpenAI](https://img.shields.io/badge/OpenAI-blue?logo=openai&logoColor=white&labelColor=gray) ![GitHub](https://img.shields.io/badge/GitHub-blue?logo=github&labelColor=gray) ![GitHub contributors](https://img.shields.io/github/contributors/openai/openai-python?color=blue) ![GitHub last commit](https://img.shields.io/github/last-commit/davidtkeane/openai-python?style=flat&color=blue&link=https%3A%2F%2Fshields.io)

The [OpenAI](#openai) [Python](#python) [library](#library) provides convenient access to the OpenAI [REST API](#rest-api) from any Python 3.7+ application. The library includes type definitions for all request [params](#parameters) and response fields, and offers both [synchronous](#synchronous) and [asynchronous](#asynchronous) clients powered by [httpx](#http).

It is generated from our [OpenAPI specification](https://github.com/openai/openai-openapi) with [Stainless](https://stainlessapi.com/).

The OpenAI documentation is like a user manual for this system. It has all the instructions and information you need to use OpenAI's AI models in your Python programs. Think of it as a detailed guide that shows you how to communicate with your smart robot assistant.

The OpenAI Python library is like a toolbox that makes it easy to use OpenAI's AI models in your Python programs. Imagine you have a smart robot assistant that can help you with various tasks like answering questions or generating text. This library helps you communicate with that robot using a set of rules (API) over the internet.

<details><summary style="font-size: 1.5em; font-weight: bold;">Table of Contents</summary

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

The **[REST API](#rest-api) documentation can be found on** **[platform.openai.com](https://platform.openai.com/docs). The full API of this** **[library](#library) can be found in** [api.md](api.md).

The OpenAI documentation is like a user manual for this system. It has all the instructions and information you need to use OpenAI's AI models in your Python programs. Think of it as a detailed guide that shows you how to communicate with your smart robot assistant.

## Installation

> [!IMPORTANT]
>
> The [SDK](#sdk) was rewritten in v1, which was released November 6th 2023. See the **[**v1 migration guide**]** ( **https://github.com/openai/openai-python/discussions/742**), which includes scripts to automatically update your code.

#### Requirements is Python 3.7 or higher

##### **How to install python on your system, follow these steps:**

[![Python](https://img.shields.io/badge/python-black?style=for-the-badge&logo=python)](https://github.com/davidtkeane)[![Linux](https://img.shields.io/badge/linux-black?style=for-the-badge&logo=Linux)](https://github.com/davidtkeane)[![Windows](https://img.shields.io/badge/Windows-black?style=for-the-badge&logo=Tower)](https://github.com/davidtkeane)[![Apple](https://img.shields.io/badge/AppleMac-black?style=for-the-badge&logo=Apple)](https://github.com/davidtkeane)

You need Python 3.7 or higher to use this library. It's like needing a specific version of an app to use certain features. Make sure your Python version is up to date before trying to use this library.

###### For Windows:

1. **Download Installer**: Go to the [official Python website](https://www.python.org/downloads/) and download the latest installer.
2. **Run Installer**: Run the downloaded file. Check the box for "Add Python to PATH" and click "Install Now."
3. **Verify Installation**: Open Command Prompt and type `python --version` to check the installed version.
   ```
   python --version
   ```

###### For macOS:

1. **Use Homebrew**: Open Terminal and install Homebrew if you haven't:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. **Install Python**: Run:
   ```
   brew update
   brew upgrade
   brew install python
   ```

###### For Linux:

1. **Use Package Manager**: For Ubuntu, open Terminal and run.
   ```
   sudo apt update
   sudo apt install python3
   ```

###### Verification

To verify the installation, type `python --version` in the terminal or command prompt. This should display the installed Python version.

To check your Python version, you can open a terminal or command prompt and type:

```python
python --version
```

If your version is lower than 3.7, you'll need to update Python to use this library. You can download the latest version of Python from the official Python website (https://www.python.org/downloads/).

🚀 **Explanation:**

To use this library, you need to install it first. This is like installing a new app on your phone, but for Python. Imagine you are adding a new tool to your toolbox so you can use it in your programming projects. The command `pip install openai` is like telling your computer to go to the Python app store (PyPI) and download the OpenAI tool for you. To use the .env file we will need a module called python-dotenv and it will need to be installed as this package allows you to load environment variables from a  `.env` file into your environment, which is useful for keeping sensitive information like API keys out of your codebase.

```python
pip install openai
pip install python-dotenv
```

### How to obtain your OpenAi API Key.

To obtain an OpenAI API key, follow these steps:

1. **Sign Up**: Go to the [OpenAI website](https://www.openai.com/) and sign up for an account if you don't already have one.
2. **Login**: Once logged in, navigate to the API section.
3. **Generate Key**: Click on "API keys" and then "Create API Key." A new key will be generated and displayed.
4. **Save the Key**: Copy and securely store the API key. You will use this key to authenticate your requests to the OpenAI API.

For more details, visit the [OpenAI API documentation](https://beta.openai.com/docs/).

## Usage

The full API of this library can be found in [api.md](api.md).

```python
import os
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
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

print(chat_completion.choices[0].message.content)
```

💡 **Explanation:**

While you can provide an `api_key` keyword argument, we recommend using [python-dotenv](https://pypi.org/project/python-dotenv/) to be able to use OpenAi API Key.

1. Open the .env and place you key after the = sign.
2. `OPENAI_API_KEY=sk-putyourkeyhere > replace `sk-putyourkeyhere
3. Save the file.
4. You can now use the API key in your script by adding from `dotenv import load_dotenv`
5. To load environment variables (your API Key ) from .env file into your script you will need to add `load_dotenv()`into the script. See below for an example.
6. Copy the code below and save it as test_openai.py
7. Then inside the terminal type `python test_openai.py`

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables (loads your API Key) from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-4o",
)

print(chat_completion.choices[0].message.content)
```

```
> python test_openai.py
This is a test.

This is what you should see afterwards, this means that you are on the right path and connected your script to the ChatGPT Model 4o using openai and dotenv modules. Congratulations!
```

Here's how you use the library to talk to the AI models. Think of this like having a conversation with your smart robot assistant. You set up the connection, ask it to say something, and then it responds. Let's break it down:

1. First, you import the necessary tools (`os` and `OpenAI`).
2. Then, you create a "client" - think of this as establishing a phone line to the AI.
3. You send a message to the AI, just like texting a friend.
4. The AI processes your message and sends back a response.

This code sets up the AI client and asks it to say "This is a test." It's like teaching a parrot to repeat a phrase!

### Polling Helpers

When interacting with the API some actions such as starting a [Run](#run) and adding files to vector stores are [asynchronous](#asynchronous) and take time to complete. The SDK includes helper functions which will poll the status until it reaches a terminal state and then return the resulting object. If an API method results in an action that could benefit from polling there will be a corresponding version of the method ending in '_and_poll'.

#### ⏳ **Explanation:**

Some actions take time to complete, like starting a process or uploading files. Polling helpers keep checking until these actions are done. Imagine you are baking a cake and you keep checking the oven until the cake is ready. In this case, you're starting a task (like asking the AI to do some work) and then waiting until it's finished before moving on. The `create_and_poll` function does this waiting for you automatically, so you don't have to keep checking manually.

#### Running a Thread

To create and poll a run within a thread using the OpenAI API, follow these steps:

#### Overview

The following example demonstrates how to initiate a run within a specific thread and automatically poll for its status. This can be useful for tracking the progress of a long-running task, such as a conversation or a job.

#### Example Code

```python
# Assuming you have already set up the OpenAI client and have a thread and assistant
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
)
```

* `thread_id`: The unique identifier for the thread in which you want to run the task. This is essential to specify the context of the run.
* `assistant_id`: The unique identifier for the assistant you want to use. This could be an AI model or a specific assistant configuration.
* More information on the lifecycle of a Run can be found in the [Run Lifecycle Documentation](https://platform.openai.com/docs/assistants/how-it-works/run-lifecycle)

#### Usage

1. **Setup** : Make sure you have the necessary API credentials and have initialized the OpenAI client properly.
2. **Run Creation** : Use the  `create_and_poll` method to start a new run within the specified thread.
3. **Polling** : The function automatically polls the run's status, providing updates until the task is complete.

#### Example Code Polling Helpers

```python
# Import the required libraries
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables (loads your API Key) from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Define thread and assistant IDs
thread_id = "your_thread_id"  # Replace with actual thread ID
assistant_id = "your_assistant_id"  # Replace with actual assistant ID

# Create and poll a new run within the specified thread
try:
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    print(f"Run successfully started with ID: {run.id}")
    print(f"Current Status: {run.status}")
except Exception as e:
    print(f"An error occurred while creating and polling the run: {e}")

# Example usage of chat completion
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-4o",
)

print(chat_completion.choices[0].message.content)

```

#### Bulk Upload Helpers

When creating and interacting with vector stores, you can use polling helpers to monitor the status of operations.
For convenience, we also provide a bulk upload helper to allow you to simultaneously upload several files at once.

```python
sample_files = [Path("sample-paper.pdf"), ...]

batch = await client.vector_stores.file_batches.upload_and_poll(
    store.id,
    files=sample_files,
)
```

📤 **Explanation:**

You can upload multiple files at once and check their status. This is like sending a bunch of letters at the post office and waiting to see when they are all delivered. In programming terms, you're sending multiple files to the AI system at the same time, which can save a lot of time compared to uploading them one by one. The `upload_and_poll` function takes care of sending all the files and waiting until they're all properly received and processed.

#### Streaming Helpers

The SDK also includes helpers to process streams and handle incoming events.

```python
with client.beta.threads.runs.stream(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Please address the user as Jane Doe. The user has a premium account.",
) as stream:
    for event in stream:
        # Print the text from text delta events
        if event.type == "thread.message.delta" and event.data.delta.content:
            print(event.data.delta.content[0].text)
```

More information on streaming helpers can be found in the dedicated documentation: [helpers.md](helpers.md)

🔄 **Explanation:**

You can stream responses from the AI, which means you get parts of the response as they come in, instead of waiting for the whole thing. It's like watching a YouTube video as it loads rather than waiting for the entire video to download first. In this code:

1. You start a "stream" of information from the AI.
2. You give some instructions to the AI (like how to address the user).
3. As the AI generates its response, you get pieces of it one at a time.
4. You can process or display these pieces as they arrive, making the interaction feel more real-time and responsive.

This is particularly useful for long responses or when you want to show progress to the user while the AI is thinking.

### Async usage

Simply import `AsyncOpenAI` instead of `OpenAI` and use `await` with each API call:

```python
import os
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(
    # This is the default and can be omitted
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

Functionality between the synchronous and asynchronous clients is otherwise identical.

🔄 **Explanation:**

You can use the library with [asynchronous](#asynchronous) code, which lets your program do other things while waiting for the AI to respond. It's like cooking several dishes at once instead of one after the other. Here's what's happening:

1. You import a special version of the OpenAI client that works asynchronously.
2. You define a function (`main()`) that uses `await` to talk to the AI.
3. This allows your program to do other tasks while it's waiting for the AI's response.
4. Finally, you run this async function using `asyncio.run(main())`.

This is particularly useful in applications that need to handle multiple tasks simultaneously, like web servers or interactive applications.

#### Streaming responses

We provide support for streaming responses using [Server Side Events (SSE)](#sse).

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

🔄 **Explanation:**

Streaming responses allow you to get and process the AI's reply piece by piece, as it's being generated. It's like reading a book as it's being written, page by page, instead of waiting for the entire book to be finished. This code:

1. Sets up a streaming connection to the AI.
2. Asks the AI to say "this is a test".
3. As the AI generates its response, it sends back small "chunks" of text.
4. The code prints out each chunk as it arrives, creating a smooth, flowing output.

This is great for creating more responsive and interactive applications, especially when dealing with longer AI responses.

#### The async client uses the exact same interface.

```python
from openai import AsyncOpenAI

client = AsyncOpenAI()


async def main():
    stream = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say this is a test"}],
        stream=True,
    )
    async for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="")


asyncio.run(main())
```

### Module-level client

> [!IMPORTANT]
> We highly recommend instantiating client instances instead of relying on the global client.

We also expose a global client instance that is accessible in a similar fashion to versions prior to v1.

```py
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

The API is the exact same as the standard client instance-based API.

This is intended to be used within REPLs or notebooks for faster iteration, **not** in application code.

We recommend that you always instantiate a client (e.g., with `client = OpenAI()`) in application code because:

- It can be difficult to reason about where client options are configured
- It's not possible to change certain client options without potentially causing race conditions
- It's harder to mock for testing purposes
- It's not possible to control cleanup of network connections

🔧 **Explanation:**

This section talks about a global client, which is like having a universal remote that works for all your devices. However, just like a universal remote might not have all the special features for each specific device, using a global client isn't always the best choice for complex programs. Here's what's happening:

1. You set up a global OpenAI client that can be used anywhere in your code.
2. You can configure various options for this client, like the API key and default settings.
3. You can then use this client to interact with the AI, like asking it how to list files in a directory.

While this method is simple and can be useful for quick experiments or small scripts, for larger projects, it's better to create specific client instances for different parts of your program. This gives you more control and makes your code easier to manage and test.

Typed requests and responses provide autocomplete and documentation within your editor. If you would like to see type errors in VS Code to help catch bugs earlier, set `python.analysis.typeCheckingMode` to `basic`.

### Using Types

Nested request parameters are [TypedDicts](#typeddict). Responses are [Pydantic models](https://docs.pydantic.dev) which also provide helper methods for things like:

- Serializing back into [JSON](#json), `model.to_json()`
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

🛠️ **Explanation:**

The library uses typed requests and responses, which means it can help you catch mistakes while you write your code. Think of it as having a spell-checker for your programming instructions. Here's what this means:

1. When you send requests to the AI, you use special Python dictionaries ([TypedDicts](#typeddict)) that help ensure you're providing the right kind of information.
2. When you get responses back, they come as Pydantic models, which are like smart containers for data.
3. These models have helpful methods, like turning the data back into JSON or into a regular Python dictionary.

In the example, we're asking the AI to create a [JSON object](#json-object) describing a fruit. The library ensures we're formatting our request correctly and helps us work with the response easily. This type system acts like a safety net, catching potential errors before they cause problems in your program.

### Pagination

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

🚀 **Explanation**:

Imagine you're reading a really long book, but instead of giving you the whole book at once, the library gives you 20 pages at a time. This code is like a magical bookmark that automatically gets the next 20 pages for you when you finish reading the current ones. You don't have to worry about asking for the next part - it just happens! In this case, instead of pages, we're getting information about AI training jobs, 20 at a time.

Or, asynchronously:

```python
import asyncio
import openai

client = AsyncOpenAI()


async def main() -> None:
    all_jobs = []
    # Iterate through items across all pages, issuing requests as needed.
    async for job in client.fine_tuning.jobs.list(
        limit=20,
    ):
        all_jobs.append(job)
    print(all_jobs)


asyncio.run(main())
```

🏃‍♂️ **Explanation**:

This is like the previous example, but it's even cooler! Imagine you're in a relay race where you can start the next runner before the current one finishes. This code does something similar - it starts getting the next batch of information while it's still processing the current one. It's a way to make things happen faster, especially when you're dealing with lots of data.

Alternatively, you can use the `.has_next_page()`, `.next_page_info()`, or `.get_next_page()` methods for more granular control working with pages:

```python
first_page = await client.fine_tuning.jobs.list(
    limit=20,
)
if first_page.has_next_page():
    print(f"will fetch next page using these details: {first_page.next_page_info()}")
    next_page = await first_page.get_next_page()
    print(f"number of items we just fetched: {len(next_page.data)}")

# Remove `await` for non-async usage.
```

Or just work directly with the returned data:

```python
first_page = await client.fine_tuning.jobs.list(
    limit=20,
)

print(f"next page cursor: {first_page.after}")  # => "next page cursor: ..."
for job in first_page.data:
    print(job.id)

# Remove `await` for non-async usage.
```

**📂 Explanation:**

This is like getting a page of a book and a bookmark that shows where the next page starts. You can look at all the information on the current page (printing each job's ID), and you also know where to start reading next (the "next page cursor"). It's a way to keep track of where you are in all the information, just like how you might use a bookmark to remember your place in a big book.

Some API responses are too large to send all at once, so they are split into pages. The library can automatically handle fetching these pages for you. It's like getting a long book in several smaller, manageable volumes instead of one big, heavy book. Here's how it works:

1. You start a request to list something, like jobs for fine-tuning AI models.
2. You set a limit (in this case, 20) for how many items you want per page.
3. The library automatically fetches new pages as you go through the list.
4. You can process each item (job) as it comes in, without worrying about the pagination.

This makes it much easier to work with large amounts of data, as you don't have to manually keep track of which page you're on or when to request the next page. The library handles all of that for you behind the scenes.

### Nested params

Nested parameters are dictionaries, typed using `TypedDict`, for example:

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

🔄 **Explanation:**

Nested parameters allow you to organize complex information in a structured way, like having folders inside folders on your computer. Here's what's happening in this code:

1. We create an OpenAI [client](#client) to communicate with the AI.
2. We use the [chat.completions.create](#chat-completions-create) method to generate a response.
3. The `messages` parameter is a list containing a dictionary. This dictionary has two nested key-value pairs: "role" and "content".
4. We specify the AI model to use with the `model` parameter.
5. The [response_format](#response-format) parameter is another nested dictionary, telling the AI to respond with a [JSON object](#json-object).

This nested structure allows us to provide detailed and organized instructions to the AI. In this case, we're asking it to generate a [JSON](#json) object describing a fruit. The use of [TypedDict](#typeddict) helps ensure that we're formatting these nested parameters correctly, reducing the chance of errors in our code.

### File uploads

Request parameters that correspond to file uploads can be passed as `bytes`, a [`PathLike`](https://docs.python.org/3/library/os.html#os.PathLike) instance or a tuple of `(filename, contents, media type)`.

```python
from pathlib import Path
from openai import OpenAI

client = OpenAI()

client.files.create(
    file=Path("input.jsonl"),
    purpose="fine-tune",
)
```

🔧 **Explanation:**

The async client uses the exact same interface. If you pass a [`PathLike`](https://docs.python.org/3/library/os.html#os.PathLike) instance, the file contents will be read asynchronously automatically.

You can upload files directly to the API, which can be used for things like fine-tuning models. It's like uploading a document to a website so that the site can use the information in the document. In this example:

1. We import the `Path` class to work with file paths easily.
2. We create an OpenAI client.
3. We use the `files.create` method to upload a file.
4. We specify the file path and its purpose (in this case, for fine-tuning a model).

This is useful when you need to provide large amounts of data to the AI, such as training data for customizing models.

## Handling errors

When the library is unable to connect to the API (for example, due to network connection problems or a timeout), a subclass of `openai.APIConnectionError` is raised.

When the API returns a non-success status code (that is, 4xx or 5xx
response), a subclass of `openai.APIStatusError` is raised, containing `status_code` and `response` properties.

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

Error codes are as followed:

| Status Code | Error Type                   |
| ----------- | ---------------------------- |
| 400         | `BadRequestError`          |
| 401         | `AuthenticationError`      |
| 403         | `PermissionDeniedError`    |
| 404         | `NotFoundError`            |
| 422         | `UnprocessableEntityError` |
| 429         | `RateLimitError`           |
| >=500       | `InternalServerError`      |
| N/A         | `APIConnectionError`       |

⚠️ **Explanation:**

The library provides error handling for different types of errors that can occur while interacting with the API. It's like having a plan for what to do if something goes wrong while you're working on a project. Here's what's happening:

1. We set up a try-except block to catch different types of errors.
2. We attempt to create a fine-tuning job.
3. If there's a connection error, we catch it and print a message.
4. If we hit a rate limit (too many requests), we catch that specific error.
5. For any other API errors, we catch them and print details about the error.

This error handling helps you write more robust code that can gracefully handle problems when they occur, rather than crashing unexpectedly.

### Retries

Certain errors are automatically retried 2 times by default, with a short exponential backoff.
Connection errors (for example, due to a network connectivity problem), 408 Request Timeout, 409 Conflict,
429 Rate Limit, and >=500 Internal errors are all retried by default.

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

🔁 **Explanation:**

Some errors are automatically retried by the library. You can configure how many times to retry or disable retries. It's like trying to reconnect your WiFi if it drops the first time. Here's what this code does:

1. We can set a default number of retries for all requests when creating the client.
2. We can also set the number of retries for a specific request using `with_options()`.
3. If an error occurs that's eligible for retry, the library will automatically try again up to the specified number of times.

This feature helps make your application more resilient to temporary network issues or server problems.

### Timeouts

By default requests time out after 10 minutes. You can configure this with a `timeout` option,
which accepts a float or an [`httpx.Timeout`](https://www.python-httpx.org/advanced/#fine-tuning-the-configuration) object:

```python
from openai import OpenAI

# Configure the default for all requests:
client = OpenAI(
    # 20 seconds (default is 10 minutes)
    timeout=20.0,
)

# More granular control:
client = OpenAI(
    timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0),
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

On timeout, an `APITimeoutError` is thrown.

Note that requests that time out are [retried twice by default](#retries).

⏲️ **Explanation:**

You can set how long to wait for a response before timing out. It's like setting a timer for how long you'll wait for a friend before leaving. Here's what's happening:

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

📜 **Explanation:**

Logging helps you see what's happening behind the scenes in your application. It's like having a detective's notebook that records everything that happens. By setting the `OPENAI_LOG` environment variable to `debug`, you're telling the library to write detailed information about its operations, which can be very helpful for troubleshooting problems.

### How to tell whether `None` means `null` or missing

In an API response, a field may be explicitly `null`, or missing entirely; in either case, its value is `None` in this library. You can differentiate the two cases with `.model_fields_set`:

```py
if response.my_field is None:
  if 'my_field' not in response.model_fields_set:
    print('Got json like {}, without a "my_field" key present at all.')
  else:
    print('Got json like {"my_field": null}.')
```

### Accessing raw response data (e.g. headers)

The "raw" Response object can be accessed by prefixing `.with_raw_response.` to any HTTP method call, e.g.,

```py
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.with_raw_response.create(
    messages=[{
        "role": "user",
        "content": "Say this is a test",
    }],
    model="gpt-3.5-turbo",
)
print(response.headers.get('X-My-Header'))

completion = response.parse()  # get the object that `chat.completions.create()` would have returned
print(completion)
```

🔧 **Explanation:**

These methods return an [`LegacyAPIResponse`](https://github.com/openai/openai-python/tree/main/src/openai/_legacy_response.py) object. This is a legacy class as we're changing it slightly in the next major version.

For the sync client this will mostly be the same with the exception
of `content` & `text` will be methods instead of properties. In the
async client, all methods will be async.

A migration script will be provided & the migration in general should
be smooth.

#### `.with_streaming_response`

The above interface eagerly reads the full response body when you make the request, which may not always be what you want.

To stream the response body, use `.with_streaming_response` instead, which requires a context manager and only reads the response body once you call `.read()`, `.text()`, `.json()`, `.iter_bytes()`, `.iter_text()`, `.iter_lines()` or `.parse()`. In the async client, these are async methods.

As such, `.with_streaming_response` methods return a different [`APIResponse`](https://github.com/openai/openai-python/tree/main/src/openai/_response.py) object, and the async client returns an [`AsyncAPIResponse`](https://github.com/openai/openai-python/tree/main/src/openai/_response.py) object.

```python
with client.chat.completions.with_streaming_response.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-3.5-turbo",
) as response:
    print(response.headers.get("X-My-Header"))

    for line in response.iter_lines():
        print(line)
```

The context manager is required so that the response will reliably be closed.

### Making custom/undocumented requests

This library is typed for convenient access to the documented API.

If you need to access undocumented endpoints, params, or response properties, the library can still be used.

#### Undocumented endpoints

To make requests to undocumented endpoints, you can make requests using `client.get`, `client.post`, and other
http verbs. Options on the client will be respected (such as retries) will be respected when making this
request.

```py
import httpx

response = client.post(
    "/foo",
    cast_to=httpx.Response,
    body={"my_param": True},
)

print(response.headers.get("x-foo"))
```

#### Undocumented request params

If you want to explicitly send an extra param, you can do so with the `extra_query`, `extra_body`, and `extra_headers` request
options.

#### Undocumented response properties

To access undocumented response properties, you can access the extra fields like `response.unknown_prop`. You
can also get all the extra fields on the Pydantic model as a dict with
[`response.model_extra`](https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_extra).

### Configuring the HTTP client

You can directly override the [httpx client](https://www.python-httpx.org/api/#client) to customize it for your use case, including:

- Support for proxies
- Custom transports
- Additional [advanced](https://www.python-httpx.org/advanced/clients/) functionality

```python
from openai import OpenAI, DefaultHttpxClient

client = OpenAI(
    # Or use the `OPENAI_BASE_URL` env var
    base_url="http://my.test.server.example.com:8083",
    http_client=DefaultHttpxClient(
        proxies="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

### Managing HTTP resources

By default the library closes underlying HTTP connections whenever the client is [garbage collected](https://docs.python.org/3/reference/datamodel.html#object.__del__). You can manually close the client using the `.close()` method if desired, or with a context manager that closes when exiting.

## Microsoft Azure OpenAI

To use this library with [Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/overview), use the `AzureOpenAI`
class instead of the `OpenAI` class.

> [!IMPORTANT]
> The Azure API shape differs from the core API shape which means that the static types for responses / params
> won't always be correct.

```py
from openai import AzureOpenAI

# gets the API Key from environment variable AZURE_OPENAI_API_KEY
client = AzureOpenAI(
    # https://learn.microsoft.com/azure/ai-services/openai/reference#rest-api-versioning
    api_version="2023-07-01-preview",
    # https://learn.microsoft.com/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
    azure_endpoint="https://example-endpoint.openai.azure.com",
)

completion = client.chat.completions.create(
    model="deployment-name",  # e.g. gpt-35-instant
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.to_json())
```

In addition to the options provided in the base `OpenAI` client, the following options are provided:

- `azure_endpoint` (or the `AZURE_OPENAI_ENDPOINT` environment variable)
- `azure_deployment`
- `api_version` (or the `OPENAI_API_VERSION` environment variable)
- `azure_ad_token` (or the `AZURE_OPENAI_AD_TOKEN` environment variable)
- `azure_ad_token_provider`

An example of using the client with Microsoft Entra ID (formerly known as Azure Active Directory) can be found [here](https://github.com/openai/openai-python/blob/main/examples/azure_ad.py).

🔧 **Explanation:**

If you are using OpenAI through Microsoft Azure, you need to use the AzureOpenAI class. It's like using a different key to unlock the same door. Here's what's happening:

1. We import the `AzureOpenAI` class instead of the regular `OpenAI` class.
2. We create a client with Azure-specific parameters like `api_version` and `azure_endpoint`.
3. We can then use this client to interact with the AI in the same way as before.

This allows you to use OpenAI's capabilities through Microsoft's Azure cloud platform, which might be preferred for certain business or integration reasons.

## Versioning

This package generally follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions, though certain backwards-incompatible changes may be released as minor versions:

1. Changes that only affect static types, without breaking runtime behavior.
2. Changes to library internals which are technically public but not intended or documented for external use. _(Please open a GitHub issue to let us know if you are relying on such internals)_.
3. Changes that we do not expect to impact the vast majority of users in practice.

We take backwards-compatibility seriously and work hard to ensure you can rely on a smooth upgrade experience.

We are keen for your feedback; please open an [issue](https://www.github.com/openai/openai-python/issues) with questions, bugs, or suggestions.

🔄 **Explanation:**

The library follows versioning rules to ensure backward compatibility. It's like updating an app on your phone to get new features without breaking the old ones. The developers try to make sure that when they release new versions:

1. Your existing code will still work (backwards-compatibility).
2. You know what to expect from each update (following SemVer conventions).
3. You have a way to give feedback or report problems (through GitHub issues).

This helps you keep your projects up-to-date while minimizing the risk of unexpected breaks in your code.

### Requirements

1. **Python 3.7 or higher** : The OpenAI Python library requires Python version 3.7 or higher. This ensures compatibility with the latest features and security updates of the Python language.
2. **Internet Access** : Since the OpenAI API communicates with OpenAI's servers over the internet, you'll need an internet connection to make API requests and receive responses.
3. **OpenAI API Key** : To use the OpenAI API, you'll need an API key, which you can obtain by signing up for an account on the OpenAI platform. This key is used to authenticate your requests.
4. **pip (Python package installer)** : You need pip to install the OpenAI Python library and its dependencies. Pip usually comes pre-installed with Python, but you can download it if needed.
5. **HTTP Client Library (httpx)** : The OpenAI Python library uses the httpx library to make HTTP requests. This library will be installed automatically when you install the OpenAI Python library using pip.
6. **Dependencies** : The library may require additional dependencies which will be installed automatically with the library. These dependencies include libraries necessary for making HTTP requests, handling JSON data, and other functionalities.

Python 3.7 or higher.

You need Python 3.7 or higher to use this library. It's like needing a specific version of an app to use certain features. Make sure your Python version is up to date before trying to use this library.

To check your Python version, you can open a terminal or command prompt and type:

```sh
python --version
```

If your version is lower than 3.7, you'll need to update Python to use this library. You can download the latest version of Python from the official Python website (https://www.python.org/downloads/).

## Quick Definitions

And here's the corresponding update to the Quick Definitions list:

* **[Library](#library)**: A collection of pre-written code that you can use to make programming easier. Think of it like a toolbox with ready-to-use tools.
* **[API](#api)**: A set of rules that lets different software programs communicate with each other.
* **[HTTP](#http)**: A protocol used for transferring data over the web. It's like the language that computers use to talk to each other on the internet.
* **[HTTPS](#https)**: The secure version of HTTP. It means the data transferred is encrypted and secure.
* **[Request](#request)**: When you ask a computer to do something or get some data.
* **[Proxy](#proxy)**: A server that acts as an intermediary between your computer and the internet.
* **[Streaming Responses](#streaming-responses)**: Getting parts of a response as they come in, rather than waiting for the whole response.
* **[Asynchronous](#asynchronous)**: Doing multiple things at the same time without waiting for each task to complete one by one.
* **[Parameters](#parameters)**: Pieces of information you provide to a function or request to control how it works.
* **[Nested Parameters](#nested-parameters)**: Parameters that are inside other parameters, like a list inside a list.
* **[Fine-Tuning Models](#fine-tuning-models)**: Customizing an AI model with additional training to improve its performance for specific tasks.
* **[Error Handling](#error-handling)**: Ways to manage and respond to errors that occur in your program.
* **[Endpoints](#endpoints)**: Specific addresses where APIs can access resources or perform actions.
* **[AzureOpenAI](#azureopenai)**: A version of OpenAI that works with Microsoft Azure, a cloud computing service.
* **[Python](#python)**: A popular programming language known for its simplicity and readability.
* **[Stainless](#stainless)**: A tool used to generate this library from the OpenAPI specification.
* **[OpenAI](#openai)**: An artificial intelligence research laboratory consisting of the for-profit corporation OpenAI LP and its parent company, the non-profit OpenAI Inc.
* **[REST API](#rest-api)**: A type of API that uses HTTP requests to GET, PUT, POST and DELETE data.
* **[Synchronous](#synchronous)**: Operations that are performed one at a time and must complete before moving on to the next operation.
