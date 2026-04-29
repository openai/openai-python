Implemented a small contribution for issue https://github.com/openai/openai-python/issues/2599.

Changed:
- `README.md`: clarified that timeouts are passed to `httpx` per request operation, not as a wall-clock deadline across retries, and that `max_retries=0` makes timeout failures stop after the first attempt.
- `tests/test_client.py`: added sync and async regression tests verifying `timeout=1.0` is passed through and timeout errors are not retried when retries are disabled.
- `NIGHTLY_REPORT.md`: added the required task summary.

Verification:
- `uv run pytest -q tests/test_client.py -k 'timeout_errors_are_not_retried_when_retries_are_disabled or request_timeout or client_timeout_option or http_client_timeout_option'` passed: 8 tests.
- `uv run ruff check tests/test_client.py` passed.

No commit, fork, push, or PR was created. Note: `.codex-nightly-prompt.md` and `uv.lock` were already untracked in the worktree; I left them alone.