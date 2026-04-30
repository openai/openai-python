Implemented a focused fix for [openai/openai-python#1677](https://github.com/openai/openai-python/issues/1677).

Changed `ChatCompletionChunk.Choice.delta` to be nullable, then updated streaming accumulation, event emission, CLI output, and checked examples to treat `delta=None` as an empty incremental update while still honoring finish events. Added a regression test for a content chunk followed by a final null-delta chunk.

Validation run:
- `pytest tests/lib/chat/test_completions_streaming.py -q` via `uv` passed: `16 passed`
- targeted `ruff check` passed
- targeted `pyright` passed
- `python -m py_compile` passed

Also wrote `NIGHTLY_REPORT.md`. Existing untracked `.codex-nightly-prompt.md` and `uv.lock` were already present in the workspace and left untouched.