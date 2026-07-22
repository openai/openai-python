# OpenAI Python API Library

[![PyPI version](https://img.shields.io/pypi/v/openai.svg?label=pypi%20(stable))](https://pypi.org/project/openai/)
[![Python version](https://img.shields.io/pypi/pyversions/openai.svg)](https://pypi.org/project/openai/)
[![License](https://img.shields.io/github/license/openai/openai-python)](LICENSE)

The OpenAI Python library provides convenient access to the OpenAI REST and Realtime APIs from any Python 3.9+ application. The library includes type definitions for all request params and response fields, and offers both synchronous and asynchronous clients powered by [httpx](https://github.com/encode/httpx).

It is generated from our [OpenAPI specification](https://github.com/openai/openai-openapi) with [Stainless](https://stainlessapi.com/).

## Documentation

The REST API documentation can be found on [platform.openai.com](https://platform.openai.com/docs/api-reference). The full API of this library can be found in [api.md](api.md).

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Responses API](#responses-api)
  - [Chat Completions API](#chat-completions-api)
  - [Authentication & Workload Identity](#authentication--workload-identity)
- [Core Capabilities](#core-capabilities)
  - [Vision](#vision)
  - [Async Usage](#async-usage)
  - [Streaming Responses](#streaming-responses)
  - [Realtime API](#realtime-api)
  - [File Uploads](#file-uploads)
  - [Nested Parameters](#nested-parameters)
- [Cloud Providers](#cloud-providers)
  - [Microsoft Azure OpenAI](#microsoft-azure-openai)
  - [Amazon Bedrock](#amazon-bedrock)
- [Advanced Usage](#advanced-usage)
  - [Using Types & Null Checking](#using-types--null-checking)
  - [Pagination](#pagination)
  - [Webhook Verification](#webhook-verification)
  - [Handling Errors](#handling-errors)
  - [Request IDs](#request-ids)
  - [Retries & Timeouts](#retries--timeouts)
  - [Logging](#logging)
  - [Accessing Raw Response Data](#accessing-raw-response-data)
  - [Making Custom/Undocumented Requests](#making-customundocumented-requests)
  - [Configuring the HTTP Client](#configuring-the-http-client)
  - [Managing HTTP Resources](#managing-http-resources)
- [Versioning & Requirements](#versioning--requirements)
- [Contributing](#contributing)

---

## Installation

```sh
# Install base package from PyPI
pip install openai

# Optional high-concurrency async backend
pip install "openai[aiohttp]"

# Optional Amazon Bedrock support
pip install "openai[bedrock]"
```

---

## Usage

### Responses API

The primary API for interacting with OpenAI models is the [Responses API](https://platform.openai.com/docs/api-reference/responses). You can generate text from the model with the code below.

```python
import os
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

response = client.responses.create(
    model="gpt-5.5",
    instructions="You are a coding assistant that talks like a pirate.",
    input="How do I check if a Python object is an instance of a class?",
)

print(response.output_text)
```

### Chat Completions API

The previous standard (supported indefinitely) for generating text is the [Chat Completions API](https://platform.openai.com/docs/api-reference/chat):

```python
from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-5.5",
    messages=[
        {"role": "developer", "content": "Talk like a pirate."},
        {
            "role": "user",
            "content": "How do I check if a Python object is an instance of a class?",
        },
    ],
)

print(completion.choices[0].message.content)
```

### Authentication & Workload Identity

While you can provide an `api_key` keyword argument, we recommend using [python-dotenv](https://pypi.org/project/python-dotenv/) to add `OPENAI_API_KEY="My API Key"` to your `.env` file so that your API key is not stored in source control. [Get an API key here](https://platform.openai.com/settings/organization/api-keys).

For secure, automated environments like cloud-managed Kubernetes, Azure, and Google Cloud Platform, you can use workload identity authentication with short-lived tokens from cloud identity providers instead of long-lived API keys.

<details>
<summary><b>Kubernetes (service account tokens)</b></summary>

```python
from openai import OpenAI
from openai.auth import k8s_service_account_token_provider

client = OpenAI(
    workload_identity={
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": k8s_service_account_token_provider(
            "/var/run/secrets/kubernetes.io/serviceaccount/token"
        ),
    },
)

response = client.chat.completions.create(
    model="gpt-5.5",
    messages=[{"role": "user", "content": "Hello!"}],
)
```
</details>

<details>
<summary><b>Azure (managed identity)</b></summary>

```python
from openai import OpenAI
from openai.auth import azure_managed_identity_token_provider

client = OpenAI(
    workload_identity={
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": azure_managed_identity_token_provider(
            resource="https://management.azure.com/",
        ),
    },
)
```
</details>

<details>
<summary><b>Google Cloud Platform (compute engine metadata)</b></summary>

```python
from openai import OpenAI
from openai.auth import gcp_id_token_provider

client = OpenAI(
    workload_identity={
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": gcp_id_token_provider(audience="https://api.openai.com/v1"),
    },
)
```
</details>

<details>
<summary><b>Custom subject token provider & refresh buffer</b></summary>

```python
from openai import OpenAI

def get_custom_token() -> str:
    return "your-jwt-token"

client = OpenAI(
    workload_identity={
        "identity_provider_id": "idp-123",
        "service_account_id": "sa-456",
        "provider": {
            "token_type": "jwt",
            "get_token": get_custom_token,
        },
        "refresh_buffer_seconds": 120.0,  # Default is 1200 seconds (20 minutes)
    }
)
```
</details>

---

## Core Capabilities

### Vision

With an image URL:

```python
prompt = "What is in this image?"
img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/2023_06_08_Raccoon1.jpg/1599px-2023_06_08_Raccoon1.jpg"

response = client.responses.create(
    model="gpt-5.5",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"{img_url}"},
            ],
        }
    ],
)
```

With the image as a base64 encoded string:

```python
import base64
from openai import OpenAI

client = OpenAI()

prompt = "What is in this image?"
with open("path/to/image.png", "rb") as image_file:
    b64_image = base64.b64encode(image_file.read()).decode("utf-8")

response = client.responses.create(
    model="gpt-5.5",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"data:image/png;base64,{b64_image}"},
            ],
        }
    ],
)
```

### Async Usage

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
    response = await client.responses.create(
        model="gpt-5.5", input="Explain disestablishmentarianism to a smart five year old."
    )
    print(response.output_text)

asyncio.run(main())
```

<details>
<summary><b>High Concurrency with <code>aiohttp</code></b></summary>

By default, the async client uses `httpx` for HTTP requests. However, for improved concurrency performance you may also use `aiohttp` as the HTTP backend (requires Python 3.10 or later).

```sh
pip install openai[aiohttp]
```

Enable it by instantiating the client with `http_client=DefaultAioHttpClient()`:

```python
import os
import asyncio
from openai import DefaultAioHttpClient, AsyncOpenAI

async def main() -> None:
    async with AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        http_client=DefaultAioHttpClient(),
    ) as client:
        chat_completion = await client.chat.completions.create(
            messages=[{"role": "user", "content": "Say this is a test"}],
            model="gpt-5.5",
        )

asyncio.run(main())
```
</details>

### Streaming Responses

We provide support for streaming responses using Server Side Events (SSE).

Synchronous streaming:

```python
from openai import OpenAI

client = OpenAI()

stream = client.responses.create(
    model="gpt-5.5",
    input="Write a one-sentence bedtime story about a unicorn.",
    stream=True,
)

for event in stream:
    print(event)
```

Asynchronous streaming:

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def main():
    stream = await client.responses.create(
        model="gpt-5.5",
        input="Write a one-sentence bedtime story about a unicorn.",
        stream=True,
    )

    async for event in stream:
        print(event)

asyncio.run(main())
```

### Realtime API

The Realtime API enables low-latency, multi-modal conversational experiences. It supports text and audio as input/output, as well as [function calling](https://platform.openai.com/docs/guides/function-calling) over a WebSocket connection using [`websockets`](https://websockets.readthedocs.io/en/stable/).

A full event reference can be found [here](https://platform.openai.com/docs/api-reference/realtime-client-events) and a guide can be found [here](https://platform.openai.com/docs/guides/realtime).

```python
import asyncio
from openai import AsyncOpenAI

async def main():
    client = AsyncOpenAI()

    async with client.realtime.connect(model="gpt-realtime-2") as connection:
        await connection.session.update(
            session={"type": "realtime", "output_modalities": ["text"]}
        )

        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Say hello!"}],
            }
        )
        await connection.response.create()

        async for event in connection:
            if event.type == "response.output_text.delta":
                print(event.delta, flush=True, end="")
            elif event.type == "response.output_text.done":
                print()
            elif event.type == "response.done":
                break

asyncio.run(main())
```

See this [TUI script example](https://github.com/openai/openai-python/blob/main/examples/realtime/push_to_talk_app.py) for a complete push-to-talk audio application.

<details>
<summary><b>Realtime Error Handling</b></summary>

Whenever an error occurs, the Realtime API sends an [`error` event](https://platform.openai.com/docs/guides/realtime-model-capabilities#error-handling) while keeping the connection open. Handle error events explicitly:

```python
client = AsyncOpenAI()

async with client.realtime.connect(model="gpt-realtime-2") as connection:
    ...
    async for event in connection:
        if event.type == 'error':
            print(event.error.type)
            print(event.error.code)
            print(event.error.event_id)
            print(event.error.message)
```
</details>

### File Uploads

Request parameters that correspond to file uploads can be passed as `bytes`, a [`PathLike`](https://docs.python.org/3/library/os.html#os.PathLike) instance, or a tuple of `(filename, contents, media type)`:

```python
from pathlib import Path
from openai import OpenAI

client = OpenAI()

client.files.create(
    file=Path("input.jsonl"),
    purpose="fine-tune",
)
```

The async client uses the exact same interface and reads `PathLike` instances asynchronously automatically.

### Nested Parameters

Nested parameters are dictionaries, typed using `TypedDict`:

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    input=[
        {
            "role": "user",
            "content": "How much ?",
        }
    ],
    model="gpt-5.5",
    text={"format": {"type": "json_object"}},
)
```

---

## Cloud Providers

### Microsoft Azure OpenAI

To use this library with [Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/overview), use the `AzureOpenAI` class instead of `OpenAI`:

```python
from openai import AzureOpenAI

# Gets the API Key from environment variable AZURE_OPENAI_API_KEY
client = AzureOpenAI(
    api_version="2023-07-01-preview",
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

> [!IMPORTANT]
> The Azure API shape differs from the core API shape which means static types for responses/params won't always be correct.

In addition to options provided in the base `OpenAI` client, Azure options include `azure_endpoint` (`AZURE_OPENAI_ENDPOINT`), `azure_deployment`, `api_version` (`OPENAI_API_VERSION`), `azure_ad_token` (`AZURE_OPENAI_AD_TOKEN`), and `azure_ad_token_provider`. An example using Microsoft Entra ID is available in [examples/azure_ad.py](https://github.com/openai/openai-python/blob/main/examples/azure_ad.py).

### Amazon Bedrock

To use this library with [Amazon Bedrock's OpenAI-compatible API](https://docs.aws.amazon.com/bedrock/latest/userguide/models-api-compatibility.html), configure the standard `OpenAI` client with the Bedrock provider.

Install optional dependencies:
```sh
pip install 'openai[bedrock]'
```

```python
from openai import OpenAI
from openai.providers import bedrock

client = OpenAI(
    provider=bedrock(
        region="us-west-2",
    )
)

response = client.responses.create(
    model="openai.gpt-5.4",
    input="Say hello!",
)

print(response.output_text)
```

<details>
<summary><b>Bedrock Credentials, Base URL, and Legacy Client Options</b></summary>

The provider configures AWS authentication and the Bedrock Mantle endpoint while retaining standard SDK features.

- **Credentials:** Supports standard AWS credential chain (environment, profile, named profile via `provider=bedrock(profile="my-profile")`, ECS/EKS/EC2 metadata).
- **Explicit Auth:** Pass `access_key_id`, `secret_access_key`, and optional `session_token`, or a refreshable `credential_provider`.
- **Base URL:** Pass `base_url` to `bedrock(...)` or set `AWS_BEDROCK_BASE_URL` to override `https://bedrock-mantle.<region>.api.aws/openai/v1`.
- **Bearer Tokens:** Set `AWS_BEARER_TOKEN_BEDROCK` to an [Amazon Bedrock API key](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html), pass `api_key`, or provide `token_provider=lambda: refresh_bedrock_token()`.

**Legacy `BedrockOpenAI` Client:**

`BedrockOpenAI` and `AsyncBedrockOpenAI` remain available for existing applications:

```python
from openai import BedrockOpenAI

client = BedrockOpenAI(
    aws_region="us-west-2",
    aws_profile="my-profile",
)
```
The legacy client also continues to support `openai.api_type = "amazon-bedrock"` or `OPENAI_API_TYPE=amazon-bedrock`.
</details>

---

## Advanced Usage

### Using Types & Null Checking

Nested request parameters are [TypedDicts](https://docs.python.org/3/library/typing.html#typing.TypedDict). Responses are [Pydantic models](https://docs.pydantic.dev) which provide helper methods:
- Serializing to JSON: `model.to_json()`
- Converting to a dictionary: `model.to_dict()`

Set `python.analysis.typeCheckingMode` to `basic` in VS Code to see type errors in your editor.

In API responses, a field may be explicitly `null` or missing entirely; both yield `None` in Python. Differentiate the cases using `.model_fields_set`:

```python
if response.my_field is None:
    if 'my_field' not in response.model_fields_set:
        print('Got json like {}, without a "my_field" key present at all.')
    else:
        print('Got json like {"my_field": null}.')
```

### Pagination

List methods provide auto-paginating iterators so you do not have to request successive pages manually.

Synchronous pagination:

```python
from openai import OpenAI

client = OpenAI()

all_jobs = []
for job in client.fine_tuning.jobs.list(limit=20):
    all_jobs.append(job)
print(all_jobs)
```

Asynchronous pagination:

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def main() -> None:
    all_jobs = []
    async for job in client.fine_tuning.jobs.list(limit=20):
        all_jobs.append(job)
    print(all_jobs)

asyncio.run(main())
```

<details>
<summary><b>Granular Page Control & Cursor Access</b></summary>

Use `.has_next_page()`, `.next_page_info()`, or `.get_next_page()` for granular control:

```python
first_page = await client.fine_tuning.jobs.list(limit=20)
if first_page.has_next_page():
    print(f"Will fetch next page using details: {first_page.next_page_info()}")
    next_page = await first_page.get_next_page()
    print(f"Number of items fetched: {len(next_page.data)}")
```

Or work directly with the returned data and cursor:

```python
first_page = await client.fine_tuning.jobs.list(limit=20)
print(f"Next page cursor: {first_page.after}")
for job in first_page.data:
    print(job.id)
```
</details>

### Webhook Verification

Verifying webhook signatures is optional but encouraged. See the [Webhook Documentation](https://platform.openai.com/docs/guides/webhooks).

Parsing and verifying payloads simultaneously using `client.webhooks.unwrap()`:

```python
from openai import OpenAI
from flask import Flask, request

app = Flask(__name__)
client = OpenAI()  # OPENAI_WEBHOOK_SECRET environment variable is used by default

@app.route("/webhook", methods=["POST"])
def webhook():
    request_body = request.get_data(as_text=True)

    try:
        event = client.webhooks.unwrap(request_body, request.headers)
        if event.type == "response.completed":
            print("Response completed:", event.data)
        elif event.type == "response.failed":
            print("Response failed:", event.data)
        return "ok"
    except Exception as e:
        print("Invalid signature:", e)
        return "Invalid signature", 400
```

<details>
<summary><b>Verifying Webhook Signatures Directly</b></summary>

If you prefer to verify the signature separately from parsing:

```python
import json
from openai import OpenAI
from flask import Flask, request

app = Flask(__name__)
client = OpenAI()

@app.route("/webhook", methods=["POST"])
def webhook():
    request_body = request.get_data(as_text=True)

    try:
        client.webhooks.verify_signature(request_body, request.headers)
        event = json.loads(request_body)
        print("Verified event:", event)
        return "ok"
    except Exception as e:
        print("Invalid signature:", e)
        return "Invalid signature", 400
```
</details>

### Handling Errors

When unable to connect to the API, a subclass of `openai.APIConnectionError` is raised. When the API returns a non-success status code (4xx or 5xx), a subclass of `openai.APIStatusError` is raised, containing `status_code` and `response` properties. All errors inherit from `openai.APIError`.

```python
import openai
from openai import OpenAI

client = OpenAI()

try:
    client.fine_tuning.jobs.create(
        model="gpt-4o",
        training_file="file-abc123",
    )
except openai.APIConnectionError as e:
    print("The server could not be reached")
    print(e.__cause__)  # Underlying Exception raised within httpx.
except openai.RateLimitError as e:
    print("A 429 status code was received; we should back off a bit.")
except openai.APIStatusError as e:
    print("Another non-200-range status code was received")
    print(e.status_code)
    print(e.response)
```

Error status code mapping:

| Status Code | Error Type |
| :--- | :--- |
| 400 | `BadRequestError` |
| 401 | `AuthenticationError` |
| 403 | `PermissionDeniedError` |
| 404 | `NotFoundError` |
| 422 | `UnprocessableEntityError` |
| 429 | `RateLimitError` |
| >=500 | `InternalServerError` |
| N/A | `APIConnectionError` |

### Request IDs

All object responses provide a public `_request_id` property extracted from the `x-request-id` response header for logging and debugging:

```python
response = await client.responses.create(
    model="gpt-5.5",
    input="Say 'this is a test'.",
)
print(response._request_id)  # req_123
```

> [!IMPORTANT]
> To access request IDs for failed requests, catch the `APIStatusError` exception:

```python
import openai

try:
    completion = await client.chat.completions.create(
        messages=[{"role": "user", "content": "Say this is a test"}], model="gpt-5.5"
    )
except openai.APIStatusError as exc:
    print(exc.request_id)  # req_123
    raise exc
```

### Retries & Timeouts

**Retries:**
Certain errors are automatically retried 2 times by default with exponential backoff (connection errors, 408, 409, 429, >=500). Configure with `max_retries`:

```python
from openai import OpenAI

# Configure default for all requests:
client = OpenAI(max_retries=0)

# Configure per-request:
client.with_options(max_retries=5).chat.completions.create(
    messages=[{"role": "user", "content": "How can I get the day name in JS?"}],
    model="gpt-5.5",
)
```

**Timeouts:**
Requests time out after 10 minutes by default. Configure with `timeout` (float or `httpx.Timeout`):

```python
from openai import OpenAI
import httpx

client = OpenAI(timeout=20.0)
client = OpenAI(timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0))
client.with_options(timeout=5.0).chat.completions.create(...)
```
*(On timeout, `APITimeoutError` is thrown and retried twice by default).*

### Logging

Enable logging by setting the `OPENAI_LOG` environment variable:

```shell
$ export OPENAI_LOG=info   # or OPENAI_LOG=debug
```

### Accessing Raw Response Data

Access raw HTTP response objects and headers using `.with_raw_response` (`LegacyAPIResponse`):

```python
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.with_raw_response.create(
    messages=[{"role": "user", "content": "Say this is a test"}],
    model="gpt-5.5",
)
print(response.headers.get('X-My-Header'))
completion = response.parse()  # Get parsed response object
```

Use `.with_streaming_response` to stream raw body content (`APIResponse` / `AsyncAPIResponse`):

```python
with client.chat.completions.with_streaming_response.create(
    messages=[{"role": "user", "content": "Say this is a test"}],
    model="gpt-5.5",
) as response:
    print(response.headers.get("X-My-Header"))
    for line in response.iter_lines():
        print(line)
```

### Making Custom/Undocumented Requests

To access undocumented endpoints or params, use request helpers:

```python
import httpx

# Undocumented endpoints
response = client.post(
    "/foo",
    cast_to=httpx.Response,
    body={"my_param": True},
)

# Undocumented request params & response fields
# Pass extra_query, extra_body, or extra_headers
# Access extra response properties or response.model_extra
```

### Configuring the HTTP Client

Override the underlying [httpx client](https://www.python-httpx.org/api/#client) for custom proxies or transports:

```python
import httpx
from openai import OpenAI, DefaultHttpxClient

client = OpenAI(
    base_url="http://my.test.server.example.com:8083/v1",
    http_client=DefaultHttpxClient(
        proxy="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

### Managing HTTP Resources

By default, underlying connections close on garbage collection. Manually close via `.close()` or a context manager:

```python
from openai import OpenAI

with OpenAI() as client:
    pass  # Make requests here
# HTTP client is now closed
```

---

## Versioning & Requirements

This package follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions.

- **Requirements:** Python 3.9 or higher.
- **Installed Version:**
  ```python
  import openai
  print(openai.__version__)
  ```

---

## Contributing

See the [contributing documentation](./CONTRIBUTING.md).
