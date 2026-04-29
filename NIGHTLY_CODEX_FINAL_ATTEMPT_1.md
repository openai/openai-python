Implemented a small regression test for `find_in_page` parsing in [tests/lib/responses/test_responses.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/lib/responses/test_responses.py). The generated types already include `Literal["find_in_page"]`, so the patch locks that behavior instead of editing generated source.

Wrote [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md).

Verification run:
- `uv run python -m pytest tests/lib/responses/test_responses.py -o addopts=""`
- `uv run ruff check tests/lib/responses/test_responses.py`
- `uv run ruff format --check tests/lib/responses/test_responses.py`

Working tree has the intended modified test file and new report. Pre-existing untracked `.codex-nightly-prompt.md` and `uv.lock` were left untouched.