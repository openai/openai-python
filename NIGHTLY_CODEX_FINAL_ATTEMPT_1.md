Implemented a small test-only regression contribution.

Changed:
- [tests/test_models.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/test_models.py:575): adds coverage that `model_dump()` works when `by_alias` is left unset, locking the behavior needed for issue #2921.
- [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md:1): summarizes the work, tests, and remaining risk.

Verified:
- `uv run pytest tests/test_models.py -k "compat_model_dump_allows_default_by_alias or compat_method_no_error_for_warnings"`
- `uv run pytest tests/lib/test_azure.py::TestAzureLogging::test_azure_api_key_redacted`
- `uv run ruff check tests/test_models.py`

Note: `.codex-nightly-prompt.md` and `uv.lock` were already untracked before my changes; I left them untouched.