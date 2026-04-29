Implemented a small targeted fix for [issue #1880](https://github.com/openai/openai-python/issues/1880).

Changed [src/openai/cli/_tools/migrate.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/cli/_tools/migrate.py:85) so the Windows migration CLI error now points users to WSL and clarifies that `openai migrate` downloads and invokes Grit directly, without `grit install` or PATH edits.

Added focused tests in [tests/cli/test_tools_migrate.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/cli/test_tools_migrate.py:1), and wrote [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md:1).

Verification passed:
- `pytest ... tests/cli/test_tools_migrate.py -q` → `2 passed`
- `ruff format --check ...` → passed
- `ruff check ...` → passed

I did not commit, push, or open a PR. Note: `.codex-nightly-prompt.md` and `uv.lock` were already untracked when I started; I left them alone.