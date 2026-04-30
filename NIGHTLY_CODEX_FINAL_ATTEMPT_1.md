Implemented a small regression test contribution for issue #2919.

Added:
- [tests/test_responses_websocket.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/test_responses_websocket.py)
- [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md)

The test verifies both sync and async Responses WebSocket helpers serialize `temperature=1.2` as a JSON numeric float in `response.create`.

Validation run:
- `uv run pytest tests/test_responses_websocket.py` → `2 passed`
- `uv run ruff format --check tests/test_responses_websocket.py` → passed
- `uv run ruff check tests/test_responses_websocket.py` → passed

Remaining risk: the reported raw WebSocket close behavior appears server-side, so this locks SDK behavior rather than fixing the production close directly.