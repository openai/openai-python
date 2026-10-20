# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
# Regression tests for the custom-code budget.
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

import custom_code_budget as budget
import custom_code_report as report
from custom_code_test_support import GitTestCase


class BudgetTests(GitTestCase):
    def setUp(self) -> None:  # pyright: ignore[reportImplicitOverride]
        super().setUp()
        self.generated, _ = self.baseline()
        self.policy(10)
        self.base = self.commit("human-owned budget")

    def policy(self, limit: int) -> None:
        self.write(
            budget.POLICY, json.dumps({"schema_version": 1, "max_custom_patch_lines": limit}) + "\n"
        )

    def evaluate(self, head: str, base: str | None = None, **kwargs: Any) -> dict[str, Any]:
        return budget.evaluate(self.repo, base or self.base, head, public=False, **kwargs)[0]

    def test_additions_and_deletions_do_not_cancel(self) -> None:
        self.write("generated.py", "replacement\n")
        result = self.evaluate(self.commit())
        self.assertEqual((result["additions"], result["deletions"], result["total"]), (1, 1, 2))
        self.assertEqual(result["checks"]["budget"]["state"], "success")

    def test_below_equal_and_above_limit(self) -> None:
        for additions in (9, 10, 11):
            with self.subTest(additions=additions):
                self.write("generated.py", "generated\n" + "custom\n" * additions)
                result = self.evaluate(self.commit())
                self.assertEqual(result["total"], additions)
                self.assertEqual(
                    result["checks"]["budget"]["state"], "failure" if additions > 10 else "success"
                )

    def test_whole_generated_file_deletion_is_counted(self) -> None:
        (self.repo / "generated.py").unlink()
        result = self.evaluate(self.commit())
        self.assertEqual((result["additions"], result["deletions"]), (0, 1))
        self.assertEqual(result["mixed_files"], 1)

    def test_restoring_generated_content_removes_customization(self) -> None:
        self.write("generated.py", "generated\ncustom\n")
        customized = self.commit()
        self.write("generated.py", "generated\n")
        result = self.evaluate(self.commit(), base=customized)
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["mixed_files"], 0)

    def test_handwritten_only_files_keep_existing_report_scope(self) -> None:
        self.write("handwritten.py", "custom\n" * 100)
        self.assertEqual(self.evaluate(self.commit())["total"], 0)

    def test_increase_is_isolated_but_does_not_apply_to_itself(self) -> None:
        self.policy(20)
        result = self.evaluate(self.commit())
        self.assertEqual(result["checks"]["isolation"]["state"], "success")
        self.assertEqual(result["limit"], 10)
        self.assertEqual(result["checked_limit"], 10)

    def test_entire_pr_must_be_budget_only_not_just_latest_commit(self) -> None:
        self.write("generated.py", "generated\n" + "custom\n" * 11)
        self.commit("SDK change first")
        self.policy(100)
        result = self.evaluate(self.commit("budget-only last commit"))
        self.assertEqual(result["checks"]["isolation"]["state"], "failure")
        self.assertIn("separate, budget-only PR", result["checks"]["isolation"]["description"])
        self.assertEqual(result["checks"]["budget"]["state"], "failure")
        self.assertEqual(result["limit"], 10)

    def test_new_base_budget_is_used_for_stale_pr_branch(self) -> None:
        self.git("checkout", "-q", "-b", "sdk", self.base)
        self.write("generated.py", "generated\n" + "custom\n" * 11)
        head = self.commit()
        self.git("checkout", "-q", "main")
        self.policy(20)
        new_base = self.commit("separate approved increase")
        result = self.evaluate(head, base=new_base)
        self.assertEqual(result["limit"], 20)
        self.assertEqual(result["checks"]["isolation"]["state"], "success")
        self.assertEqual(result["checks"]["budget"]["state"], "success")

    def test_next_uses_main_policy_and_target_diff_independently(self) -> None:
        self.git("checkout", "-q", "-b", "next", self.base)
        self.policy(100)
        target = self.commit("next carries a different policy")
        self.write("generated.py", "generated\n" + "custom\n" * 11)
        head = self.commit("next change")
        result = self.evaluate(head, base=target, policy_sha=self.base)
        self.assertEqual(result["base_sha"], target)
        self.assertEqual(result["policy_sha"], self.base)
        self.assertEqual(result["checks"]["isolation"]["state"], "success")
        self.assertEqual(result["checks"]["budget"]["state"], "failure")
        self.assertEqual(result["limit"], 10)
        self.git("checkout", "-q", "main")
        self.policy(20)
        policy = self.commit("approved main policy")
        result = self.evaluate(head, base=target, policy_sha=policy)
        self.assertEqual(result["checks"]["budget"]["state"], "success")
        self.policy(1)
        policy = self.commit("main lowers policy after PR passed")
        result = self.evaluate(head, base=target, policy_sha=policy, pull_heads=[head])
        self.assertEqual(result["checks"]["budget"]["state"], "failure")
        self.assertEqual(result["limit"], 1)

    def test_decrease_must_fit_current_usage(self) -> None:
        self.write("generated.py", "generated\ncustom\ncustom\n")
        base = self.commit()
        self.policy(1)
        result = self.evaluate(self.commit(), base=base)
        self.assertEqual(result["checks"]["isolation"]["state"], "success")
        self.assertEqual(result["checks"]["budget"]["state"], "failure")
        self.assertEqual(result["checked_limit"], 1)

    def test_missing_base_policy_fails_closed(self) -> None:
        (self.repo / budget.POLICY).unlink()
        base = self.commit()
        self.policy(100)
        result = self.evaluate(self.commit(), base=base)
        self.assertTrue(all(c["state"] == "failure" for c in result["checks"].values()))

    def test_policy_deletion_rename_symlink_and_mode_change_fail(self) -> None:
        for change in ("delete", "rename", "symlink", "executable"):
            with self.subTest(change=change):
                self.git("checkout", "--detach", "-q", self.base)
                path = self.repo / budget.POLICY
                if change == "delete":
                    path.unlink()
                elif change == "rename":
                    path.rename(self.repo / "renamed.json")
                elif change == "symlink":
                    path.unlink()
                    path.symlink_to("generated.py")
                else:
                    path.chmod(0o755)
                result = self.evaluate(self.commit())
                self.assertEqual(result["checks"]["isolation"]["state"], "failure")

    def test_invalid_policy_values_fail(self) -> None:
        invalid = [
            "[]",
            "{}",
            "not json",
            '{"schema_version":1,"max_custom_patch_lines":true}',
            '{"schema_version":true,"max_custom_patch_lines":10}',
            '{"schema_version":2,"max_custom_patch_lines":10}',
            '{"schema_version":1,"max_custom_patch_lines":-1}',
            '{"schema_version":1,"max_custom_patch_lines":10.5}',
            '{"schema_version":1,"max_custom_patch_lines":null}',
            '{"schema_version":1,"max_custom_patch_lines":10,"mode":"report-only"}',
            '{"schema_version":1,"max_custom_patch_lines":10,"max_custom_patch_lines":999}',
            " " * 4097,
        ]
        for contents in invalid:
            with self.subTest(contents=contents[:100]):
                self.write(budget.POLICY, contents)
                result = self.evaluate(self.commit())
                self.assertEqual(result["checks"]["isolation"]["state"], "failure")

    def test_bad_snapshot_and_binary_change_fail_budget(self) -> None:
        self.write("generated.py", "binary\0content")
        result = self.evaluate(self.commit())
        self.assertIn("non-text", result["checks"]["budget"]["description"])
        self.write("generated.py", "generated\n")
        path = self.repo / ".castiron.stats.yml"
        path.write_text(
            path.read_text().replace(
                budget.report.hash_codegen_commit(self.repo, self.generated), "f" * 64
            )
        )
        result = self.evaluate(self.commit())
        self.assertIn("codegen_hash mismatch", result["checks"]["budget"]["description"])

    def test_budget_uses_existing_reporter_with_strict_verification(self) -> None:
        with mock.patch.object(
            budget.report, "build_report", wraps=budget.report.build_report
        ) as measured:
            self.evaluate(self.base)
        self.assertEqual(
            measured.call_args.kwargs, {"public": False, "fetch": False, "require_head_hash": True}
        )

    def test_queue_isolates_prs_but_uses_main_budget_for_combined_tree(self) -> None:
        self.git("checkout", "-q", "-b", "policy", self.base)
        self.policy(100)
        policy_head = self.commit()
        self.git("checkout", "-q", "-b", "sdk", self.base)
        self.write("generated.py", "generated\n" + "custom\n" * 11)
        sdk_head = self.commit()
        self.git("checkout", "-q", "-b", "queue", self.base)
        self.git("merge", "--no-ff", "-m", "queue policy", policy_head)
        self.git("merge", "--no-ff", "-m", "queue SDK", sdk_head)
        result = self.evaluate(self.git("rev-parse", "HEAD"), pull_heads=[policy_head, sdk_head])
        self.assertEqual(result["checks"]["isolation"]["state"], "success")
        self.assertEqual(result["checks"]["budget"]["state"], "failure")
        self.assertEqual(result["limit"], 10)

    def test_queue_without_verified_members_fails(self) -> None:
        self.assertEqual(
            self.evaluate(self.base, pull_heads=[])["checks"]["isolation"]["state"], "failure"
        )

    def test_cli_executes_trusted_reporter_not_inspected_repo(self) -> None:
        self.write(
            "scripts/castiron/custom_code_report.py", 'raise RuntimeError("PR CODE EXECUTED")\n'
        )
        self.write("sitecustomize.py", 'raise RuntimeError("PR IMPORTED")\n')
        head = self.commit()
        out = self.repo / "result"
        command = [
            sys.executable,
            "-I",
            str(Path(budget.__file__).resolve()),
            "check",
            "--repo",
            str(self.repo),
            "--base",
            self.base,
            "--head",
            head,
            "--out",
            str(out),
        ]
        completed = subprocess.run(
            command, cwd=self.repo, capture_output=True, text=True, check=False
        )
        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        self.assertEqual(json.loads((out / "budget.json").read_text())["total"], 0)

    def test_summary_has_counts_revisions_and_no_longer_generated(self) -> None:
        self.write("generated.py", "replacement\n")
        result = self.evaluate(self.commit())
        out = self.repo / "report-output"
        budget.write_result(out, result)
        summary = (out / "summary.md").read_text()
        self.assertIn("+1 / -1 = 2", summary)
        self.assertIn(self.generated, summary)
        self.assertIn(self.base, summary)
        self.assertIn("human approving review", summary)


