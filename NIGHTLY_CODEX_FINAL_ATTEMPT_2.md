Implemented a small, directly related patch for issue `#2680`.

Changed [src/openai/types/__init__.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/src/openai/types/__init__.py) to export `ChatCompletion`, `Response`, and `ResponseUsage` from `openai.types`, and added [tests/test_type_exports.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/tests/test_type_exports.py) to lock those aliases to the existing nested types. Updated [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md) with the rationale, search surface, verification, and generator overwrite risk.

Verification passed:

- `.venv/bin/python -m pytest tests/test_type_exports.py -q` -> `1 passed`
- `.venv/bin/ruff check src/openai/types/__init__.py tests/test_type_exports.py` -> `All checks passed!`
- Direct import identity check -> `True True True`