# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
# Regression tests for strict generated-file ownership.
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any, cast
from unittest import mock

import custom_code_budget as budget
import custom_code_report as report
from custom_code_test_support import GitTestCase


class StrictTests(GitTestCase):
    workflow = ".github/workflows/castiron-custom-code.yml"
    tooling_dir = "scripts/castiron"
    checker_path = f"{tooling_dir}/custom_code_budget.py"
    manifest_path = f"{tooling_dir}/generated-files.json"
    alternate_manifest_path = (
        "scripts/castiron/generated-files.json"
        if tooling_dir == "generated/castiron"
        else "generated/castiron/generated-files.json"
    )

    def setUp(self) -> None:  # pyright: ignore[reportImplicitOverride]
        super().setUp()
        self.write("generated.py", "generated\n")
        for path in budget.GENERATED_GITHUB_PATHS:
            self.write(path.decode(), "workflow\n")
        self.inventory(budget.GENERATED_GITHUB_PATHS)
        self.manifest()
        self.generated, _ = self.baseline()
        self.write(
            budget.POLICY,
            json.dumps(
                {"schema_version": 2, "generated_files": "strict", "max_custom_patch_lines": 0}
            ),
        )
        self.base = self.commit("enable strict ownership")

    def inventory(self, paths: frozenset[bytes]) -> None:
        # Checkpoint code is data. A verifier must never execute this statement.
        self.write(
            self.checker_path,
            "raise AssertionError('checkpoint code must not execute')\n"
            f"GENERATED_GITHUB_PATHS = frozenset({set(paths)!r})\n",
        )

    def manifest(self, extra: tuple[str, ...] = ()) -> None:
        files = {
            p: {
                "mode": "100644",
                "sha256": hashlib.sha256((self.repo / p).read_bytes()).hexdigest(),
            }
            for p in (
                "generated.py",
                *(path.decode() for path in budget.GENERATED_GITHUB_PATHS),
                self.checker_path,
                *extra,
            )
        }
        self.write(self.manifest_path, json.dumps({"schema_version": 1, "files": files}))

    def evaluate(self) -> dict[str, Any]:
        return budget.evaluate(self.repo, self.base, self.commit(), public=False)[0]

    def test_handwritten_change_passes(self) -> None:
        self.write("handwritten.py", "custom behavior\n")
        self.assertEqual(self.evaluate()["checks"]["budget"]["state"], "success")

    def test_strict_main_checks_migration_target_and_candidate(self) -> None:
        self.git("checkout", "-q", "-b", "next", self.base)
        self.write(budget.POLICY, '{"schema_version":1,"max_custom_patch_lines":1000}')
        target = self.commit("next still uses migration policy")
        self.write(self.workflow, "manual workflow edit\n")
        head = self.commit()
        for pull_heads in (None, [head]):
            with self.subTest(pull_heads=pull_heads):
                result, _ = budget.evaluate(
                    self.repo,
                    target,
                    head,
                    public=False,
                    policy_sha=self.base,
                    pull_heads=pull_heads,
                )
                self.assertEqual(result["total"], 0)
                self.assertEqual(result["checks"]["isolation"]["state"], "success")
                self.assertEqual(result["checks"]["budget"]["state"], "failure")
                self.assertIn(self.workflow, result["strict_violations"][0])

    def test_exact_main_snapshot_bootstrap_verifies_real_checkpoints(self) -> None:
        self.assert_exact_main_snapshot_bootstrap()

    def test_exact_main_snapshot_bootstrap_preserves_go_ratchet(self) -> None:
        self.assert_exact_main_snapshot_bootstrap(ratchet="go")

    def test_exact_main_snapshot_bootstrap_accepts_ssh_origin(self) -> None:
        self.assert_exact_main_snapshot_bootstrap(origin="git@github.com:openai/example.git")

    def test_next_preparation_rejects_wrong_origin_before_network(self) -> None:
        self.git("remote", "add", "origin", "https://github.com/attacker/example.git")
        for origin in (
            "https://github.com/attacker/example.git",
            "git@github.com:attacker/example.git",
            "https://github.com/openai/example-internal.git",
            "https://github.com.example.org/openai/example.git",
        ):
            with self.subTest(origin=origin), mock.patch.object(budget, "read_public_api") as api:
                self.git("remote", "set-url", "origin", origin)
                with self.assertRaisesRegex(ValueError, "public repository as origin"):
                    budget.prepare_next_baseline(self.repo, "openai/example", "codex/prepare")
                api.assert_not_called()

    def assert_exact_main_snapshot_bootstrap(
        self, ratchet: str | None = None, *, origin: str | None = None
    ) -> None:
        repository = "openai/example"
        self.git("remote", "add", "origin", origin or f"https://github.com/{repository}.git")

        def public_snapshot(generated: str, parent: str | None) -> str:
            stats = report.read_stats(self.repo, self.git("rev-parse", "HEAD"))
            return report.create_public_snapshot(
                self.repo,
                self.git("rev-parse", f"{generated}^{{tree}}"),
                stats["generation_id"],
                report.hash_codegen_commit(self.repo, generated),
                "codegen/test",
                parent,
            )

        old_public = public_snapshot(self.generated, None)
        stats_path = self.repo / ".castiron.stats.yml"
        stats_path.write_text(stats_path.read_text() + f"public_codegen_sha: {old_public}\n")
        self.write(budget.POLICY, '{"schema_version":1,"max_custom_patch_lines":4000}')
        self.write("generated.py", "legacy custom edit\n")
        legacy = self.commit("legacy unpinned next")
        self.write("generated.py", "generated\n")
        checker = self.repo / self.checker_path
        checker.write_text(checker.read_text() + "NEXT_POLICY_VERSION = 1\n")
        self.manifest()
        # Generated checkpoints exclude integration metadata and repository policy.
        stats_path.unlink()
        (self.repo / budget.POLICY).unlink()
        generated, _ = self.baseline()
        current_public = public_snapshot(generated, old_public)
        self.git("update-ref", "refs/remotes/origin/codegen/test", current_public)
        stats_path.write_text(stats_path.read_text() + f"public_codegen_sha: {current_public}\n")
        strict = {"schema_version": 2, "max_custom_patch_lines": 0, "generated_files": "strict"}
        if ratchet is not None:
            strict["ratchet"] = ratchet
        self.write(budget.POLICY, json.dumps(strict))
        main = self.commit("verified strict main")
        self.git("update-ref", "refs/remotes/origin/main", main)
        self.git("update-ref", "refs/remotes/origin/next", legacy)
        real_git = budget.report.git

        def offline_git(repo: Path, *args: str, **kwargs: Any) -> bytes:
            # Only network transport is mocked; refs, trees, metadata and verification are real Git.
            if args[0] == "fetch":
                for spec in args:
                    if spec.startswith("+refs/heads/"):
                        source, destination = spec[1:].split(":", 1)
                        revision = (
                            real_git(
                                repo,
                                "rev-parse",
                                source.replace("refs/heads/", "refs/remotes/origin/", 1),
                            )
                            .decode()
                            .strip()
                        )
                        real_git(repo, "update-ref", destination, revision)
                return b""
            return cast(bytes, real_git(repo, *args, **kwargs))

        def public_api(path: str) -> dict[str, Any]:
            if path == f"repos/{repository}":
                return {"private": False, "default_branch": "main", "full_name": repository}
            return {"object": {"sha": main if path.endswith("/main") else legacy}}

        original_index = self.git("write-tree")
        with (
            mock.patch.object(budget.report, "git", side_effect=offline_git),
            mock.patch.object(budget, "read_public_api", side_effect=public_api),
        ):
            prepared = budget.prepare_next_baseline(self.repo, repository, "codex/adopt-main")
        candidate = prepared["head_sha"]
        self.assertEqual(
            budget.read_policy(self.repo, candidate),
            {**strict, "next_policy": {"repository": repository, "main_sha": main}},
        )
        self.assertEqual(self.git("rev-parse", "refs/heads/codex/adopt-main"), candidate)
        self.assertEqual(self.git("write-tree"), original_index)
        self.assertEqual(self.git("rev-parse", "HEAD"), main)
        self.assertEqual(
            self.git("show", f"{candidate}:.castiron.stats.yml"),
            self.git("show", f"{main}:.castiron.stats.yml"),
        )
        refs_read = 0

        def moving_api(path: str) -> dict[str, Any]:
            nonlocal refs_read
            if path.endswith("/main"):
                refs_read += 1
                if refs_read > 1:
                    return {"object": {"sha": legacy}}
            return public_api(path)

        with (
            mock.patch.object(budget.report, "git", side_effect=offline_git),
            mock.patch.object(budget, "read_public_api", side_effect=moving_api),
            self.assertRaisesRegex(ValueError, "refs changed"),
        ):
            budget.prepare_next_baseline(self.repo, repository, "codex/stale-main")
        self.assertEqual(self.git("for-each-ref", "refs/heads/codex/stale-main"), "")
        self.git("checkout", "--detach", "-q", candidate)
        wrapper = self.git(
            "commit-tree",
            f"{candidate}^{{tree}}",
            "-p",
            legacy,
            "-p",
            candidate,
            "-m",
            "verified queue wrapper",
        )
        for heads in (None, [candidate]):
            with self.subTest(queue=heads is not None):
                result, _ = budget.evaluate(
                    self.repo,
                    legacy,
                    candidate if heads is None else wrapper,
                    public=True,
                    target_branch="next",
                    policy_sha=main,
                    main_snapshot=main,
                    repository=repository,
                    pull_heads=heads,
                )
                self.assertEqual(result["total"], 0)
                self.assertTrue(
                    all(c["state"] == "success" for c in result["checks"].values()), result
                )
        # Exercise the real hosted evaluator with independent, initially empty
        # object stores. The selector's origin/main ref is not shared with them.
        from test_custom_code_github import GitHubAPI

        remote = self.repo / "bootstrap-remote.git"
        self.git("clone", "--bare", str(self.repo), str(remote))
        real_git(remote, "update-ref", "refs/heads/main", main)
        real_git(remote, "update-ref", "refs/heads/codegen/test", current_public)
        real_git(remote, "update-ref", "refs/heads/queue", wrapper)
        named_fetches: list[Path] = []

        def transport(repo: Path, *args: str, **kwargs: Any) -> bytes:
            if args[0] == "fetch":
                self.assertIn("origin", args)
                if "+refs/heads/main:refs/remotes/origin/main" in args:
                    named_fetches.append(repo)
                args = tuple(str(remote) if arg == "origin" else arg for arg in args)
            self.assertNotIn("checkout", args)
            return cast(bytes, real_git(repo, *args, **kwargs))

        for mode in ("pr", "reused-pr", "queue", "moved-main"):
            with self.subTest(object_store=mode):
                queue = mode in ("queue", "moved-main")
                revision = wrapper if queue else candidate
                hosted_api = GitHubAPI(main, revision, "merge_group" if queue else "pull_request")
                hosted_api.next = legacy
                hosted_api.pull["base"]["ref"] = "next"
                if queue:
                    hosted_api.run["head_branch"] = "gh-readonly-queue/next/pr-3-test"
                objects = self.repo / f"bootstrap-{mode}.git"
                out = self.repo / f"bootstrap-{mode}-report"
                receipt = {
                    "schema_version": 1,
                    "target_branch": "next",
                    "base_sha": legacy,
                    "head_sha": revision,
                    "policy_sha": main,
                    "bootstrap": True,
                    "main_snapshot": main,
                }
                with (
                    mock.patch.object(report, "git", side_effect=transport),
                    mock.patch.object(budget.report, "git", side_effect=transport),
                    mock.patch.object(report, "api", side_effect=hosted_api),
                    mock.patch.object(budget.report, "api", side_effect=hosted_api),
                    mock.patch.object(
                        budget, "queued_entries", return_value=[(candidate, wrapper)]
                    ),
                ):
                    if mode == "reused-pr":
                        report.trusted_report(objects, repository, 123, 1, out, base=main)
                        self.assertEqual(
                            real_git(objects, "for-each-ref", "refs/remotes/origin/main"), b""
                        )
                    if mode == "moved-main":
                        # API receipt remains captured at main while Git's named
                        # ref changes before fetch: the evaluator must fail closed.
                        real_git(remote, "update-ref", "refs/heads/main", legacy)
                        with self.assertRaisesRegex(ValueError, "authenticated main changed"):
                            budget.github_evaluate(
                                objects,
                                repository,
                                {
                                    "repository": {"full_name": repository},
                                    "workflow_run": hosted_api.run,
                                },
                                main,
                                selection=receipt,
                            )
                    else:
                        result, _ = budget.github_evaluate(
                            objects,
                            repository,
                            {
                                "repository": {"full_name": repository},
                                "workflow_run": hosted_api.run,
                            },
                            main,
                            out if mode == "reused-pr" else None,
                            selection=receipt,
                        )
                        self.assertTrue(
                            all(c["state"] == "success" for c in result["checks"].values()), result
                        )
                        self.assertEqual(result["total"], 0)
                        self.assertEqual(
                            real_git(objects, "rev-parse", "refs/remotes/origin/main")
                            .decode()
                            .strip(),
                            main,
                        )
                    self.assertIn(objects, named_fetches)
                    self.assertFalse((objects / "scripts").exists())
        self.write("generated.py", "unauthorized custom edit\n")
        tampered = self.commit("tampered candidate")
        result, _ = budget.evaluate(
            self.repo,
            legacy,
            tampered,
            public=True,
            target_branch="next",
            policy_sha=main,
            main_snapshot=main,
            repository=repository,
        )
        self.assertEqual(result["checks"]["isolation"]["state"], "failure")
        self.assertEqual(result["checks"]["budget"]["state"], "failure")

    def test_activation_accepts_stale_pr_without_policy_edits(self) -> None:
        strict = (self.repo / budget.POLICY).read_text()
        self.git("checkout", "-q", "-b", "migration", f"{self.base}^")
        self.write(budget.POLICY, '{"schema_version":1,"max_custom_patch_lines":1000}')
        migration = self.commit("migration policy before activation")
        self.git("checkout", "-q", "-b", "stale", migration)
        self.write("handwritten.py", "custom behavior\n")
        stale = self.commit("PR predates strict activation")
        self.git("checkout", "-q", "migration")
        self.write(budget.POLICY, strict)
        activated = self.commit("activate strict policy")
        result, _ = budget.evaluate(self.repo, activated, stale, public=False)
        self.assertTrue(all(c["state"] == "success" for c in result["checks"].values()))
        self.git("merge", "--no-ff", "-m", "queue stale PR", stale)
        result, _ = budget.evaluate(
            self.repo,
            activated,
            self.git("rev-parse", "HEAD"),
            public=False,
            pull_heads=[stale],
        )
        self.assertTrue(all(c["state"] == "success" for c in result["checks"].values()))

    def test_stale_policy_edit_cannot_downgrade_activated_base(self) -> None:
        strict = (self.repo / budget.POLICY).read_text()
        self.git("checkout", "-q", "-b", "migration", f"{self.base}^")
        self.write(budget.POLICY, '{"schema_version":1,"max_custom_patch_lines":10}')
        migration = self.commit("migration policy before activation")
        self.git("checkout", "-q", "-b", "stale", migration)
        self.write(budget.POLICY, '{"schema_version":1,"max_custom_patch_lines":1000}')
        stale = self.commit("stale policy increase")
        self.git("checkout", "-q", "migration")
        self.write(budget.POLICY, strict)
        activated = self.commit("activate strict policy")
        result, _ = budget.evaluate(self.repo, activated, stale, public=False)
        self.assertEqual(result["checks"]["isolation"]["state"], "failure")
        self.assertIn("cannot be downgraded", result["checks"]["isolation"]["description"])

    def test_workflow_edit_fails_despite_zero_legacy_patch(self) -> None:
        self.write(self.workflow, "edited workflow\n")
        result = self.evaluate()
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["checks"]["budget"]["state"], "failure")
        self.assertIn(self.workflow, result["strict_violations"][0])

    def test_merge_queue_checks_combined_generated_ownership(self) -> None:
        self.git("checkout", "-q", "-b", "handwritten", self.base)
        self.write("handwritten.py", "custom behavior\n")
        handwritten = self.commit()
        self.git("checkout", "-q", "-b", "workflow", self.base)
        self.write(self.workflow, "manual workflow edit\n")
        workflow = self.commit()
        self.git("checkout", "-q", "-b", "queue", self.base)
        self.git("merge", "--no-ff", "-m", "queue handwritten", handwritten)
        passing, _ = budget.evaluate(
            self.repo,
            self.base,
            self.git("rev-parse", "HEAD"),
            public=False,
            pull_heads=[handwritten],
        )
        self.assertTrue(all(c["state"] == "success" for c in passing["checks"].values()))
        self.git("merge", "--no-ff", "-m", "queue workflow", workflow)
        failing, _ = budget.evaluate(
            self.repo,
            self.base,
            self.git("rev-parse", "HEAD"),
            public=False,
            pull_heads=[handwritten, workflow],
        )
        self.assertEqual(failing["total"], 0)
        self.assertEqual(failing["checks"]["isolation"]["state"], "success")
        self.assertEqual(failing["checks"]["budget"]["state"], "failure")
        self.assertIn(self.workflow, failing["strict_violations"][0])

    def test_content_deletion_rename_mode_and_symlink_fail(self) -> None:
        for mutation in ("edit", "delete", "rename", "mode", "symlink"):
            with self.subTest(mutation=mutation):
                self.git("reset", "--hard", self.base)
                path = self.repo / "generated.py"
                if mutation == "edit":
                    path.write_text("header removed and manually changed\n")
                elif mutation == "delete":
                    path.unlink()
                elif mutation == "rename":
                    path.rename(self.repo / "renamed.py")
                elif mutation == "mode":
                    path.chmod(0o755)
                else:
                    path.unlink()
                    path.symlink_to("handwritten.py")
                self.assertEqual(self.evaluate()["checks"]["budget"]["state"], "failure")

    def test_candidate_cannot_rewrite_its_manifest_or_disable_strict(self) -> None:
        self.write(self.workflow, "custom\n")
        self.manifest()
        self.write(budget.POLICY, json.dumps({"schema_version": 1, "max_custom_patch_lines": 1000}))
        result = self.evaluate()
        self.assertEqual(result["checks"]["isolation"]["state"], "failure")
        self.assertEqual(result["checks"]["budget"]["state"], "failure")

    def test_missing_manifest_cannot_activate(self) -> None:
        self.git("checkout", "-q", self.generated)
        (self.repo / self.manifest_path).unlink()
        checkpoint = self.commit(self.git("show", "-s", "--format=%B", self.generated))
        self.git("update-ref", "refs/remotes/origin/codegen/test", checkpoint)
        self.git("checkout", "-q", "main")
        stats = (self.repo / ".castiron.stats.yml").read_text()
        self.write(
            ".castiron.stats.yml",
            stats.replace(self.generated, checkpoint).replace(
                report.hash_codegen_commit(self.repo, self.generated),
                report.hash_codegen_commit(self.repo, checkpoint),
            ),
        )
        self.assertEqual(self.evaluate()["checks"]["budget"]["state"], "failure")

    def test_legitimate_new_generated_checkpoint_passes(self) -> None:
        self.git("checkout", "-q", self.generated)
        self.write("generated.py", "new generated output\n")
        self.write(self.workflow, "new generated workflow\n")
        self.manifest()
        checkpoint = self.commit(self.git("show", "-s", "--format=%B", self.generated))
        self.git("update-ref", "refs/remotes/origin/codegen/test", checkpoint)
        self.git("checkout", "-q", "main")
        for path in ("generated.py", self.workflow, self.manifest_path):
            self.write(path, self.git("show", f"{checkpoint}:{path}") + "\n")
        # Preserve exact manifest bytes (the fixture writes JSON without a newline).
        self.write(self.manifest_path, self.git("show", f"{checkpoint}:{self.manifest_path}"))
        stats = (self.repo / ".castiron.stats.yml").read_text()
        self.write(
            ".castiron.stats.yml",
            stats.replace(self.generated, checkpoint).replace(
                report.hash_codegen_commit(self.repo, self.generated),
                report.hash_codegen_commit(self.repo, checkpoint),
            ),
        )
        self.assertEqual(self.evaluate()["checks"]["budget"]["state"], "success")

    def test_worktree_verification_catches_uncommitted_edits(self) -> None:
        self.assertEqual(
            budget.verify_generated(self.repo, self.generated, self.base, worktree=True), []
        )
        self.write(self.workflow, "uncommitted\n")
        failures = budget.verify_generated(self.repo, self.generated, self.base, worktree=True)
        self.assertEqual(len(failures), 1)
        self.assertIn(self.workflow, failures[0])

    def test_activation_is_policy_only_and_checks_workflows(self) -> None:
        strict = (self.repo / budget.POLICY).read_text()
        self.write(budget.POLICY, '{"schema_version":1,"max_custom_patch_lines":1000}')
        migration = self.commit()
        self.write(budget.POLICY, strict)
        activation = self.commit()
        result, _ = budget.evaluate(self.repo, migration, activation, public=False)
        self.assertTrue(all(check["state"] == "success" for check in result["checks"].values()))
        self.write(self.workflow, "custom workflow\n")
        result, _ = budget.evaluate(self.repo, migration, self.commit(), public=False)
        self.assertTrue(all(check["state"] == "failure" for check in result["checks"].values()))

    def test_manifest_must_cover_snapshot_and_match_its_bytes(self) -> None:
        self.git("checkout", "-q", self.generated)
        manifest = json.loads((self.repo / self.manifest_path).read_text())
        manifest["files"].pop("generated.py")
        self.write(self.manifest_path, json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "cover.*exactly"):
            budget.generated_manifest(self.repo, self.commit())
        self.manifest()
        self.write("generated.py", "snapshot changed without updating manifest\n")
        with self.assertRaisesRegex(ValueError, "disagrees"):
            budget.generated_manifest(self.repo, self.commit())

    def test_relocated_tooling_preserves_ownership_and_retirement_checks(self) -> None:
        self.git("checkout", "--detach", "-q", self.generated)
        old_manifest = self.manifest_path
        new_manifest = self.alternate_manifest_path
        old_checker = self.checker_path
        new_checker = str(Path(new_manifest).with_name("custom_code_budget.py"))
        manifest = json.loads((self.repo / old_manifest).read_text())
        manifest["files"][new_checker] = manifest["files"].pop(old_checker)
        checker = (self.repo / old_checker).read_text()
        self.write(new_checker, checker)
        self.write(new_manifest, json.dumps(manifest))
        (self.repo / old_checker).unlink()
        (self.repo / old_manifest).unlink()
        relocated = self.commit("relocate generated tooling")
        self.assertEqual(
            budget.verify_generated(self.repo, relocated, relocated, previous=self.generated), []
        )
        ownership = budget.generated_manifest(self.repo, relocated)
        self.assertIn(new_manifest.encode(), ownership)
        self.assertIn(new_checker.encode(), ownership)
        self.assertNotIn(old_manifest.encode(), ownership)
        self.write(old_checker, checker)
        self.write("generated.py", "handwritten modification\n")
        failures = budget.verify_generated(
            self.repo, relocated, self.commit(), previous=self.generated
        )
        self.assertTrue(
            any(old_checker in failure and "retired" in failure for failure in failures)
        )
        self.assertTrue(any("generated.py: differs" in failure for failure in failures))
        # Candidate manifest edits cannot change the verified ownership contract.
        self.write(new_manifest, '{"schema_version": 1, "files": {}}')
        failures = budget.verify_generated(self.repo, relocated, self.commit())
        self.assertTrue(
            any(new_manifest in failure and "differs" in failure for failure in failures)
        )

    def test_checkpoint_rejects_ambiguous_manifest_locations(self) -> None:
        self.git("checkout", "--detach", "-q", self.generated)
        self.write(
            self.alternate_manifest_path,
            (self.repo / self.manifest_path).read_text(),
        )
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            budget.generated_manifest(self.repo, self.commit())

    def test_relocated_manifest_requires_colocated_checker_inventory(self) -> None:
        self.git("checkout", "--detach", "-q", self.generated)
        self.write(
            self.alternate_manifest_path,
            (self.repo / self.manifest_path).read_text(),
        )
        (self.repo / self.manifest_path).unlink()
        with self.assertRaisesRegex(ValueError, "missing its generated GitHub inventory"):
            budget.generated_manifest(self.repo, self.commit())

    def test_manifest_preserves_inherited_sdk_owned_github_files(self) -> None:
        self.git("checkout", "--detach", "-q", self.generated)
        inherited = (".github/workflows/ci.yml", ".github/actions/setup-go/action.yml")
        for path in inherited:
            self.write(path, "SDK-owned configuration\n")
        generated = self.commit("checkpoint preserves protected parent subtrees")
        manifest = budget.generated_manifest(self.repo, generated)
        for path in inherited:
            self.assertNotIn(path.encode(), manifest)
            self.write(path, "SDK-owned configuration update\n")
        head = self.commit("handwritten configuration remains outside generated ownership")
        self.assertEqual(budget.verify_generated(self.repo, generated, head), [])

    def test_private_manifest_checks_excluded_workflows_and_actions(self) -> None:
        self.assertIn(self.workflow.encode(), budget.GENERATED_GITHUB_PATHS)
        for path in (self.workflow, ".github/actions/generated/action.yml"):
            for mutation in ("omit", "content", "mode"):
                with (
                    self.subTest(path=path, mutation=mutation),
                    mock.patch.object(
                        budget,
                        "GENERATED_GITHUB_PATHS",
                        budget.GENERATED_GITHUB_PATHS | {path.encode()},
                    ),
                ):
                    self.git("checkout", "--detach", "-q", self.generated)
                    self.write(path, "generated workflow or action\n")
                    self.inventory(budget.GENERATED_GITHUB_PATHS)
                    self.manifest((path,))
                    manifest = json.loads((self.repo / self.manifest_path).read_text())
                    manifest["files"][path] = {
                        "mode": "100644",
                        "sha256": hashlib.sha256((self.repo / path).read_bytes()).hexdigest(),
                    }
                    if mutation == "omit":
                        del manifest["files"][path]
                    elif mutation == "content":
                        self.write(path, "unrecorded change\n")
                    else:
                        (self.repo / path).chmod(0o755)
                    self.write(self.manifest_path, json.dumps(manifest))
                    error = (
                        "omits generated GitHub inventory path"
                        if mutation == "omit"
                        else "disagrees"
                    )
                    with self.assertRaisesRegex(ValueError, error):
                        budget.generated_manifest(self.repo, self.commit())

    def test_checkpoint_inventory_can_add_and_retire_generated_ci(self) -> None:
        for path in (".github/workflows/new.yml", ".github/actions/new/action.yml"):
            with self.subTest(path=path):
                self.git("checkout", "--detach", "-q", self.generated)
                self.write(path, "new generated CI\n")
                self.inventory(budget.GENERATED_GITHUB_PATHS | {path.encode()})
                self.manifest((path,))
                newer = self.commit("new compiler inventory")
                # The executing verifier still has the old inventory.
                self.assertNotIn(path.encode(), budget.GENERATED_GITHUB_PATHS)
                self.assertEqual(
                    budget.verify_generated(self.repo, newer, newer, previous=self.generated), []
                )
                (self.repo / path).unlink()
                public = self.commit("public checkpoint omits private CI blob")
                self.assertEqual(
                    budget.verify_generated(self.repo, public, newer, previous=self.generated), []
                )
                # A newer verifier must also read the prior inventory to enforce retirement.
                self.assertEqual(
                    budget.verify_generated(self.repo, self.generated, self.base, previous=public),
                    [],
                )
                self.git("checkout", "--detach", "-q", self.base)
                self.write(path, "retired generated CI\n")
                failures = budget.verify_generated(
                    self.repo, self.generated, self.commit(), previous=public
                )
                self.assertTrue(
                    any(path in failure and "retired" in failure for failure in failures)
                )

    def test_manifest_cannot_claim_sdk_owned_workflows_or_actions(self) -> None:
        for path in (".github/workflows/ci.yml", ".github/actions/setup-go/action.yml"):
            for keep_blob in (True, False):
                with self.subTest(path=path, keep_blob=keep_blob):
                    self.git("checkout", "--detach", "-q", self.generated)
                    self.write(path, "SDK-owned configuration\n")
                    manifest = json.loads((self.repo / self.manifest_path).read_text())
                    manifest["files"][path] = {
                        "mode": "100644",
                        "sha256": hashlib.sha256((self.repo / path).read_bytes()).hexdigest(),
                    }
                    if not keep_blob:
                        (self.repo / path).unlink()
                    self.write(self.manifest_path, json.dumps(manifest))
                    with self.assertRaisesRegex(ValueError, "SDK-owned GitHub path"):
                        budget.generated_manifest(self.repo, self.commit())

    def test_public_snapshot_requires_every_inventory_identity(self) -> None:
        for path in (self.workflow, ".github/actions/generated/action.yml"):
            with self.subTest(path=path):
                self.git("checkout", "--detach", "-q", self.generated)
                self.write(path, "generated CI\n")
                self.inventory(budget.GENERATED_GITHUB_PATHS | {path.encode()})
                self.manifest((path,))
                (self.repo / path).unlink()
                manifest = json.loads((self.repo / self.manifest_path).read_text())
                del manifest["files"][path]
                self.write(self.manifest_path, json.dumps(manifest))
                with self.assertRaisesRegex(ValueError, "omits generated GitHub inventory path"):
                    budget.generated_manifest(
                        self.repo, self.commit("incomplete public checkpoint")
                    )

    def test_public_snapshot_keeps_strict_workflow_identity_without_private_blob(self) -> None:
        self.git("checkout", "--detach", "-q", self.generated)
        (self.repo / self.workflow).unlink()
        public = self.commit("sanitized public checkpoint")
        self.assertIn(self.workflow.encode(), budget.generated_manifest(self.repo, public))
        self.assertEqual(budget.verify_generated(self.repo, public, self.base), [])
        self.git("checkout", "--detach", "-q", self.base)
        self.write(self.workflow, "manual workflow edit\n")
        violations = budget.verify_generated(self.repo, public, self.commit())
        self.assertEqual(len(violations), 1)
        self.assertIn(self.workflow, violations[0])

    def test_generated_deletion_requires_removing_retired_file(self) -> None:
        self.git("checkout", "-q", self.generated)
        (self.repo / "generated.py").unlink()
        manifest = json.loads((self.repo / self.manifest_path).read_text())
        del manifest["files"]["generated.py"]
        self.write(self.manifest_path, json.dumps(manifest))
        new = self.commit()
        self.assertEqual(budget.verify_generated(self.repo, new, new, previous=self.generated), [])
        self.write("generated.py", "retained handwritten replacement\n")
        failures = budget.verify_generated(self.repo, new, self.commit(), previous=self.generated)
        self.assertEqual(len(failures), 1)
        self.assertIn("retired generated file", failures[0])

    def test_generated_file_can_become_a_directory(self) -> None:
        self.git("checkout", "-q", self.generated)
        (self.repo / "generated.py").unlink()
        self.write("generated.py/nested.py", "new generated file\n")
        manifest = json.loads((self.repo / self.manifest_path).read_text())
        del manifest["files"]["generated.py"]
        manifest["files"]["generated.py/nested.py"] = {
            "mode": "100644",
            "sha256": hashlib.sha256(b"new generated file\n").hexdigest(),
        }
        self.write(self.manifest_path, json.dumps(manifest))
        new = self.commit()
        for worktree in (False, True):
            with self.subTest(worktree=worktree):
                self.assertEqual(
                    budget.verify_generated(
                        self.repo, new, new, previous=self.generated, worktree=worktree
                    ),
                    [],
                )

    def test_compiler_entrypoint_preserves_failed_worktree(self) -> None:
        self.write(self.workflow, "uncommitted custom workflow\n")
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                str(Path(budget.__file__)),
                "verify-generated",
                "--repo",
                str(self.repo),
                "--policy-ref",
                self.base,
                "--generated",
                self.generated,
                "--head",
                self.base,
                "--worktree",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn(self.workflow, result.stderr)
        self.assertEqual((self.repo / self.workflow).read_text(), "uncommitted custom workflow\n")


if __name__ == "__main__":
    unittest.main()
