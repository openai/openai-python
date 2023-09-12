# OpenAI Python Library

The OpenAI Python library provides convenient access to the OpenAI API
from applications written in the Python language. It includes a
pre-defined set of classes for API resources that initialize
themselves dynamically from API responses which makes it compatible
with a wide range of versions of the OpenAI API.

You can find usage examples for the OpenAI Python library in our [API reference](https://platform.openai.com/docs/api-reference?lang=python) and the [OpenAI Cookbook](https://github.com/openai/openai-cookbook/).

## Installation

To start, ensure you have Python 3.7.1 or newer. If you just
want to use the package, run:

```sh
pip install --upgrade openai
```

After you have installed the package, import it at the top of a file:

```python
import openai
```

To install this package from source to make modifications to it, run the following command from the root of the repository:

```sh
python setup.py install
```

### Optional dependencies

Install dependencies for [`openai.embeddings_utils`](openai/embeddings_utils.py):

```sh
pip install openai[embeddings]
```

Install support for [Weights & Biases](https://wandb.me/openai-docs):

```sh
pip install openai[wandb]
```

Data libraries like `numpy` and `pandas` are not installed by default due to their size. They’re needed for some functionality of this library, but generally not for talking to the API. If you encounter a `MissingDependencyError`, install them with:

```sh
pip install openai[datalib]
```

## Usage

The library needs to be configured with your account's secret key which is available on the [website](https://platform.openai.com/account/api-keys). Either set it as the `OPENAI_API_KEY` environment variable before using the library:

```bash
export OPENAI_API_KEY='sk-...'
```

Or set `openai.api_key` to its value:

```python
openai.api_key = "sk-..."
```

Examples of how to use this library to accomplish various tasks can be found in the [OpenAI Cookbook](https://github.com/openai/openai-cookbook/). It contains code examples for: classification using fine-tuning, clustering, code search, customizing embeddings, question answering from a corpus of documents. recommendations, visualization of embeddings, and more.

Most endpoints support a `request_timeout` param. This param takes a `Union[float, Tuple[float, float]]` and will raise an `openai.error.Timeout` error if the request exceeds that time in seconds (See: https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts).

### Chat completions

Chat models such as `gpt-3.5-turbo` and `gpt-4` can be called using the [chat completions endpoint](https://platform.openai.com/docs/api-reference/chat/create).

```python
completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}])
print(completion.choices[0].message.content)
```

You can learn more in our [chat completions guide](https://platform.openai.com/docs/guides/gpt/chat-completions-api).

### Completions

Text models such as `babbage-002` or `davinci-002` (and our [legacy completions models](https://platform.openai.com/docs/deprecations/deprecation-history)) can be called using the completions endpoint.

```python
completion = openai.Completion.create(model="davinci-002", prompt="Hello world")
print(completion.choices[0].text)
```

You can learn more in our [completions guide](https://platform.openai.com/docs/guides/gpt/completions-api).

### Embeddings

Embeddings are designed to measure the similarity or relevance between text strings. To get an embedding for a text string, you can use following:

```python
text_string = "sample text"

model_id = "text-embedding-ada-002"

embedding = openai.Embedding.create(input=text_string, model=model_id)['data'][0]['embedding']
```

You can learn more in our [embeddings guide](https://platform.openai.com/docs/guides/embeddings/embeddings).

### Fine-tuning

Fine-tuning a model on training data can both improve the results (by giving the model more examples to learn from) and lower the cost/latency of API calls by reducing the need to include training examples in prompts.

```python
# Create a fine-tuning job with an already uploaded file
openai.FineTuningJob.create(training_file="file-abc123", model="gpt-3.5-turbo")

# List 10 fine-tuning jobs
openai.FineTuningJob.list(limit=10)

# Retrieve the state of a fine-tune
openai.FineTuningJob.retrieve("ft-abc123")

# Cancel a job
openai.FineTuningJob.cancel("ft-abc123")

# List up to 10 events from a fine-tuning job
openai.FineTuningJob.list_events(id="ft-abc123", limit=10)

# Delete a fine-tuned model (must be an owner of the org the model was created in)
openai.Model.delete("ft:gpt-3.5-turbo:acemeco:suffix:abc123")
```

You can learn more in our [fine-tuning guide](https://platform.openai.com/docs/guides/fine-tuning).

To log the training results from fine-tuning to Weights & Biases use:

```
openai wandb sync
```

For more information, read the [wandb documentation](https://docs.wandb.ai/guides/integrations/openai) on Weights & Biases.

### Moderation

OpenAI provides a free Moderation endpoint that can be used to check whether content complies with the OpenAI [content policy](https://platform.openai.com/docs/usage-policies).

```python
moderation_resp = openai.Moderation.create(input="Here is some perfectly innocuous text that follows all OpenAI content policies.")
```

You can learn more in our [moderation guide](https://platform.openai.com/docs/guides/moderation).

### Image generation (DALL·E)

DALL·E is a generative image model that can create new images based on a prompt. 

```python
image_resp = openai.Image.create(prompt="two dogs playing chess, oil painting", n=4, size="512x512")
```

You can learn more in our [image generation guide](https://platform.openai.com/docs/guides/images).

### Audio (Whisper)

The speech to text API provides two endpoints, transcriptions and translations, based on our state-of-the-art [open source large-v2 Whisper model](https://github.com/openai/whisper).

```python
f = open("path/to/file.mp3", "rb")
transcript = openai.Audio.transcribe("whisper-1", f)

transcript = openai.Audio.translate("whisper-1", f)
```

You can learn more in our [speech to text guide](https://platform.openai.com/docs/guides/speech-to-text).

### Async API

Async support is available in the API by prepending `a` to a network-bound method:

```python
async def create_chat_completion():
    chat_completion_resp = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}])
```

To make async requests more efficient, you can pass in your own
`aiohttp.ClientSession`, but you must manually close the client session at the end
of your program/event loop:

```python
from aiohttp import ClientSession
openai.aiosession.set(ClientSession())

# At the end of your program, close the http session
await openai.aiosession.get().close()
```

### Command-line interface

This library additionally provides an `openai` command-line utility
which makes it easy to interact with the API from your terminal. Run
`openai api -h` for usage.

```sh
# list models
openai api models.list

# create a chat completion (gpt-3.5-turbo, gpt-4, etc.)
openai api chat_completions.create -m gpt-3.5-turbo -g user "Hello world"

# create a completion (text-davinci-003, text-davinci-002, ada, babbage, curie, davinci, etc.)
openai api completions.create -m ada -p "Hello world"

# generate images via DALL·E API
openai api image.create -p "two dogs playing chess, cartoon" -n 1

# using openai through a proxy
openai --proxy=http://proxy.com api models.list
```

### Microsoft Azure Endpoints

In order to use the library with Microsoft Azure endpoints, you need to set the `api_type`, `api_base` and `api_version` in addition to the `api_key`. The `api_type` must be set to 'azure' and the others correspond to the properties of your endpoint.
In addition, the deployment name must be passed as the engine parameter.

```python
import openai
openai.api_type = "azure"
openai.api_key = "..."
openai.api_base = "https://example-endpoint.openai.azure.com"
openai.api_version = "2023-05-15"

# create a chat completion
chat_completion = openai.ChatCompletion.create(deployment_id="deployment-name", model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}])

# print the completion
print(chat_completion.choices[0].message.content)
```

Please note that for the moment, the Microsoft Azure endpoints can only be used for completion, embedding, and fine-tuning operations.
For a detailed example of how to use fine-tuning and other operations using Azure endpoints, please check out the following Jupyter notebooks:

- [Using Azure completions](https://github.com/openai/openai-cookbook/tree/main/examples/azure/completions.ipynb)
- [Using Azure chat](https://github.com/openai/openai-cookbook/tree/main/examples/azure/chat.ipynb)
- [Using Azure embeddings](https://github.com/openai/openai-cookbook/blob/main/examples/azure/embeddings.ipynb)

### Microsoft Azure Active Directory Authentication

In order to use Microsoft Active Directory to authenticate to your Azure endpoint, you need to set the `api_type` to "azure_ad" and pass the acquired credential token to `api_key`. The rest of the parameters need to be set as specified in the previous section.

```python
from azure.identity import DefaultAzureCredential
import openai

# Request credential
default_credential = DefaultAzureCredential()
token = default_credential.get_token("https://cognitiveservices.azure.com/.default")

# Setup parameters
openai.api_type = "azure_ad"
openai.api_key = token.token
openai.api_base = "https://example-endpoint.openai.azure.com/"
openai.api_version = "2023-05-15"
```

## Credit

This library is forked from the [Stripe Python Library](https://github.com/stripe/stripe-python).
