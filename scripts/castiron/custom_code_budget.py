#!/usr/bin/env python3
"""Handwritten Python SDK budget gate. Run only from a trusted checkout, never PR code.

Reuses Castiron's vendored snapshot verifier and generated-file accounting. This
file and its workflow are SDK-owned during the Python-only rollout.
"""

from __future__ import annotations

import argparse
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


def read_budget(repo: Path, revision: str) -> int:
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
        raise ValueError("budget file must be an object")
    value = cast(dict[str, Any], value)
    if set(value) != {"schema_version", "max_custom_patch_lines"}:
        raise ValueError("budget file must contain only schema_version and max_custom_patch_lines")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise ValueError("unsupported budget schema_version")
    limit = value["max_custom_patch_lines"]
    if type(limit) is not int or limit < 0:
        raise ValueError("max_custom_patch_lines must be a nonnegative integer")
    return limit


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
) -> tuple[dict[str, Any], bytes]:
    """In a queue, isolate each PR but budget the complete merged candidate."""
    base, head = report.require_sha(base), report.require_sha(head)
    result: dict[str, Any] = {"base_sha": base, "head_sha": head, "checks": {}}
    checks = result["checks"]
    proposed_limits: list[int] = []
    try:
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
        limit = read_budget(repo, base)
        result["limit"] = limit
        measured, patch = report.build_report(
            repo,
            base,
            head,
            public=public,
            fetch=fetch,
            require_head_hash=True,
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
        checks["budget"] = outcome(
            state, f"+{added} / -{removed} = {total} custom lines; limit {checked_limit}."
        )
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
            f"Policy: `{result['base_sha']}` · candidate: `{result['head_sha']}`.",
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
    event_name: str,
    event: dict[str, Any],
    trusted_sha: str,
) -> tuple[dict[str, Any], bytes]:
    """Fetch data into a fresh bare repo; the executable checkout remains trusted."""
    if not report.REPOSITORY.fullmatch(repository):
        raise ValueError("invalid repository")
    root = f"repos/{repository}"
    metadata = report.api("GET", root)
    if event["repository"]["full_name"] != repository:
        raise ValueError("event repository mismatch")
    branch = metadata["default_branch"]
    main = report.require_sha(report.api("GET", f"{root}/git/ref/heads/{branch}")["object"]["sha"])
    if report.require_sha(trusted_sha) != main:
        raise ValueError("trusted checkout is stale; rerun against current main")
    if event_name == "pull_request_target":
        number = event["number"]
        if type(number) is not int or number <= 0:
            raise ValueError("invalid PR number")
        pull = report.api("GET", f"{root}/pulls/{number}")
        if (
            pull["state"] != "open"
            or pull["head"]["sha"] != event["pull_request"]["head"]["sha"]
            or pull["base"]["repo"]["full_name"] != repository
            or pull["base"]["ref"] != branch
            or pull["base"]["sha"] != main
        ):
            raise ValueError("PR head/base changed or does not target main; rerun the check")
        head = report.require_sha(pull["head"]["sha"])
    elif event_name == "merge_group":
        group = event["merge_group"]
        if group["base_sha"] != main or group["base_ref"] != f"refs/heads/{branch}":
            raise ValueError("merge group no longer targets current main")
        head = report.require_sha(group["head_sha"])
    else:
        raise ValueError("unsupported budget event")
    if repo.exists():
        raise ValueError("Git object directory must be fresh")
    subprocess.run(["git", "init", "--bare", str(repo)], check=True, capture_output=True)
    report.git(repo, "remote", "add", "origin", f"https://github.com/{repository}.git")
    report.git(repo, "fetch", "--quiet", "--no-tags", "origin", main, head)
    pull_heads: list[str] | None = None
    if event_name == "merge_group":
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
    return evaluate(
        repo, main, head, public=not metadata["private"], fetch=True, pull_heads=pull_heads
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    local = commands.add_parser("check")
    local.add_argument("--base", required=True)
    local.add_argument("--head", required=True)
    local.add_argument("--public", action="store_true")
    local.add_argument("--fetch", action="store_true")
    github = commands.add_parser("github")
    github.add_argument("--repository", required=True)
    github.add_argument(
        "--event-name", choices=["pull_request_target", "merge_group"], required=True
    )
    github.add_argument("--event-path", type=Path, required=True)
    github.add_argument("--trusted-sha", required=True)
    for command in (local, github):
        command.add_argument("--repo", type=Path, required=True)
        command.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "check":
            result, patch = evaluate(
                args.repo, args.base, args.head, public=args.public, fetch=args.fetch
            )
        else:
            result, patch = github_evaluate(
                args.repo,
                args.repository,
                args.event_name,
                json.loads(args.event_path.read_text()),
                args.trusted_sha,
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
            for name in ("isolation", "budget"):
                output.write(f"{name}={result['checks'][name]['state']}\n")
            output.write(f"base_sha={result.get('base_sha', '')}\n")
            output.write(f"head_sha={result.get('head_sha', '')}\n")
    return 0 if all(c["state"] == "success" for c in result["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
