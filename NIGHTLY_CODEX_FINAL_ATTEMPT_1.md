Wrote [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md) and made no code changes.

Reason: upstream already has an active duplicate PR, `openai/openai-python#2742`, that directly fixes `openai/openai-python#2736` with the same intended `ActionSearchSource` type updates. Opening another PR for the same two generated files would be misleading.

Tests were not run because no code was changed. Existing untracked files `.codex-nightly-prompt.md` and `uv.lock` were left untouched.