#!/usr/bin/env python3
# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
"""SDK custom-code budget gate. Run only from a trusted checkout, never PR code.

Reuses Castiron's vendored snapshot verifier and generated-file accounting. This
file and its workflows are generated from shared Castiron templates.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import html
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

# Explicitly load the reporter beside this trusted script, including under python -I.
# The inspected repository is only a Git object store, not a Python import path.
_spec = importlib.util.spec_from_file_location(
    "castiron_budget_reporter", Path(__file__).with_name("custom_code_report.py")
)
assert _spec is not None and _spec.loader is not None
report = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = report
_spec.loader.exec_module(report)

POLICY = ".castiron-ratchet.json"
ISOLATION_MESSAGE = (
    "Budget changes require a separate, budget-only PR. "
    "Put the justification in the PR description."
)


def unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate policy key: {key}")
        value[key] = item
    return value


def read_policy(repo: Path, revision: str) -> dict[str, Any]:
    revision = report.require_sha(revision)
    entry = report.git(repo, "ls-tree", revision, "--", POLICY).split()
    if len(entry) != 4 or entry[:2] != [b"100644", b"blob"]:
        raise ValueError(f"{POLICY} must exist as a regular, non-executable file at {revision}")
    if int(report.git(repo, "cat-file", "-s", entry[2].decode())) > 4096:
        raise ValueError("budget file exceeds 4096 bytes")
    value = json.loads(
        report.git(repo, "show", f"{revision}:{POLICY}"), object_pairs_hook=unique_keys
    )
    if not isinstance(value, dict):
        raise ValueError("budget file must be an object")  # noqa: TRY004 - malformed policy is a value error
    value = cast(dict[str, Any], value)
    version = value.get("schema_version")
    if type(version) is not int or version not in (1, 2):
        raise ValueError("unsupported budget schema_version")
    keys = {"schema_version", "max_custom_patch_lines"}
    if version == 2:
        keys.add("generated_files")
    if set(value) != keys:
        raise ValueError("budget file contains missing or unsupported fields")
    limit = value["max_custom_patch_lines"]
    if type(limit) is not int or limit < 0:
        raise ValueError("max_custom_patch_lines must be a nonnegative integer")
    if version == 2 and (value["generated_files"] != "strict" or limit != 0):
        raise ValueError("schema v2 requires generated_files=strict and a zero budget")
    return value


def read_budget(repo: Path, revision: str) -> int:
    return cast(int, read_policy(repo, revision)["max_custom_patch_lines"])


def strict_policy(repo: Path, revision: str) -> bool:
    return cast(int, read_policy(repo, revision)["schema_version"]) == 2


MANIFEST = b"scripts/castiron/generated-files.json"
# Derived from the renderer's repository-file inventory, also used by checkpoint
# publication to distinguish generated tooling from protected SDK-owned CI.
GENERATED_GITHUB_PATHS = frozenset(
    {
        b".github/workflows/castiron-custom-code.yml",
        b".github/workflows/castiron-custom-code-comment.yml",
    }
)


def checkpoint_github_inventory(source: bytes) -> frozenset[bytes]:
    """Read literal compiler inventory from verified checkpoint data, without execution."""
    values = [
        node.value
        for node in ast.parse(source).body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "GENERATED_GITHUB_PATHS"
            for target in node.targets
        )
    ]
    if len(values) != 1:
        raise ValueError("checkpoint must contain one generated GitHub inventory")
    value = values[0]
    if (
        not isinstance(value, ast.Call)
        or not isinstance(value.func, ast.Name)
        or value.func.id != "frozenset"
        or len(value.args) != 1
        or value.keywords
    ):
        raise ValueError("checkpoint generated GitHub inventory must be literal")
    literal_paths: object = ast.literal_eval(value.args[0])
    # An empty renderer inventory is written with an empty pair of braces.
    if isinstance(literal_paths, dict) and not literal_paths:
        return frozenset()
    if not isinstance(literal_paths, set) or any(
        not isinstance(path, bytes) or not path.startswith(b".github/")
        for path in cast(set[object], literal_paths)
    ):
        raise ValueError("invalid checkpoint generated GitHub inventory")
    return frozenset(cast(set[bytes], literal_paths))


def generated_manifest(repo: Path, generated: str) -> dict[bytes, dict[str, str]]:
    """Read ownership from the verified snapshot, never the candidate's manifest."""
    entries = report.tree_entries(repo, generated, include_workflows=True)
    entry = entries.get(MANIFEST)
    if entry is None or entry.mode != b"100644":
        raise ValueError(
            "strict mode requires a generated ownership manifest; regenerate with Castiron"
        )
    blobs = report.read_blobs(repo, entries)
    inventory_entry = entries.get(b"scripts/castiron/custom_code_budget.py")
    if inventory_entry is None or inventory_entry.mode not in (b"100644", b"100755"):
        raise ValueError("checkpoint is missing its generated GitHub inventory")
    github_paths = checkpoint_github_inventory(blobs[inventory_entry.oid])
    value = json.loads(blobs[entry.oid], object_pairs_hook=unique_keys)
    if not isinstance(value, dict) or set(cast(dict[str, Any], value)) != {"schema_version", "files"}:
        raise ValueError("invalid generated ownership manifest")
    value = cast(dict[str, Any], value)
    if (
        type(value["schema_version"]) is not int
        or value["schema_version"] != 1
        or not isinstance(value["files"], dict)
    ):
        raise ValueError("invalid generated ownership manifest")
    files: dict[bytes, dict[str, str]] = {}
    for name, identity in cast(dict[Any, Any], value["files"]).items():
        if (
            not isinstance(name, str)
            or not name
            or "\\" in name
            or "\0" in name
            or any(part in ("", ".", "..", ".git") for part in name.split("/"))
        ):
            raise ValueError("invalid generated manifest path")
        path = name.encode("utf-8")
        if path == MANIFEST:
            raise ValueError("generated manifest cannot include itself")
        # A matching identity cannot turn inherited, SDK-owned CI into generated
        # output. Use this verified checkpoint's literal compiler inventory, not
        # the executing verifier's version or candidate Python/manifest claims.
        # Public checkpoints may omit the private workflow/action blobs.
        if not report.included(path) and path not in github_paths:
            raise ValueError(f"generated manifest claims SDK-owned GitHub path: {name}")
        if not isinstance(identity, dict) or set(cast(dict[str, Any], identity)) != {"mode", "sha256"}:
            raise ValueError(f"invalid generated identity: {name}")
        identity = cast(dict[str, Any], identity)
        if (
            identity["mode"] not in ("100644", "100755")
            or not isinstance(identity["sha256"], str)
            or not report.HASH.fullmatch(identity["sha256"])
        ):
            raise ValueError(f"invalid generated identity: {name}")
        files[path] = identity
    # Sanitized public checkpoints omit GitHub blobs, not their ownership entries.
    # Otherwise an omitted identity would also escape strict candidate checks.
    if missing := github_paths - files.keys():
        raise ValueError(
            f"generated manifest omits generated GitHub inventory path: {min(missing).decode()}"
        )
    # Checkpoints retain SDK-owned workflow/action subtrees from their parent.
    # Those are outside generated ownership. Every other snapshot path, including
    # renderer-owned GitHub files omitted from the legacy hash, must be listed.
    # Public snapshots retain generated identities without the private blobs.
    snapshot_paths = set(entries) - {MANIFEST}
    if any(
        report.included(path) or path in github_paths
        for path in snapshot_paths - files.keys()
    ) or any(report.included(path) for path in files.keys() - snapshot_paths):
        raise ValueError("generated manifest does not cover the verified snapshot exactly")
    for path, identity in files.items():
        if path in entries:
            actual = entries[path]
            if (
                actual.mode.decode() != identity["mode"]
                or hashlib.sha256(blobs[actual.oid]).hexdigest() != identity["sha256"]
            ):
                raise ValueError(f"manifest disagrees with generated snapshot: {path.decode()}")
    # The manifest is itself immutable, bound by the existing snapshot hash.
    files[MANIFEST] = {"mode": "100644", "sha256": hashlib.sha256(blobs[entry.oid]).hexdigest()}
    return files


