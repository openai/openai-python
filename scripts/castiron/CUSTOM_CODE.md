<!-- File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details. -->

# Custom code

The custom-code reporter measures the SDK's remaining customization of generated
files. The budget gate checks that measurement against the repository's policy.
See [CONTRIBUTING.md](../../CONTRIBUTING.md#custom-code-budget) for budget changes
and human review, and [AGENTS.md](../../AGENTS.md#custom-code-budget) for agent rules.

## What is counted

Repositories may separately activate `"ratchet": "go"` in their policy after
this checker reaches trusted main. Activation must be a human-reviewed,
policy-only PR; SDK promotion does not carry policy edits. Keep the existing
`max_custom_patch_lines` ceiling.

The Go ratchet rejects net growth in generated-owned custom patch additions
plus deletions **and physical lines of handwritten Go** compared with the
captured live target. It includes helpers, tests, comments, blank lines, nested
modules, and SDK-owned CI Go retained in private checkpoints. Non-text and
nonregular handwritten Go fail validation. Both revisions use their own verified
generated snapshots, read as Git objects without executing candidate code.

Stale PRs compare with the live target, not their historical merge base. Merge
queues check the complete combined candidate. Every landed reduction becomes
the next baseline automatically. An activated ratchet cannot be disabled;
raising the independent patch-only ceiling does not restore retired headroom.
Existing policy isolation, human review, and snapshot ownership rules still apply.

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
  read-only selector authenticates the target base and selects a main commit.
  Main uses its captured current commit. Next uses the reviewed `next_policy`
  version stored in its protected target base. A second checkout executes only
  that authenticated main version of the reporter/checker and reads its policy.
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

Next uses separate `Castiron next / budget-only change` and
`Castiron next / custom-code budget` contexts, so identical commit SHAs on the
two tracks cannot overwrite each other's authorization. The policy version is
fixed by next's protected base; advancing main does not silently change it.
Changing the reviewed pin changes next's own base and rebuilds its merge queue.

The effective policy is read from the selected authenticated main commit. The
next base selects that version; a candidate never selects its own executing
checker or grants itself a larger budget. Target baseline, trusted policy, and candidate identities are recorded
separately in the report and budget result. Reusing a report requires matching
branch, policy, and head identities; retargeted PRs fail closed.

PR results describe a captured snapshot even if a branch moves during computation.
They do not authorize merging without queue validation. Queue checks require
current target baseline and its approved policy version (current main for main,
reviewed pin for next). Immediately before publishing, the handler rechecks the
PR head/target or queue membership and the bound target baseline/policy identities. A stale queue evaluation cannot publish success. Missing
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
onto main. Add a reviewed policy pin in a separate `.castiron-ratchet.json`-only
PR targeting next; preserve the existing budget/schema fields:

```json
"next_policy": {
  "repository": "openai/your-sdk",
  "main_sha": "<full approved main commit SHA>"
}
```

The SHA must belong to that same repository's authenticated main first-parent
history and support this pin protocol. Selection reads the protected target
base, never the candidate. Updates require an exact-head human approving review
from a repository owner, member, or collaborator, in addition to ordinary
CODEOWNERS and required reviews. Bot reviews, review-body markers, stale reviews,
and dismissed approvals do not authorize activation.

For these policy-only reviews, the approving reviewer must explicitly attest that
they personally performed the human review. The entire review body must be the
following sentence, substituting the exact full current head SHA:

```text
I personally reviewed and approve this policy change as a human: <40-character head SHA>
```

Blank reviews, ordinary code-review text, quoted attestations, and attestations for
an earlier head do not qualify. Agents must never submit this attestation, even
through a human account. This is an explicit reviewer attestation, not a claim that
GitHub account type or team membership proves who operated the account. Ordinary
SDK code reviews continue to accept automation under their normal repository gates.

For initial adoption only, a base with no pin may accept an exact policy-only
pin-initialization PR under authenticated current-main checker/policy, with the
same human review requirement. The proposed pin is validated but never executed
for its own initialization. A malformed base pin cannot enter this path; other
changes without a base pin fail closed. Ordinary pin updates execute under the
previous approved version and cannot include SDK/tooling changes.

Keep required status activation separate until hosted tests have exercised main
and next PRs, forks, retargeting, policy changes, and both merge queues. Require
the target-specific next contexts after observing their genuine producers;
never reuse main's context names on next. Establish missing ordinary CI triggers
through a reviewed trusted workflow path before the policy-only initialization.
Preserve reviews, CODEOWNERS, merge queues, and all existing main protections.
This policy contract does not enable package releases from next.

For `next` policy activations and budget increases, the trusted computation also
records the exact constituent PR numbers and head SHAs requiring human approval.
The isolated status publisher rechecks those live PRs and their latest reviews
immediately before publication. Dismissed, replaced, stale, automated or missing
approvals fail closed even if ordinary automated approvals keep the queue live.
The publisher consumes the selector's versioned review rules, with cross-runtime
predicate fixtures; candidate artifacts never supply authorization or outcomes.

### Review changes after publication

The unprivileged reporter workflow signals submitted, edited and dismissed reviews.
For a current next PR changing the policy file, the trusted main handler marks its
required budget statuses and affected live queue statuses pending, then requests
normal reporter reruns. Only the ordinary authenticated evaluator may restore
success; the review signal never selects executable code, approval rules or an
arbitrary status target. Fork runs with empty PR lists use authenticated commit
associations and open-PR lookup, retaining live head/merge binding. The handler
marks each authenticated snapshot pending before slow run pagination, then retries
discovery if the PR or queue changes. Pending statuses on superseded affected
SHAs cannot authorize a merge; observed successes stay revoked even if a later
lookup fails. Reporter reruns must resolve to this same PR under the canonical
main-preference rule, not merely share its head SHA. Missing or ambiguous reporter
runs remain pending. Status writers share a serialization group.

Retain native required approving reviews and CODEOWNERS at merge time. Review-event
delivery and reevaluation are asynchronous; this mechanism is not an atomic human
approval check at merge. In particular, automated reviews using human accounts do
not become human policy authorization. Do not weaken native gates or treat this
handler as their replacement. A failed invalidation or rerun must be investigated;
missing reporter runs remain pending until the normal trusted run is requested.
Install and validate the review signal on the protected target before activating
next policy checks, including actual PR and queue revocation after dismissal.
