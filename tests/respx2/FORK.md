# HTTPX2-native RESPX fork

This directory contains an SDK test-only fork of RESPX 0.23.1.

- Upstream: https://github.com/lundberg/respx
- Upstream tag: `0.23.1`
- Upstream commit: `fc8b43bc74a69d07a6bdccf61522069b12bb8fad`
- License: BSD 3-Clause; the original license is preserved in `LICENSE.md`.
- The upstream README is preserved without modification in `README.md`.

The fork replaces HTTPX and HTTPCORE imports and interception targets with HTTPX2 and HTTPCORE2, exposes the `respx2` pytest marker and `respx2_mock` fixture, and changes package imports to `tests.respx2`. This lets the SDK retain RESPX request matching, response side effects, decorators, and call history without installing legacy HTTPX in its normal test environment.

The fork is limited to the SDK test suite and may be removed or upstreamed once RESPX supports HTTPX2 without requiring legacy HTTPX.
