Implemented the nightly fix.

Changed [responses.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/resources/responses/responses.py:1164) so `responses.stream(response_id=..., starting_after=...)` forwards `starting_after` to the retrieve request in both sync and async paths. Added focused request-level tests in [test_responses.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/lib/responses/test_responses.py:72). Wrote [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md:1).

Verification passed:
- `.venv/bin/python -m pytest tests/lib/responses/test_responses.py -q`
- `.venv/bin/python -m ruff check src/openai/resources/responses/responses.py tests/lib/responses/test_responses.py`
- `.venv/bin/pyright --pythonpath .venv/bin/python src/openai/resources/responses/responses.py tests/lib/responses/test_responses.py`

No commit, push, or PR was created.