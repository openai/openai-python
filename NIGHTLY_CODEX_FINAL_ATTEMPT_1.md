Implemented a small fix for issue #2626: Azure sync/async clients now refresh callable `api_key` providers before preparing Azure auth headers in [src/openai/lib/azure.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/lib/azure.py:327).

Added sync and async regression coverage in [tests/lib/test_azure.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/lib/test_azure.py:118), verifying callable API keys are used on the initial request and refreshed on retry. Wrote the required [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md:1).

Verification passed:
- `.venv/bin/python -m pytest tests/lib/test_azure.py`
- `.venv/bin/python -m ruff check src/openai/lib/azure.py tests/lib/test_azure.py`
- `.venv/bin/python -m ruff format --check src/openai/lib/azure.py tests/lib/test_azure.py`

No commit, push, or PR was created. Untracked `.codex-nightly-prompt.md` and `uv.lock` were already present and left untouched.