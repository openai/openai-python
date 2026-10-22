#!/usr/bin/env python3
# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
"""Select reviewed policy using current main; emit a local, versioned receipt.

The pinned budget evaluator remains a separate executable authority. This module
never executes candidate code, and receipts must not come from candidate artifacts.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, TypedDict, cast

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
NEXT_POLICY_VERSION = 1
SELECTION_RECEIPT_VERSION = 1


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
    if "ratchet" in value:
        keys.add("ratchet")
        if value["ratchet"] != "go":
            raise ValueError("ratchet must be go")
    if version == 2:
        keys.add("generated_files")
    if "next_policy" in value:
        keys.add("next_policy")
        pin: Any = value["next_policy"]
        if not isinstance(pin, dict) or set(cast(dict[str, Any], pin)) != {
            "repository",
            "main_sha",
        }:
            raise ValueError("next_policy must contain exactly repository and main_sha")
        if not isinstance(pin["repository"], str) or not report.REPOSITORY.fullmatch(
            pin["repository"]
        ):
            raise ValueError("invalid next_policy repository")
        if not isinstance(pin["main_sha"], str):
            raise ValueError("invalid next_policy main_sha")
        report.require_sha(pin["main_sha"])
    if set(value) != keys:
        raise ValueError("budget file contains missing or unsupported fields")
    limit = value["max_custom_patch_lines"]
    if type(limit) is not int or limit < 0:
        raise ValueError("max_custom_patch_lines must be a nonnegative integer")
    if version == 2 and (value["generated_files"] != "strict" or limit != 0):
        raise ValueError("schema v2 requires generated_files=strict and a zero budget")
    return value


def next_policy_sha(repo: Path, repository: str, base: str, authenticated_main: str) -> str:
    """Select executable policy only from an authenticated target base, never its candidate."""
    base = report.require_sha(base)
    authenticated_main = report.require_sha(authenticated_main)
    if not report.REPOSITORY.fullmatch(repository):
        raise ValueError("invalid policy repository")
    expected_origin = f"https://github.com/{repository}.git"
    if report.git(repo, "remote", "get-url", "origin").decode().strip() != expected_origin:
        raise ValueError("policy repository origin mismatch")
    fetched_main = report.git(repo, "rev-parse", "refs/remotes/origin/main").decode().strip()
    if fetched_main != authenticated_main:
        raise ValueError("authenticated main changed during policy selection; retry")
    pin = read_policy(repo, base).get("next_policy")
    # read_policy validates the shape of every present next_policy pin.
    if pin is None:
        raise ValueError("trusted next base has no reviewed policy pin")
    if pin["repository"] != repository:
        raise ValueError("next policy pin belongs to another repository")
    policy = report.require_sha(pin["main_sha"])
    # A reachable side-branch commit is not an adopted main policy revision.
    adopted = report.git(repo, "rev-list", "--first-parent", authenticated_main).splitlines()
    if policy.encode() not in adopted:
        raise ValueError("next policy pin is not in authenticated main first-parent history")
    read_policy(repo, policy)
    # Reject pre-protocol checkers rather than executing code that cannot bind a next pin.
    source = report.git(repo, "show", f"{policy}:scripts/castiron/custom_code_budget.py")
    tree = ast.parse(source)
    capable = any(
        isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "NEXT_POLICY_VERSION"
            for target in node.targets
        )
        and isinstance(node.value, ast.Constant)
        and type(node.value.value) is int
        and node.value.value == NEXT_POLICY_VERSION
        for node in tree.body
    )
    if not capable:
        raise ValueError("pinned checker does not support reviewed next policies")
    return cast(str, policy)


class HumanReviewRules(TypedDict):
    version: int
    associations: list[str]
    negative_pattern: str
    attestation_prefix: str


HUMAN_REVIEW_RULES: HumanReviewRules = {
    "version": 2,
    "attestation_prefix": "I personally reviewed and approve this policy change as a human: ",
    "associations": ["OWNER", "MEMBER", "COLLABORATOR"],
    "negative_pattern": (
        r"automated[\s_:-]*(?:source[\s_:-]*)?review|source[- ]only review|"
        r"(?:not|isn't|does not constitute|does not substitute for)\s+(?:an?\s+)?human\s+approv|"
        r"non[- ]human[- ]approval"
    ),
}


def has_human_approval(reviews: list[dict[str, Any]], author: str, head: str) -> bool:
    """Versioned review predicate; publisher consumes these same trusted rules."""
    latest: dict[str, dict[str, Any]] = {}
    for review in reviews:
        if review["state"] != "PENDING":
            login = review["user"]["login"]
            if login not in latest or review["id"] > latest[login]["id"]:
                latest[login] = review
    return any(
        review["state"] == "APPROVED"
        and review["commit_id"] == head
        and review["user"]["type"] == "User"
        and review.get("author_association") in HUMAN_REVIEW_RULES["associations"]
        and not review["user"]["login"].endswith("[bot]")
        and review["user"]["login"] != author
        and (review.get("body") or "").strip() == HUMAN_REVIEW_RULES["attestation_prefix"] + head
        and not re.search(
            HUMAN_REVIEW_RULES["negative_pattern"], review.get("body") or "", re.IGNORECASE
        )
        for review in latest.values()
    )


def require_human_policy_review(repository: str, head: str) -> int:
    """Only live, exact-head human reviews authorize a next policy activation/update."""
    root = f"repos/{repository}"
    pulls = report.api("GET", f"{root}/commits/{head}/pulls?per_page=100")
    current: list[dict[str, Any]] = []
    for item in pulls:
        pull = report.api("GET", f"{root}/pulls/{item['number']}")
        if (
            pull["state"] == "open"
            and pull["head"]["sha"] == head
            and pull["base"]["ref"] == "next"
            and pull["base"]["repo"]["full_name"] == repository
        ):
            current.append(pull)
    if len(current) != 1:
        raise ValueError("policy change must identify one open next PR")
    pull = current[0]
    all_reviews: list[dict[str, Any]] = []
    page = 1
    while True:
        reviews = report.api(
            "GET", f"{root}/pulls/{pull['number']}/reviews?per_page=100&page={page}"
        )
        all_reviews.extend(reviews)
        if len(reviews) < 100:
            break
        page += 1
    if not has_human_approval(all_reviews, pull["user"]["login"], head):
        raise ValueError("next policy changes require an exact-head human approving review")
    return int(pull["number"])


def select_policy(
    repo: Path,
    repository: str,
    branch: str,
    base: str,
    head: str,
    authenticated_main: str,
    *,
    pull_heads: list[str] | None = None,
) -> dict[str, Any]:
    """The trusted selector runs before checking out any pinned executable code."""
    base, head, authenticated_main = map(report.require_sha, (base, head, authenticated_main))
    if branch == "main":
        return {
            "schema_version": SELECTION_RECEIPT_VERSION,
            "target_branch": branch,
            "base_sha": base,
            "head_sha": head,
            "policy_sha": authenticated_main,
            "bootstrap": False,
        }
    if branch != "next":
        raise ValueError("unsupported policy target")
    # Malformed policies are errors, never a reason to enter bootstrap mode.
    base_policy = read_policy(repo, base)
    head_policy = read_policy(repo, head)
    bootstrap = "next_policy" not in base_policy
    if bootstrap:
        if "next_policy" not in head_policy or (
            pull_heads is None and changed_paths(repo, base, head) != {POLICY.encode()}
        ):
            raise ValueError("missing next pin allows only reviewed policy-only initialization")
        policy = authenticated_main
    else:
        policy = next_policy_sha(repo, repository, base, authenticated_main)
    # No candidate-selected version executes, including in a policy-only PR.
    head_base_policy = read_policy(repo, merge_base(repo, base, head))
    if head_policy.get("next_policy") != head_base_policy.get("next_policy"):
        if "next_policy" not in head_policy or (
            pull_heads is None and changed_paths(repo, base, head) != {POLICY.encode()}
        ):
            raise ValueError("next pin changes must be policy-only and cannot remove the pin")
        next_policy_sha(repo, repository, head, authenticated_main)
    policy_reviews: list[dict[str, Any]] = []
    candidates = pull_heads if pull_heads is not None else [head]
    if not candidates:
        raise ValueError("next evaluation has no verified constituent PR")
    for candidate in candidates:
        candidate_policy = read_policy(repo, candidate)
        candidate_base_policy = read_policy(repo, merge_base(repo, base, candidate))
        pin_changed = candidate_policy.get("next_policy") != candidate_base_policy.get(
            "next_policy"
        )
        budget_increased = (
            candidate_policy["max_custom_patch_lines"]
            > candidate_base_policy["max_custom_patch_lines"]
        )
        ratchet_activated = (
            candidate_policy.get("ratchet") == "go" and candidate_base_policy.get("ratchet") != "go"
        )
        if pin_changed or budget_increased or ratchet_activated:
            if changed_paths(repo, base, candidate) != {POLICY.encode()}:
                raise ValueError("each next policy activation or increase must be policy-only")
            number = require_human_policy_review(repository, candidate)
            policy_reviews.append({"number": number, "head_sha": candidate})
    return {
        "schema_version": SELECTION_RECEIPT_VERSION,
        "target_branch": branch,
        "base_sha": base,
        "head_sha": head,
        "policy_sha": policy,
        "bootstrap": bootstrap,
        "policy_reviews": policy_reviews,
        "human_review_rules": HUMAN_REVIEW_RULES,
    }


def select_github_policy(
    repo: Path,
    repository: str,
    event: dict[str, Any],
    trusted_sha: str,
    *,
    source_workflow: str = ".github/workflows/castiron-custom-code.yml",
) -> dict[str, Any]:
    """Authenticate event, refs and graph in a fresh store before choosing checker code."""
    if source_workflow not in (
        ".github/workflows/castiron-custom-code.yml",
        ".github/workflows/ci.yml",
    ):
        raise ValueError("unsupported policy source workflow")
    if (
        not report.REPOSITORY.fullmatch(repository)
        or event["repository"]["full_name"] != repository
    ):
        raise ValueError("policy event repository mismatch")
    root = f"repos/{repository}"
    metadata = report.api("GET", root)
    if metadata["default_branch"] != "main":
        raise ValueError("policy selector requires the main default branch")
    signal = event["workflow_run"]
    run = report.api("GET", f"{root}/actions/runs/{signal['id']}")
    if (
        run["repository"]["full_name"] != repository
        or run["head_sha"] != signal["head_sha"]
        or run["status"] != "completed"
        or run["event"] != signal["event"]
        or run["run_attempt"] != signal["run_attempt"]
        or run["path"].split("@", 1)[0] != source_workflow
    ):
        raise ValueError("unexpected or superseded policy source run")
    workflow = report.api("GET", f"{root}/actions/workflows/{source_workflow.rsplit('/', 1)[1]}")
    if (
        type(run.get("workflow_id")) is not int
        or run["workflow_id"] != workflow["id"]
        or workflow["path"] != source_workflow
    ):
        raise ValueError("policy source run is not the canonical workflow")
    head = report.require_sha(run["head_sha"])
    if run["event"] == "pull_request":
        current = report.current_pull(repository, run)
        if current is None:
            raise ValueError("policy run must identify one current target PR")
        _, branch = current
    elif run["event"] == "merge_group":
        branch = next(
            (
                name
                for name in report.TARGET_BRANCHES
                if run["head_branch"].startswith(f"gh-readonly-queue/{name}/")
            ),
            "",
        )
        if not branch:
            raise ValueError("policy queue target is unsupported")
    else:
        raise ValueError("unsupported policy source event")
    trusted_sha = report.require_sha(trusted_sha)
    if branch == "main":
        if source_workflow != ".github/workflows/castiron-custom-code.yml":
            raise ValueError("CI policy adapter is restricted to next")
        return select_policy(repo, repository, branch, trusted_sha, head, trusted_sha)
    main = report.require_sha(report.api("GET", f"{root}/git/ref/heads/main")["object"]["sha"])
    base = report.require_sha(report.api("GET", f"{root}/git/ref/heads/next")["object"]["sha"])
    if repo.exists():
        raise ValueError("policy object directory must be fresh")
    repo.mkdir()
    report.git(repo, "init", "--quiet", "--bare")
    report.git(repo, "remote", "add", "origin", f"https://github.com/{repository}.git")
    report.git(
        repo,
        "fetch",
        "--quiet",
        "--no-tags",
        "origin",
        "+refs/heads/main:refs/remotes/origin/main",
        "+refs/heads/next:refs/remotes/origin/next",
        head,
    )
    if report.git(repo, "rev-parse", "refs/remotes/origin/next").decode().strip() != base:
        raise ValueError("next base changed during selection; retry")
    heads: list[str] | None = None
    if run["event"] == "merge_group":
        if report.git(repo, "merge-base", base, head).decode().strip() != base:
            raise ValueError("policy queue does not contain current next base")
        entries = queued_entries(repository, branch)
        if not any(queue == head for _, queue in entries):
            raise ValueError("policy queue entry is no longer live")
        heads = []
        for candidate, queue in entries:
            report.git(repo, "fetch", "--quiet", "--no-tags", "origin", queue)
            if report.git(repo, "merge-base", queue, head).decode().strip() == queue:
                report.git(repo, "fetch", "--quiet", "--no-tags", "origin", candidate)
                heads.append(candidate)
        if not heads:
            raise ValueError("policy queue has no verified constituent PRs")
    return select_policy(repo, repository, branch, base, head, main, pull_heads=heads)


def merge_base(repo: Path, base: str, head: str) -> str:
    """Distinguish actual PR policy edits from later changes on the target."""
    return cast(
        str,
        report.git(repo, "merge-base", report.require_sha(base), report.require_sha(head))
        .decode()
        .strip(),
    )


def changed_paths(repo: Path, base: str, head: str) -> set[bytes]:
    """Use the entire PR diff, not its last commit or a truncated API file list."""
    start = merge_base(repo, base, head)
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    selection = commands.add_parser("select-policy")
    selection.add_argument("--repo", type=Path, required=True)
    selection.add_argument("--repository", required=True)
    selection.add_argument("--event-path", type=Path, required=True)
    selection.add_argument("--trusted-sha", required=True)
    selection.add_argument("--out", type=Path, required=True)
    selection.add_argument(
        "--source-workflow",
        choices=(".github/workflows/castiron-custom-code.yml", ".github/workflows/ci.yml"),
        default=".github/workflows/castiron-custom-code.yml",
    )
    args = parser.parse_args(argv)
    selected = select_github_policy(
        args.repo,
        args.repository,
        json.loads(args.event_path.read_text()),
        args.trusted_sha,
        source_workflow=args.source_workflow,
    )
    args.out.write_text(json.dumps(selected, sort_keys=True) + "\n")
    if "GITHUB_OUTPUT" in os.environ:
        with Path(os.environ["GITHUB_OUTPUT"]).open("a") as output:
            output.writelines(
                f"{key}={json.dumps(value) if isinstance(value, (bool, list, dict)) else value}\n"
                for key, value in selected.items()
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
