Implemented a small, reviewable patch.

Changed [src/openai/_models.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/_models.py:802) so the Pydantic v2 `TypeAdapter` cache is bounded at 4096 entries instead of `maxsize=None`.

Added [tests/test_models.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/test_models.py:26) to lock that behavior with a focused Pydantic-v2-only regression test.

Updated [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md:1) with rationale and verification.

Verification:
- `uv run --with pytest --with pytest-asyncio pytest tests/test_models.py -q -o addopts=""` passed: `49 passed`
- `uv run --with ruff ruff check src/openai/_models.py tests/test_models.py` passed

Note: an ad-hoc Pyright run failed on environment/setup issues and pre-existing diagnostics unrelated to this patch, so I did not treat it as a gating result.