def verify_generated(
    repo: Path,
    generated: str,
    head: str,
    *,
    previous: str | None = None,
    worktree: bool = False,
) -> list[str]:
    files = generated_manifest(repo, generated)
    old = generated_manifest(repo, previous) if previous and previous != generated else files
    entries = report.tree_entries(repo, head, include_workflows=True)
    blobs = report.read_blobs(repo, {p: e for p, e in entries.items() if p in files})
    failures: list[str] = []
    for path, identity in files.items():
        entry = entries.get(path)
        content = blobs.get(entry.oid) if entry else None
        mode = entry.mode.decode() if entry else None
        if worktree:
            full = repo / path.decode()
            # Never follow a symlink introduced by an agent or formatter.
            unsafe = any(
                (repo / Path(*Path(path.decode()).parts[:i])).is_symlink()
                for i in range(1, len(Path(path.decode()).parts) + 1)
            )
            if unsafe or not full.is_file():
                content, mode = None, None
            else:
                content = full.read_bytes()
                mode = "100755" if full.stat().st_mode & 0o111 else "100644"
        if (
            content is None
            or mode != identity["mode"]
            or hashlib.sha256(content).hexdigest() != identity["sha256"]
        ):
            failures.append(
                f"{path.decode()}: differs from Castiron output; change inputs/compiler or handwritten code"
            )
    for path in old.keys() - files.keys():
        retired = repo / path.decode()
        present = (
            retired.is_symlink() or (retired.exists() and not retired.is_dir())
            if worktree
            else path in entries
        )
        if present:
            failures.append(f"{path.decode()}: retired generated file remains in candidate")
    return failures


