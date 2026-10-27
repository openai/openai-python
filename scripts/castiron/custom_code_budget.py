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

# Load only the policy helpers beside this immutable checker, including under -I.
_spec = importlib.util.spec_from_file_location(
    "castiron_budget_policy", Path(__file__).with_name("custom_code_policy.py")
)
assert _spec is not None and _spec.loader is not None
policy = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = policy
_spec.loader.exec_module(policy)
report = policy.report
unique_keys = policy.unique_keys
read_policy = policy.read_policy
changed_paths = policy.changed_paths
queued_entries = policy.queued_entries
is_main_snapshot_bootstrap = policy.is_main_snapshot_bootstrap

POLICY = ".castiron-ratchet.json"
NEXT_POLICY_VERSION = 1
ISOLATION_MESSAGE = (
    "Budget changes require a separate, budget-only PR. "
    "Put the justification in the PR description."
)


def read_budget(repo: Path, revision: str) -> int:
    return cast(int, read_policy(repo, revision)["max_custom_patch_lines"])


def strict_policy(repo: Path, revision: str) -> bool:
    return cast(int, read_policy(repo, revision)["schema_version"]) == 2


def go_ratchet(repo: Path, revision: str) -> bool:
    return cast(bool, read_policy(repo, revision).get("ratchet") == "go")


MANIFEST = b"scripts/castiron/generated-files.json"
# Accept the relocated tooling only from the verified checkpoint. Deploy this
# reader before changing the producer so trusted-main checks can validate moves.
MANIFEST_PATHS = (MANIFEST, b"generated/castiron/generated-files.json")
# Derived from the renderer's repository-file inventory, also used by checkpoint
# publication to distinguish generated tooling from protected SDK-owned CI.
GENERATED_GITHUB_PATHS = frozenset(
    {
        b".github/workflows/castiron-custom-code.yml",
        b".github/workflows/castiron-custom-code-comment.yml",
    }
)


