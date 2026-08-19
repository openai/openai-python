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

During the draft rollout, `CASTIRON_CUSTOM_CODE_BRANCHES` is a repository-local
JSON array of maintainer-protected branch names. Only those branches can publish
comments. A general contributor/fork rollout requires a trusted default-branch
publisher. Never execute PR-controlled code with write credentials.
Changing the workflow may require one-time AM permission. Its reporter checksum
is a credential-safety check, not a requirement that every generated file remain
identical to its template.
