Implemented the targeted fix.

Changed [src/openai/types/moderation.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/types/moderation.py) so `CategoryScores.illicit` and `CategoryScores.illicit_violent` are `Optional[float] = None`, matching the nullable API behavior described in issue #1786.

Added [tests/test_moderation_types.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/test_moderation_types.py) covering API-style alias keys with `None` values and serialization back to API names.

Wrote [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md).

Verification passed:
- `.venv/bin/python -m pytest tests/test_moderation_types.py`
- `.venv/bin/python -m ruff check src/openai/types/moderation.py tests/test_moderation_types.py`
- `.venv/bin/pyright --pythonpath .venv/bin/python src/openai/types/moderation.py tests/test_moderation_types.py`