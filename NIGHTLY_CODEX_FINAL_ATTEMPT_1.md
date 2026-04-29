Implemented a small related contribution for openai/openai-python issue #2544.

Changed:
- [tests/test_models.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/test_models.py): added a regression test that `CompletionUsage` preserves provider-specific extra usage fields like `promptTokensDetails`.
- [README.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/README.md): clarified nested undocumented response fields are available from the nested Pydantic model.
- [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md): added the required nightly summary.

Validation run:
- `uv run pytest tests/test_models.py::test_completion_usage_preserves_unknown_token_details -q -o addopts=''`
- `uv run pytest tests/test_models.py -q -o addopts=''`
- `uv run ruff format --check tests/test_models.py`
- `uv run ruff check tests/test_models.py`
- `uv run python scripts/utils/ruffen-docs.py README.md`

Note: I avoided the direct `prompt_tokens_details=None` behavior change because GitHub shows an existing open PR for that exact approach: https://github.com/openai/openai-python/pull/2773. The issue context used was https://github.com/openai/openai-python/issues/2544.