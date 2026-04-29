Implemented a small tracked patch:

- [src/openai/_client.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/_client.py:465): `copy()` now preserves an explicit `api_key=""` instead of falling back to the old key.
- [tests/test_client.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/test_client.py:1194): added sync and async regression coverage for empty copied API keys.
- [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md:1): updated with rationale, scope, and verification.

Verification passed:

```bash
uv run --with pytest --with pytest-asyncio --with pytest-xdist --with respx --with dirty-equals --with time-machine --with inline-snapshot --with-editable . pytest tests/test_client.py -k 'copy_auth or api_key_before_after_refresh'
uv run --with ruff ruff format src/openai/_client.py tests/test_client.py
uv run --with ruff ruff check src/openai/_client.py tests/test_client.py
```