# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
"""Run the trusted publishers against offline GitHub state."""

from __future__ import annotations

import hashlib
import json
import shutil
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

import custom_code_report as report
from custom_code_test_support import (
    WORKFLOW,
    GitTestCase,
    run_publisher,
    run_workflow_script,
    source_head,
    source_run,
)


class WorkflowTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "GitHub Actions JavaScript runtime")
    def test_workflow_path_filters_accept_refs_without_accepting_other_files(self) -> None:
        compute = WORKFLOW.read_text().split("\n  compute:\n", 1)[1]
        condition = next(
            line.removeprefix("    if: ")
            for line in compute.splitlines()
            if line.startswith("    if: ")
        )
        expected_path = ".github/workflows/castiron-custom-code.yml"
        cases = [
            (expected_path, True),
            (expected_path + "@main", True),
            (expected_path + "@refs/heads/next", True),
            (expected_path + "@refs/pull/42/merge", True),
            (".github/workflows/other.yml@main", False),
            (expected_path + ".bak@main", False),
            (expected_path + "/other@main", False),
            ("other/" + expected_path + "@main", False),
            ("", False),
        ]
        head = "a" * 40
        pull = {
            "number": 3,
            "state": "open",
            "head": source_head(head),
            "base": {"ref": "next", "repo": {"full_name": "openai/example"}},
        }
        for path, accepted in cases:
            for event in ("pull_request", "merge_group", "push"):
                with self.subTest(path=path, event=event):
                    run = {**source_run(head), "id": 20, "path": path, "event": event}
                    payload = {
                        "context": {
                            "payload": {"workflow_run": run},
                            "runId": 20,
                            "repo": {"owner": "openai", "repo": "example"},
                            "serverUrl": "https://github.com",
                        },
                        "current": pull,
                    }
                    # Evaluate the emitted job condition with its Actions builtins.
                    script = (
                        "const fromJSON = JSON.parse;\n"
                        "const contains = (items, value) => items.includes(value);\n"
                        "const startsWith = (value, prefix) => value.startsWith(prefix);\n"
                        "github.event = context.payload;\n"
                        f"if ({condition}) await github.rest.issues.createComment({{}});"
                    )
                    self.assertEqual(
                        bool(run_workflow_script(script, payload)),
                        accepted and event in ("pull_request", "merge_group"),
                    )
                    self.assertEqual(
                        bool(run_publisher("Publish a trusted failure status", payload)),
                        accepted and event == "pull_request",
                    )

    def test_candidate_tests_cannot_modify_credentialed_reporter_runner(self) -> None:
        producer = (WORKFLOW.parent / "castiron-custom-code.yml").read_text()
        tests, reporter = producer.split("\n  report:\n", 1)
        tests = tests.split("\n  candidate-tests:\n", 1)[1]
        self.assertIn("runs-on: ubuntu-latest", tests)
        self.assertIn("persist-credentials: false", tests)
        self.assertIn("python3 -m unittest discover", tests)
        self.assertNotIn("GH_TOKEN", tests)
        self.assertNotIn("upload-artifact@", tests)
        self.assertNotIn("unittest", reporter)
        self.assertIn("GH_TOKEN:", reporter)
        self.assertNotIn("needs: candidate-tests", reporter)

    @unittest.skipUnless(shutil.which("node"), "GitHub Actions JavaScript runtime")
    def test_trusted_failure_publisher_updates_one_current_comment(self) -> None:
        head = "a" * 40
        run = {**source_run(head), "id": 20}
        current = {
            "number": 3,
            "state": "open",
            "head": source_head(head),
            "base": {"ref": "main", "repo": {"full_name": "openai/example"}},
        }
        previous = {
            "id": 42,
            "user": {"type": "Bot", "login": "github-actions[bot]"},
            "body": report.MARKER + "\n<!-- castiron:run:v1:10:1 -->",
        }
        cases: dict[str, tuple[list[dict[str, Any]], dict[str, Any], str | None]] = {
            "create": ([], current, "create"),
            "update": ([previous], current, "update"),
            "changed head": ([previous], {**current, "head": {"sha": "c" * 40}}, None),
            "newer comment": (
                [{**previous, "body": report.MARKER + "\n<!-- castiron:run:v1:21:1 -->"}],
                current,
                None,
            ),
        }
        for fork in (False, True):
            for name, (comments, pull, expected) in cases.items():
                with self.subTest(name=name, fork=fork):
                    event: dict[str, Any] = {**run, "pull_requests": []} if fork else run
                    writes = run_publisher(
                        "Publish a trusted failure status",
                        {
                            "context": {
                                "payload": {"workflow_run": event},
                                "runId": 20,
                                "repo": {"owner": "openai", "repo": "example"},
                                "serverUrl": "https://github.com",
                            },
                            "current": pull,
                            "comments": comments,
                            "fallback_pulls": [{"number": 3}],
                        },
                    )
                    self.assertEqual(
                        [w["operation"] for w in writes], [expected] if expected else []
                    )
                    if expected:
                        self.assertIn("Report unavailable", writes[0]["body"])
                        self.assertIn("castiron:run:v1:20:1", writes[0]["body"])

    @unittest.skipUnless(shutil.which("node"), "GitHub Actions JavaScript runtime")
    def test_failure_comments_require_one_supported_target(self) -> None:
        head = "a" * 40

        def pull(number: int, branch: str = "main", repo: str = "openai/example") -> dict[str, Any]:
            return {
                "number": number,
                "state": "open",
                "head": source_head(head),
                "base": {"ref": branch, "repo": {"full_name": repo}},
            }

        cases: list[tuple[str, list[dict[str, Any]], list[int]]] = [
            ("retargeted", [pull(3, "release")], []),
            ("other repository", [pull(3, repo="other/example")], []),
            ("ambiguous main", [pull(3), pull(4)], []),
            ("ambiguous next", [pull(3, "next"), pull(4, "next")], []),
            ("prefer main", [pull(3, "next"), pull(4)], [4]),
            ("one next", [pull(3, "next")], [3]),
            ("ignore unsupported", [pull(3, "release"), pull(4)], [4]),
        ]
        for name, pulls, expected in cases:
            for fallback in (False, True):
                with self.subTest(name=name, fallback=fallback):
                    run = {
                        **source_run(head),
                        "id": 20,
                        "pull_requests": [] if fallback else pulls,
                    }
                    writes = run_publisher(
                        "Publish a trusted failure status",
                        {
                            "context": {
                                "payload": {"workflow_run": run},
                                "runId": 20,
                                "repo": {"owner": "openai", "repo": "example"},
                                "serverUrl": "https://github.com",
                            },
                            "pulls_by_number": {str(pr["number"]): pr for pr in pulls},
                            "fallback_pulls": pulls,
                        },
                    )
                    self.assertEqual([write["issue_number"] for write in writes], expected)

    def test_workflow_reports_all_branches_without_write_credentials(self) -> None:
        workflows = Path(__file__).resolve().parents[2] / ".github/workflows"
        producer = (workflows / "castiron-custom-code.yml").read_text()
        publisher = (workflows / "castiron-custom-code-comment.yml").read_text()
        self.assertIn("pull_request:", producer)
        self.assertNotIn("CASTIRON_CUSTOM_CODE_BRANCHES", producer + publisher)
        self.assertNotIn("pull-requests: write", producer)
        self.assertNotIn("head.repo.full_name ==", producer)
        self.assertIn("workflow_run:", publisher)
        concurrency = publisher.split("\nconcurrency:\n", 1)[1].split("\njobs:\n", 1)[0]
        self.assertIn("queue: max", concurrency)
        self.assertIn("cancel-in-progress: false", concurrency)
        self.assertIn("ref: ${{ github.workflow_sha }}", publisher)
        self.assertNotIn("ref: ${{ github.event.pull_request.head.sha }}", publisher)
        self.assertIn("persist-credentials: false", publisher)
        self.assertIn("--report", publisher)
        compute, comment = publisher.split("\n  comment:\n", 1)
        self.assertNotIn("pull-requests: write", compute)
        self.assertIn("pull-requests: read", compute)
        self.assertIn(" trusted-report ", compute)
        self.assertIn("ref: main", compute)
        self.assertIn('--base "$(git -C .castiron-policy-checker rev-parse HEAD)"', compute)
        self.assertIn("trusted_sha=$(git -C .castiron-policy-checker rev-parse HEAD)", compute)
        self.assertIn("merge_group:", producer)
        self.assertNotIn("download-artifact@", compute)
        self.assertNotIn("unittest", compute)
        self.assertIn("needs: compute", comment)
        self.assertIn("artifact-ids: ${{ needs.compute.outputs.artifact-id }}", comment)
        self.assertNotIn("run-id: ${{ github.event.workflow_run.id }}", comment)
        self.assertNotIn("git fetch", comment)
        self.assertIn("--artifact-run-id", comment)
        digest = hashlib.sha256(
            (workflows.parents[1] / "scripts/castiron/custom_code_report.py").read_bytes()
        ).hexdigest()
        self.assertIn(f"REPORTER_SHA256: {digest}", producer)

    @unittest.skipUnless(shutil.which("node"), "GitHub Actions JavaScript runtime")
    def test_review_signals_cannot_replace_pending_candidate_validation(self) -> None:
        producer = (WORKFLOW.parent / "castiron-custom-code.yml").read_text()
        group = producer.split("concurrency:\n", 1)[1].splitlines()[0].removeprefix("  group: ")
        expression = group.replace("${{", "${").replace("}}", "}")
        groups: list[str] = []
        for event in ("pull_request", "pull_request_review", "pull_request"):
            payload = {"context": {"payload": {"pull_request": {"number": 42}}}}
            script = (
                "github.event = context.payload;\n"
                f"github.event_name = {json.dumps(event)};\n"
                f"await github.rest.issues.createComment({{body: `{expression}`}});"
            )
            groups.append(run_workflow_script(script, payload)[0]["body"])
        self.assertNotEqual(groups[0], groups[1])
        self.assertEqual(groups[0], groups[2])

    @unittest.skipUnless(shutil.which("node"), "GitHub Actions JavaScript runtime")
    def test_failure_publisher_binds_one_source_before_writing(self) -> None:
        head = "a" * 40
        run: dict[str, Any] = {**source_run(head), "id": 20, "pull_requests": []}
        own: dict[str, Any] = {
            "number": 3,
            "state": "open",
            "head": source_head(head),
            "base": {"ref": "main", "repo": {"full_name": "openai/example"}},
        }
        previous = {
            "id": 42,
            "user": {"type": "Bot", "login": "github-actions[bot]"},
            "body": report.MARKER + "\n<!-- castiron:run:v1:10:1 -->",
        }

        def publish(**overrides: Any) -> list[dict[str, Any]]:
            return run_publisher(
                "Publish a trusted failure status",
                {
                    "context": {
                        "payload": {"workflow_run": run},
                        "runId": 30,
                        "repo": {"owner": "openai", "repo": "example"},
                        "serverUrl": "https://github.com",
                    },
                    "run": run,
                    "current": own,
                    "comments": [previous],
                    "comments_by_number": {3: [previous], 4: [{**previous, "id": 43}]},
                    "associated_pulls": [{"number": 3}, {"number": 4}],
                    **overrides,
                },
            )

        for foreign_head in (
            {**own["head"], "ref": "victim"},
            {**own["head"], "repo": {"id": 11, "full_name": "victim/example"}},
        ):
            victim = {**own, "number": 4, "head": foreign_head}
            with self.subTest(head=foreign_head):
                writes = publish(pulls_by_number={3: own, 4: victim})
                self.assertEqual([write["comment_id"] for write in writes], [42])
                writes = publish(
                    associated_pulls=[{"number": 4}],
                    fallback_pulls=[{"number": 3}],
                    pulls_by_number={3: own, 4: victim},
                )
                self.assertEqual([write["comment_id"] for write in writes], [42])
                self.assertEqual(
                    publish(
                        run={**run, "pull_requests": [{"number": 4}]},
                        fallback_pulls=[{"number": 3}],
                        pulls_by_number={3: own, 4: victim},
                    ),
                    [],
                )
        # Even two equally authorized PRs are ambiguous: no write to either.
        self.assertEqual(publish(), [])
        for changed_run in (
            {**run, "run_attempt": 2},
            {**run, "status": "in_progress"},
            {**run, "head_repository": None},
            {**run, "repository": {"full_name": "other/repo"}},
        ):
            with self.subTest(run=changed_run):
                self.assertEqual(publish(run=changed_run), [])
        changed = {**own, "head": {**own["head"], "ref": "other"}}
        self.assertEqual(
            publish(associated_pulls=[{"number": 3}], current_sequence=[own, changed]), []
        )


