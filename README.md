# OpenAI Python Library

The OpenAI Python library provides convenient access to the OpenAI API
from applications written in the Python language. It includes a
pre-defined set of classes for API resources that initialize
themselves dynamically from API responses which makes it compatible
with a wide range of versions of the OpenAI API.

This library additionally provides an `openai` command-line utility
which makes it easy to interact with the API from your terminal. Run
`openai api -h` for usage.

## Documentation

See the [OpenAI API docs](https://beta.openai.com/docs/api-reference?lang=python). (During
the beta, you'll need to be signed into your account to see them.)

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

## Requirements

-   Python 2.7+ or Python 3.4+ (PyPy supported)

In general we want to support the versions of Python that our
customers are using, so if you run into issues with any version
issues, please let us know at support@openai.com.

## Credit

This library is forked from the [Stripe Python Library](https://github.com/stripe/stripe-python).
