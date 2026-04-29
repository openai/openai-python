Implemented a small fix for `openai/openai-python#2806`.

Changed:
- `src/openai/lib/streaming/chat/_completions.py`: normalizes streamed tool-call delta indices so `index: null` falls back to the delta’s position before accumulation/event emission.
- `tests/lib/chat/test_completions_streaming.py`: adds a regression test for tool-call argument streaming with missing/null indices.
- `NIGHTLY_REPORT.md`: added summary, tests, and remaining risk.

Verified:
- `pytest tests/lib/chat/test_completions_streaming.py` passes: 16 passed.
- `ruff format` and `ruff check` pass on touched files.
- `mypy src/openai/lib/streaming/chat/_completions.py` passes.
- `git diff --check` passes.

Note: `.codex-nightly-prompt.md` and `uv.lock` were already untracked in the checkout; I left them alone.