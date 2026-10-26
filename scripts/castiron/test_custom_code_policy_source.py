# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
"""Current-main policy selection and review authorization regressions."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
import unittest.mock as mock  # noqa: PLR0402 - keep unittest imports consistent
from pathlib import Path
from typing import Any

import custom_code_budget as budget
import custom_code_policy as selector

REPO = "openai/example"


POLICY_SOURCE_ROOT = "repos/" + REPO
CANONICAL_POLICY_WORKFLOW = ".github/workflows/castiron-custom-code.yml"
CI_POLICY_WORKFLOW = ".github/workflows/ci.yml"


class PolicySourceWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:  # pyright: ignore[reportImplicitOverride]
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "objects"
        self.workflow_run: dict[str, Any] = {
            "id": 42,
            "workflow_id": 456,
            "repository": {"full_name": REPO},
            "head_sha": "a" * 40,
            "status": "completed",
            "event": "pull_request",
            "run_attempt": 3,
            "path": CANONICAL_POLICY_WORKFLOW + "@refs/pull/12/merge",
        }
        self.event: dict[str, Any] = {
            "repository": {"full_name": REPO},
            "workflow_run": copy.deepcopy(self.workflow_run),
        }
        self.branch = "next"
        self.select = self.start_patch(
            mock.patch.object(selector, "select_policy", return_value={"selected": True})
        )
        self.start_patch(mock.patch.object(selector.report, "api", side_effect=self.api))
        self.start_patch(
            mock.patch.object(selector.report, "current_pull", side_effect=self.current_pull)
        )
        self.start_patch(
            mock.patch.object(
                selector.report,
                "git",
                side_effect=self.git_result,
            )
        )

    def current_pull(self, *args: Any) -> tuple[int, str]:
        return 12, self.branch

    def git_result(self, repo: Path, *args: str) -> bytes:
        return b"b" * 40 if args[0] == "rev-parse" else b""

    def start_patch(self, patcher: Any) -> Any:
        result = patcher.start()
        self.addCleanup(patcher.stop)
        return result

    def api(self, method: str, path: str, *args: Any) -> Any:
        return {
            POLICY_SOURCE_ROOT: {"default_branch": "main"},
            POLICY_SOURCE_ROOT + "/actions/runs/42": self.workflow_run,
            POLICY_SOURCE_ROOT + "/actions/workflows/castiron-custom-code.yml": {
                "id": 456,
                "path": CANONICAL_POLICY_WORKFLOW,
            },
            POLICY_SOURCE_ROOT + "/actions/workflows/ci.yml": {
                "id": 456,
                "path": CI_POLICY_WORKFLOW,
            },
            POLICY_SOURCE_ROOT + "/git/ref/heads/main": {"object": {"sha": "c" * 40}},
            POLICY_SOURCE_ROOT + "/git/ref/heads/next": {"object": {"sha": "b" * 40}},
        }[path]

    def call(self, **kwargs: Any) -> dict[str, Any]:
        return selector.select_github_policy(self.repo, REPO, self.event, "c" * 40, **kwargs)

    def use_ci(self) -> None:
        self.workflow_run["path"] = CI_POLICY_WORKFLOW + "@refs/pull/12/merge"

    def test_lookalike_workflow_cannot_select_policy(self) -> None:
        self.workflow_run["path"] = CANONICAL_POLICY_WORKFLOW + "@evil.yml"
        self.workflow_run["workflow_id"] = 789
        with self.assertRaisesRegex(ValueError, "canonical workflow"):
            self.call()
        self.select.assert_not_called()

    def test_default_canonical_unchanged(self) -> None:
        self.branch = "main"
        self.assertEqual(self.call(), {"selected": True})

    def test_explicit_ci_uses_same_base_pin_selector(self) -> None:
        self.use_ci()
        self.assertEqual(self.call(source_workflow=CI_POLICY_WORKFLOW), {"selected": True})
        self.select.assert_called_once_with(
            self.repo,
            REPO,
            "next",
            "b" * 40,
            "a" * 40,
            "c" * 40,
            pull_heads=None,
            pull_numbers={"a" * 40: 12},
        )

    def test_candidate_event_cannot_select_ci_adapter(self) -> None:
        self.use_ci()
        self.event["source_workflow"] = CI_POLICY_WORKFLOW
        with self.assertRaisesRegex(ValueError, "source run"):
            self.call()
        self.select.assert_not_called()

    def test_unknown_workflow_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "source workflow"):
            self.call(source_workflow=".github/workflows/evil.yml")
        self.select.assert_not_called()

    def test_ci_adapter_cannot_retarget_main(self) -> None:
        self.use_ci()
        self.branch = "main"
        with self.assertRaisesRegex(ValueError, "restricted to next"):
            self.call(source_workflow=CI_POLICY_WORKFLOW)
        self.select.assert_not_called()

    def test_wrong_actual_workflow(self) -> None:
        with self.assertRaisesRegex(ValueError, "source run"):
            self.call(source_workflow=CI_POLICY_WORKFLOW)
        self.select.assert_not_called()

    def test_stale_or_mismatched_authenticated_identity(self) -> None:
        self.use_ci()
        for field, value in [
            ("head_sha", "d" * 40),
            ("run_attempt", 4),
            ("status", "in_progress"),
            ("event", "push"),
            ("repository", {"full_name": "attacker/example"}),
        ]:
            with self.subTest(field=field):
                old = self.workflow_run[field]
                self.workflow_run[field] = value
                with self.assertRaisesRegex(ValueError, "source run"):
                    self.call(source_workflow=CI_POLICY_WORKFLOW)
                self.workflow_run[field] = old
        self.select.assert_not_called()


class SelectorInterfaceTests(unittest.TestCase):
    def test_review_rules_cli_exports_the_canonical_predicate(self) -> None:
        import subprocess

        assert budget.__file__ is not None
        completed = subprocess.run(
            [sys.executable, "-I", budget.__file__, "review-rules"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(json.loads(completed.stdout), selector.HUMAN_REVIEW_RULES)

    def test_budget_cli_forwards_to_adjacent_selector(self) -> None:
        args = ["select-policy", "--repo", "objects", "--repository", REPO]
        with (
            mock.patch.object(sys, "argv", ["budget", *args]),
            mock.patch.object(budget.policy, "main", return_value=0) as select,
        ):
            self.assertEqual(budget.main(), 0)
        select.assert_called_once_with(args)

    def test_isolated_cli_loads_only_adjacent_modules(self) -> None:
        import subprocess

        for module in (budget, selector):
            assert module.__file__ is not None
            completed = subprocess.run(
                [sys.executable, "-I", module.__file__, "select-policy", "--help"],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("--source-workflow", completed.stdout)


if __name__ == "__main__":
    unittest.main()
