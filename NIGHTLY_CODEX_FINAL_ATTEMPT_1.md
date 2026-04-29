Implemented a small fix for issue #2489: `logprobs` is now optional on Responses text delta/done events, matching the fact that streamed text events may omit it.

Changed:
- [response_text_delta_event.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/types/responses/response_text_delta_event.py:48)
- [response_text_done_event.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/types/responses/response_text_done_event.py:45)
- Added regression coverage in [test_responses.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/lib/responses/test_responses.py:46)
- Wrote [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md)

Validation:
- `pytest -o addopts='' tests/lib/responses/test_responses.py -q` passed: 6 tests
- `ruff check` on touched files passed

I left changes uncommitted as requested. Existing untracked `.codex-nightly-prompt.md` and `uv.lock` are still present; I did not modify them intentionally. Source issue used: https://github.com/openai/openai-python/issues/2489