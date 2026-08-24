<!-- File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details. -->

# Castiron custom-code reporting

Castiron maintains shared templates for these files. Prefer changing those templates
for cross-SDK improvements; repository-specific customizations use the normal
three-way merge and are allowed.
The reporter uses Python 3.10+, Git, and `gh`; it does not import SDK code.

Run `python3 scripts/castiron/test_custom_code_report.py` for focused tests.
The report comment includes commands to inspect the exact custom-code patch.
Public reporting uses only public snapshots and needs no private repository access.

The workflow validates the recorded `codegen_hash`.
Its hash format is documented in the reporter. Only `.github/actions/` and
`.github/workflows/` are excluded from the content hash.

The read-only pull-request workflow runs on every branch, including drafts and
forks. A separate read-only `workflow_run` job computes the authoritative report from
current, GitHub-associated base/head Git objects using the trusted workflow
revision. It fetches those objects into a new bare repository and never checks
out or executes PR code. The comment-writing job consumes only the artifact
from that trusted job, rechecks freshness, and links to its report and patch.
PR-produced reports are advisory run output, not the published assessment. The
publisher becomes active once its workflow is on the default branch. No branch
allowlist or repository variable is needed. Never execute PR-controlled code with
write credentials. Changing either workflow may require one-time AM permission.
