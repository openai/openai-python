Implemented a small fix for [openai/openai-python#2872](https://github.com/openai/openai-python/issues/2872).

Changed:
- [src/openai/lib/_parsing/_responses.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/lib/_parsing/_responses.py): `parse_response()` now constructs parsed response models with the actual `text_format` type, avoiding unresolved `TypeVar` serialization warnings.
- [tests/lib/responses/test_responses.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/lib/responses/test_responses.py): added a regression test for `to_dict()` after parsing a Pydantic model.
- [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md): added the required summary.

Verification passed:
- `pytest tests/lib/responses/test_responses.py`
- `ruff check` on touched files
- `pyright` on touched files

I did not run the full suite or Pydantic v1 nox session because this environment does not have `rye` installed. Untracked `.codex-nightly-prompt.md` and `uv.lock` were already present and left untouched.