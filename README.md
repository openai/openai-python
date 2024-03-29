# Getting started with Not Diamond

Not Diamond helps you leverage multiple LLMs dynamically, sending queries to the best-suited model in real-time.

# Key features

- **Not a proxy**: When we receive a query, our backend service returns a recommendation of the model you should call and the actual call goes out client-side. _So we never see your response outputs._
- **Privacy preserving**: To protect your privacy, we use [fuzzy hashing](https://en.wikipedia.org/wiki/Fuzzy_hashing) to conceal your query strings from us, and our model recommendation engine works entirely using the fuzzy hashed queries. _This means we also never see the raw query strings you send to an LLM._
- **Maximize performance**: By dynamically routing to the best-suited LLM for each query, we improve your overall LLM output quality and enhance product quality. Our recommendations are based on millions of data points from rigorous evaluation benchmarks and real-world data.
- **Reduce cost and latency**: Most of the time, a small and specialized model can optimally handle a given query. We can help you determine this in real-time, cutting your LLM inference costs while reducing latency.

> 👍 **Free to use!**
>
> Not Diamond is free up to 100K monthly requests. Beyond this pay just $10 per 10K requests.

# Installation

Requires **Python 3.9+**

```shell
pip install notdiamond
```

# API keys

### [Sign up](https://app.notdiamond.ai) and get a Not Diamond API key.

Create a `.env` file with your Not Diamond API key, and the API keys of the models you want to route between.

```shell
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
NOTDIAMOND_API_KEY="YOUR_NOTDIAMOND_API_KEY"
```

Alternatively, you can also set API keys programmatically [as described further below](#defining-our-selection-of-llms).

> 📘 **API keys**
>
> The `notdiamond` library uses your API keys client-side to call the LLM we recommend. **We never pass your keys to our servers.**

> 🚧 **Model access**
>
> Since `notdiamond` calls the LLMs client-side using your keys, we will only call models you have access to. You can also use our router to determine the best model to call regardless of whether you have access or not (see [example](https://notdiamond.readme.io/v1.1/docs/fallbacks-and-custom-routing-logic#custom-routing-logic)). Our router supports most of the popular open and proprietary models (see [full list](https://notdiamond.readme.io/v1.0/docs/supported-models)).
>
> [Drop me a line](mailto:t5@notdiamond.ai) if you have a specific model requirement and we're happy to work with you to support it.

# Example

_If you already have existing projects in either OpenAI SDK or LangChain, check out our [OpenAI](https://notdiamond.readme.io/v1.0/docs/openai-sdk-integration) and [Langchain](https://notdiamond.readme.io/v1.0/docs/langchain-integration) integration guides. Otherwise, continue reading._

Create a `main.py` file in the same folder as the [`.env`](#api-keys) file you created earlier, or **[try it in Colab](https://colab.research.google.com/drive/1Ao-YhYF_S6QP5UGp_kYhgKps_Sw3a2RO?usp=sharing).**

```python
from notdiamond.llms.llm import NDLLM
from notdiamond.prompts.prompt import NDPrompt, NDContext, NDQuery, NDPromptTemplate


# Define your prompt and query
prompt = NDPrompt("You are a world class software developer.") # The system prompt, defines the LLM's role
query = NDQuery("Write a merge sort in Python.") # The specific query written by an end-user

# Define the prompt template to combine prompt and query into a single string
prompt_template = NDPromptTemplate("About you: {prompt}\n{query}",
                                   partial_variables={"prompt": prompt, "query": query})

# Define the available LLMs you'd like to route between
llm_providers = ['openai/gpt-3.5-turbo', 'openai/gpt-4','openai/gpt-4-1106-preview', 'openai/gpt-4-turbo-preview',
                 'anthropic/claude-2.1', 'anthropic/claude-3-sonnet-20240229', 'anthropic/claude-3-opus-20240229',
                 'google/gemini-pro']

# Create the NDLLM object -> like a 'meta-LLM' combining all of the specified models
nd_llm = NDLLM(llm_providers=llm_providers)

# After fuzzy hashing the inputs, the best LLM is determined by the ND API and the LLM is called client-side
result, session_id, provider = nd_llm.invoke(prompt_template=prompt_template)


print("ND session ID: ", session_id)  # A unique ID of the invoke. Important for future references back to ND API
print("LLM called: ", provider.model)  # The LLM routed to
print("LLM output: ", result.content)  # The LLM response
```

> 👍 **Run it!**
>
> `python main.py`
