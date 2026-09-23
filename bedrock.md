# Amazon Bedrock

The Bedrock provider connects the standard synchronous and asynchronous OpenAI clients to Amazon Bedrock's
OpenAI-compatible endpoints. The provider supports bearer tokens without additional dependencies. AWS Signature
Version 4 (SigV4) requires the optional Bedrock dependencies:

```sh
pip install 'openai[bedrock]'
```

Runtime endpoint selection requires a Python SDK release that includes SDK-290. The SDK supports Python 3.10 and newer.

## Endpoint selection

| `endpoint` | Default API root | SigV4 signing service |
| --- | --- | --- |
| `"mantle"` (default) | `https://bedrock-mantle.<region>.api.aws/openai/v1` | `bedrock-mantle` |
| `"runtime"` | `https://bedrock-runtime.<region>.amazonaws.com/openai/v1` | `bedrock` |

Runtime hostnames use the DNS suffix for the selected AWS partition. For example, the European sovereign region
`eusc-de-east-1` uses `amazonaws.eu`. Canonical Runtime FIPS and dual-stack hostnames are also recognized.

The region comes from `region`, `AWS_REGION`, `AWS_DEFAULT_REGION`, or, for AWS authentication, the selected AWS profile.
Pass `base_url` or set `AWS_BEDROCK_BASE_URL` to override the derived API root. When `endpoint` is omitted, canonical
Mantle and Runtime URLs select the corresponding endpoint and signing service automatically; otherwise Mantle remains
the default. Custom or proxy URLs likewise use Mantle signing by default; pass `endpoint="runtime"` when a custom host
requires Runtime signing.

## Runtime Chat Completions

Use an inference-profile ID such as `us.openai.gpt-5.6-sol`, `us.openai.gpt-5.6-terra`, or
`us.openai.gpt-5.6-luna`. These deployments do not accept the corresponding bare model ID. Global inference profiles,
such as `global.openai.gpt-5.6-sol`, require an AWS account and permissions that allow the corresponding profile.

```python
from openai import OpenAI
from openai.providers import bedrock

client = OpenAI(
    provider=bedrock(
        endpoint="runtime",
        region="us-west-2",
        api_key=None,
    )
)

completion = client.chat.completions.create(
    model="us.openai.gpt-5.6-sol",
    messages=[{"role": "user", "content": "Say hello!"}],
)
print(completion.choices[0].message.content)
```

`api_key=None` prevents `AWS_BEARER_TOKEN_BEDROCK` from shadowing AWS credentials and forces SigV4 authentication. Omit
`region` to use the normal environment or AWS profile region chain.

For streaming, set `stream=True`:

```python
stream = client.chat.completions.create(
    model="us.openai.gpt-5.6-sol",
    messages=[{"role": "user", "content": "Say hello!"}],
    stream=True,
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
```

The asynchronous client uses the same provider configuration:

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(provider=bedrock(endpoint="runtime", region="us-west-2", api_key=None))
completion = await client.chat.completions.create(
    model="us.openai.gpt-5.6-sol",
    messages=[{"role": "user", "content": "Say hello!"}],
)
```

See [`examples/bedrock_runtime.py`](examples/bedrock_runtime.py) for a runnable example supporting SigV4, bearer
authentication, model selection, AWS profiles, and opt-in streaming.

## Authentication

Authentication is chosen in this order:

1. Explicit bearer credentials, static AWS credentials, a named profile, or an AWS credential provider.
2. The bearer token in `AWS_BEARER_TOKEN_BEDROCK`, unless `api_key=None` disables this fallback.
3. The default AWS credential chain.

Explicit bearer and AWS credential modes cannot be combined. A stale environment bearer token takes precedence over the
implicit AWS credential chain; unset it or pass `api_key=None` when SigV4 is required.

### Bearer credentials

```python
client = OpenAI(
    provider=bedrock(
        endpoint="runtime",
        region="us-west-2",
        api_key="your-bedrock-api-key",
    )
)
```

A callable token provider is invoked before every request attempt, including retries. `AsyncOpenAI` also accepts an
asynchronous callable:

```python
client = AsyncOpenAI(
    provider=bedrock(
        endpoint="runtime",
        region="us-west-2",
        token_provider=refresh_bedrock_token,
    )
)
```

### AWS credentials and profiles

Use the default AWS credential chain or select a named shared-config profile:

```python
client = OpenAI(
    provider=bedrock(
        endpoint="runtime",
        profile="my-aws-profile",
        api_key=None,
    )
)
```

Temporary static credentials can include a session token:

```python
client = OpenAI(
    provider=bedrock(
        endpoint="runtime",
        region="us-west-2",
        access_key_id="your-access-key",
        secret_access_key="your-secret-key",
        session_token="your-session-token",
    )
)
```

Pass `credential_provider` for refreshing AWS credentials. The provider is called for every signed request attempt.
Signed requests require replayable request bodies and do not automatically follow redirects.

## API routes and support limitations

The SDK defaults to `/openai/v1`, matching
[AWS's OpenAI model documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-openai.html).
[AWS's Chat Completions documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-chat-completions-mantle.html)
also describes a `/v1` Runtime route. Override `base_url` when a deployment requires that route:

```python
client = OpenAI(
    provider=bedrock(
        endpoint="runtime",
        region="us-west-2",
        base_url="https://bedrock-runtime.us-west-2.amazonaws.com/v1",
        api_key=None,
    )
)
```

The provider exposes normal Chat Completions and Responses resources, but AWS determines which routes, models,
inference profiles, authentication methods, and streaming features each deployment accepts. Runtime Responses and
streaming should be live-validated for the selected model, profile, route, authentication mode, and AWS account.

Canonical AWS endpoints must use HTTPS and match the configured endpoint family and region. Bedrock credentials are
never attached to a request whose origin differs from the configured API root. Explicitly configured custom or local
HTTP proxies remain available when required; use them only inside a trusted environment.

## Opt-in live verification

The existing live harness requires explicit opt-in and valid AWS credentials:

```sh
BEDROCK_LIVE_TEST=1 BEDROCK_LIVE_ENDPOINT=runtime AWS_REGION=us-west-2 \
  uv run --locked --all-extras pytest -q -s tests/lib/bedrock_live.py
```

Runtime verification defaults to all three US GPT-5.6 inference profiles. Select authentication modes with
`BEDROCK_LIVE_AUTHS=bearer,environment-bearer,token-provider,default-chain,profile,static`; select specific models with
`BEDROCK_LIVE_MODELS`. Set `BEDROCK_LIVE_STREAM=1` to include streaming and `BEDROCK_LIVE_RESPONSES=1` to include
Runtime Responses. Provide `AWS_PROFILE` or `BEDROCK_LIVE_PROFILE` for named-profile verification.
