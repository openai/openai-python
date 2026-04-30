Implemented a small, issue-related test change.

Changed [tests/test_client.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/test_client.py:949) to add a focused regression test that calls `chat.completions.with_raw_response.create(..., verbosity="low")` and asserts the request body sends `verbosity` as a top-level `/chat/completions` field, not nested under `text`.

Updated [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md:1) with the rationale, verification, and test limitations.

Verification:
- Passed a direct `uv run python` serialization check showing:
  `{"messages": [{"content": "string", "role": "developer"}], "model": "gpt-5.4", "verbosity": "low"}`

Could not run pytest locally because:
- system Python has no `pytest`
- `uv run python -m pytest ...` has no `pytest`
- `scripts/test ...` requires `rye`, which is not installed here.