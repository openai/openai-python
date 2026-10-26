# Google Cloud Vertex AI

Use the standard `OpenAI` or `AsyncOpenAI` client to send Responses API requests to Vertex AI. Model and feature availability depend on your Google Cloud deployment.

Install the optional Vertex dependencies to use Google Application Default Credentials (ADC):

```sh
pip install 'openai[vertex]'
```

Configure ADC for a Google Cloud project with access to the target model, then create a client:

```python
from openai import OpenAI
from openai.providers import vertex

client = OpenAI(provider=vertex(project="my-google-project", location="us-east5"))
response = client.responses.create(model="your-enabled-model", input="Hello", store=False)
print(response.output_text)
```

You can set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` instead of passing `project` and `location`. Use a model enabled for that project and location.

To supply existing Google credentials, pass `credentials=` to `vertex()`. If your application manages token refresh, pass `token_provider=` instead; the callback returns a bearer token and is invoked for each request attempt. This mode works without the `vertex` extra.

With `AsyncOpenAI`, the token callback may return an awaitable. It runs on the event loop and must not block. The read timeout bounds the callback. If it finishes after that deadline, the client raises `APITimeoutError` before sending the Vertex request.

Google authentication uses the configured connect and read timeouts separately. Waiting for another request to refresh shared credentials uses the pool timeout. Async caller cancellation stops waiting for authentication, while any in-progress Google credential operation finishes in its worker thread.

Pass `base_url=` only when you trust the full API root to receive Google credentials. Google endpoints require HTTPS, and redirects are disabled.