def changed_paths(repo: Path, base: str, head: str) -> set[bytes]:
    """Use the entire PR diff, not its last commit or a truncated API file list."""
    start = (
        report.git(repo, "merge-base", report.require_sha(base), report.require_sha(head))
        .decode()
        .strip()
    )
    return set(
        report.git(
            repo,
            "diff",
            "--name-only",
            "-z",
            "--no-renames",
            "--no-ext-diff",
            "--no-textconv",
            start,
            head,
            "--",
        ).split(b"\0")
    ) - {b""}


def check_isolation(repo: Path, base: str, head: str) -> int | None:
    # Validate even if the policy was removed by an earlier commit in this PR.
    proposed = read_budget(repo, head)
    paths = changed_paths(repo, base, head)
    if POLICY.encode() not in paths:
        return None
    if strict_policy(repo, base) and not strict_policy(repo, head):
        raise ValueError("strict generated-file ownership cannot be downgraded")
    if paths != {POLICY.encode()}:
        raise ValueError(ISOLATION_MESSAGE)
    return proposed


def count_custom_lines(result: dict[str, Any]) -> tuple[int, int]:
    if result.get("status") != "ok":
        raise ValueError("custom-code report could not verify the generated baseline")
    added = removed = 0
    for file in result["files"]:
        if not file["custom_after"]:
            continue
        counts = [file["added"], file["removed"]]
        if any(not isinstance(n, str) or not n.isascii() or not n.isdecimal() for n in counts):
            raise ValueError(f"cannot count non-text customization: {file['path']}")
        added += int(counts[0])
        removed += int(counts[1])
    return added, removed


def outcome(state: str, description: str) -> dict[str, str]:
    return {"state": state, "description": description}


def evaluate(
    repo: Path,
    base: str,
    head: str,
    *,
    public: bool,
    fetch: bool = False,
    pull_heads: list[str] | None = None,
    measurement: tuple[dict[str, Any], bytes] | None = None,
    policy_sha: str | None = None,
) -> tuple[dict[str, Any], bytes]:
    """In a queue, isolate each PR but budget the complete merged candidate."""
    base, head = report.require_sha(base), report.require_sha(head)
    policy_sha = cast(str, report.require_sha(policy_sha or base))
    result: dict[str, Any] = {
        "base_sha": base,
        "policy_sha": policy_sha,
        "head_sha": head,
        "checks": {},
    }
    checks = result["checks"]
    proposed_limits: list[int] = []
    try:
        read_budget(repo, policy_sha)
        read_budget(repo, base)
        read_budget(repo, head)
        if pull_heads is not None and not pull_heads:
            raise ValueError("merge group has no verified constituent PRs")
        for pr_head in pull_heads if pull_heads is not None else [head]:
            proposed = check_isolation(repo, base, pr_head)
            if proposed is not None:
                proposed_limits.append(proposed)
        checks["isolation"] = outcome(
            "success", "Budget changes are isolated; human review is required for increases."
        )
    except (report.ReportError, ValueError, UnicodeError) as exc:
        checks["isolation"] = outcome("failure", str(exc))

    patch = b""
    try:
        limit = read_budget(repo, policy_sha)
        result["limit"] = limit
        measured, patch = (
            measurement
            if measurement is not None
            else report.build_report(
                repo,
                base,
                head,
                public=public,
                fetch=fetch,
                require_head_hash=True,
            )
        )
        added, removed = count_custom_lines(measured)
        total = added + removed
        result.update(
            additions=added,
            deletions=removed,
            total=total,
            mixed_files=measured["counts"]["after"],
            generated=measured["after"],
            files=measured["files"],
        )
        # Increases never apply to their own PR/group. Decreases must be viable too.
        checked_limit = min([limit, *proposed_limits])
        result["checked_limit"] = checked_limit
        state = "success" if total <= checked_limit else "failure"
        description = f"+{added} / -{removed} = {total} custom lines; limit {checked_limit}."
        # Main's strict policy applies even if the candidate tries to remove it.
        # A proposed activation must itself satisfy the stricter contract.
        if (
            strict_policy(repo, policy_sha)
            or strict_policy(repo, base)
            or strict_policy(repo, head)
        ):
            violations = verify_generated(
                repo, measured["after"]["commit"], head, previous=measured["before"]["commit"]
            )
            result["strict_violations"] = violations
            if violations:
                state = "failure"
                description = "Strict generated-file verification failed: " + "; ".join(violations)
            else:
                description += " All generated files exactly match the verified manifest."
        checks["budget"] = outcome(state, description)
    except (report.ReportError, ValueError, UnicodeError, KeyError) as exc:
        checks["budget"] = outcome("failure", str(exc))
    return result, patch


