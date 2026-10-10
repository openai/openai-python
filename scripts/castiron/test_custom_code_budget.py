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
        completed = subprocess.run(command, cwd=self.repo, capture_output=True, text=True, check=False)
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


if __name__ == "__main__":
    unittest.main()
