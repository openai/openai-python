Implemented a small PR-ready patch for the `ActionSearchSource` typing gap.

Changed:
- [response_function_web_search.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/types/responses/response_function_web_search.py): allows `type="api"`, adds optional `name`, makes `url` optional.
- [response_function_web_search_param.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/types/responses/response_function_web_search_param.py): mirrors the param `TypedDict` shape.
- [test_response_function_web_search.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/api_resources/responses/test_response_function_web_search.py): regression test for API search sources.
- [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md): updated rationale, tests, risks.

Verification:
- `uv run --with pytest --with pytest-asyncio --with pytest-xdist pytest tests/api_resources/responses/test_response_function_web_search.py -q` passed.
- `uv run --with pyright pyright ...` on touched files passed.
- `uv run --with ruff ruff check ...` on touched files passed.

Note: there are unrelated/untracked nightly artifacts already present in the worktree, plus `uv.lock` is untracked. I left them untouched.