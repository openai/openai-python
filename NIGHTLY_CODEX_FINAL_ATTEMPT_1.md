Implemented the fix for [openai/openai-python#2722](https://github.com/openai/openai-python/issues/2722).

Changed:
- [src/openai/_streaming.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/_streaming.py:66): sync/async stream iteration now skips SSE frames with empty or whitespace-only `data` before JSON parsing.
- [tests/test_streaming.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/test_streaming.py:219): added regression coverage for `retry`, `id`, `event`, and empty `data` frames.
- [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md:1): written as requested.

Verification passed:
- `.venv/bin/python -m pytest tests/test_streaming.py -q` (`22 passed`)
- `.venv/bin/python -m ruff check src/openai/_streaming.py tests/test_streaming.py`
- `.venv/bin/python -m ruff format --check src/openai/_streaming.py tests/test_streaming.py`

I did not commit, push, fork, or open a PR. Existing untracked `.codex-nightly-prompt.md` and `uv.lock` remain unmodified from the workflow state.