# Audited inventory of the authenticated pre-inventory checker format. These
# historical snapshots bind the checker bytes and manifest through their codegen
# hash. Never infer their inventory from the running compiler or candidate tree.
LEGACY_CHECKPOINT_INVENTORIES = {
    "e504abba2701f4733eb4b8ce26856cca596e13feab1e7e323adc8e7d2ccb64bc": frozenset(
        {
            b".github/workflows/castiron-custom-code-comment.yml",
            b".github/workflows/castiron-custom-code.yml",
        }
    ),
}


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
    if not values:
        historical = LEGACY_CHECKPOINT_INVENTORIES.get(hashlib.sha256(source).hexdigest())
        if historical is not None:
            return historical
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
    manifests = [path for path in MANIFEST_PATHS if path in entries]
    if len(manifests) > 1:
        raise ValueError("checkpoint contains ambiguous generated ownership manifests")
    manifest_path = manifests[0] if manifests else MANIFEST
    entry = entries.get(manifest_path)
    if entry is None or entry.mode != b"100644":
        raise ValueError(
            "strict mode requires a generated ownership manifest; regenerate with Castiron"
        )
    blobs = report.read_blobs(repo, entries)
    inventory_path = manifest_path.rsplit(b"/", 1)[0] + b"/custom_code_budget.py"
    inventory_entry = entries.get(inventory_path)
    if inventory_entry is None or inventory_entry.mode not in (b"100644", b"100755"):
        raise ValueError("checkpoint is missing its generated GitHub inventory")
    github_paths = checkpoint_github_inventory(blobs[inventory_entry.oid])
    value = json.loads(blobs[entry.oid], object_pairs_hook=unique_keys)
    if not isinstance(value, dict) or set(cast(dict[str, Any], value)) != {
        "schema_version",
        "files",
    }:
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
        if path in MANIFEST_PATHS:
            raise ValueError("generated manifest cannot include itself")
        # A matching identity cannot turn inherited, SDK-owned CI into generated
        # output. Use this verified checkpoint's literal compiler inventory, not
        # the executing verifier's version or candidate Python/manifest claims.
        # Public checkpoints may omit the private workflow/action blobs.
        if not report.included(path) and path not in github_paths:
            raise ValueError(f"generated manifest claims SDK-owned GitHub path: {name}")
        if not isinstance(identity, dict) or set(cast(dict[str, Any], identity)) != {
            "mode",
            "sha256",
        }:
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
    snapshot_paths = set(entries) - {manifest_path}
    if any(
        report.included(path) or path in github_paths for path in snapshot_paths - files.keys()
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
    files[manifest_path] = {
        "mode": "100644",
        "sha256": hashlib.sha256(blobs[entry.oid]).hexdigest(),
    }
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


def check_isolation(repo: Path, base: str, head: str) -> int | None:
    # Validate even if the policy was removed by an earlier commit in this PR.
    proposed = read_budget(repo, head)
    paths = changed_paths(repo, base, head)
    if POLICY.encode() not in paths:
        return None
    if strict_policy(repo, base) and not strict_policy(repo, head):
        raise ValueError("strict generated-file ownership cannot be downgraded")
    if go_ratchet(repo, base) and not go_ratchet(repo, head):
        raise ValueError("Go customization ratchet cannot be disabled")
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


def go_customization(repo: Path, revision: str, measured: dict[str, Any]) -> dict[str, Any]:
    """Count patches plus physical handwritten Go, using only verified Git objects."""
    added, removed = count_custom_lines(measured)
    # Use the reporter's ownership view. Private snapshots also retain SDK-owned
    # CI files excluded from that view; those Go files are still handwritten.
    generated = report.tree_entries(repo, measured["after"]["commit"])
    handwritten = {
        path: entry
        for path, entry in report.tree_entries(repo, revision, include_workflows=True).items()
        if path.endswith(b".go") and path not in generated
    }
    for path, entry in handwritten.items():
        if entry.mode not in {b"100644", b"100755"}:
            raise ValueError(f"nonregular handwritten Go: {path!r}")
    blobs = report.read_blobs(repo, handwritten)
    files: list[dict[str, Any]] = []
    for path, entry in sorted(handwritten.items()):
        content = blobs[entry.oid]
        content.decode("utf-8")
        if b"\0" in content:
            raise ValueError(f"non-text handwritten Go: {path!r}")
        lines = content.count(b"\n") + int(bool(content) and not content.endswith(b"\n"))
        files.append({"path": path.decode("utf-8"), "lines": lines})
    handwritten_lines = sum(file["lines"] for file in files)
    return {
        "revision": revision,
        "generated": measured["after"],
        "patch_lines": added + removed,
        "handwritten_lines": handwritten_lines,
        "handwritten_files": files,
        "total": added + removed + handwritten_lines,
    }


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
    target_branch: str = "main",
    main_snapshot: str | None = None,
    repository: str | None = None,
) -> tuple[dict[str, Any], bytes]:
    """In a queue, isolate each PR but budget the complete merged candidate."""
    base, head = report.require_sha(base), report.require_sha(head)
    policy = cast(str, report.require_sha(policy_sha or base))
    result: dict[str, Any] = {
        "base_sha": base,
        "target_branch": target_branch,
        "policy_sha": policy,
        "head_sha": head,
        "checks": {},
    }
    checks = result["checks"]
    proposed_limits: list[int] = []
    try:
        read_budget(repo, policy)
        read_budget(repo, base)
        read_budget(repo, head)
        if pull_heads is not None and not pull_heads:
            raise ValueError("merge group has no verified constituent PRs")
        if main_snapshot is not None and (
            target_branch != "next"
            or main_snapshot != policy
            or repository is None
            or (pull_heads is not None and len(pull_heads) != 1)
            or not is_main_snapshot_bootstrap(
                repo,
                repository,
                base,
                head,
                policy,
                constituent=pull_heads[0]
                if pull_heads is not None and len(pull_heads) == 1
                else None,
            )
            or any(
                not is_main_snapshot_bootstrap(repo, repository, base, candidate, policy)
                for candidate in (pull_heads if pull_heads is not None else [head])
            )
        ):
            raise ValueError("invalid authenticated main snapshot bootstrap")
        for pr_head in pull_heads if pull_heads is not None else [head]:
            proposed = 0 if main_snapshot is not None else check_isolation(repo, base, pr_head)
            if proposed is not None:
                proposed_limits.append(proposed)
        checks["isolation"] = outcome(
            "success",
            "Exact authenticated strict-zero main snapshot adoption."
            if main_snapshot is not None
            else "Budget changes are isolated; human review is required for increases.",
        )
    except (report.ReportError, ValueError, UnicodeError) as exc:
        checks["isolation"] = outcome("failure", str(exc))

    patch = b""
    try:
        limit = read_budget(repo, policy)
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
                target_branch=target_branch,
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
        if any(go_ratchet(repo, revision) for revision in (policy, base, head)):
            # The report's historical merge base is for presentation only. Measure
            # the captured live target against its own hash-verified snapshot.
            baseline, _ = report.build_report(
                repo,
                base,
                base,
                public=public,
                fetch=fetch,
                require_head_hash=True,
                target_branch=target_branch,
            )
            before = go_customization(repo, base, baseline)
            after = go_customization(repo, head, measured)
            delta = after["total"] - before["total"]
            result["ratchet"] = {"kind": "go", "before": before, "after": after, "delta": delta}
            description += (
                f" Go customization {before['total']} -> {after['total']} (delta {delta:+d})."
            )
            if delta > 0:
                state = "failure"
            if go_ratchet(repo, base) and not go_ratchet(repo, head):
                state = "failure"
                description += " Go customization ratchet cannot be disabled."
        # Main's strict policy applies even if the candidate tries to remove it.
        # A proposed activation must itself satisfy the stricter contract.
        if strict_policy(repo, policy) or strict_policy(repo, base) or strict_policy(repo, head):
            violations = verify_generated(
                repo,
                measured["after"]["commit"],
                head,
                previous=(measured["before"] or measured["adoption_baseline"])["commit"],
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


def github_evaluate(
    repo: Path,
    repository: str,
    event: dict[str, Any],
    trusted_sha: str,
    trusted_report_dir: Path | None = None,
    selection: dict[str, Any] | None = None,
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
        if branch == "main" and main != current_main:
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
    # This receipt is created locally by the trusted-main selector before the
    # pinned checkout. It must never come from candidate workflow artifacts.
    if (
        selection is None
        or type(selection.get("schema_version")) is not int
        or any(
            selection.get(key) != value
            for key, value in {
                "schema_version": 1,
                "target_branch": branch,
                "base_sha": base,
                "head_sha": head,
                "policy_sha": main,
            }.items()
        )
    ):
        raise ValueError("trusted policy selection does not match evaluation")
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
    main_snapshot = selection.get("main_snapshot") or None
    if main_snapshot is not None:
        if (
            branch != "next"
            or main_snapshot != main
            or report.api("GET", f"{root}/git/ref/heads/main")["object"]["sha"] != main
        ):
            raise ValueError("authenticated main snapshot changed; retry bootstrap")
        # This evaluator has its own bare object store, including when reusing
        # the PR report. SHA fetches do not create the selector's named main ref.
        report.git(
            repo,
            "fetch",
            "--quiet",
            "--no-tags",
            "origin",
            "+refs/heads/main:refs/remotes/origin/main",
        )
        if report.git(repo, "rev-parse", "refs/remotes/origin/main").decode().strip() != main:
            raise ValueError("authenticated main changed during snapshot fetch; retry")
        if not is_main_snapshot_bootstrap(
            repo,
            repository,
            base,
            head,
            main,
            constituent=pull_heads[0] if pull_heads is not None and len(pull_heads) == 1 else None,
        ):
            raise ValueError("authenticated main snapshot changed; retry bootstrap")
    if branch == "next":
        assert selection is not None
        base_pin = read_policy(repo, base).get("next_policy")
        if base_pin is None:
            # evaluate() checks each verified queue constituent for policy isolation.
            if (
                selection.get("bootstrap") is not True
                or "next_policy" not in read_policy(repo, head)
                or (
                    main_snapshot is None
                    and pull_heads is None
                    and changed_paths(repo, base, head) != {POLICY.encode()}
                )
            ):
                raise ValueError("unreviewed next policy initialization")
        elif selection.get("bootstrap") is not False or base_pin != {
            "repository": repository,
            "main_sha": main,
        }:
            raise ValueError("trusted next base pin changed; rerun policy selection")
    result, patch = evaluate(
        repo,
        base,
        head,
        public=not metadata["private"],
        fetch=True,
        pull_heads=pull_heads,
        measurement=measurement,
        policy_sha=main,
        target_branch=branch,
        main_snapshot=main_snapshot,
        repository=repository,
    )
    result["target_branch"] = branch
    return result, patch


def prepare_main_snapshot(
    repo: Path, repository: str, base: str, authenticated_main: str, *, fetch: bool = False
) -> str:
    """Create and verify an adoption commit without altering a ref, index or metadata."""
    base, authenticated_main = map(report.require_sha, (base, authenticated_main))
    strict = {"schema_version": 2, "max_custom_patch_lines": 0, "generated_files": "strict"}
    main_policy = read_policy(repo, authenticated_main)
    if {
        key: value for key, value in main_policy.items() if key != "ratchet"
    } != strict or "next_policy" in read_policy(repo, base):
        raise ValueError("main snapshot preparation requires strict-zero main and unpinned next")
    if policy.merge_base(repo, base, authenticated_main) != base:
        raise ValueError("protected next must be an ancestor of authenticated main")
    value = {
        **main_policy,
        "next_policy": {"repository": repository, "main_sha": authenticated_main},
    }
    blob = report.git(
        repo,
        "hash-object",
        "-w",
        "--stdin",
        input_bytes=(json.dumps(value, indent=2) + "\n").encode(),
    ).strip()
    entries = report.git(repo, "ls-tree", "-z", authenticated_main).split(b"\0")
    # Replace only the root policy blob, preserving every other entry and mode.
    replacement = b"100644 blob " + blob + b"\t" + POLICY.encode()
    tree = (
        report.git(
            repo,
            "mktree",
            "-z",
            input_bytes=b"\0".join(
                replacement if entry.partition(b"\t")[2] == POLICY.encode() else entry
                for entry in entries
            ),
        )
        .decode()
        .strip()
    )
    head = (
        report.git(
            repo,
            "commit-tree",
            tree,
            "-p",
            base,
            "-p",
            authenticated_main,
            "-m",
            "Adopt verified strict-zero main baseline on next",
        )
        .decode()
        .strip()
    )
    if not is_main_snapshot_bootstrap(repo, repository, base, head, authenticated_main):
        raise ValueError("prepared snapshot does not match authenticated main")
    result, _ = evaluate(
        repo,
        base,
        head,
        public=True,
        fetch=fetch,
        target_branch="next",
        policy_sha=authenticated_main,
        main_snapshot=authenticated_main,
        repository=repository,
    )
    if not all(check["state"] == "success" for check in result["checks"].values()):
        raise ValueError("main snapshot verification failed: " + json.dumps(result["checks"]))
    return cast(str, head)


def read_public_api(path: str) -> Any:
    # Reuse the local gh login without reading or printing its credential.
    output = subprocess.run(
        ["gh", "api", "--hostname", "github.com", "--method", "GET", path],
        capture_output=True,
        check=True,
        timeout=60,
    )
    return json.loads(output.stdout)


def prepare_next_baseline(repo: Path, repository: str, branch: str) -> dict[str, str]:
    """Authenticate public refs and create one new local review branch; never push."""
    if not report.REPOSITORY.fullmatch(repository) or not branch.startswith("codex/"):
        raise ValueError("expected a repository and a new codex/ review branch")
    report.git(repo, "check-ref-format", "--branch", branch)
    origin = report.git(repo, "remote", "get-url", "origin").decode().strip()
    if origin not in report.github_origin_urls(repository):
        raise ValueError("preparation requires the public repository as origin")
    root = f"repos/{repository}"
    metadata = read_public_api(root)
    if (
        metadata["private"]
        or metadata["default_branch"] != "main"
        or metadata["full_name"] != repository
    ):
        raise ValueError("preparation requires a public repository with default main")

    def ref(name: str) -> str:
        return cast(
            str,
            report.require_sha(read_public_api(f"{root}/git/ref/heads/{name}")["object"]["sha"]),
        )

    main, base = ref("main"), ref("next")
    report.git(
        repo,
        "fetch",
        "--quiet",
        "--no-tags",
        "origin",
        "+refs/heads/main:refs/remotes/origin/main",
        "+refs/heads/next:refs/remotes/origin/next",
    )
    for name, expected in (("main", main), ("next", base)):
        if (
            report.git(repo, "rev-parse", f"refs/remotes/origin/{name}").decode().strip()
            != expected
        ):
            raise ValueError("public refs changed during preparation; retry")
    head = prepare_main_snapshot(repo, repository, base, main, fetch=True)
    if ref("main") != main or ref("next") != base:
        raise ValueError("public refs changed during verification; retry")
    # Compare-and-create only. Existing review branches and working trees are preserved.
    report.git(repo, "update-ref", f"refs/heads/{branch}", head, "0" * 40)
    return {"head_sha": head, "base_sha": base, "main_sha": main, "branch": branch}


def main() -> int:
    if sys.argv[1:2] == ["select-policy"]:
        return cast(int, policy.main(sys.argv[1:]))
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("review-rules")
    prepare = commands.add_parser("prepare-next-baseline")
    prepare.add_argument("--repo", type=Path, required=True)
    prepare.add_argument("--repository", required=True)
    prepare.add_argument("--branch", required=True)
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
    local.add_argument("--target-branch", choices=sorted(report.TARGET_BRANCHES), default="main")
    github = commands.add_parser("github")
    github.add_argument("--repository", required=True)
    github.add_argument("--event-path", type=Path, required=True)
    github.add_argument("--trusted-sha", required=True)
    github.add_argument("--trusted-report-dir", type=Path)
    github.add_argument("--selected-policy-json", type=Path)
    for command in (local, github):
        command.add_argument("--repo", type=Path, required=True)
        command.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "review-rules":
        print(json.dumps(policy.HUMAN_REVIEW_RULES, separators=(",", ":")))
        return 0
    if args.command == "prepare-next-baseline":
        try:
            preparation = prepare_next_baseline(args.repo, args.repository, args.branch)
        except (ValueError, OSError, report.ReportError, subprocess.SubprocessError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(json.dumps(preparation, sort_keys=True))
        return 0
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
                args.repo,
                args.base,
                args.head,
                public=args.public,
                fetch=args.fetch,
                target_branch=args.target_branch,
            )
        else:
            result, patch = github_evaluate(
                args.repo,
                args.repository,
                json.loads(args.event_path.read_text()),
                args.trusted_sha,
                args.trusted_report_dir,
                json.loads(args.selected_policy_json.read_text())
                if args.selected_policy_json
                else None,
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