def write_result(out: Path, result: dict[str, Any], patch: bytes = b"") -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "budget.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (out / "custom-code.patch").write_bytes(patch)
    lines = ["## Custom-code budget", ""]
    for name in ("isolation", "budget"):
        check = result["checks"][name]
        lines.append(f"- **{name}: {check['state']}** — {html.escape(check['description'])}")
    if "total" in result:
        lines += [
            "",
            f"Mixed files: **{result['mixed_files']}**. Base-budget headroom: **{result['limit'] - result['total']} lines**.",
        ]
        lines += [
            "",
            f"Policy: `{result['policy_sha']}` · candidate: `{result['head_sha']}`.",
            f"Target {result.get('target_branch', 'baseline')}: `{result['base_sha']}`.",
            f"Verified generated snapshot: `{result['generated']['commit']}`.",
            "",
            "| Largest custom patches | Added | Deleted |",
            "|---|---:|---:|",
        ]
        files = [f for f in result["files"] if f["custom_after"]]
        for file in sorted(files, key=lambda f: int(f["added"]) + int(f["removed"]), reverse=True)[
            :10
        ]:
            path = html.escape(file["path"]).replace("|", "&#124;").replace("\n", "&#10;")
            lines.append(f"| <code>{path}</code> | {file['added']} | {file['removed']} |")
        ownership = [f for f in result["files"] if f["category"] == "no_longer_generated"]
        if ownership:
            lines += ["", "**No longer generated (outside the current budget):**"]
            lines += [f"- <code>{html.escape(f['path'])}</code>" for f in ownership]
    lines += [
        "",
        "Budget increases require a separate budget-only PR, explicit justification, and a human approving review. Agents may not approve or bypass an increase.",
    ]
    summary = "\n".join(lines) + "\n"
    (out / "summary.md").write_text(summary)
    print(summary)


def queued_entries(repository: str, branch: str) -> list[tuple[str, str]]:
    """Query the actual queue; never infer PR membership from commit messages."""
    owner, name = repository.split("/")
    query = """query($owner:String!,$name:String!,$branch:String!,$cursor:String) {
      repository(owner:$owner,name:$name) { mergeQueue(branch:$branch) {
        entries(first:100,after:$cursor) {
          nodes { pullRequest { headRefOid } headCommit { oid } }
          pageInfo { hasNextPage endCursor }
        }
      } }
    }"""
    cursor = None
    heads: list[tuple[str, str]] = []
    while True:
        response = report.api(
            "POST",
            "graphql",
            {
                "query": query,
                "variables": {"owner": owner, "name": name, "branch": branch, "cursor": cursor},
            },
        )
        entries = response["data"]["repository"]["mergeQueue"]["entries"]
        for node in entries["nodes"]:
            # Entries still awaiting preparation have no synthetic queue commit.
            if node["headCommit"] is not None:
                heads.append(
                    (
                        report.require_sha(node["pullRequest"]["headRefOid"]),
                        report.require_sha(node["headCommit"]["oid"]),
                    )
                )
        page = entries["pageInfo"]
        if not page["hasNextPage"]:
            return heads
        if not page["endCursor"] or page["endCursor"] == cursor:
            raise ValueError("invalid merge-queue pagination")
        cursor = page["endCursor"]


