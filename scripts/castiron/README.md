# Castiron custom-code reporting

DO NOT MERGE: draft workflow experiment. This manually vendored reporter uses
Python, Git, and `gh`; it does not execute SDK code.

Run `python3 scripts/castiron/test_custom_code_report.py` for focused tests.
Use the report comment’s expander to download the exact custom patch or reproduce
it from pinned revisions. A public checkout uses `report --public` and resolves
only public codegen snapshots. It never needs access to another repository.

The hash format is specified in the reporter’s module docstring. It covers Git
paths, modes, and blob bytes, excluding `.github/actions/` and
`.github/workflows/`. The head must record a matching `codegen_hash`. Older base
revisions can use the verified snapshot lineage with a legacy notice.

The experimental workflow is limited to explicitly protected maintainer-owned
branches listed in the repository variable `CASTIRON_CUSTOM_CODE_BRANCHES`
(a JSON array). Its workflow definition is trusted because those branch writers and
ruleset administrators are trusted. Before execution, both jobs verify the
reporter’s reviewed SHA-256. This content pin is defense in depth, not a
substitute for the branch restrictions. General contributor/fork support needs
a publisher defined on a trusted default branch.
