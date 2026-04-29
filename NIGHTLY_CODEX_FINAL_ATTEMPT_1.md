Implemented the nightly contribution.

Changed:
- Wrapped `pydantic.ValidationError` raised by response post-parsers into `APIResponseValidationError` in:
  - `src/openai/_response.py`
  - `src/openai/_legacy_response.py`
- Added a focused regression test for `client.beta.chat.completions.parse()` with malformed structured-output JSON in:
  - `tests/lib/chat/test_completions.py`
- Added required `NIGHTLY_REPORT.md`.

Verification run:
- `uv run python -m pytest tests/lib/chat/test_completions.py -k "invalid_json or parse_pydantic_model"`: 6 passed
- `uv run python -m ruff check src/openai/_response.py src/openai/_legacy_response.py tests/lib/chat/test_completions.py`: passed
- `git diff --check`: passed

I left changes uncommitted. Pre-existing untracked files `.codex-nightly-prompt.md` and `uv.lock` remain untouched.