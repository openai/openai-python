Implemented a focused regression test for [openai/openai-python#2886](https://github.com/openai/openai-python/issues/2886).

Changed:
- [tests/lib/test_azure.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/lib/test_azure.py): added an Azure `AsyncAzureOpenAI.beta.chat.completions.parse()` test that asserts `max_tokens` and `max_completion_tokens` are not sent unless explicitly provided.
- [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md): summarized the work, tests, and remaining risk.

Verification:
- `uv run --with pytest --with pytest-asyncio --with pytest-xdist --with respx --with inline-snapshot pytest tests/lib/test_azure.py::test_parse_does_not_send_default_token_limits_to_azure`
- `uv run --with ruff ruff check tests/lib/test_azure.py`

Both passed. Existing untracked `.codex-nightly-prompt.md` and `uv.lock` were left alone.