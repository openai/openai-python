# OpenAI Python API Library

[![PyPI version](https://img.shields.io/pypi/v/openai.svg)](https://pypi.org/project/openai/)

The OpenAI Python library provides convenient access to the OpenAI REST API from any Python 3.7+
application. It includes type definitions for all request params and response fields,
and offers both synchronous and asynchronous clients powered by [httpx](https://github.com/encode/httpx).

## Documentation

The API documentation can be found [here](https://platform.openai.com/docs).

## Installation

```sh
pip install --pre openai
```

## Usage

The full API of this library can be found in [api.md](https://www.github.com/openai/openai-python/blob/main/api.md).

```python
from openai import OpenAI

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="my api key",
)

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
)
print(completion.choices)
```

While you can provide an `api_key` keyword argument, we recommend using [python-dotenv](https://pypi.org/project/python-dotenv/)
and adding `OPENAI_API_KEY="my api key"` to your `.env` file so that your API Key is not stored in source control.

## Async Usage

Simply import `AsyncOpenAI` instead of `OpenAI` and use `await` with each API call:

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="my api key",
)


async def main():
    completion = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
    )
    print(completion.choices)


asyncio.run(main())
```

Functionality between the synchronous and asynchronous clients is otherwise identical.

## Streaming Responses

We provide support for streaming responses using Server Side Events (SSE).

```python
from openai import OpenAI

client = OpenAI()

stream = client.completions.create(
    prompt="Say this is a test",
    model="text-davinci-003",
    stream=True,
)
for part in stream:
    print(part.choices[0].delta.content or "")
```

The async client uses the exact same interface.

```python
from openai import AsyncOpenAI

client = AsyncOpenAI()

stream = await client.completions.create(
    prompt="Say this is a test",
    model="text-davinci-003",
    stream=True,
)
async for part in stream:
    print(part.choices[0].delta.content or "")
```

## Module-level client

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

The API is the exact same as the standard client instance based API.

This is intended to be used within REPLs or notebooks for faster iteration, **not** in application code.

We recommend that you always instantiate a client (e.g., with `client = OpenAI()`) in application code because:

- It can be difficult to reason about where client options are configured
- It's not possible to change certain client options without potentially causing race conditions
- It's harder to mock for testing purposes
- It's not possible to control cleanup of network connections

## Using Types

Nested request parameters are [TypedDicts](https://docs.python.org/3/library/typing.html#typing.TypedDict). Responses are [Pydantic models](https://docs.pydantic.dev), which provide helper methods for things like serializing back into json ([v1](https://docs.pydantic.dev/1.10/usage/models/), [v2](https://docs.pydantic.dev/latest/usage/serialization/)). To get a dictionary, you can call `dict(model)`.

This helps provide autocomplete and documentation within your editor. If you would like to see type errors in VS Code to help catch bugs earlier, set `python.analysis.typeCheckingMode` to `"basic"`.

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

## Nested params

Nested parameters are dictionaries, typed using `TypedDict`, for example:

```python
from openai import OpenAI

client = OpenAI()

client.files.list()
```

## File Uploads

Request parameters that correspond to file uploads can be passed as `bytes` or a tuple of `(filename, contents, media type)`.

```python
from pathlib import Path
from openai import OpenAI

client = OpenAI()

contents = Path("input.jsonl").read_bytes()
client.files.create(
    file=contents,
    purpose="fine-tune",
)
```

The async client uses the exact same interface. This example uses `aiofiles` to asynchronously read the file contents but you can use whatever method you would like.

```python
import aiofiles
from openai import OpenAI

client = OpenAI()

async with aiofiles.open("input.jsonl", mode="rb") as f:
    contents = await f.read()

await client.files.create(
    file=contents,
    purpose="fine-tune",
)
```

## Handling errors

When the library is unable to connect to the API (e.g., due to network connection problems or a timeout), a subclass of `openai.APIConnectionError` is raised.

When the API returns a non-success status code (i.e., 4xx or 5xx
response), a subclass of `openai.APIStatusError` will be raised, containing `status_code` and `response` properties.

All errors inherit from `openai.APIError`.

```python
import openai
from openai import OpenAI

client = OpenAI()

try:
    client.fine_tunes.create(
        training_file="file-XGinujblHPwGLSztz8cPS8XY",
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

| Status Code | Error Type                 |
| ----------- | -------------------------- |
| 400         | `BadRequestError`          |
| 401         | `AuthenticationError`      |
| 403         | `PermissionDeniedError`    |
| 404         | `NotFoundError`            |
| 422         | `UnprocessableEntityError` |
| 429         | `RateLimitError`           |
| >=500       | `InternalServerError`      |
| N/A         | `APIConnectionError`       |

### Retries

Certain errors will be automatically retried 2 times by default, with a short exponential backoff.
Connection errors (for example, due to a network connectivity problem), 408 Request Timeout, 409 Conflict,
429 Rate Limit, and >=500 Internal errors will all be retried by default.

You can use the `max_retries` option to configure or disable this:

```python
from openai import OpenAI

# Configure the default for all requests:
client = OpenAI(
    # default is 2
    max_retries=0,
)

# Or, configure per-request:
client.with_options(max_retries=5).chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "user",
            "content": "How can I get the name of the current day in Node.js?",
        }
    ],
)
```

### Timeouts

Requests time out after 10 minutes by default. You can configure this with a `timeout` option,
which accepts a float or an [`httpx.Timeout`](https://www.python-httpx.org/advanced/#fine-tuning-the-configuration):

```python
from openai import OpenAI

# Configure the default for all requests:
client = OpenAI(
    # default is 60s
    timeout=20.0,
)

# More granular control:
client = OpenAI(
    timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0),
)

# Override per-request:
client.with_options(timeout=5 * 1000).chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "user",
            "content": "How can I list all files in a directory using Python?",
        }
    ],
)
```

On timeout, an `APITimeoutError` is thrown.

Note that requests which time out will be [retried twice by default](#retries).

## Advanced

### How to tell whether `None` means `null` or missing

In an API response, a field may be explicitly null, or missing entirely; in either case, its value is `None` in this library. You can differentiate the two cases with `.model_fields_set`:

```py
if response.my_field is None:
  if 'my_field' not in response.model_fields_set:
    print('Got json like {}, without a "my_field" key present at all.')
  else:
    print('Got json like {"my_field": null}.')
```

### Configuring custom URLs, proxies, and transports

You can configure the following keyword arguments when instantiating the client:

```python
import httpx
from openai import OpenAI

client = OpenAI(
    # Use a custom base URL
    base_url="http://my.test.server.example.com:8083",
    proxies="http://my.test.proxy.example.com",
    transport=httpx.HTTPTransport(local_address="0.0.0.0"),
)
```

See the httpx documentation for information about the [`proxies`](https://www.python-httpx.org/advanced/#http-proxying) and [`transport`](https://www.python-httpx.org/advanced/#custom-transports) keyword arguments.

### Managing HTTP resources

By default we will close the underlying HTTP connections whenever the client is [garbage collected](https://docs.python.org/3/reference/datamodel.html#object.__del__) is called but you can also manually close the client using the `.close()` method if desired, or with a context manager that closes when exiting.

## Versioning

This package generally attempts to follow [SemVer](https://semver.org/spec/v2.0.0.html) conventions, though certain backwards-incompatible changes may be released as minor versions:

1. Changes that only affect static types, without breaking runtime behavior.
2. Changes to library internals which are technically public but not intended or documented for external use. _(Please open a GitHub issue to let us know if you are relying on such internals)_.
3. Changes that we do not expect to impact the vast majority of users in practice.

We take backwards-compatibility seriously and work hard to ensure you can rely on a smooth upgrade experience.

We are keen for your feedback; please open an [issue](https://www.github.com/openai/openai-python/issues) with questions, bugs, or suggestions.

## Requirements

Python 3.7 or higher.
