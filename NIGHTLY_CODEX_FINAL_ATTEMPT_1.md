Investigated issue #2610 and stopped without a source/test diff because the checkout already fixes the SDK-side bug: `verbosity` is accepted by `chat.completions.create()` and is serialized as a top-level request body field.

I added [NIGHTLY_REPORT.md](/home/runner/work/oss-nightly-control/oss-nightly-control/target/NIGHTLY_REPORT.md) with the investigation, verification, failed pytest attempts, and remaining risk.

Verification run:
`client.chat.completions.create(..., verbosity="low")` produced request JSON containing `"verbosity": "low"`.

Tests could not run because `pytest` is not installed in the available Python/venv/uv environment. Source: GitHub issue https://github.com/openai/openai-python/issues/2610.