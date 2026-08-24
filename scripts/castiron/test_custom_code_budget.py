# Regression tests for the custom-code budget.
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, cast
from unittest import mock

import custom_code_budget as budget
import test_custom_code_report as fixtures


def source_run(head: str, event: str = "pull_request") -> dict[str, Any]:
    return {
        "id": 123,
        "event": event,
        "head_sha": head,
        "head_branch": "gh-readonly-queue/main/pr-7-example" if event == "merge_group" else "sdk",
        "repository": {"full_name": "openai/example"},
        "path": ".github/workflows/castiron-custom-code.yml",
        "status": "completed",
        "run_attempt": 1,
        "pull_requests": [{"number": 3}] if event == "pull_request" else [],
        "conclusion": "failure",  # The candidate's result is deliberately ignored.
    }


class BudgetTests(unittest.TestCase):
    def setUp(self) -> None:  # pyright: ignore[reportImplicitOverride]
        # Reuse the reporter's real Git/checkpoint fixture without inheriting its tests.
        self.fixture = fixtures.CustomCodeTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo = self.fixture.repo
        self.generated, _ = self.fixture.baseline()
        self.policy(10)
        self.base = self.fixture.commit("human-owned budget")

    def policy(self, limit: int) -> None:
        self.fixture.write(
            budget.POLICY, json.dumps({"schema_version": 1, "max_custom_patch_lines": limit}) + "\n"
        )

    def evaluate(self, head: str, base: str | None = None, **kwargs: Any) -> dict[str, Any]:
        return budget.evaluate(self.repo, base or self.base, head, public=False, **kwargs)[0]

    def test_additions_and_deletions_do_not_cancel(self) -> None:
        self.fixture.write("generated.py", "replacement\n")
        result = self.evaluate(self.fixture.commit())
        self.assertEqual((result["additions"], result["deletions"], result["total"]), (1, 1, 2))
        self.assertEqual(result["checks"]["budget"]["state"], "success")

    def test_below_equal_and_above_limit(self) -> None:
        for additions in (9, 10, 11):
            with self.subTest(additions=additions):
                self.fixture.write("generated.py", "generated\n" + "custom\n" * additions)
                result = self.evaluate(self.fixture.commit())
                self.assertEqual(result["total"], additions)
                self.assertEqual(
                    result["checks"]["budget"]["state"], "failure" if additions > 10 else "success"
                )

    def test_whole_generated_file_deletion_is_counted(self) -> None:
        (self.repo / "generated.py").unlink()
        result = self.evaluate(self.fixture.commit())
        self.assertEqual((result["additions"], result["deletions"]), (0, 1))
        self.assertEqual(result["mixed_files"], 1)

    def test_restoring_generated_content_removes_customization(self) -> None:
        self.fixture.write("generated.py", "generated\ncustom\n")
        customized = self.fixture.commit()
        self.fixture.write("generated.py", "generated\n")
        result = self.evaluate(self.fixture.commit(), base=customized)
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["mixed_files"], 0)

    def test_handwritten_only_files_keep_existing_report_scope(self) -> None:
        self.fixture.write("handwritten.py", "custom\n" * 100)
        self.assertEqual(self.evaluate(self.fixture.commit())["total"], 0)

    def test_increase_is_isolated_but_does_not_apply_to_itself(self) -> None:
        self.policy(20)
        result = self.evaluate(self.fixture.commit())
        self.assertEqual(result["checks"]["isolation"]["state"], "success")
        self.assertEqual(result["limit"], 10)
        self.assertEqual(result["checked_limit"], 10)

    def test_entire_pr_must_be_budget_only_not_just_latest_commit(self) -> None:
        self.fixture.write("generated.py", "generated\n" + "custom\n" * 11)
        self.fixture.commit("SDK change first")
        self.policy(100)
        result = self.evaluate(self.fixture.commit("budget-only last commit"))
        self.assertEqual(result["checks"]["isolation"]["state"], "failure")
        self.assertIn("separate, budget-only PR", result["checks"]["isolation"]["description"])
        self.assertEqual(result["checks"]["budget"]["state"], "failure")
        self.assertEqual(result["limit"], 10)

    def test_new_base_budget_is_used_for_stale_pr_branch(self) -> None:
        self.fixture.git("checkout", "-q", "-b", "sdk", self.base)
        self.fixture.write("generated.py", "generated\n" + "custom\n" * 11)
        head = self.fixture.commit()
        self.fixture.git("checkout", "-q", "main")
        self.policy(20)
        new_base = self.fixture.commit("separate approved increase")
        result = self.evaluate(head, base=new_base)
        self.assertEqual(result["limit"], 20)
        self.assertEqual(result["checks"]["isolation"]["state"], "success")
        self.assertEqual(result["checks"]["budget"]["state"], "success")

    def test_decrease_must_fit_current_usage(self) -> None:
        self.fixture.write("generated.py", "generated\ncustom\ncustom\n")
        base = self.fixture.commit()
        self.policy(1)
        result = self.evaluate(self.fixture.commit(), base=base)
        self.assertEqual(result["checks"]["isolation"]["state"], "success")
        self.assertEqual(result["checks"]["budget"]["state"], "failure")
        self.assertEqual(result["checked_limit"], 1)

    def test_missing_base_policy_fails_closed(self) -> None:
        (self.repo / budget.POLICY).unlink()
        base = self.fixture.commit()
        self.policy(100)
        result = self.evaluate(self.fixture.commit(), base=base)
        self.assertTrue(all(c["state"] == "failure" for c in result["checks"].values()))

    def test_policy_deletion_rename_symlink_and_mode_change_fail(self) -> None:
        for change in ("delete", "rename", "symlink", "executable"):
            with self.subTest(change=change):
                self.fixture.git("checkout", "--detach", "-q", self.base)
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
                result = self.evaluate(self.fixture.commit())
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
                self.fixture.write(budget.POLICY, contents)
                result = self.evaluate(self.fixture.commit())
                self.assertEqual(result["checks"]["isolation"]["state"], "failure")

    def test_bad_snapshot_and_binary_change_fail_budget(self) -> None:
        self.fixture.write("generated.py", "binary\0content")
        result = self.evaluate(self.fixture.commit())
        self.assertIn("non-text", result["checks"]["budget"]["description"])
        self.fixture.write("generated.py", "generated\n")
        path = self.repo / ".castiron.stats.yml"
        path.write_text(
            path.read_text().replace(
                budget.report.hash_codegen_commit(self.repo, self.generated), "f" * 64
            )
        )
        result = self.evaluate(self.fixture.commit())
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
        self.fixture.git("checkout", "-q", "-b", "policy", self.base)
        self.policy(100)
        policy_head = self.fixture.commit()
        self.fixture.git("checkout", "-q", "-b", "sdk", self.base)
        self.fixture.write("generated.py", "generated\n" + "custom\n" * 11)
        sdk_head = self.fixture.commit()
        self.fixture.git("checkout", "-q", "-b", "queue", self.base)
        self.fixture.git("merge", "--no-ff", "-m", "queue policy", policy_head)
        self.fixture.git("merge", "--no-ff", "-m", "queue SDK", sdk_head)
        result = self.evaluate(
            self.fixture.git("rev-parse", "HEAD"), pull_heads=[policy_head, sdk_head]
        )
        self.assertEqual(result["checks"]["isolation"]["state"], "success")
        self.assertEqual(result["checks"]["budget"]["state"], "failure")
        self.assertEqual(result["limit"], 10)

    def test_queue_without_verified_members_fails(self) -> None:
        self.assertEqual(
            self.evaluate(self.base, pull_heads=[])["checks"]["isolation"]["state"], "failure"
        )

    def test_queue_membership_uses_synthetic_commit_not_original_pr_ancestry(self) -> None:
        self.fixture.git("checkout", "-q", "-b", "sdk", self.base)
        self.fixture.write("generated.py", "generated\ncustom\n")
        pr_head = self.fixture.commit()
        self.fixture.git("checkout", "-q", "-b", "queue", self.base)
        self.fixture.git("merge", "--squash", "sdk")
        queue_head = self.fixture.commit("synthetic queue commit")
        self.assertNotEqual(self.fixture.git("merge-base", pr_head, queue_head), pr_head)
        event = {
            "repository": {"full_name": "openai/example"},
            "workflow_run": source_run(queue_head, "merge_group"),
        }
        original_git = budget.report.git

        def local_fetch(repo: Path, *args: str) -> bytes:
            if args[0] == "fetch":
                args = tuple(str(self.repo) if arg == "origin" else arg for arg in args)
            return cast(bytes, original_git(repo, *args))

        with (
            tempfile.TemporaryDirectory() as temp,
            mock.patch.object(
                budget.report,
                "api",
                side_effect=[
                    {"default_branch": "main", "private": False},
                    {"object": {"sha": self.base}},
                    source_run(queue_head, "merge_group"),
                    [{"type": "merge_queue"}],
                ],
            ),
            mock.patch.object(budget, "queued_entries", return_value=[(pr_head, queue_head)]),
            mock.patch.object(
                budget.report,
                "git",
                side_effect=local_fetch,
            ),
            mock.patch.object(budget, "evaluate", return_value=({}, b"")) as evaluate,
        ):
            repo = Path(temp) / "queue.git"
            budget.github_evaluate(repo, "openai/example", event, self.base)
            evaluate.assert_called_once_with(
                repo,
                self.base,
                queue_head,
                public=True,
                fetch=True,
                pull_heads=[pr_head],
                measurement=None,
            )

    def test_cli_executes_trusted_reporter_not_inspected_repo(self) -> None:
        self.fixture.write(
            "scripts/castiron/custom_code_report.py", 'raise RuntimeError("PR CODE EXECUTED")\n'
        )
        self.fixture.write("sitecustomize.py", 'raise RuntimeError("PR IMPORTED")\n')
        head = self.fixture.commit()
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
        completed = subprocess.run(command, cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        self.assertEqual(json.loads((out / "budget.json").read_text())["total"], 0)

    def test_summary_has_counts_revisions_and_no_longer_generated(self) -> None:
        self.fixture.write("generated.py", "replacement\n")
        result = self.evaluate(self.fixture.commit())
        out = self.repo / "report-output"
        budget.write_result(out, result)
        summary = (out / "summary.md").read_text()
        self.assertIn("+1 / -1 = 2", summary)
        self.assertIn(self.generated, summary)
        self.assertIn(self.base, summary)
        self.assertIn("human approving review", summary)


@unittest.skipUnless(shutil.which("node"), "Node is needed to execute the status-publisher fixture")
class StatusPublisherTests(unittest.TestCase):
    def publish(
        self,
        *,
        event_name: str = "pull_request",
        head_changed: bool = False,
        base_changed: bool = False,
        no_result: bool = False,
        failed_budget: bool = False,
        run_overrides: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        path = (
            Path(__file__).resolve().parents[2]
            / ".github/workflows/castiron-custom-code-comment.yml"
        )
        section = path.read_text().split("\n  budget-status:\n", 1)[1].split("\n  comment:\n", 1)[0]
        publisher = section.split("          script: |\n", 1)[1]
        script = "\n".join(line[12:] for line in publisher.splitlines())
        base, head = "a" * 40, "b" * 40
        payload = {
            "script": script,
            "context": {
                "eventName": "workflow_run",
                "repo": {"owner": "openai", "repo": "example"},
                "serverUrl": "https://github.com",
                "runId": 123,
                "payload": {
                    "workflow_run": source_run(head, event_name),
                },
            },
            "run": {**source_run(head, event_name), **(run_overrides or {})},
            "current": {
                "state": "open",
                "head": {"sha": "c" * 40 if head_changed else head},
                "base": {
                    "sha": "c" * 40 if base_changed else base,
                    "ref": "main",
                    "repo": {"full_name": "openai/example"},
                },
            },
            "env": {
                "BASE_SHA": "" if no_result else base,
                "HEAD_SHA": "" if no_result else head,
                "ISOLATION_RESULT": "success",
                "BUDGET_RESULT": "failure" if failed_budget else "success",
            },
        }
        harness = """
          const fs = require('node:fs');
          const data = JSON.parse(fs.readFileSync(0, 'utf8'));
          const published = [];
          const github = {rest: {
            pulls: {get: async () => ({data: data.current})},
            actions: {getWorkflowRun: async () => ({data: data.run})},
            git: {getRef: async () => ({data: {object: {sha: data.current.base.sha}}})},
            repos: {createCommitStatus: async value => published.push(value)},
          }};
          const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
          new AsyncFunction('github','context','process', data.script)(github, data.context, {env:data.env})
            .then(() => process.stdout.write(JSON.stringify(published)))
            .catch(error => { console.error(error); process.exitCode = 1; });
        """
        output = subprocess.run(
            ["node", "-e", harness],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=True,
        )
        return cast(list[dict[str, Any]], json.loads(output.stdout))

    def test_statuses_attach_to_candidate_not_main(self) -> None:
        for event in ("pull_request", "merge_group"):
            with self.subTest(event=event):
                results = self.publish(event_name=event)
                self.assertEqual(len(results), 2)
                self.assertTrue(
                    all(r["sha"] == "b" * 40 and r["state"] == "success" for r in results)
                )

    def test_stale_pr_head_is_not_published(self) -> None:
        self.assertEqual(self.publish(head_changed=True), [])

    def test_stale_base_and_missing_evaluation_cannot_publish_success(self) -> None:
        for event in ("pull_request", "merge_group"):
            for base_changed, no_result in ((True, False), (False, True)):
                results = self.publish(
                    event_name=event, base_changed=base_changed, no_result=no_result
                )
                self.assertEqual(len(results), 2)
                self.assertTrue(all(r["state"] == "failure" for r in results))

    def test_superseded_or_wrong_source_run_cannot_publish(self) -> None:
        for overrides in (
            {"run_attempt": 2},
            {"head_sha": "c" * 40},
            {"event": "push"},
            {"path": "other.yml"},
        ):
            with self.subTest(overrides=overrides):
                self.assertEqual(self.publish(run_overrides=overrides), [])

    def test_independent_check_failures_are_preserved(self) -> None:
        results = self.publish(failed_budget=True)
        self.assertEqual([r["state"] for r in results], ["success", "failure"])


class GitHubBudgetTests(unittest.TestCase):
    def test_merge_queue_rule_is_required_before_passing(self) -> None:
        base, head = "a" * 40, "b" * 40
        event = {
            "repository": {"full_name": "openai/example"},
            "workflow_run": source_run(head, "merge_group"),
        }
        with (
            tempfile.TemporaryDirectory() as temp,
            mock.patch.object(
                budget.report,
                "api",
                side_effect=[
                    {"default_branch": "main"},
                    {"object": {"sha": base}},
                    source_run(head, "merge_group"),
                    [{"type": "required_status_checks"}],
                ],
            ),
        ):
            repo = Path(temp) / "objects.git"
            with self.assertRaisesRegex(ValueError, "must require a merge queue"):
                budget.github_evaluate(repo, "openai/example", event, base)
            self.assertFalse(repo.exists())

    def test_wrong_or_superseded_source_runs_fail_before_fetching(self) -> None:
        base, head = "a" * 40, "b" * 40
        event = {"repository": {"full_name": "openai/example"}, "workflow_run": source_run(head)}
        for overrides in (
            {"run_attempt": 2},
            {"status": "in_progress"},
            {"path": "other.yml"},
            {"head_sha": "c" * 40},
            {"repository": {"full_name": "wrong/repo"}},
        ):
            with (
                self.subTest(overrides=overrides),
                tempfile.TemporaryDirectory() as temp,
                mock.patch.object(
                    budget.report,
                    "api",
                    side_effect=[
                        {"default_branch": "main"},
                        {"object": {"sha": base}},
                        {**source_run(head), **overrides},
                    ],
                ),
            ):
                repo = Path(temp) / "objects.git"
                with self.assertRaisesRegex(ValueError, "source workflow run"):
                    budget.github_evaluate(repo, "openai/example", event, base)
                self.assertFalse(repo.exists())

    def test_reuses_only_matching_main_job_report(self) -> None:
        base, head = "a" * 40, "b" * 40
        event = {"repository": {"full_name": "openai/example"}, "workflow_run": source_run(head)}
        pull = {
            "state": "open",
            "head": {"sha": head},
            "base": {
                "sha": base,
                "ref": "main",
                "repo": {"full_name": "openai/example"},
            },
        }
        for stale in (False, True):
            with self.subTest(stale=stale), tempfile.TemporaryDirectory() as temp:
                trusted = Path(temp)
                measured = {"target_base_sha": "c" * 40 if stale else base, "head_sha": head}
                (trusted / "report.json").write_text(json.dumps(measured))
                (trusted / "custom-code.patch").write_bytes(b"verified patch")
                repo = trusted / "objects.git"
                repo.mkdir()
                with (
                    mock.patch.object(
                        budget.report,
                        "api",
                        side_effect=[
                            {"default_branch": "main", "private": False},
                            {"object": {"sha": base}},
                            source_run(head),
                            pull,
                            [{"type": "merge_queue"}],
                        ],
                    ),
                    mock.patch.object(budget.report, "git", return_value=b"true\n") as git,
                    mock.patch.object(budget, "evaluate", return_value=({}, b"")) as evaluate,
                ):
                    if stale:
                        with self.assertRaisesRegex(ValueError, "trusted report is stale"):
                            budget.github_evaluate(repo, "openai/example", event, base, trusted)
                        evaluate.assert_not_called()
                    else:
                        budget.github_evaluate(repo, "openai/example", event, base, trusted)
                        evaluate.assert_called_once_with(
                            repo,
                            base,
                            head,
                            public=True,
                            fetch=True,
                            pull_heads=None,
                            measurement=(measured, b"verified patch"),
                        )
                        git.assert_called_once_with(repo, "rev-parse", "--is-bare-repository")

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

    def test_pull_context_refuses_stale_checkout_before_fetching(self) -> None:
        with (
            tempfile.TemporaryDirectory() as temp,
            mock.patch.object(
                budget.report,
                "api",
                side_effect=[{"default_branch": "main"}, {"object": {"sha": "a" * 40}}],
            ),
        ):
            repo = Path(temp) / "objects.git"
            with self.assertRaisesRegex(ValueError, "trusted checkout is stale"):
                budget.github_evaluate(
                    repo,
                    "openai/example",
                    {"repository": {"full_name": "openai/example"}},
                    "b" * 40,
                )
            self.assertFalse(repo.exists())

    def test_github_uses_fresh_bare_data_repo_and_checks_current_head(self) -> None:
        base, head = "a" * 40, "b" * 40
        event = {
            "repository": {"full_name": "openai/example"},
            "workflow_run": source_run(head),
        }
        pull = {
            "state": "open",
            "head": {"sha": head},
            "base": {"sha": base, "ref": "main", "repo": {"full_name": "openai/example"}},
        }
        responses = [
            {"default_branch": "main", "private": False},
            {"object": {"sha": base}},
            source_run(head),
            pull,
            [{"type": "merge_queue"}],
        ]
        with (
            tempfile.TemporaryDirectory() as temp,
            mock.patch.object(budget.report, "api", side_effect=responses),
            mock.patch.object(budget.report, "git") as git,
            mock.patch.object(budget, "evaluate", return_value=({}, b"")) as evaluate,
        ):
            repo = Path(temp) / "objects.git"
            budget.github_evaluate(repo, "openai/example", event, base)
            self.assertTrue((repo / "HEAD").exists())
            self.assertFalse((repo / "src").exists())
            self.assertIn(
                mock.call(repo, "fetch", "--quiet", "--no-tags", "origin", base, head),
                git.call_args_list,
            )
            evaluate.assert_called_once_with(
                repo, base, head, public=True, fetch=True, pull_heads=None, measurement=None
            )

    def test_stale_pull_and_wrong_target_fail_before_objects_created(self) -> None:
        for kind in ("head", "base", "repository", "branch", "closed"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                base, head = "a" * 40, "b" * 40
                event = {
                    "repository": {"full_name": "openai/example"},
                    "workflow_run": source_run(head),
                }
                pull: dict[str, Any] = {
                    "state": "open",
                    "head": {"sha": head},
                    "base": {"sha": base, "ref": "main", "repo": {"full_name": "openai/example"}},
                }
                if kind == "head":
                    pull["head"]["sha"] = "c" * 40
                elif kind == "base":
                    pull["base"]["sha"] = "c" * 40
                elif kind == "repository":
                    pull["base"]["repo"]["full_name"] = "wrong/repo"
                elif kind == "branch":
                    pull["base"]["ref"] = "other"
                else:
                    pull["state"] = "closed"
                with mock.patch.object(
                    budget.report,
                    "api",
                    side_effect=[
                        {"default_branch": "main"},
                        {"object": {"sha": base}},
                        source_run(head),
                        pull,
                    ],
                ):
                    with self.assertRaisesRegex(ValueError, "exactly one current PR"):
                        budget.github_evaluate(
                            Path(temp) / "objects.git",
                            "openai/example",
                            event,
                            base,
                        )


if __name__ == "__main__":
    unittest.main()
