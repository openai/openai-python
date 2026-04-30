Implemented the patch and left changes in the working tree.

Changed:
- [src/openai/_base_client.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/_base_client.py): retry/wrap only `httpx.RequestError` in sync and async request loops.
- [tests/test_client.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/test_client.py): updated retry exception tests to use `httpx.ConnectError`; added sync/async regressions proving non-httpx exceptions propagate without retry/wrapping.
- [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md): required summary, tests, risks.

Verified:
- `uv run --with-requirements requirements-dev.lock pytest -q tests/test_client.py -k "retries_taken or non_httpx_request_errors_are_not_retried_or_wrapped or retrying_timeout_errors_doesnt_leak"` passed: 22 tests.
- `ruff format` and `ruff check` passed on touched Python files.

Note: issue [#2737](https://github.com/openai/openai-python/issues/2737) has active PR [#3002](https://github.com/openai/openai-python/pull/3002) with the same core code change; this patch adds the missing focused regression coverage.