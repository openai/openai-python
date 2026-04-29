Implemented a small examples-only fix for the Realtime issue.

Changed:
- [examples/realtime/realtime.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/examples/realtime/realtime.py)
- [examples/realtime/azure_realtime.py](/home/runner/work/oss-nightly-control/oss-nightly-control/target/examples/realtime/azure_realtime.py)
- [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md)

The examples now request text output via `connection.response.create(response={"output_modalities": ["text"]})` instead of sending `output_modalities` inside `session.update`, which directly avoids the `session.output_modalities` unknown-parameter confusion from the Azure Realtime issue.

Verification run:
- `python -m py_compile examples/realtime/realtime.py examples/realtime/azure_realtime.py`
- `ast.parse` on both changed files
- `git diff --check`

Could not run `ruff` or `pyright` because the checkout environment does not have those dev tools installed, including via `uv run`.