Implemented a small focused contribution for `openai/openai-python#2537`.

Changed:
- Added `test_streaming_allowed_tools_tool_choice_body` in [tests/lib/responses/test_responses.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/lib/responses/test_responses.py)
- Added required [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md)

Verified:
- `uv run --with pytest --with pytest-asyncio --with respx --with inline-snapshot pytest tests/lib/responses/test_responses.py -q -o addopts=''` passed: `6 passed`
- `uv run --with ruff ruff check tests/lib/responses/test_responses.py` passed
- `uv run --with ruff ruff format --check tests/lib/responses/test_responses.py` passed

Notes:
- The original 400 appears server/model-policy driven, so I did not add SDK-side validation that could go stale. The test locks the SDK’s request serialization for the reported GPT-5 + streamed `allowed_tools` tool choice shape.
- Existing untracked `.codex-nightly-prompt.md` and `uv.lock` were left untouched.