# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
# Regression tests for the custom-code budget.
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

import custom_code_budget as budget
from custom_code_test_support import GitTestCase


class GoRatchetTests(GitTestCase):
    def prepare(self, *, inherited_ci: bool = False) -> str:
        if inherited_ci:
            self.write(".github/actions/check/main.go", "package main\n")
        self.baseline()
        self.policy()
        return self.commit("activate Go ratchet")

    def policy(self, *, active: bool = True, limit: int = 2000) -> None:
        value: dict[str, Any] = {"schema_version": 1, "max_custom_patch_lines": limit}
        if active:
            value["ratchet"] = "go"
        self.write(budget.POLICY, json.dumps(value) + "\n")

    def evaluate(self, base: str, head: str, **kwargs: Any) -> dict[str, Any]:
        return budget.evaluate(self.repo, base, head, public=False, **kwargs)[0]

    def test_handwritten_helpers_tests_comments_and_nested_modules_count(self) -> None:
        base = self.prepare()
        for path in (
            "helper.go",
            "helper_test.go",
            "nested/module/helper.go",
            ".github/workflows/check.go",
        ):
            with self.subTest(path=path):
                self.git("checkout", "--detach", "-q", base)
                self.write(path, "// comment\n\npackage example\n// final line")
                result = self.evaluate(base, self.commit())
                self.assertEqual(result["checks"]["budget"]["state"], "failure")
                self.assertEqual(result["ratchet"]["delta"], 4)
                self.assertEqual(
                    result["ratchet"]["after"]["handwritten_files"], [{"path": path, "lines": 4}]
                )

    def test_inherited_private_checkpoint_ci_is_handwritten(self) -> None:
        base = self.prepare(inherited_ci=True)
        self.write(".github/actions/check/main.go", "package main\n// added\n")
        result = self.evaluate(base, self.commit())
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["ratchet"]["before"]["handwritten_lines"], 1)
        self.assertEqual(result["ratchet"]["delta"], 1)
        self.assertEqual(
            result["ratchet"]["after"]["handwritten_files"],
            [{"path": ".github/actions/check/main.go", "lines": 2}],
        )
        self.assertEqual(result["checks"]["budget"]["state"], "failure")

    def test_patch_reduction_can_pay_for_handwritten_lines(self) -> None:
        self.prepare()
        self.write("generated.py", "generated\ncustom\ncustom\n")
        base = self.commit()
        self.write("generated.py", "generated\n")
        self.write("helper.go", "package example\n")
        result = self.evaluate(base, self.commit())
        self.assertEqual(result["ratchet"]["delta"], -1)
        self.assertEqual(result["checks"]["budget"]["state"], "success")

    def test_stale_branch_cannot_reclaim_landed_reduction(self) -> None:
        self.prepare()
        self.write("helper.go", "package example\n// old allowance\n")
        old = self.commit()
        self.git("checkout", "-q", "-b", "stale")
        head = self.commit()
        self.git("checkout", "-q", "main")
        self.write("helper.go", "package example\n")
        base = self.commit()
        self.assertEqual(self.git("merge-base", base, head), old)
        result = self.evaluate(base, head)
        self.assertEqual(result["ratchet"]["before"]["revision"], base)
        self.assertEqual(result["ratchet"]["delta"], 1)
        self.assertEqual(result["checks"]["budget"]["state"], "failure")

    def test_complete_merge_queue_candidate_is_counted(self) -> None:
        base = self.prepare()
        constituent = self.commit("empty constituent")
        self.write("helper.go", "package example\n")
        result = self.evaluate(base, self.commit("combined queue"), pull_heads=[constituent])
        self.assertEqual(result["checks"]["isolation"]["state"], "success")
        self.assertEqual(result["checks"]["budget"]["state"], "failure")

    def test_ratchet_cannot_be_disabled(self) -> None:
        base = self.prepare()
        self.policy(active=False)
        result = self.evaluate(base, self.commit())
        for name in ("budget", "isolation"):
            self.assertEqual(result["checks"][name]["state"], "failure")
            self.assertIn("cannot be disabled", result["checks"][name]["description"])

    def test_old_ceiling_increase_cannot_restore_ratchet_headroom(self) -> None:
        self.prepare()
        self.policy(limit=3000)
        base = self.commit("separately reviewed ceiling increase")
        self.write("helper.go", "package example\n")
        result = self.evaluate(base, self.commit())
        self.assertEqual(result["limit"], 3000)
        self.assertEqual(result["checks"]["budget"]["state"], "failure")

    def test_fixed_patch_ceiling_remains_independent(self) -> None:
        self.prepare()
        self.policy(limit=1)
        self.write("helper.go", "package example\n// two\n// three\n")
        base = self.commit()
        (self.repo / "helper.go").unlink()
        self.write("generated.py", "generated\ncustom\ncustom\n")
        result = self.evaluate(base, self.commit())
        self.assertEqual(result["ratchet"]["delta"], -1)
        self.assertEqual(result["checks"]["budget"]["state"], "failure")

    def test_nontext_and_symlink_go_fail_closed(self) -> None:
        base = self.prepare()
        for content in (b"package example\0", b"\xff", None):
            with self.subTest(content=content):
                self.git("checkout", "--detach", "-q", base)
                path = self.repo / "helper.go"
                if content is None:
                    path.symlink_to("generated.py")
                else:
                    path.write_bytes(content)
                result = self.evaluate(base, self.commit())
                self.assertEqual(result["checks"]["budget"]["state"], "failure")

    def test_live_target_snapshot_hash_is_verified(self) -> None:
        self.prepare()
        self.git("checkout", "-q", "-b", "candidate")
        head = self.commit()
        self.git("checkout", "-q", "main")
        stats = self.repo / ".castiron.stats.yml"
        stats.write_text(stats.read_text().replace("codegen_hash: ", "codegen_hash: bad"))
        result = self.evaluate(self.commit(), head)
        self.assertEqual(result["checks"]["budget"]["state"], "failure")

    def test_activation_must_be_policy_only(self) -> None:
        self.prepare()
        self.policy(active=False)
        base = self.commit()
        self.policy()
        head = self.commit()
        result = self.evaluate(base, head)
        self.assertTrue(all(check["state"] == "success" for check in result["checks"].values()))
        self.write("helper.go", "package example\n")
        result = self.evaluate(base, self.commit())
        self.assertEqual(result["checks"]["isolation"]["state"], "failure")
        self.assertEqual(result["checks"]["budget"]["state"], "failure")


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
            measured.call_args.kwargs,
            {"public": False, "fetch": False, "require_head_hash": True, "target_branch": "main"},
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


if __name__ == "__main__":
    unittest.main()