def github_evaluate(
    repo: Path,
    repository: str,
    event: dict[str, Any],
    trusted_sha: str,
    trusted_report_dir: Path | None = None,
) -> tuple[dict[str, Any], bytes]:
    """Fetch data into a fresh bare repo; the executable checkout remains trusted."""
    if not report.REPOSITORY.fullmatch(repository):
        raise ValueError("invalid repository")
    root = f"repos/{repository}"
    metadata = report.api("GET", root)
    if event["repository"]["full_name"] != repository:
        raise ValueError("event repository mismatch")
    branch = metadata["default_branch"]
    if branch != "main":
        raise ValueError("budget gate requires main as the default branch")
    main = report.require_sha(trusted_sha)
    signal = event["workflow_run"]
    run_id = signal["id"]
    if type(run_id) is not int or run_id <= 0:
        raise ValueError("invalid source run ID")
    run = report.api("GET", f"{root}/actions/runs/{run_id}")
    if (
        run["head_sha"] != signal["head_sha"]
        or run["repository"]["full_name"] != repository
        or run["path"].split("@", 1)[0] != ".github/workflows/castiron-custom-code.yml"
        or run["status"] != "completed"
        or run["run_attempt"] != signal["run_attempt"]
        or run["event"] != signal["event"]
    ):
        raise ValueError("unexpected or superseded source workflow run")
    head = report.require_sha(run["head_sha"])
    measured = None
    if run["event"] == "pull_request":
        current = report.current_pull(repository, run)
        if current is None:
            raise ValueError(
                "source run must identify exactly one current PR targeting main or next"
            )
        _, branch = current
        if trusted_report_dir is not None:
            measured = json.loads((trusted_report_dir / "report.json").read_text())
            base = report.require_sha(measured["target_base_sha"])
        else:
            base = (
                main
                if branch == "main"
                else report.require_sha(
                    report.api("GET", f"{root}/git/ref/heads/{branch}")["object"]["sha"]
                )
            )
    elif run["event"] == "merge_group":
        # Both the target baseline and trusted policy must still be current.
        branch = next(
            (
                name
                for name in report.TARGET_BRANCHES
                if run["head_branch"].startswith(f"gh-readonly-queue/{name}/")
            ),
            "",
        )
        if not branch:
            raise ValueError("queue signal does not target main or next")
        current_main = report.require_sha(
            report.api("GET", f"{root}/git/ref/heads/main")["object"]["sha"]
        )
        if main != current_main:
            raise ValueError("trusted checkout is stale; rerun against current main")
        base = (
            main
            if branch == "main"
            else report.require_sha(
                report.api("GET", f"{root}/git/ref/heads/{branch}")["object"]["sha"]
            )
        )
    else:
        raise ValueError("unsupported budget event")
    # PR statuses can outlive their base revision. Require the queue's fresh,
    # combined candidate check before merging rather than relying on those alone.
    page = 1
    while True:
        rules = report.api("GET", f"{root}/rules/branches/{branch}?per_page=100&page={page}")
        if any(rule["type"] == "merge_queue" for rule in rules):
            break
        if len(rules) < 100:
            raise ValueError(
                f"{branch} must require a merge queue before activating the budget gate"
            )
        page += 1
    measurement = None
    if trusted_report_dir is not None:
        # Only the preceding main-branch step may supply this directory. Never
        # download a candidate artifact here. Reuse its verified report and bare
        # object store, avoiding a second snapshot fetch/hash/diff computation.
        if run["event"] != "pull_request":
            raise ValueError("only PR runs can reuse the trusted report")
        assert measured is not None
        if (
            measured["target_branch"] != branch
            or measured["policy_sha"] != main
            or measured["head_sha"] != head
            or (branch == "main" and base != main)
        ):
            raise ValueError("trusted report does not match the captured base/head")
        if report.git(repo, "rev-parse", "--is-bare-repository").strip() != b"true":
            raise ValueError("trusted report must use a bare object store")
        measurement = (measured, (trusted_report_dir / "custom-code.patch").read_bytes())
    else:
        if repo.exists():
            raise ValueError("Git object directory must be fresh")
        subprocess.run(["git", "init", "--bare", str(repo)], check=True, capture_output=True)
        report.git(repo, "remote", "add", "origin", f"https://github.com/{repository}.git")
        report.git(
            repo, "fetch", "--quiet", "--no-tags", "origin", *dict.fromkeys((main, base, head))
        )
    pull_heads: list[str] | None = None
    if run["event"] == "merge_group":
        if report.git(repo, "merge-base", base, head).decode().strip() != base:
            raise ValueError("merge group does not include current target; retry the current group")
        pull_heads = []
        entries = queued_entries(repository, branch)
        if not any(queue_head == head for _, queue_head in entries):
            raise ValueError("merge-group head is no longer in the current queue")
        for candidate, queue_head in entries:
            report.git(repo, "fetch", "--quiet", "--no-tags", "origin", queue_head)
            ancestor = report.git(repo, "merge-base", queue_head, head).decode().strip()
            if ancestor == queue_head:
                report.git(repo, "fetch", "--quiet", "--no-tags", "origin", candidate)
                pull_heads.append(candidate)
        if not pull_heads:
            raise ValueError("cannot verify merge-group PR membership; retry the current group")
    result, patch = evaluate(
        repo,
        base,
        head,
        public=not metadata["private"],
        fetch=True,
        pull_heads=pull_heads,
        measurement=measurement,
        policy_sha=main,
    )
    result["target_branch"] = branch
    return result, patch


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generated = commands.add_parser("verify-generated")
    generated.add_argument("--repo", type=Path, required=True)
    generated.add_argument("--policy-ref", required=True)
    generated.add_argument("--generated", required=True)
    generated.add_argument("--previous-generated")
    generated.add_argument("--head", required=True)
    generated.add_argument("--worktree", action="store_true")
    local = commands.add_parser("check")
    local.add_argument("--base", required=True)
    local.add_argument("--head", required=True)
    local.add_argument("--public", action="store_true")
    local.add_argument("--fetch", action="store_true")
    github = commands.add_parser("github")
    github.add_argument("--repository", required=True)
    github.add_argument("--event-path", type=Path, required=True)
    github.add_argument("--trusted-sha", required=True)
    github.add_argument("--trusted-report-dir", type=Path)
    for command in (local, github):
        command.add_argument("--repo", type=Path, required=True)
        command.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "verify-generated":
        # Local pipeline integration pins policy and checkpoint before merging.
        # Legacy SDKs without a policy retain their existing behavior.
        try:
            policy_ref = report.require_sha(args.policy_ref)
            if not report.git(args.repo, "ls-tree", policy_ref, "--", POLICY):
                return 0
            if not strict_policy(args.repo, policy_ref):
                return 0
            failures = verify_generated(
                args.repo,
                args.generated,
                args.head,
                previous=args.previous_generated,
                worktree=args.worktree,
            )
            if failures:
                raise ValueError("\n".join(failures))
        except (ValueError, OSError, report.ReportError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        return 0
    try:
        if args.command == "check":
            result, patch = evaluate(
                args.repo, args.base, args.head, public=args.public, fetch=args.fetch
            )
        else:
            result, patch = github_evaluate(
                args.repo,
                args.repository,
                json.loads(args.event_path.read_text()),
                args.trusted_sha,
                args.trusted_report_dir,
            )
    except (
        report.ReportError,
        ValueError,
        OSError,
        KeyError,
        TypeError,
        subprocess.SubprocessError,
    ) as exc:
        result = {
            "checks": {name: outcome("failure", str(exc)) for name in ("isolation", "budget")}
        }
        patch = b""
    write_result(args.out, result, patch)
    if args.command == "github" and "GITHUB_OUTPUT" in os.environ:
        with Path(os.environ["GITHUB_OUTPUT"]).open("a") as output:
            output.writelines(
                f"{name}={result['checks'][name]['state']}\n" for name in ("isolation", "budget")
            )
            output.write(f"target_branch={result.get('target_branch', '')}\n")
            output.write(f"policy_sha={result.get('policy_sha', '')}\n")
            output.write(f"base_sha={result.get('base_sha', '')}\n")
            output.write(f"head_sha={result.get('head_sha', '')}\n")
    return 0 if all(c["state"] == "success" for c in result["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
