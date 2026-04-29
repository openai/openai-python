Implemented a small contribution for [openai/openai-python#2677](https://github.com/openai/openai-python/issues/2677).

Changed:
- Added a focused regression test in [tests/lib/responses/test_responses.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/lib/responses/test_responses.py:46) that verifies `responses.create()` sends Responses-native `function_call` and `function_call_output` input items.
- Added a minimal migration example in [examples/responses/function_call_inputs.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/examples/responses/function_call_inputs.py:1).
- Wrote [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md:1).

Checks run:
- `uv run --with pytest --with pytest-xdist --with respx --with inline-snapshot --with pytest-asyncio pytest tests/lib/responses/test_responses.py -q`
- `uv run --with ruff ruff check tests/lib/responses/test_responses.py examples/responses/function_call_inputs.py`
- `python -m py_compile examples/responses/function_call_inputs.py tests/lib/responses/test_responses.py`

All passed. I left the working tree uncommitted as requested.