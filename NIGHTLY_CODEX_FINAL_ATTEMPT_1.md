Implemented the nightly contribution.

Changed [completions.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/resources/chat/completions/completions.py:184) so sync and async `parse()` post-parser closures clear captured `response_format` and tools after parsing. Added a focused regression in [test_completions.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/lib/chat/test_completions.py:989) for dynamically created Pydantic models being garbage collectible after async parsing.

Validation passed:
- `pytest tests/lib/chat/test_completions.py -o addopts=''`
- `ruff check` and `ruff format --check` on touched files
- `pyright src/openai/resources/chat/completions/completions.py`

Also wrote [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md). Untracked `.codex-nightly-prompt.md` and `uv.lock` were already present and left untouched.