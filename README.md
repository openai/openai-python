# OpenAI Python Library

The OpenAI Python library provides convenient access to the OpenAI API
from applications written in the Python language. It includes a
pre-defined set of classes for API resources that initialize
themselves dynamically from API responses which makes it compatible
with a wide range of versions of the OpenAI API.

## Documentation

See the [OpenAI API docs](https://beta.openai.com/docs/api-reference?lang=python).

## Installation

You don't need this source code unless you want to modify the package. If you just
want to use the package, just run:

```sh
pip install --upgrade openai
```

Install from source with:

```sh
python setup.py install
```

## Usage

The library needs to be configured with your account's secret key which is available on the [website](https://beta.openai.com/account/api-keys). Either set it as the `OPENAI_API_KEY` environment variable before using the library:

```bash
export OPENAI_API_KEY='sk-...'
```

Or set `openai.api_key` to its value:

```python
import openai
openai.api_key = "sk-..."

# list engines
engines = openai.Engine.list()

# print the first engine's id
print(engines.data[0].id)

# create a completion
completion = openai.Completion.create(engine="ada", prompt="Hello world")

# print the completion
print(completion.choices[0].text)
```


### Params
All endpoints have a `.create` method that support a `request_timeout` param.  This param takes a `Union[float, Tuple[float, float]]` and will raise a `openai.error.TimeoutError` error if the request exceeds that time in seconds (See: https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts).

### Microsoft Azure Endpoints

In order to use the library with Microsoft Azure endpoints, you need to set the api_type, api_base and api_version in addition to the api_key. The api_type must be set to 'azure' and the others correspond to the properties of your endpoint.
In addition, the deployment name must be passed as the engine parameter.

```python
import openai
openai.api_type = "azure"
openai.api_key = "..."
openai.api_base = "https://example-endpoint.openai.azure.com"
openai.api_version = "2021-11-01-preview"

# create a completion
completion = openai.Completion.create(engine="deployment-name", prompt="Hello world")

# print the completion
print(completion.choices[0].text)

# create a search and pass the deployment-name as the engine Id.
search = openai.Engine(id="deployment-name").search(documents=["White House", "hospital", "school"], query ="the president")

# print the search
print(search)
```

Please note that for the moment, the Microsoft Azure endpoints can only be used for completion, search and fine-tuning operations.
For a detailed example on how to use fine-tuning and other operations using Azure endpoints, please check out the following Jupyter notebooks:
* [Using Azure fine-tuning](https://github.com/openai/openai-cookbook/tree/main/examples/azure/finetuning.ipynb)
* [Using Azure embeddings](https://github.com/openai/openai-cookbook/blob/main/examples/azure/embeddings.ipynb)

### Microsoft Azure Active Directory Authentication

In order to use Microsoft Active Directory to authenticate to your Azure endpoint, you need to set the api_type to "azure_ad" and pass the acquired credential token to api_key. The rest of the parameters need to be set as specified in the previous section.


```python
from azure.identity import DefaultAzureCredential
import openai

# Request credential
default_credential = DefaultAzureCredential()
token = default_credential.get_token("https://cognitiveservices.azure.com")

# Setup parameters
openai.api_type = "azure_ad"
openai.api_key = token.token
openai.api_base = "https://example-endpoint.openai.azure.com/"
openai.api_version = "2022-03-01-preview"

# ...
```
### Command-line interface

This library additionally provides an `openai` command-line utility
which makes it easy to interact with the API from your terminal. Run
`openai api -h` for usage.

```sh
# list engines
openai api engines.list

# create a completion
openai api completions.create -e ada -p "Hello world"

# generate images via DALL·E API
openai api image.create -p "two dogs playing chess, cartoon" -n 1
```

## Example code

Examples of how to use this Python library to accomplish various tasks can be found in the [OpenAI Cookbook](https://github.com/openai/openai-cookbook/). It contains code examples for:

* Classification using fine-tuning
* Clustering
* Code search
* Customizing embeddings
* Question answering from a corpus of documents
* Recommendations
* Visualization of embeddings
* And more

Prior to July 2022, this OpenAI Python library hosted code examples in its examples folder, but since then all examples have been migrated to the [OpenAI Cookbook](https://github.com/openai/openai-cookbook/).

### Embeddings

In the OpenAI Python library, an embedding represents a text string as a fixed-length vector of floating point numbers. Embeddings are designed to measure the similarity or relevance between text strings.

To get an embedding for a text string, you can use the embeddings method as follows in Python:

```python
import openai
openai.api_key = "sk-..."  # supply your API key however you choose

# choose text to embed
text_string = "sample text"

# choose an embedding
model_id = "text-similarity-davinci-001"

# compute the embedding of the text
embedding = openai.Embedding.create(input=text_string, engine=model_id)['data'][0]['embedding']
```

An example of how to call the embeddings method is shown in this [get embeddings notebook](https://github.com/openai/openai-cookbook/blob/main/examples/Get_embeddings.ipynb).

Examples of how to use embeddings are shared in the following Jupyter notebooks:

- [Classification using embeddings](https://github.com/openai/openai-cookbook/blob/main/examples/Classification_using_embeddings.ipynb)
- [Clustering using embeddings](https://github.com/openai/openai-cookbook/blob/main/examples/Clustering.ipynb)
- [Code search using embeddings](https://github.com/openai/openai-cookbook/blob/main/examples/Code_search.ipynb)
- [Semantic text search using embeddings](https://github.com/openai/openai-cookbook/blob/main/examples/Semantic_text_search_using_embeddings.ipynb)
- [User and product embeddings](https://github.com/openai/openai-cookbook/blob/main/examples/User_and_product_embeddings.ipynb)
- [Zero-shot classification using embeddings](https://github.com/openai/openai-cookbook/blob/main/examples/Zero-shot_classification_with_embeddings.ipynb)
- [Recommendation using embeddings](https://github.com/openai/openai-cookbook/blob/main/examples/Recommendation_using_embeddings.ipynb)

For more information on embeddings and the types of embeddings OpenAI offers, read the [embeddings guide](https://beta.openai.com/docs/guides/embeddings) in the OpenAI documentation.

### Fine tuning

Fine tuning a model on training data can both improve the results (by giving the model more examples to learn from) and reduce the cost/latency of API calls (chiefly through reducing the need to include training examples in prompts).

Examples of fine tuning are shared in the following Jupyter notebooks:

- [Classification with fine tuning](https://github.com/openai/openai-cookbook/blob/main/examples/Fine-tuned_classification.ipynb) (a simple notebook that shows the steps required for fine tuning)
- Fine tuning a model that answers questions about the 2020 Olympics
  - [Step 1: Collecting data](https://github.com/openai/openai-cookbook/blob/main/examples/fine-tuned_qa/olympics-1-collect-data.ipynb)
  - [Step 2: Creating a synthetic Q&A dataset](https://github.com/openai/openai-cookbook/blob/main/examples/fine-tuned_qa/olympics-2-create-qa.ipynb)
  - [Step 3: Train a fine-tuning model specialized for Q&A](https://github.com/openai/openai-cookbook/blob/main/examples/fine-tuned_qa/olympics-3-train-qa.ipynb)

Sync your fine-tunes to [Weights & Biases](https://wandb.me/openai-docs) to track experiments, models, and datasets in your central dashboard with:

```bash
openai wandb sync
```

For more information on fine tuning, read the [fine-tuning guide](https://beta.openai.com/docs/guides/fine-tuning) in the OpenAI documentation.

### Moderation

OpenAI provides a Moderation endpoint that can be used to check whether content complies with the OpenAI [content policy](https://beta.openai.com/docs/usage-policies)

```python
import openai
openai.api_key = "sk-..."  # supply your API key however you choose

moderation_resp = openai.Moderation.create(input="Here is some perfectly innocuous text that follows all OpenAI content policies.")
```

See the [moderation guide](https://beta.openai.com/docs/guides/moderation) for more details.

## Image generation (DALL·E)

```python
import openai
openai.api_key = "sk-..."  # supply your API key however you choose

image_resp = openai.Image.create(prompt="two dogs playing chess, oil painting", n=4, size="512x512")

```

See the [usage guide](https://beta.openai.com/docs/guides/images) for more details.

## Requirements

- Python 3.7.1+

In general, we want to support the versions of Python that our
customers are using. If you run into problems with any version
issues, please let us know at support@openai.com.

## Credit

This library is forked from the [Stripe Python Library](https://github.com/stripe/stripe-python).
