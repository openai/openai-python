# Martian Python API library

The Martin Python library is a drop in replacement for OpenAI package

## Documentation

The API documentation can be found [here](https://docs.withmartian.com/martian-api/).

## Installation

```sh
pip install martian-python
```

## Usage

```python
from martian import OpenAI

client = OpenAI(
    api_key="My MARTIAN API Key",  # defaults to os.environ.get("MARTIAN_API_KEY")
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    # model="gpt-3.5-turbo",  # Optional argument, router chooses the best model for you
)
```
