Implemented the nightly contribution for openai/openai-python#2819: https://github.com/openai/openai-python/issues/2819

Changes left in the worktree:
- Lazy `openai.types` proxy so plain `import openai` no longer imports generated type modules.
- Deferred related top-level convenience imports that were still pulling `openai.types`.
- Lazy `openai.lib` helper exports.
- `OAuthErrorCode` import moved behind `TYPE_CHECKING`.
- Added `tests/test_imports.py` subprocess regression coverage.
- Added required `NIGHTLY_REPORT.md`.

Verification run:
- `uv run --with ruff ruff check ...`
- `uv run --with pytest --with pytest-asyncio --with pytest-xdist pytest tests/test_imports.py tests/test_module_client.py`
- Import-time check confirmed no `openai.types` import during `import openai`.

Note: pre-existing untracked `.codex-nightly-prompt.md` and `uv.lock` were left untouched.