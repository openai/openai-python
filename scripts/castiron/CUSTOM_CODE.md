<!-- File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details. -->

# Custom code

The custom-code reporter measures the SDK's remaining customization of generated
files. The budget gate checks that measurement against the repository's policy.
See [CONTRIBUTING.md](../../CONTRIBUTING.md#custom-code-budget) for budget changes
and human review, and [AGENTS.md](../../AGENTS.md#custom-code-budget) for agent rules.

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

The ceiling is defined in [`.castiron-ratchet.json`](../../.castiron-ratchet.json).
Migration policy contains an integer `schema_version` of 1 and a
nonnegative integer `max_custom_patch_lines`. Strict schema v2 is described below.
Missing, deleted, renamed, executable, symlinked,
malformed, or unsupported policy files fail closed. There is no disable flag or
automatic budget update command.

Budget-file isolation is checked against the complete PR diff, not just its latest
commit. Increases never apply to their own PR or merge group. Decreases must also
fit the measured usage. Human approval is contributor and agent policy plus normal
review, not an automated claim that GitHub can identify who operated an account.

## Trusted CI

### Strict generated-file ownership

Schema v1 remains migration mode with its existing patch budget. An SDK with
zero customizations can opt into schema v2 through a policy-only PR:

```json
{ "schema_version": 2, "generated_files": "strict", "max_custom_patch_lines": 0 }
```

First land shared compiler/verifier support and regenerate the SDK, including
`scripts/castiron/generated-files.json`. Then activate strict policy. Both the
main policy and a proposed activation are enforced; strict policy cannot be
downgraded. A policy change cannot be combined with SDK or generated-source edits.
SDK promotion rejects policy-file changes; submit the policy-only PR directly
in the SDK repository.

Strict mode compares generated paths, final file bytes, and Git modes against
the manifest in the verified generated snapshot. The candidate's manifest is
also checked exactly. Header removal, deletion, renaming, symlink substitution,
or manifest edits cannot exempt a generated file. Generated workflow/action
hashes are covered by the manifest even though the legacy patch counter and
public snapshot publication continue to exclude those subtrees. Handwritten
files and repository-owned governance remain outside generated ownership.
Private checkpoints retain SDK-owned CI workflows and actions from their parent;
the generated ownership inventory does not claim those inherited files.

The existing required `Castiron / custom-code budget` status fails on any strict
violation. Its trusted-main execution and merge-queue checks remain mandatory.
Local generation validates before integration and publication using compiler-owned
code. New generated snapshots still require the existing generation/promotion
provenance and review controls; a self-computed hash is not approval to publish.

Agents must fix inputs/compiler code or handwritten extensions, regenerate, and
verify. Never patch generated files or the manifest, disable strict mode, change
ownership exclusions, or rewrite provenance to get a passing result. Verification
failure must preserve edits for inspection rather than overwrite them.

The custom-code workflow pair separates candidate execution from trusted checks:

- `castiron-custom-code.yml` runs proposed offline tests and the advisory report
  on `pull_request` with read-only permissions.
- `castiron-custom-code-comment.yml` handles `workflow_run` from **main**. Its
  read-only compute job pins executable checker code and budget policy to main.
  It independently resolves the live PR target (`main` or `next`) and captures
  the target baseline and candidate SHA. For main, the target baseline is the
  pinned main checkout; for next, it is the live next ref, not stale PR metadata.
  It reads only Git objects in a fresh bare repository, never candidate code.
- An unprivileged `merge_group` job in the first workflow signals that a candidate
  needs checking. The trusted handler resolves the target from the queue ref,
  requires an effective merge-queue rule on that target, and verifies current
  queue membership and target ancestry. It checks isolation against the target
  per constituent PR and budgets the complete candidate using trusted main policy.
  A policy increase in next or the same group cannot grant a higher limit.

A separate publisher with no checkout attaches these statuses only to PRs and
merge groups targeting `main`, after rechecking the PR head/target or queue base freshness:

- `Castiron / budget-only change`
- `Castiron / custom-code budget`

These contexts are reserved for `main`. Reports for `next` are advisory and
never write required statuses, even when both targets use the same commit.
GitHub does not rebuild the `next` queue when policy on `main` changes, so a
captured `next` result cannot safely authorize a merge against current policy.

The policy is read from the captured main commit, not next, the PR, or its merge
base. Target baseline, trusted policy, and candidate identities are recorded
separately in the report and budget result. Reusing a report requires matching
branch, policy, and head identities; retargeted PRs fail closed.

PR results describe a captured snapshot even if a branch moves during computation.
They do not authorize merging without queue validation. Queue checks require
current main policy and current target baseline. Immediately before publishing,
the handler rechecks the PR head/target or queue membership, target baseline,
and main policy. A stale queue evaluation cannot publish success. Missing
snapshots, invalid hashes, unavailable membership, and policy errors fail closed.

The queue signal cannot supply a passing result, and removing it leaves required
statuses missing. No write-capable job executes from the candidate's workflow
definition. See GitHub's [workflow_run trust model](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_run)
and [merge-queue behavior](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue).

The trusted run summary reports additions, deletions, total, mixed-file count,
headroom, largest patches, and exact policy/candidate/generated revisions. The
existing custom-code comment remains unchanged, including when the budget fails.
The trusted compute job reuses its own report, never the candidate's artifacts.
The checker, workflows, and offline tests are generated from shared Castiron
templates. The budget policy remains repository-owned and is never generated.
Repository-specific customizations are preserved through the normal three-way
merge during generation.

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
for the private SDK repository's checkpoints. Local checks are diagnostic and
use the supplied base as policy; CI independently binds the target, main policy,
and candidate to live GitHub metadata.

## Activation order

1. Merge the initial budget policy in its budget-only PR after human review.
2. Merge the tooling and guidance separately. Do not enable required
   statuses before the policy and trusted checker exist on main. There is no
   permanent bootstrap exemption in the checker.
3. Exercise a passing PR, over-budget PR, mixed budget/code PR, a fork PR, and a
   merge-queue candidate. Policy increases must still use the old limit.
4. Have a human administrator retain/enable **require merge queue** and add both
   exact status names above to the main ruleset, bound to GitHub Actions. Retain
   normal review and CODEOWNERS settings. Exercise a main-policy decrease after
   an unchanged PR head passed, and confirm its queued candidate uses the new limit.
   The tests job is separate from these authoritative statuses.

This is an accidental-change guardrail, not an adversarial approval boundary.
Workflow definitions and ruleset changes still have the normal repository review
and administrator controls; GitHub Actions status names alone are not a unique
workflow identity. Stronger organization-required workflow enforcement can be
added later.

## Activating next

Land shared tooling in Castiron first, then generate and review its SDK update
onto main. Keep required status activation separate until hosted tests have
exercised main and next PRs, forks, retargeting, policy changes, and both merge
queues. Do not require the `main` status contexts on `next`. Authoritative next
checks need separate contexts and a mechanism that keeps queue authorization
bound to current main policy, including changes after a result is published.
Until that mechanism is implemented and reviewed, next reports remain advisory.
Preserve its reviews, CODEOWNERS, merge queue, and all existing main protections.
This checker support does not enable generation or promotion to next, or releases
from next. Those require separate reviewed implementation.
