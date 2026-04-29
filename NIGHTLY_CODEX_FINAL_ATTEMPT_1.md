Implemented a small lifecycle-focused contribution for the async client issue.

Changed:
- [README.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/README.md:894): added `AsyncOpenAI` context-manager guidance and ASGI startup/shutdown lifecycle note.
- [tests/test_client.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/test_client.py:1906): added a focused test that `AsyncOpenAI` closes a supplied `httpx.AsyncClient` when used as an async context manager.
- [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md): summarized work, test run, and remaining risk.

Verification:
- `uv run --with-requirements requirements-dev.lock pytest tests/test_client.py::TestAsyncOpenAI::test_client_context_manager_closes_custom_http_client` passed.

I left the existing untracked scheduler files alone (`.codex-nightly-prompt.md`, `uv.lock`).