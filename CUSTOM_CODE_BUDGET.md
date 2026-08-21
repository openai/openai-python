# Custom-code budget

This is a handwritten, Python-only rollout. The checker, tests, workflow, and
`.castiron-ratchet.json` are maintained in this SDK, not in Castiron's compiler.
Leave existing CODEOWNERS unchanged. Normal generation must preserve these files.

## What is counted

The budget is **added lines plus deleted lines in the entire current custom patch**
against the candidate's verified pure-generated snapshot. It is not the PR's diff
against main, and additions and deletions never cancel. Replacing 500 generated
lines with 500 handwritten lines costs 1,000 lines. Deleting a generated file
counts all its removed lines. Restoring generated content reduces the budget.

The checker reuses `scripts/castiron/custom_code_report.py` without changing its
snapshot/hash validation or generated-file ownership. It counts generated-owned
files, including runtime code, tests, and generated documentation. Wholly
handwritten-only files are outside this existing report's scope. Changes in
generation ownership remain visible in the report; do not change exclusions or
checkpoints to hide customization. Non-text custom patches fail as uncountable.

The initial Python ceiling is **10,000 lines**. The policy file contains only an
integer `schema_version` (currently 1) and a nonnegative integer
`max_custom_patch_lines`. Missing, deleted, renamed, executable, symlinked,
malformed, or unsupported policy files fail closed. There is no disable flag or
automatic budget update command.

## Changing the budget

Every budget-file change must be in a separate PR containing **only that file**.
The check examines the complete PR diff, not just its latest commit. Put the
justification in the PR description; do not add a justification file to that PR.

For an increase, explain the current usage, proposed ceiling, why the additional
customization is necessary, and why fixing generation is not appropriate. Obtain
a **human approving review**, then merge the budget PR before relying on it in
an SDK PR. Keep the default CODEOWNERS and ordinary human-admin override process.

Agents may investigate and draft a budget-only proposal. They **must not approve
a budget increase**, including through a human's credentials, or bypass the gate.
They must not weaken counting, broaden exclusions, or alter generation metadata
to make a failing change pass. A bot review or agent assertion is not a human
approval. This approval requirement is agent policy plus normal review, not an
automated claim that GitHub can identify who operated an account.

Lower the ceiling deliberately after substantial cleanup, retaining headroom.
A budget-only decrease must also fit the current measured usage.

## Trusted CI

`.github/workflows/custom-code-budget.yml` has separate execution paths:

- `pull_request` runs proposed offline tests with read-only permissions.
- `pull_request_target` checks out current **main**, verifies it is still current,
  and runs main's checker and reporter against candidate Git objects in a new bare
  repository. It never checks out, imports, installs, or executes candidate code.
- `merge_group` uses the same trusted checkout. It verifies queue membership from
  GitHub and commit ancestry, checks isolation per constituent PR, and measures
  the complete merged candidate against the budget on actual main. A budget PR
  queued in the same group cannot grant the SDK PR a higher limit.

A separate publisher with no checkout attaches these statuses to the exact PR
head or merge-group SHA, after rechecking head/base freshness:

- `Castiron / budget-only change`
- `Castiron / custom-code budget`

The policy is read from the current base commit, not the PR or its merge base.
Reporter changes in a PR cannot change the checker executing on that PR. Missing
snapshots, invalid hashes, unavailable queue membership, and policy errors fail
closed. If main moves during evaluation, rerun the workflow; reruns check out the
new main. The normal merge queue rechecks combined usage before merging.

The trusted run summary reports additions, deletions, total, mixed-file count,
headroom, largest patches, and exact policy/candidate/generated revisions. The
existing custom-code comment remains unchanged; this pilot does not modify the
generated reporter or its comment publisher.

## Local verification

Run from the SDK repository with Python 3.10+; no SDK dependencies are needed:

```sh
python3 -m unittest discover -s scripts/castiron -p 'test_custom_code*.py'
```

Use a **trusted checkout's** script to inspect committed revisions:

```sh
python3 -I scripts/castiron/custom_code_budget.py check \
  --repo /path/to/sdk --base FULL_MAIN_SHA --head FULL_CANDIDATE_SHA \
  --public --fetch --out /tmp/custom-code-budget
```

The inspected repo's `origin` must match its snapshot source. Omit `--public`
for the private SDK repository's checkpoints. Local checks are diagnostic; CI
independently binds main and the candidate to live GitHub metadata.

## Activation order

1. Merge the initial 10,000-line policy in its budget-only PR after human review.
2. Merge this handwritten tooling and guidance separately. Do not enable required
   statuses before the policy and trusted checker exist on main. There is no
   permanent bootstrap exemption in the checker.
3. Exercise a passing PR, over-budget PR, mixed budget/code PR, a fork PR, and a
   merge-queue candidate. Policy increases must still use the old limit.
4. Have a human administrator add both exact status names above to the main
   ruleset, bound to GitHub Actions. Retain normal review and CODEOWNERS settings.
   The tests job is separate from these authoritative statuses.

This is an accidental-change guardrail, not an adversarial approval boundary.
Workflow definitions and ruleset changes still have the normal repository review
and administrator controls; GitHub Actions status names alone are not a unique
workflow identity. Stronger organization-required workflow enforcement can be
added later. No other language's budget is enabled by this rollout.
