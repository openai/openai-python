<p align="center">
  <a href="https://lundberg.github.io/respx/"><img width="350" height="208" src="https://raw.githubusercontent.com/lundberg/respx/master/docs/img/respx.png" alt='RESPX'></a>
</p>
<p align="center">
  <strong>RESPX</strong> <em>- Mock HTTPX with awesome request patterns and response side effects.</em>
</p>

---

[![tests](https://img.shields.io/github/actions/workflow/status/lundberg/respx/test.yml?branch=master&label=tests&logo=github&logoColor=white&style=for-the-badge)](https://github.com/lundberg/respx/actions/workflows/test.yml)
[![codecov](https://img.shields.io/codecov/c/github/lundberg/respx?logo=codecov&logoColor=white&style=for-the-badge)](https://codecov.io/gh/lundberg/respx)
[![PyPi Version](https://img.shields.io/pypi/v/respx?logo=pypi&logoColor=white&style=for-the-badge)](https://pypi.org/project/respx/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/respx?style=for-the-badge&logo=pypi&logoColor=white&color=mediumpurple)](https://pypi.org/project/respx/)
[![Python Versions](https://img.shields.io/pypi/pyversions/respx?logo=python&logoColor=white&style=for-the-badge)](https://pypi.org/project/respx/)

## Documentation

Full documentation is available at
[lundberg.github.io/respx](https://lundberg.github.io/respx/)

## QuickStart

RESPX is a simple, _yet powerful_, utility for mocking out the
[HTTPX](https://www.python-httpx.org/), _and
[HTTP Core](https://www.encode.io/httpcore/)_, libraries.

Start by [patching](https://lundberg.github.io/respx/guide/#mock-httpx) `HTTPX`, using
`respx.mock`, then add request
[routes](https://lundberg.github.io/respx/guide/#routing-requests) to mock
[responses](https://lundberg.github.io/respx/guide/#mocking-responses).

```python
import httpx
import respx

from httpx import Response


@respx.mock
def test_example():
    my_route = respx.get("https://example.org/").mock(return_value=Response(204))
    response = httpx.get("https://example.org/")
    assert my_route.called
    assert response.status_code == 204
```

> Read the [User Guide](https://lundberg.github.io/respx/guide/) for a complete
> walk-through.

### pytest + httpx

For a neater `pytest` experience, RESPX includes a `respx_mock` _fixture_ for easy
`HTTPX` mocking, along with an optional `respx` _marker_ to fine-tune the mock
[settings](https://lundberg.github.io/respx/api/#configuration).

```python
import httpx
import pytest


def test_default(respx_mock):
    respx_mock.get("https://foo.bar/").mock(return_value=httpx.Response(204))
    response = httpx.get("https://foo.bar/")
    assert response.status_code == 204


@pytest.mark.respx(base_url="https://foo.bar")
def test_with_marker(respx_mock):
    respx_mock.get("/baz/").mock(return_value=httpx.Response(204))
    response = httpx.get("https://foo.bar/baz/")
    assert response.status_code == 204
```

## Installation

Install with pip:

```console
$ pip install respx
```

Requires Python 3.8+ and HTTPX 0.25+. See
[Changelog](https://github.com/lundberg/respx/blob/master/CHANGELOG.md) for older HTTPX
compatibility.
