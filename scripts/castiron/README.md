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
forks. A separate `workflow_run` publisher reads its report as untrusted data and
uses only code from the trusted default branch to update the PR comment. The
publisher becomes active once its workflow is on the default branch. No branch
allowlist or repository variable is needed. Never execute PR-controlled code with
write credentials. Changing either workflow may require one-time AM permission.
