# Migrating to HTTPX2

The OpenAI Python SDK now uses [HTTPX2](https://httpx2.pydantic.dev/) for its
synchronous and asynchronous HTTP clients. HTTPX2 is installed automatically
with `openai`; the previous `httpx` package is not. This guide explains what
changes for applications that interact with the SDK's HTTP layer.

## If you use the SDK's default HTTP client

If you construct an `OpenAI` or
`AsyncOpenAI` client without providing `http_client`, your existing API calls,
parsed response models, streaming APIs, authentication, retries, and numeric
timeouts continue to work:

```python
from openai import OpenAI

client = OpenAI(timeout=30.0)
response = client.responses.create(model="gpt-5.5", input="Hello")
```

No HTTPX2 extra or separate installation is required:

```sh
pip install openai
```

If your application imported `httpx` only because an earlier SDK installed it
transitively, add your own `httpx` dependency or migrate those imports to
`httpx2`. Installing the SDK no longer installs `httpx` for you.

## TLS certificates and trust stores

**HTTPX2 changes the default TLS trust store, including for applications that
use the SDK's default HTTP client.** HTTPX previously verified certificates
against the CA bundle provided by `certifi`. HTTPX2 instead uses the
operating-system trust store, and the SDK no longer installs `certifi`.

This can break certificate verification in minimal container images without
system CA certificates, environments using corporate TLS-inspecting proxies,
and deployments that relied on a custom or modified `certifi` bundle. Install
the required CA certificates in the operating-system trust store, or configure
an explicit certificate bundle:

```sh
export SSL_CERT_FILE=/path/to/ca-bundle.pem
```

Alternatively, configure a directory of trusted CA certificates:

```sh
export SSL_CERT_DIR=/path/to/ca-directory
```

These environment variables are honored when `trust_env=True`, which is the
default. To control trust explicitly on a custom client, pass an
`ssl.SSLContext` through `verify`:

```python
import ssl
from openai import OpenAI, DefaultHttpx2Client

ssl_context = ssl.create_default_context(cafile="/path/to/ca-bundle.pem")
client = OpenAI(http_client=DefaultHttpx2Client(verify=ssl_context))
```

Use `DefaultAsyncHttpx2Client(verify=ssl_context)` for the equivalent async
configuration. The SDK's aiohttp transport uses the same HTTPX2 TLS settings.

## If you provide a custom HTTP client

Use HTTPX2 clients and HTTPX2 configuration objects. The SDK provides helpers
that preserve its recommended timeout, connection-pool, and redirect defaults:

```python
import httpx2
from openai import OpenAI, AsyncOpenAI, DefaultHttpx2Client, DefaultAsyncHttpx2Client

proxy_client = OpenAI(http_client=DefaultHttpx2Client(proxy="http://proxy.example.com:8080"))

transport_client = OpenAI(
    http_client=DefaultHttpx2Client(
        transport=httpx2.HTTPTransport(local_address="0.0.0.0"),
        timeout=httpx2.Timeout(30.0, connect=5.0),
    )
)

async_client = AsyncOpenAI(http_client=DefaultAsyncHttpx2Client(timeout=httpx2.Timeout(30.0)))
```

Directly constructed `httpx2.Client` and `httpx2.AsyncClient` instances are
also supported. When you construct a client directly, its own HTTPX2 defaults
apply unless you configure them yourself.

The existing `DefaultHttpxClient` and `DefaultAsyncHttpxClient` names continue
to work, but now construct HTTPX2 clients. Prefer `DefaultHttpx2Client` and
`DefaultAsyncHttpx2Client` when making the HTTP client family explicit.

Module-level configuration follows the same rule:

```python
import openai

openai.http_client = openai.DefaultHttpx2Client()
```

## Timeouts, URLs, transports, and connection settings

Replace HTTPX-specific objects with the corresponding HTTPX2 objects:

| Previous object | HTTPX2 object |
| --- | --- |
| `httpx.Client` | `httpx2.Client` |
| `httpx.AsyncClient` | `httpx2.AsyncClient` |
| `httpx.Timeout` | `httpx2.Timeout` |
| `httpx.URL` | `httpx2.URL` |
| `httpx.Limits` | `httpx2.Limits` |
| `httpx.HTTPTransport` | `httpx2.HTTPTransport` |
| `httpx.AsyncHTTPTransport` | `httpx2.AsyncHTTPTransport` |
| `httpx.MockTransport` | `httpx2.MockTransport` |

For example, a granular SDK timeout becomes:

```python
import httpx2
from openai import OpenAI

client = OpenAI(timeout=httpx2.Timeout(60.0, connect=5.0, read=20.0))
```

Numeric timeout values do not change. Existing string URLs do not change.
Custom transport subclasses, mounted transports, proxy integrations, and
connection-pool instrumentation must target HTTPX2's transport interfaces.

## Authentication and event hooks

Authentication handlers and hooks receive HTTPX2 request and response objects.
Update custom auth classes and annotations accordingly:

```python
import httpx2
from openai import OpenAI, DefaultHttpx2Client


def log_request(request: httpx2.Request) -> None:
    print(request.method, request.url)


client = OpenAI(http_client=DefaultHttpx2Client(event_hooks={"request": [log_request]}))
```

If you subclass an HTTP authentication or transport interface, subclass the
matching `httpx2` class. Third-party instrumentation, tracing middleware, and
auth integrations must explicitly support HTTPX2.

## Raw responses, streaming, and exceptions

Parsed SDK response models are unchanged. When using a native HTTPX2 client,
transport-facing objects belong to HTTPX2:

```python
import httpx2
from openai import OpenAI

client = OpenAI()
response = client.models.with_raw_response.list()

assert isinstance(response.http_response, httpx2.Response)
assert isinstance(response.http_request, httpx2.Request)
```

With a native client, use `cast_to=httpx2.Response` when requesting an unparsed
HTTP response. Streaming response wrappers also expose HTTPX2 response objects.
Application code should usually catch SDK exceptions such as
`openai.APITimeoutError` and `openai.APIConnectionError`; with a native client,
an exception's underlying transport cause is an HTTPX2 exception.

These type guarantees apply only to native HTTPX2 clients. An injected legacy
HTTPX client produces `httpx.Request`, `httpx.Response`, and HTTPX transport
exceptions instead, even if `cast_to=httpx2.Response` is supplied.

## aiohttp

The supported aiohttp extra uses an HTTPX2-native transport. It does not
install legacy HTTPX or the external `httpx-aiohttp` adapter:

```sh
pip install 'openai[aiohttp]'
```

```python
from openai import AsyncOpenAI, DefaultAioHttpClient

client = AsyncOpenAI(http_client=DefaultAioHttpClient())
```

`DefaultAioHttpClient()` is an `httpx2.AsyncClient`. Applications using this
helper do not need to construct or import the transport directly.

## Request mocking and tests

Mocks must intercept HTTPX2 requests and return HTTPX2 responses. For example:

```python
import httpx2
from openai import OpenAI


def handler(request: httpx2.Request) -> httpx2.Response:
    return httpx2.Response(
        200,
        request=request,
        json={"object": "list", "data": []},
    )


client = OpenAI(http_client=httpx2.Client(transport=httpx2.MockTransport(handler)))
assert client.models.list().data == []
```

If your test suite uses RESPX, update to an HTTPX2-compatible RESPX version or
fork. A RESPX version that patches only legacy HTTPX cannot intercept the SDK's
default HTTPX2 client. If you cannot migrate that integration immediately, the
temporary legacy-client escape hatch below lets existing HTTPX-only RESPX
setups continue to work while you migrate.

## Temporary escape hatch: a legacy HTTPX client

Applications that depend on an HTTPX-only transport, integration, or mocking
library can explicitly install legacy HTTPX and inject a legacy client:

```sh
pip install openai httpx
```

**Legacy HTTPX support is runtime-only.** The SDK's public type annotations
accept HTTPX2 clients, so passing a legacy client directly fails static type
checking in mypy, Pyright, and similar tools. Use `cast(Any, ...)` or a
targeted type-ignore when deliberately choosing this compatibility path:

```python
from typing import Any, cast

import httpx
from openai import OpenAI

client = OpenAI(http_client=cast(Any, httpx.Client()))
```

The asynchronous form requires the same workaround:

```python
from typing import Any, cast

import httpx
from openai import AsyncOpenAI

client = AsyncOpenAI(http_client=cast(Any, httpx.AsyncClient()))
```

Legacy clients preserve the HTTPX request, response, and exception families.
Request raw responses as `httpx.Response`, using the same type-checking
workaround for the legacy response class:

```python
from typing import Any, cast

import httpx
from openai import OpenAI

client = OpenAI(http_client=cast(Any, httpx.Client()))
response = client.get("/models", cast_to=cast(Any, httpx.Response))

assert isinstance(response, httpx.Response)
```

Passing `cast_to=httpx2.Response` does not convert a legacy HTTPX response into
an HTTPX2 response. Install and maintain the legacy dependency yourself.
Legacy HTTPX support is provided as a migration aid and may be discontinued.

### Existing legacy aiohttp adapters

If you must retain an existing `httpx-aiohttp` integration, install it
explicitly and inject its legacy client:

```sh
pip install openai httpx-aiohttp
```

```python
from typing import Any, cast

from httpx_aiohttp import HttpxAiohttpClient
from openai import AsyncOpenAI

client = AsyncOpenAI(http_client=cast(Any, HttpxAiohttpClient()))
```

This path is covered by dedicated compatibility tests, including a real
request through the aiohttp transport, but remains a temporary escape hatch.
Prefer `openai[aiohttp]` and `DefaultAioHttpClient()` for new code.
