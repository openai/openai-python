# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
"""Run the trusted publishers against offline GitHub state."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import unittest
from pathlib import Path
from typing import Any, cast
from unittest import mock

import custom_code_report as report
from custom_code_test_support import GitTestCase, source_run


WORKFLOW = (
    Path(__file__).resolve().parents[2] / ".github/workflows/castiron-custom-code-comment.yml"
)


def run_publisher(step: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    section = WORKFLOW.read_text().split(f"- name: {step}\n", 1)[1]
    script = section.split("          script: |\n", 1)[1]
    lines: list[str] = []
    for line in script.splitlines():
        if line and not line.startswith("            "):
            break
        lines.append(line[12:])
    output = subprocess.run(
        ["node", str(Path(__file__).with_name("fixtures") / "github_publisher.cjs")],
        input=json.dumps({**payload, "script": "\n".join(lines)}),
        text=True,
        capture_output=True,
        check=True,
    )
    return cast(list[dict[str, Any]], json.loads(output.stdout))


class WorkflowTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "GitHub Actions JavaScript runtime")
    def test_trusted_failure_publisher_updates_one_current_comment(self) -> None:
        head = "a" * 40
        run = {**source_run(head), "id": 20}
        current = {"state": "open", "head": {"sha": head}}
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
        self.assertIn('--base "$(git rev-parse HEAD)"', compute)
        self.assertIn("trusted_sha=$(git rev-parse HEAD)", compute)
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
            "head": {"sha": base},
            "base": {"sha": base, "ref": "main", "repo": {"full_name": "openai/example"}},
        }
        run = {
            "event": "pull_request",
            "path": ".github/workflows/castiron-custom-code.yml",
            "head_sha": base,
            "run_attempt": 1,
            "pull_requests": [{"number": 1}],
        }
        with mock.patch.object(
            report, "api", side_effect=[pull, run, [], pull, {"html_url": "published"}]
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
                    "head": {"sha": base},
                    "base": {"sha": base, "ref": "main", "repo": {"full_name": "openai/example"}},
                }
            if "/actions/runs/" in path:
                return {
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
                report.publish_comment(result, "openai/example", 1, 2, 1), "Skipped stale report"
            )
            self.assertEqual(len(calls), 1)

    def test_comment_rejects_older_runs_attempts_and_wrong_pr(self) -> None:
        _, base = self.baseline()
        result, _ = report.build_report(self.repo, base, base)
        pull: dict[str, Any] = {
            "state": "open",
            "head": {"sha": base},
            "base": {"sha": base, "ref": "main", "repo": {"full_name": "openai/example"}},
        }
        run = {
            "event": "pull_request",
            "path": ".github/workflows/castiron-custom-code.yml",
            "head_sha": base,
            "run_attempt": 2,
            "pull_requests": [{"number": 1}],
            "head_repository": {"owner": {"login": "contributor"}},
            "head_branch": "fix/branch",
        }
        comment = {
            "id": 8,
            "user": {"login": "github-actions[bot]"},
            "body": report.MARKER + "\n<!-- castiron:run:v1:3:1 -->",
            "html_url": "existing",
        }
        with mock.patch.object(report, "api", side_effect=[pull, run]) as api:
            self.assertEqual(
                report.publish_comment(result, "openai/example", 1, 2, 1), "Skipped stale report"
            )
            self.assertEqual(api.call_count, 2)
        with mock.patch.object(report, "api", side_effect=[pull, run, [comment]]) as api:
            self.assertEqual(
                report.publish_comment(result, "openai/example", 1, 2, 2), "Skipped stale report"
            )
            self.assertEqual(api.call_count, 3)
        with (
            mock.patch.object(
                report, "api", side_effect=[pull, {**run, "pull_requests": []}, [], []]
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
            side_effect=[pull, {**run, "pull_requests": []}, [{"number": 1}], [comment]],
        ) as api:
            self.assertEqual(
                report.publish_comment(result, "openai/example", 1, 2, 2), "Skipped stale report"
            )
            self.assertIn(f"/commits/{base}/pulls", api.call_args_list[2].args[1])
        changed = {**pull, "head": {"sha": "f" * 40}}
        with mock.patch.object(report, "api", side_effect=[pull, run, [], changed]) as api:
            self.assertEqual(
                report.publish_comment(result, "openai/example", 1, 2, 2), "Skipped stale report"
            )
            self.assertEqual(api.call_count, 4)
        for target in (
            {**pull["base"], "ref": "other"},
            {**pull["base"], "repo": {"full_name": "other/repo"}},
        ):
            with mock.patch.object(
                report, "api", side_effect=[pull, run, [], {**pull, "base": target}]
            ):
                self.assertEqual(
                    report.publish_comment(result, "openai/example", 1, 2, 2),
                    "Skipped stale report",
                )


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
        fallback_pulls: list[dict[str, int]] | None = None,
        run_overrides: dict[str, Any] | None = None,
        previous_statuses: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        base, head = "a" * 40, "b" * 40
        payload = {
            "fallback_pulls": fallback_pulls,
            "previous_statuses": previous_statuses or [],
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
                "PUBLISH_ATTEMPT": "1",
            },
        }
        return run_publisher("Publish exact-head statuses after checking freshness", payload)

    def test_statuses_attach_to_candidate_not_main(self) -> None:
        for event in ("pull_request", "merge_group"):
            with self.subTest(event=event):
                results = self.publish(event_name=event)
                self.assertEqual(len(results), 2)
                self.assertTrue(
                    all(r["sha"] == "b" * 40 and r["state"] == "success" for r in results)
                )

    def test_fork_statuses_with_no_commit_association(self) -> None:
        options: dict[str, Any] = {
            "run_overrides": {"pull_requests": []},
            "fallback_pulls": [{"number": 3}],
        }
        results = self.publish(**options)
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r["sha"] == "b" * 40 and r["state"] == "success" for r in results))
        self.assertEqual(self.publish(**options, head_changed=True), [])
        self.assertTrue(
            all(r["state"] == "failure" for r in self.publish(**options, no_result=True))
        )
        self.assertEqual(self.publish(run_overrides={"pull_requests": []}, fallback_pulls=[]), [])
        self.assertEqual(
            self.publish(
                run_overrides={"pull_requests": []}, fallback_pulls=[{"number": 3}, {"number": 4}]
            ),
            [],
        )

    def test_stale_pr_head_is_not_published(self) -> None:
        self.assertEqual(self.publish(head_changed=True), [])

    def test_pr_snapshot_survives_main_advancing(self) -> None:
        results = self.publish(base_changed=True)
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r["state"] == "success" for r in results))
        self.assertTrue(all("a" * 12 in r["description"] for r in results))

    def test_queue_still_rejects_main_advancing(self) -> None:
        results = self.publish(event_name="merge_group", base_changed=True)
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r["state"] == "failure" for r in results))

    def test_missing_evaluation_publishes_actionable_failures(self) -> None:
        for event in ("pull_request", "merge_group"):
            results = self.publish(event_name=event, no_result=True, base_changed=True)
            self.assertEqual(len(results), 2)
            for result in results:
                self.assertEqual(result["state"], "failure")
                self.assertIn("inspect the trusted run", result["description"])
                self.assertTrue(result["target_url"].endswith("/actions/runs/123"))

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

    def test_older_evaluation_cannot_overwrite_newer_failure(self) -> None:
        for order in ("124:1:125:1", "123:2:125:1", "123:1:125:1", "123:1:123:2"):
            with self.subTest(order=order):
                previous = {
                    "context": "Castiron / custom-code budget",
                    "creator": {"login": "github-actions[bot]"},
                    "state": "failure",
                    "description": f"Failed against newer main. [evaluation {order}]",
                    "target_url": f"https://github.com/openai/example/actions/runs/{order.split(':')[2]}",
                }
                self.assertEqual(self.publish(previous_statuses=[previous]), [])

    def test_publication_guard_allows_current_retry_and_ignores_unrelated_statuses(self) -> None:
        previous = {
            "context": "Castiron / custom-code budget",
            "creator": {"login": "github-actions[bot]"},
            "description": "Failed. [evaluation 123:1:123:1]",
            "target_url": "https://github.com/openai/example/actions/runs/123",
        }
        for overrides in (
            {},  # A partial publication can retry the same evaluation.
            {
                "description": "Failed. [evaluation 122:9:999:9]",
                "target_url": "https://github.com/openai/example/actions/runs/999",
            },
            {"description": "Legacy status without evaluation marker"},
            {"context": "Other check", "description": "[evaluation 999:9:999:9]"},
            {"creator": {"login": "someone"}, "description": "[evaluation 999:9:999:9]"},
            {"description": "[evaluation 999:9:999:9]", "target_url": "https://example.com/999"},
        ):
            with self.subTest(overrides=overrides):
                results = self.publish(previous_statuses=[{**previous, **overrides}])
                self.assertEqual(len(results), 2)
                self.assertTrue(all(r["state"] == "success" for r in results))
                self.assertTrue(all(len(r["description"]) <= 140 for r in results))


if __name__ == "__main__":
    unittest.main()
