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

### Microsoft Azure Endpoints

In order to use the library with Microsoft Azure endpoints, you need to set the api_type, api_base and api_version in addition to the api_key. The api_type must be set to 'azure' and the others correspond to the properites of your endpoint.
In addition, the deployment name must be passed as the engine parameter.

```python
import openai
openai.api_type = "azure"
openai.api_key = "..."
openai.api_base = "https://example-endpoint.openai.azure.com"
openai.api_version = "2021-11-01-preview"

# create a completion
completion = openai.Completion.create(engine="deployment-namme", prompt="Hello world")

# print the completion
print(completion.choices[0].text)

# create a search and pass the deployment-name as the engine Id.
search = openai.Engine(id="deployment-namme").search(documents=["White House", "hospital", "school"], query ="the president")

# print the search
print(search)
```
Please note that for the moment, the Microsoft Azure endpoints can only be used for completion and search operations.

### Command-line interface

This library additionally provides an `openai` command-line utility
which makes it easy to interact with the API from your terminal. Run
`openai api -h` for usage.

```sh
# list engines
openai api engines.list

# create a completion
openai api completions.create -e ada -p "Hello world"
```

## Example code

Examples of how to use [embeddings](https://github.com/openai/openai-python/tree/main/examples/embeddings), [fine tuning](https://github.com/openai/openai-python/tree/main/examples/finetuning), [semantic search](https://github.com/openai/openai-python/tree/main/examples/semanticsearch), and [codex](https://github.com/openai/openai-python/tree/main/examples/codex) can be found in the [examples folder](https://github.com/openai/openai-python/tree/main/examples).

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

An example of how to call the embeddings method is shown in the [get embeddings notebook](https://github.com/openai/openai-python/blob/main/examples/embeddings/Get_embeddings.ipynb).

Examples of how to use embeddings are shared in the following Jupyter notebooks:

- [Classification using embeddings](https://github.com/openai/openai-python/blob/main/examples/embeddings/Classification.ipynb)
- [Clustering using embeddings](https://github.com/openai/openai-python/blob/main/examples/embeddings/Clustering.ipynb)
- [Code search using embeddings](https://github.com/openai/openai-python/blob/main/examples/embeddings/Code_search.ipynb)
- [Semantic text search using embeddings](https://github.com/openai/openai-python/blob/main/examples/embeddings/Semantic_text_search_using_embeddings.ipynb)
- [User and product embeddings](https://github.com/openai/openai-python/blob/main/examples/embeddings/User_and_product_embeddings.ipynb)
- [Zero-shot classification using embeddings](https://github.com/openai/openai-python/blob/main/examples/embeddings/Zero-shot_classification.ipynb)
- [Recommendation using embeddings](https://github.com/openai/openai-python/blob/main/examples/embeddings/Recommendation.ipynb)

For more information on embeddings and the types of embeddings OpenAI offers, read the [embeddings guide](https://beta.openai.com/docs/guides/embeddings) in the OpenAI documentation.

### Fine tuning

Fine tuning a model on training data can both improve the results (by giving the model more examples to learn from) and reduce the cost & latency of API calls (by reducing the need to include training examples in prompts).

Examples of fine tuning are shared in the following Jupyter notebooks:

- [Classification with fine tuning](https://github.com/openai/openai-python/blob/main/examples/finetuning/finetuning-classification.ipynb) (a simple notebook that shows the steps required for fine tuning)
- Fine tuning a model that answers questions about the 2020 Olympics
  - [Step 1: Collecting data](https://github.com/openai/openai-python/blob/main/examples/finetuning/olympics-1-collect-data.ipynb)
  - [Step 2: Creating a synthetic Q&A dataset](https://github.com/openai/openai-python/blob/main/examples/finetuning/olympics-2-create-qa.ipynb)
  - [Step 3: Train a fine-tuning model specialized for Q&A](https://github.com/openai/openai-python/blob/main/examples/finetuning/olympics-3-train-qa.ipynb)

For more information on fine tuning, read the [fine-tuning guide](https://beta.openai.com/docs/guides/fine-tuning) in the OpenAI documentation.

## Requirements

- Python 3.7.1+

In general we want to support the versions of Python that our
customers are using, so if you run into issues with any version
issues, please let us know at support@openai.com.

## Credit

This library is forked from the [Stripe Python Library](https://github.com/stripe/stripe-python).
