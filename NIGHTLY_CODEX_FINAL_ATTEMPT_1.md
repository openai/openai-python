Implemented a focused regression test for issue #2749.

Changed [tests/lib/test_azure.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/lib/test_azure.py:157) to cover sync and async Azure `images.edit(...)`, asserting the deployment URL, multipart `Content-Type` with boundary, API key header, and multipart body fields.

Added [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md:1) with summary, tests, and remaining risk.

Verification:
- `uv run --with pytest --with pytest-asyncio --with pytest-xdist --with respx pytest tests/lib/test_azure.py -q` passed, 53 tests.
- `uv run --with ruff ruff format --check tests/lib/test_azure.py` passed.
- `uv run --with ruff ruff check tests/lib/test_azure.py` passed.

No commit, fork, push, or PR was created.