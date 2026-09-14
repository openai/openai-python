# HTTPX2-native aiohttp adapter

This directory vendors the HTTPX2-specific adapter from httpx-aiohttp 0.2.0.

- Upstream: https://github.com/karpetrosyan/httpx-aiohttp
- Upstream tag: `0.2.0`
- Upstream commit: `52266a66f6bd73f828133d0fd09114179fd45b60`
- License: BSD 3-Clause; the original license is preserved in `LICENSE`.
- The upstream README is preserved without modification in `README.md`.

The upstream distribution always installs and imports legacy HTTPX even when only its HTTPX2 adapter is used. Vendoring the three HTTPX2-specific modules lets `openai[aiohttp]` depend only on HTTPX2 and aiohttp while preserving the upstream transport behavior. No functional changes have been made to the upstream adapter.

The fork may be removed when upstream provides an HTTPX2-only distribution or makes legacy HTTPX genuinely optional.
