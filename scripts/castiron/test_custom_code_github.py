# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
"""Trusted GitHub evaluation with real local Git objects and an offline API."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

import custom_code_budget as budget
import custom_code_report as report
from custom_code_test_support import GENERATION, GitTestCase, source_run

REPOSITORY = "openai/example"


class GitHubAPI:
    """Mutable remote state; unexpected requests fail instead of reaching GitHub."""

    def __init__(self, base: str, head: str, event: str = "pull_request") -> None:
        self.main = base
        self.run = source_run(head, event)
        self.pull: dict[str, Any] = {
            "state": "open",
            "head": {"sha": head},
            "base": {"sha": base, "ref": "main", "repo": {"full_name": REPOSITORY}},
        }
        self.associations = [{"number": 3}]
        self.branches = [{"number": 3}]
        self.rules = [{"type": "merge_queue"}]
        self.bodies: list[str] = []

    def __call__(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        root = f"repos/{REPOSITORY}"
        if method == "POST" and path == f"{root}/issues/3/comments" and payload:
            self.bodies.append(payload["body"])
            return {"html_url": "published"}
        responses = {
            root: {"default_branch": "main", "private": False},
            f"{root}/actions/runs/123": self.run,
            f"{root}/pulls/3": self.pull,
            f"{root}/pulls/4": self.pull,
            f"{root}/git/ref/heads/main": {"object": {"sha": self.main}},
            f"{root}/rules/branches/main": self.rules,
            f"{root}/commits/{self.run['head_sha']}/pulls?per_page=100": self.associations,
            f"{root}/pulls?state=open&head=contributor%3Asdk&per_page=100&page=1": self.branches,
            f"{root}/issues/3/comments?per_page=100&page=1": [],
        }
        if method != "GET" or path not in responses:
            raise AssertionError(f"Unexpected GitHub request: {method} {path}")
        return responses[path]


class GitHubReportTests(GitTestCase):
    def test_trusted_report_recomputes_pr_output_in_a_bare_repository(self) -> None:
        generated, _ = self.baseline()
        content_hash = report.hash_codegen_commit(self.repo, generated)
        snapshot = report.create_public_snapshot(
            self.repo,
            self.git("rev-parse", f"{generated}^{{tree}}"),
            GENERATION,
            content_hash,
            "codegen/public-test",
            None,
        )
        self.git("branch", "codegen/public-test", snapshot)
        stats = (self.repo / ".castiron.stats.yml").read_text()
        self.write(".castiron.stats.yml", stats + f"public_codegen_sha: {snapshot}\n")
        self.write(budget.POLICY, json.dumps({"schema_version": 1, "max_custom_patch_lines": 10}))
        base = self.commit()
        legitimate, _ = report.build_report(self.repo, base, base, require_head_hash=True)
        self.write("generated.py", "generated\n# custom\n")
        self.write("scripts/castiron/custom_code_report.py", "raise RuntimeError('PR code ran')\n")
        self.write("report.json", json.dumps(legitimate))
        head = self.commit()
        self.write(
            ".castiron.stats.yml",
            (self.repo / ".castiron.stats.yml").read_text().replace(content_hash, "0" * 64),
        )
        broken = self.commit()
        remote = self.repo / "public.git"
        self.git("clone", "--bare", str(self.repo), str(remote))
        real_git = report.git

        def local_git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
            if args[:3] == ("remote", "add", "origin"):
                self.assertEqual(args[3], f"https://github.com/{REPOSITORY}.git")
                args = (*args[:3], str(remote))
            self.assertNotIn("checkout", args)
            return real_git(repo, *args, input_bytes=input_bytes)

        for label, revision, total in (
            ("baseline", base, 0),
            ("custom", head, 1),
            ("fork", head, 1),
            ("bad-hash", broken, None),
        ):
            with self.subTest(label=label):
                api = GitHubAPI(
                    "d" * 40, revision
                )  # PR metadata already differs from captured main.
                if label == "fork":
                    api.run["pull_requests"] = []
                    api.associations = []
                objects, out = self.repo / f"{label}.git", self.repo / f"{label}-report"
                with (
                    mock.patch.object(report, "api", side_effect=api),
                    mock.patch.object(budget.report, "api", side_effect=api),
                    mock.patch.object(report, "git", side_effect=local_git),
                ):
                    report.trusted_report(objects, REPOSITORY, 123, 1, out, base=base)
                    self.assertEqual(
                        real_git(objects, "rev-parse", "--is-bare-repository"), b"true\n"
                    )
                    self.assertFalse((objects / "scripts").exists())
                    self.assertEqual(api.bodies, [])
                    measured = json.loads((out / "report.json").read_text())
                    self.assertEqual(
                        (measured["target_base_sha"], measured["head_sha"]), (base, revision)
                    )
                    # Advance main before both budget evaluation and publication.
                    api.main = api.pull["base"]["sha"] = "e" * 40
                    result, _ = budget.github_evaluate(
                        objects,
                        REPOSITORY,
                        {"repository": {"full_name": REPOSITORY}, "workflow_run": api.run},
                        base,
                        out,
                    )
                    self.assertEqual((result["base_sha"], result["head_sha"]), (base, revision))
                    report.publish_comment(
                        measured, REPOSITORY, 3, 123, 1, artifact_run_id=9, artifact_run_attempt=3
                    )
                self.assertEqual(len(api.bodies), 1)
                body = api.bodies[0]
                self.assertIn("castiron:run:v1:123:1", body)
                self.assertIn(base, body)
                self.assertIn("/actions/runs/9", body)
                if total is None:
                    self.assertEqual(result["checks"]["budget"]["state"], "failure")
                    self.assertIn("could not verify", result["checks"]["budget"]["description"])
                    self.assertIn("codegen_hash mismatch", measured["error"])
                    self.assertIn("Report unavailable", body)
                    self.assertNotIn("Generated baselines verified", body)
                else:
                    self.assertEqual(result["total"], total)
                    self.assertEqual(result["checks"]["budget"]["state"], "success")
                    self.assertIn("Generated baselines verified", body)
                    self.assertIn("--name castiron-custom-code-9-3", body)
                    if total:
                        self.assertIn("1 newly customized", body)
                        self.assertIn("generated.py", body)
                        self.assertIn(b"+# custom", (out / "custom-code.patch").read_bytes())
                        self.assertNotIn("No new custom-code files detected", body)
                    else:
                        self.assertIn("No new custom-code files detected", body)

    def test_fork_association_fallback_paginates_candidates(self) -> None:
        run: dict[str, Any] = {
            "head_sha": "a" * 40,
            "pull_requests": [],
            "head_repository": {"owner": {"login": "contributor"}},
            "head_branch": "fix/branch&other=value",
        }
        first = [{"number": number} for number in range(1, 101)]
        with mock.patch.object(report, "api", side_effect=[[], first, [{"number": 101}]]) as api:
            self.assertEqual(len(report.associated_pulls("openai/example", run)), 101)
        self.assertEqual(
            api.call_args.args,
            (
                "GET",
                "repos/openai/example/pulls?state=open&head=contributor%3Afix%2Fbranch%26other%3Dvalue&per_page=100&page=2",
            ),
        )

    def test_trusted_report_rejects_invalid_or_stale_association_before_fetch(self) -> None:
        cases: dict[str, tuple[dict[str, Any], dict[str, Any], bool]] = {
            "wrong workflow": ({"path": "other.yml"}, {}, True),
            "unfinished run": ({"status": "in_progress"}, {}, True),
            "old attempt": ({"run_attempt": 2}, {}, False),
            "closed PR": ({}, {"state": "closed"}, False),
            "changed head": ({}, {"head": {"sha": "c" * 40}}, False),
            "other branch": (
                {},
                {"base": {"ref": "other", "repo": {"full_name": REPOSITORY}}},
                False,
            ),
            "other repository": (
                {},
                {"base": {"ref": "main", "repo": {"full_name": "other/repo"}}},
                False,
            ),
            "multiple PRs": ({"pull_requests": [{"number": 3}, {"number": 4}]}, {}, True),
        }
        for fallback in (False, True):
            for label, (run, pull, raises) in cases.items():
                with self.subTest(label=label, fallback=fallback):
                    api = GitHubAPI("b" * 40, "a" * 40)
                    api.run.update(run)
                    api.pull.update(pull)
                    if fallback:
                        api.branches = api.run["pull_requests"]
                        api.run["pull_requests"] = []
                        api.associations = []
                    with (
                        mock.patch.object(report, "api", side_effect=api),
                        mock.patch.object(report, "git") as git,
                    ):
                        if raises:
                            with self.assertRaises(report.ReportError):
                                report.trusted_report(
                                    self.repo / "objects",
                                    REPOSITORY,
                                    123,
                                    1,
                                    self.repo / "out",
                                    base="b" * 40,
                                )
                        else:
                            report.trusted_report(
                                self.repo / "objects",
                                REPOSITORY,
                                123,
                                1,
                                self.repo / "out",
                                base="b" * 40,
                            )
                        git.assert_not_called()
                        self.assertFalse((self.repo / "out").exists())
        api = GitHubAPI("b" * 40, "a" * 40)
        api.run["pull_requests"] = api.associations = api.branches = []
        with (
            mock.patch.object(report, "api", side_effect=api),
            mock.patch.object(report, "git") as git,
        ):
            report.trusted_report(
                self.repo / "objects", REPOSITORY, 123, 1, self.repo / "out", base="b" * 40
            )
            git.assert_not_called()

    def test_queue_membership_uses_synthetic_commit_not_original_pr_ancestry(self) -> None:
        generated, _ = self.baseline()
        self.git("branch", "codegen/test", generated)
        self.write(budget.POLICY, json.dumps({"schema_version": 1, "max_custom_patch_lines": 10}))
        base = self.commit("budget")
        self.git("checkout", "-q", "-b", "sdk", base)
        self.write("generated.py", "generated\ncustom\n")
        pr_head = self.commit()
        self.git("checkout", "-q", "-b", "queue", base)
        self.git("merge", "--squash", "sdk")
        queue_head = self.commit("synthetic queue commit")
        self.assertNotEqual(self.git("merge-base", pr_head, queue_head), pr_head)
        event = {
            "repository": {"full_name": "openai/example"},
            "workflow_run": source_run(queue_head, "merge_group"),
        }
        original_git = report.git

        def local_fetch(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
            if args[0] == "fetch":
                args = tuple(str(self.repo) if arg == "origin" else arg for arg in args)
            return original_git(repo, *args, input_bytes=input_bytes)

        with (
            tempfile.TemporaryDirectory() as temp,
            mock.patch.object(
                budget.report,
                "api",
                side_effect=[
                    {"default_branch": "main", "private": True},
                    source_run(queue_head, "merge_group"),
                    {"object": {"sha": base}},
                    [{"type": "merge_queue"}],
                ],
            ),
            mock.patch.object(budget, "queued_entries", return_value=[(pr_head, queue_head)]),
            mock.patch.object(
                budget.report,
                "git",
                side_effect=local_fetch,
            ),
        ):
            repo = Path(temp) / "queue.git"
            result, _ = budget.github_evaluate(repo, "openai/example", event, base)
            self.assertEqual(result["head_sha"], queue_head)
            self.assertEqual(result["checks"]["budget"]["state"], "success", result["checks"])
            self.assertEqual(result["total"], 1)
            self.assertEqual(
                [c["state"] for c in result["checks"].values()], ["success", "success"]
            )


class GitHubBudgetTests(unittest.TestCase):
    def setUp(self) -> None:  # pyright: ignore[reportImplicitOverride]
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo = self.root / "objects.git"
        self.base, self.head = "a" * 40, "b" * 40
        self.api = GitHubAPI(self.base, self.head)
        patch = mock.patch.object(budget.report, "api", side_effect=self.api)
        patch.start()
        self.addCleanup(patch.stop)

    def evaluate(self, *, trusted_report: Path | None = None) -> tuple[dict[str, Any], bytes]:
        event = {
            "repository": {"full_name": REPOSITORY},
            "workflow_run": source_run(self.head, self.api.run["event"]),
        }
        return budget.github_evaluate(self.repo, REPOSITORY, event, self.base, trusted_report)

    def test_merge_queue_rule_is_required_before_passing(self) -> None:
        self.api.run = source_run(self.head, "merge_group")
        self.api.rules = [{"type": "required_status_checks"}]
        with self.assertRaisesRegex(ValueError, "must require a merge queue"):
            self.evaluate()
        self.assertFalse(self.repo.exists())

    def test_wrong_or_superseded_source_runs_fail_before_fetching(self) -> None:
        for changes in (
            {"run_attempt": 2},
            {"status": "in_progress"},
            {"path": "other.yml"},
            {"head_sha": "c" * 40},
            {"repository": {"full_name": "wrong/repo"}},
        ):
            with self.subTest(changes=changes):
                self.api.run = {**source_run(self.head), **changes}
                with self.assertRaisesRegex(ValueError, "source workflow run"):
                    self.evaluate()
                self.assertFalse(self.repo.exists())

    def test_reuses_only_matching_main_job_report(self) -> None:
        self.api.main = self.api.pull["base"]["sha"] = "d" * 40
        self.repo.mkdir()
        (self.root / "custom-code.patch").write_bytes(b"verified patch")
        for stale in (None, "base", "head"):
            with self.subTest(stale=stale):
                measured = {
                    "target_base_sha": "c" * 40 if stale == "base" else self.base,
                    "head_sha": "c" * 40 if stale == "head" else self.head,
                }
                (self.root / "report.json").write_text(json.dumps(measured))
                with (
                    mock.patch.object(budget.report, "git", return_value=b"true\n"),
                    mock.patch.object(budget, "evaluate", return_value=({}, b"")) as evaluate,
                ):
                    if stale:
                        with self.assertRaisesRegex(ValueError, "trusted report does not match"):
                            self.evaluate(trusted_report=self.root)
                        evaluate.assert_not_called()
                    else:
                        self.evaluate(trusted_report=self.root)
                        self.assertEqual(evaluate.call_args.args, (self.repo, self.base, self.head))
                        self.assertEqual(
                            evaluate.call_args.kwargs["measurement"], (measured, b"verified patch")
                        )

    def test_queue_cannot_reuse_pr_measurement(self) -> None:
        self.api.run = source_run(self.head, "merge_group")
        with self.assertRaisesRegex(ValueError, "only PR runs can reuse"):
            self.evaluate(trusted_report=self.root)
        self.assertFalse(self.repo.exists())

    def test_evaluation_error_emits_failure_outputs_and_diagnostic_summary(self) -> None:
        event = self.root / "event.json"
        event.write_text(
            json.dumps({"repository": {"full_name": REPOSITORY}, "workflow_run": self.api.run})
        )
        output, result = self.root / "outputs", self.root / "result"
        self.api.rules = []  # Real validation failure, before any Git objects are fetched.
        args = [
            "budget",
            "github",
            "--repository",
            REPOSITORY,
            "--event-path",
            str(event),
            "--trusted-sha",
            self.base,
            "--repo",
            str(self.repo),
            "--out",
            str(result),
        ]
        with (
            mock.patch.object(sys, "argv", args),
            mock.patch.dict(os.environ, {"GITHUB_OUTPUT": str(output)}),
        ):
            self.assertEqual(budget.main(), 1)
        self.assertIn("isolation=failure\nbudget=failure\n", output.read_text())
        self.assertIn("must require a merge queue", (result / "summary.md").read_text())

    def test_queue_pagination(self) -> None:
        pages = [
            {
                "nodes": [
                    {"pullRequest": {"headRefOid": "a" * 40}, "headCommit": {"oid": "c" * 40}}
                ],
                "pageInfo": {"hasNextPage": True, "endCursor": "cursor"},
            },
            {
                "nodes": [
                    {"pullRequest": {"headRefOid": "b" * 40}, "headCommit": {"oid": "d" * 40}}
                ],
                "pageInfo": {"hasNextPage": False, "endCursor": None},
            },
        ]
        with mock.patch.object(
            budget.report,
            "api",
            side_effect=[{"data": {"repository": {"mergeQueue": {"entries": p}}}} for p in pages],
        ) as api:
            self.assertEqual(
                budget.queued_entries("openai/example", "main"),
                [("a" * 40, "c" * 40), ("b" * 40, "d" * 40)],
            )
        self.assertEqual(api.call_args_list[1].args[2]["variables"]["cursor"], "cursor")

    def test_queue_context_refuses_stale_checkout_before_fetching(self) -> None:
        self.api.run = source_run(self.head, "merge_group")
        self.api.main = "c" * 40
        with self.assertRaisesRegex(ValueError, "trusted checkout is stale"):
            self.evaluate()
        self.assertFalse(self.repo.exists())

    def test_github_uses_fresh_bare_data_repo_and_checks_current_head(self) -> None:
        self.api.run["pull_requests"] = self.api.associations = []
        self.api.pull["base"]["sha"] = "c" * 40
        with (
            mock.patch.object(budget.report, "git") as git,
            mock.patch.object(budget, "evaluate", return_value=({}, b"")) as evaluate,
        ):
            self.evaluate()
            self.assertTrue((self.repo / "HEAD").exists())
            self.assertFalse((self.repo / "src").exists())
            self.assertIn(
                mock.call(
                    self.repo, "fetch", "--quiet", "--no-tags", "origin", self.base, self.head
                ),
                git.call_args_list,
            )
            evaluate.assert_called_once_with(
                self.repo,
                self.base,
                self.head,
                public=True,
                fetch=True,
                pull_heads=None,
                measurement=None,
            )

    def test_stale_pull_and_wrong_target_fail_before_objects_created(self) -> None:
        original = self.api.pull
        self.api.run["pull_requests"] = self.api.associations = []
        for changes in (
            {"head": {"sha": "c" * 40}},
            {"base": {**original["base"], "repo": {"full_name": "wrong/repo"}}},
            {"base": {**original["base"], "ref": "other"}},
            {"state": "closed"},
        ):
            with self.subTest(changes=changes):
                self.api.pull = {**original, **changes}
                with self.assertRaisesRegex(ValueError, "exactly one current PR"):
                    self.evaluate()
                self.assertFalse(self.repo.exists())


if __name__ == "__main__":
    unittest.main()
