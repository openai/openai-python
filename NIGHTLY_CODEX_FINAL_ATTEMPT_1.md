Implemented a small test-only contribution.

Changed [tests/lib/responses/test_responses.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/lib/responses/test_responses.py) to add coverage for `responses.parse` with a Pydantic model containing `decimal.Decimal` fields, asserting parsed JSON string values become `Decimal` instances in `response.output_parsed`.

Also added [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md) with summary, tests, and risk notes. I avoided duplicating the broader schema fix because upstream PR [openai/openai-python#2733](https://github.com/openai/openai-python/pull/2733) is already active for issue [#2718](https://github.com/openai/openai-python/issues/2718).

Verification run:

`uv run --with pytest --with pytest-asyncio --with respx --with inline-snapshot pytest tests/lib/responses/test_responses.py -o addopts=''`

Result: `6 passed`.