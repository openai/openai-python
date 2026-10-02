
<p align="center"><strong>httpx-aiohttp</strong> <em>- provides transports for httpx to work on top of aiohttp, handling all high-level features like authentication, retries, and cookies through httpx, while delegating low-level socket-level HTTP messaging to aiohttp</em></p>

<p align="center">

  <a href="https://pypi.org/project/httpx-aiohttp">
      <img src="https://img.shields.io/pypi/v/httpx-aiohttp.svg" alt="pypi">
  </a>
</p>

## Installation

```shell
uv pip install httpx-aiohttp
```

For [httpx2](https://github.com/pydantic/httpx2) support, install the `httpx2` extra and use `httpx_aiohttp.httpx2.Httpx2AiohttpClient` / `httpx_aiohttp.httpx2.AiohttpTransport`:

```shell
uv pip install httpx-aiohttp[httpx2]
```

## Documentation

Project documentation is available at https://karpetrosyan.github.io/httpx-aiohttp/
