Implemented the focused fix for openai/openai-python#2502.

Changed:
- [src/openai/types/realtime/realtime_response_status.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/types/realtime/realtime_response_status.py): added optional `Error.message`.
- [src/openai/types/beta/realtime/realtime_response_status.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/types/beta/realtime/realtime_response_status.py): added the same field for beta realtime.
- [tests/test_realtime_response_status.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/test_realtime_response_status.py): added regression coverage for declared model fields and failed `response.done` payload parsing.
- [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md): written with summary, tests, and risks.

Verified:
- `uv run python -m pytest tests/test_realtime_response_status.py -q` passed: `4 passed`
- `uv run ruff check ...` passed
- `uv run ruff format --check ...` passed
- `uv run python -m compileall -q ...` passed

I did not commit, push, or open a PR. The issue context used was https://github.com/openai/openai-python/issues/2502.