class InventoryTests(unittest.TestCase):
    def test_literal_inventory_is_data_not_executable_code(self) -> None:
        source = (
            b"raise AssertionError('must not execute')\n"
            b"GENERATED_GITHUB_PATHS = frozenset({b'.github/workflows/generated.yml'})\n"
        )
        self.assertEqual(
            budget.checkpoint_github_inventory(source),
            frozenset({b".github/workflows/generated.yml"}),
        )
        self.assertEqual(
            budget.checkpoint_github_inventory(b"GENERATED_GITHUB_PATHS = frozenset({})"),
            frozenset(),
        )

    def test_inventory_rejects_missing_ambiguous_and_nonliteral_values(self) -> None:
        for source in (
            b"pass",
            b"GENERATED_GITHUB_PATHS = frozenset({})\nGENERATED_GITHUB_PATHS = frozenset({})",
            b"GENERATED_GITHUB_PATHS = __import__('os').environ",
            b"GENERATED_GITHUB_PATHS = frozenset(__import__('os').environ)",
            b"GENERATED_GITHUB_PATHS = frozenset({'text'})",
            b"GENERATED_GITHUB_PATHS = frozenset({b'not-github'})",
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                budget.checkpoint_github_inventory(source)


class StrictTests(GitTestCase):
    workflow = ".github/workflows/castiron-custom-code.yml"

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
            "scripts/castiron/custom_code_budget.py",
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
                "scripts/castiron/custom_code_budget.py",
                *extra,
            )
        }
        self.write(budget.MANIFEST.decode(), json.dumps({"schema_version": 1, "files": files}))

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
        (self.repo / budget.MANIFEST.decode()).unlink()
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
        for path in ("generated.py", self.workflow, budget.MANIFEST.decode()):
            self.write(path, self.git("show", f"{checkpoint}:{path}") + "\n")
        # Preserve exact manifest bytes (the fixture writes JSON without a newline).
        self.write(
            budget.MANIFEST.decode(), self.git("show", f"{checkpoint}:{budget.MANIFEST.decode()}")
        )
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
        manifest = json.loads((self.repo / budget.MANIFEST.decode()).read_text())
        manifest["files"].pop("generated.py")
        self.write(budget.MANIFEST.decode(), json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "cover.*exactly"):
            budget.generated_manifest(self.repo, self.commit())
        self.manifest()
        self.write("generated.py", "snapshot changed without updating manifest\n")
        with self.assertRaisesRegex(ValueError, "disagrees"):
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
                    manifest = json.loads((self.repo / budget.MANIFEST.decode()).read_text())
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
                    self.write(budget.MANIFEST.decode(), json.dumps(manifest))
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
                    budget.verify_generated(self.repo, self.generated, self.base, previous=public), []
                )
                self.git("checkout", "--detach", "-q", self.base)
                self.write(path, "retired generated CI\n")
                failures = budget.verify_generated(
                    self.repo, self.generated, self.commit(), previous=public
                )
                self.assertTrue(any(path in failure and "retired" in failure for failure in failures))

    def test_manifest_cannot_claim_sdk_owned_workflows_or_actions(self) -> None:
        for path in (".github/workflows/ci.yml", ".github/actions/setup-go/action.yml"):
            for keep_blob in (True, False):
                with self.subTest(path=path, keep_blob=keep_blob):
                    self.git("checkout", "--detach", "-q", self.generated)
                    self.write(path, "SDK-owned configuration\n")
                    manifest = json.loads((self.repo / budget.MANIFEST.decode()).read_text())
                    manifest["files"][path] = {
                        "mode": "100644",
                        "sha256": hashlib.sha256((self.repo / path).read_bytes()).hexdigest(),
                    }
                    if not keep_blob:
                        (self.repo / path).unlink()
                    self.write(budget.MANIFEST.decode(), json.dumps(manifest))
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
                manifest = json.loads((self.repo / budget.MANIFEST.decode()).read_text())
                del manifest["files"][path]
                self.write(budget.MANIFEST.decode(), json.dumps(manifest))
                with self.assertRaisesRegex(ValueError, "omits generated GitHub inventory path"):
                    budget.generated_manifest(self.repo, self.commit("incomplete public checkpoint"))

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
        manifest = json.loads((self.repo / budget.MANIFEST.decode()).read_text())
        del manifest["files"]["generated.py"]
        self.write(budget.MANIFEST.decode(), json.dumps(manifest))
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
        manifest = json.loads((self.repo / budget.MANIFEST.decode()).read_text())
        del manifest["files"]["generated.py"]
        manifest["files"]["generated.py/nested.py"] = {
            "mode": "100644",
            "sha256": hashlib.sha256(b"new generated file\n").hexdigest(),
        }
        self.write(budget.MANIFEST.decode(), json.dumps(manifest))
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
