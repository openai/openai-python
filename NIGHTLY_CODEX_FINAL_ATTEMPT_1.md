Implemented a small fix for issue #2834.

Changed [src/openai/_response.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/_response.py) so Pydantic validation failures raised during SDK helper post-parsing are wrapped as `APIResponseValidationError` for both sync and async responses.

Added focused regression tests in [tests/lib/responses/test_responses.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/lib/responses/test_responses.py) covering `responses.parse` receiving non-JSON text for a structured output schema.

Wrote [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md).

Verification:
- `uv run --with pytest --with pytest-asyncio --with pytest-xdist --with respx --with inline-snapshot pytest tests/lib/responses/test_responses.py -q` passed, `7 passed`
- `uv run --with ruff ruff format --check src/openai/_response.py tests/lib/responses/test_responses.py` passed
- `uv run --with ruff ruff check src/openai/_response.py tests/lib/responses/test_responses.py` passed
- `git diff --check` passed

Working tree has the intended modified files plus pre-existing untracked `.codex-nightly-prompt.md` and `uv.lock`.