class CommentTests(GitTestCase):
    def test_comment_only_rerun_links_to_the_compute_artifact_attempt(self) -> None:
        workflow = (
            Path(__file__).resolve().parents[2]
            / ".github/workflows/castiron-custom-code-comment.yml"
        ).read_text()
        compute, comment = workflow.split("\n  comment:\n", 1)

        def field(section: str, prefix: str) -> str:
            return next(
                line.removeprefix(prefix)
                for line in section.splitlines()
                if line.startswith(prefix)
            )

        def resolve(value: str, context: dict[str, str]) -> str:
            for key, replacement in context.items():
                value = value.replace("${{ " + key + " }}", replacement)
            self.assertNotIn("${{", value)
            return value

        # A successful compute job's outputs survive a comment-only rerun.
        compute_context = {"github.run_id": "9", "github.run_attempt": "3"}
        uploaded_name = resolve(field(compute, "          name: "), compute_context)
        saved_attempt = resolve(field(compute, "      artifact-run-attempt: "), compute_context)
        comment_context = {
            "github.run_id": "9",
            "github.run_attempt": "4",
            "needs.compute.outputs.artifact-run-attempt": saved_attempt,
        }
        artifact_attempt = resolve(
            field(comment, "          ARTIFACT_RUN_ATTEMPT: "), comment_context
        )
        self.assertEqual(uploaded_name, "castiron-custom-code-9-3")
        self.assertEqual(artifact_attempt, "3")

        _, base = self.baseline()
        result, _ = report.build_report(self.repo, base, base)
        pull: dict[str, Any] = {
            "state": "open",
            "head": source_head(base),
            "base": {"sha": base, "ref": "main", "repo": {"full_name": "openai/example"}},
        }
        run = {
            **source_run(base),
            "event": "pull_request",
            "path": ".github/workflows/castiron-custom-code.yml",
            "head_sha": base,
            "run_attempt": 1,
            "pull_requests": [{"number": 1}],
        }
        with mock.patch.object(
            report, "api", side_effect=[pull, run, pull, [], pull, {"html_url": "published"}]
        ) as api:
            self.assertEqual(
                report.publish_comment(
                    result,
                    "openai/example",
                    1,
                    2,
                    1,
                    artifact_run_id=9,
                    artifact_run_attempt=int(artifact_attempt),
                ),
                "published",
            )
        body = api.call_args.args[2]["body"]
        self.assertIn(f"--name {uploaded_name}", body)
        self.assertNotIn("--name castiron-custom-code-9-4", body)
        self.assertIn("castiron:run:v1:2:1", body)

    def test_comment_updates_existing_bot_comment_and_skips_stale(self) -> None:
        _, base = self.baseline()
        result, _ = report.build_report(self.repo, base, base)
        calls: list[tuple[str, str, object]] = []

        def fake_api(method: str, path: str, payload: object = None) -> object:
            calls.append((method, path, payload))
            if "/pulls/" in path:
                return {
                    "state": "open",
                    "head": source_head(base),
                    "base": {
                        "sha": base,
                        "ref": "main",
                        "repo": {"full_name": "openai/example"},
                    },
                }
            if "/actions/runs/" in path:
                return {
                    **source_run(base),
                    "event": "pull_request",
                    "path": ".github/workflows/castiron-custom-code.yml",
                    "head_sha": base,
                    "run_attempt": 1,
                    "pull_requests": [{"number": 1}],
                }
            if "/comments?" in path:
                return [
                    {"id": 7, "user": {"login": "someone"}, "body": report.MARKER},
                    {
                        "id": 8,
                        "user": {"login": "github-actions[bot]"},
                        "body": report.MARKER,
                        "html_url": "existing",
                    },
                ]
            return {"html_url": "updated"}

        with mock.patch.object(report, "api", side_effect=fake_api):
            self.assertEqual(report.publish_comment(result, "openai/example", 1, 2, 1), "updated")
            self.assertEqual(calls[-1][:2], ("PATCH", "repos/openai/example/issues/comments/8"))
            calls.clear()
            result["head_sha"] = "f" * 40
            self.assertEqual(
                report.publish_comment(result, "openai/example", 1, 2, 1),
                "Skipped stale report",
            )
            self.assertEqual(len(calls), 1)

    def test_comment_rejects_older_runs_attempts_and_wrong_pr(self) -> None:
        _, base = self.baseline()
        result, _ = report.build_report(self.repo, base, base)
        pull: dict[str, Any] = {
            "state": "open",
            "head": source_head(base),
            "base": {"sha": base, "ref": "main", "repo": {"full_name": "openai/example"}},
        }
        run = {
            **source_run(base),
            "event": "pull_request",
            "path": ".github/workflows/castiron-custom-code.yml",
            "head_sha": base,
            "run_attempt": 2,
            "pull_requests": [{"number": 1}],
            "head_repository": source_run(base)["head_repository"],
            "head_branch": "sdk",
        }
        comment = {
            "id": 8,
            "user": {"login": "github-actions[bot]"},
            "body": report.MARKER + "\n<!-- castiron:run:v1:3:1 -->",
            "html_url": "existing",
        }
        with mock.patch.object(report, "api", side_effect=[pull, run]) as api:
            self.assertEqual(
                report.publish_comment(result, "openai/example", 1, 2, 1),
                "Skipped stale report",
            )
            self.assertEqual(api.call_count, 2)
        with mock.patch.object(report, "api", side_effect=[pull, run, pull, [comment]]) as api:
            self.assertEqual(
                report.publish_comment(result, "openai/example", 1, 2, 2),
                "Skipped stale report",
            )
            self.assertEqual(api.call_count, 4)
        with (
            mock.patch.object(
                report, "api", side_effect=[pull, {**run, "pull_requests": []}, [], [], []]
            ),
            self.assertRaisesRegex(report.ReportError, "does not match report PR"),
        ):
            report.publish_comment(result, "openai/example", 1, 2, 2)
        with (
            mock.patch.object(report, "api", side_effect=[pull, {**run, "path": "other.yml"}]),
            self.assertRaisesRegex(report.ReportError, "does not match report PR"),
        ):
            report.publish_comment(result, "openai/example", 1, 2, 2)
        with mock.patch.object(
            report,
            "api",
            side_effect=[pull, {**run, "pull_requests": []}, [{"number": 1}], pull, [comment]],
        ) as api:
            self.assertEqual(
                report.publish_comment(result, "openai/example", 1, 2, 2),
                "Skipped stale report",
            )
            self.assertIn(f"/commits/{base}/pulls", api.call_args_list[2].args[1])
        changed = {**pull, "head": source_head("f" * 40)}
        with mock.patch.object(report, "api", side_effect=[pull, run, pull, [], changed]) as api:
            self.assertEqual(
                report.publish_comment(result, "openai/example", 1, 2, 2),
                "Skipped stale report",
            )
            self.assertEqual(api.call_count, 5)
        for target in (
            {**pull["base"], "ref": "other"},
            {**pull["base"], "repo": {"full_name": "other/repo"}},
        ):
            with mock.patch.object(
                report, "api", side_effect=[pull, run, pull, [], {**pull, "base": target}]
            ):
                self.assertEqual(
                    report.publish_comment(result, "openai/example", 1, 2, 2),
                    "Skipped stale report",
                )

    def test_comment_uses_canonical_branch_fallback(self) -> None:
        run = source_run("a" * 40)
        run["pull_requests"] = []
        own: dict[str, Any] = {
            "state": "open",
            "head": source_head("a" * 40),
            "base": {"ref": "main", "repo": {"full_name": "openai/example"}},
        }
        foreign = {**own, "head": {**own["head"], "ref": "other"}}
        branches = [{"number": 3}]
        writes: list[str] = []
        measured = {
            "schema_version": 1,
            "status": "error",
            "head_sha": "a" * 40,
            "target_base_sha": "b" * 40,
            "error": "synthetic failure",
        }

        def api(method: str, path: str, payload: Any = None) -> Any:
            if method == "POST":
                writes.append(path)
                return {"html_url": "published"}
            if "/actions/runs/" in path:
                return run
            if "/commits/" in path:
                return [{"number": 4}]
            if "/pulls?" in path:
                return branches
            if "/comments?" in path:
                return []
            return {"3": own, "4": foreign, "5": own}[path.rsplit("/", 1)[1]]

        with mock.patch.object(report, "api", side_effect=api):
            self.assertEqual(report.current_pull("openai/example", run), (3, "main"))
            self.assertEqual(
                report.publish_comment(measured, "openai/example", 3, 123, 1), "published"
            )
            self.assertEqual(writes, ["repos/openai/example/issues/3/comments"])
            writes.clear()
            run["pull_requests"] = [{"number": 4}]
            with self.assertRaisesRegex(report.ReportError, "does not match report PR"):
                report.publish_comment(measured, "openai/example", 3, 123, 1)
            run["pull_requests"] = []
            branches.append({"number": 5})
            with self.assertRaisesRegex(report.ReportError, "multiple current"):
                report.publish_comment(measured, "openai/example", 3, 123, 1)
            self.assertEqual(writes, [])

    def test_successful_comment_rejects_another_source_before_and_after_pagination(
        self,
    ) -> None:
        head = "a" * 40
        run = source_run(head)
        own: dict[str, Any] = {
            "state": "open",
            "head": source_head(head),
            "base": {"ref": "main", "repo": {"full_name": "openai/example"}},
        }
        measured = {
            "schema_version": 1,
            "status": "error",
            "head_sha": head,
            "target_base_sha": "b" * 40,
            "error": "synthetic failure",
        }
        for foreign_head in (
            {**own["head"], "ref": "other"},
            {**own["head"], "repo": {**own["head"]["repo"], "id": 11}},
            {**own["head"], "repo": {**own["head"]["repo"], "full_name": "other/repo"}},
            {**own["head"], "repo": None},
        ):
            foreign = {**own, "head": foreign_head}
            cases: tuple[list[Any], ...] = ([foreign, run], [own, run, own, [], foreign])
            for states in cases:
                with (
                    self.subTest(head=foreign_head, reads=len(states)),
                    mock.patch.object(report, "api", side_effect=states) as api,
                ):
                    self.assertEqual(
                        report.publish_comment(measured, "openai/example", 3, 123, 1),
                        "Skipped stale report",
                    )
                    self.assertTrue(all(call.args[0] == "GET" for call in api.call_args_list))


if __name__ == "__main__":
    unittest.main()
