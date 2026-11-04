# HTTPX2-native aiohttp adapter

This directory vendors the HTTPX2-specific adapter from httpx-aiohttp 0.2.0.

- Upstream: https://github.com/karpetrosyan/httpx-aiohttp
- Upstream tag: `0.2.0`
- Upstream commit: `52266a66f6bd73f828133d0fd09114179fd45b60`
- License: BSD 3-Clause; the original license is preserved in `LICENSE`.
- The upstream README is preserved without modification in `README.md`.

The upstream distribution always installs and imports legacy HTTPX even when only its HTTPX2 adapter is used. Vendoring the three HTTPX2-specific modules lets `openai[aiohttp]` depend only on HTTPX2 and aiohttp while preserving the upstream transport behavior.

Local changes:

- Import `SocketTimeoutError` explicitly. aiohttp before 3.10 does not export
  this exception, so importing the adapter raises `ImportError` and the SDK
  keeps its default HTTPX2 clients available. This does not enable the aiohttp
  adapter on older versions or lower the `openai[aiohttp]` dependency minimum.

The fork may be removed when upstream provides an HTTPX2-only distribution or makes legacy HTTPX genuinely optional.
