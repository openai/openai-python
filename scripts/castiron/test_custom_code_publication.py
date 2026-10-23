# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
"""Run the trusted publishers against offline GitHub state."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any, cast
from unittest import mock

import custom_code_policy as policy
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
    return run_workflow_script("\n".join(lines), payload)


def run_workflow_script(script: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    output = subprocess.run(
        ["node", str(Path(__file__).with_name("fixtures") / "github_publisher.cjs")],
        input=json.dumps({**payload, "script": script}),
        text=True,
        capture_output=True,
        check=True,
    )
    return cast(list[dict[str, Any]], json.loads(output.stdout))


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
            "head": {"sha": head},
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
            "head": {"sha": head},
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
                "head": {"sha": head},
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
        branch: str = "main",
        evaluated_branch: str | None = None,
        policy_changed: bool = False,
        policy_sha: str | None = None,
        selected_policy_matches: bool = True,
        queue_absent: bool = False,
        queue_pages: list[dict[str, Any]] | None = None,
        retarget_during_publication: bool = False,
        same_head_next_pr: bool = False,
        policy_reviews: list[dict[str, Any]] | None = None,
        reviews: list[dict[str, Any]] | None = None,
        review_nodes: list[dict[str, Any]] | None = None,
        review_pages: list[dict[str, Any]] | None = None,
        policy_pull: dict[str, Any] | None = None,
        missing_review_contract: bool = False,
        review_contract: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        base, head = "a" * 40, "b" * 40
        run = source_run(head, event_name)
        if event_name == "merge_group":
            run["head_branch"] = f"gh-readonly-queue/{branch}/pr-7-example"
        payload: dict[str, Any] = {
            "reviews": reviews or [],
            "review_nodes": review_nodes
            if review_nodes is not None
            else [
                {
                    "fullDatabaseId": str(review["id"]),
                    "state": review["state"],
                    "body": review.get("body"),
                    "commit": {"oid": review.get("commit_id")},
                    "author": {
                        "login": review["user"]["login"],
                        "__typename": review["user"]["type"],
                    },
                    "authorAssociation": review.get("author_association"),
                }
                for review in reviews or []
            ],
            "review_pages": review_pages,
            "main_sha": "d" * 40
            if policy_changed
            else (policy_sha or ("c" * 40 if branch == "main" and base_changed else base)),
            "queue_absent": queue_absent,
            "queue_pages": queue_pages,
            "fallback_pulls": fallback_pulls,
            "previous_statuses": previous_statuses or [],
            "context": {
                "eventName": "workflow_run",
                "repo": {"owner": "openai", "repo": "example"},
                "serverUrl": "https://github.com",
                "runId": 123,
                "payload": {
                    "workflow_run": run,
                },
            },
            "run": {**run, **(run_overrides or {})},
            "current": {
                "number": 3,
                "user": {"login": "author"},
                "state": "open",
                "head": {"sha": "c" * 40 if head_changed else head},
                "base": {
                    "sha": "c" * 40 if base_changed else base,
                    "ref": branch,
                    "repo": {"full_name": "openai/example"},
                },
            },
            "env": {
                "POLICY_REVIEWS": json.dumps(policy_reviews or []),
                "HUMAN_REVIEW_RULES": ""
                if missing_review_contract
                else json.dumps(
                    policy.HUMAN_REVIEW_RULES if review_contract is None else review_contract
                ),
                "SELECTED_BRANCH": branch,
                "SELECTED_BASE_SHA": base,
                "SELECTED_HEAD_SHA": head,
                "SELECTED_POLICY_SHA": (policy_sha or base)
                if selected_policy_matches
                else "f" * 40,
                "TARGET_BRANCH": "" if no_result else (evaluated_branch or branch),
                "POLICY_SHA": "" if no_result else (policy_sha or base),
                "BASE_SHA": "" if no_result else base,
                "HEAD_SHA": "" if no_result else head,
                "ISOLATION_RESULT": "success",
                "BUDGET_RESULT": "failure" if failed_budget else "success",
                "PUBLISH_ATTEMPT": "1",
            },
        }
        if policy_pull:
            payload["pulls_by_number"] = {policy_pull["number"]: policy_pull}
        if same_head_next_pr:
            current = payload["current"]
            payload["pulls_by_number"] = {
                3: current,
                4: {**current, "number": 4, "base": {**current["base"], "ref": "next"}},
            }
        if retarget_during_publication:
            current = payload["current"]
            payload["current_sequence"] = [
                current,
                {**current, "base": {**current["base"], "ref": "other"}},
            ]
        return run_publisher("Publish exact-head statuses after checking freshness", payload)

    def test_live_human_review_predicate_matches_selector(self) -> None:
        head = "b" * 40
        approved = {
            "id": 10,
            "state": "APPROVED",
            "commit_id": head,
            "user": {"login": "human", "type": "User"},
            "author_association": "MEMBER",
            "body": policy.HUMAN_REVIEW_RULES["attestation_prefix"] + head,
        }
        cases = [
            [approved],
            [],
            [{**approved, "state": "DISMISSED"}],
            [approved, {**approved, "id": 11, "state": "CHANGES_REQUESTED"}],
            [approved, {**approved, "id": 11, "state": "COMMENTED"}],
            [{**approved, "commit_id": "f" * 40}],
            [{**approved, "user": {"login": "author", "type": "User"}}],
            [{**approved, "user": {"login": "bot", "type": "Bot"}}],
            [{**approved, "author_association": "NONE"}],
        ]
        for body in [
            "",
            "Looks good to me",
            policy.HUMAN_REVIEW_RULES["attestation_prefix"] + "f" * 40,
            "> " + policy.HUMAN_REVIEW_RULES["attestation_prefix"] + head,
            "<!-- pr-review:automated-review:v1 -->",
            "Automated source review.",
            "Source-only review; I did not execute candidate code or workflows.",
            "This does not substitute for human approval.",
            "This is not a human approving review.",
        ]:
            cases.append([{**approved, "body": body}])
        for reviews in cases:
            with self.subTest(reviews=reviews):
                expected = (
                    "success" if policy.has_human_approval(reviews, "author", head) else "failure"
                )
                writes = self.publish(
                    branch="next", policy_reviews=[{"number": 3, "head_sha": head}], reviews=reviews
                )
                self.assertEqual([w["state"] for w in writes], [expected, expected])

    def test_final_publisher_preserves_review_identity_precision(self) -> None:
        head = "b" * 40
        approval = {
            "id": 9007199254740992,
            "state": "APPROVED",
            "commit_id": head,
            "user": {"login": "human", "type": "User"},
            "author_association": "MEMBER",
            "body": policy.HUMAN_REVIEW_RULES["attestation_prefix"] + head,
        }
        replacement = {**approval, "id": 9007199254740993, "state": "COMMENTED"}
        for reviews in ([approval, replacement], [replacement, approval]):
            with self.subTest(reviews=reviews):
                writes = self.publish(
                    branch="next",
                    policy_reviews=[{"number": 3, "head_sha": head}],
                    reviews=reviews,
                )
                self.assertEqual([w["state"] for w in writes], ["failure"] * 2)
        writes = self.publish(
            branch="next",
            policy_reviews=[{"number": 3, "head_sha": head}],
            reviews=[{**replacement, "state": "APPROVED"}, {**approval, "state": "DISMISSED"}],
        )
        self.assertEqual([w["state"] for w in writes], ["success"] * 2)

    def test_final_publisher_review_pages_and_malformed_identity(self) -> None:
        head = "b" * 40
        approval = {
            "fullDatabaseId": "9007199254740992",
            "state": "APPROVED",
            "commit": {"oid": head},
            "author": {"login": "human", "__typename": "User"},
            "authorAssociation": "MEMBER",
            "body": policy.HUMAN_REVIEW_RULES["attestation_prefix"] + head,
        }

        def publish(**kwargs: Any) -> list[str]:
            return [
                w["state"]
                for w in self.publish(
                    branch="next",
                    policy_reviews=[{"number": 3, "head_sha": head}],
                    **kwargs,
                )
            ]

        self.assertEqual(publish(review_nodes=[approval]), ["success"] * 2)
        for identity in (None, "", "1.5", "-1", "0", 9007199254740992):
            with self.subTest(identity=identity):
                self.assertEqual(
                    publish(review_nodes=[{**approval, "fullDatabaseId": identity}]),
                    ["failure"] * 2,
                )
        pages: list[dict[str, Any]] = [
            {
                "expected_cursor": None,
                "nodes": [approval],
                "pageInfo": {"hasNextPage": True, "endCursor": "page2"},
            },
            {
                "expected_cursor": "page2",
                "nodes": [{**approval, "fullDatabaseId": "9007199254740993", "state": "DISMISSED"}],
                "pageInfo": {"hasNextPage": False, "endCursor": None},
            },
        ]
        self.assertEqual(publish(review_pages=pages), ["failure"] * 2)
        self.assertEqual(
            publish(
                review_pages=[{**pages[0], "pageInfo": {"hasNextPage": True, "endCursor": None}}]
            ),
            ["failure"] * 2,
        )

    def test_queue_policy_approval_dismissal_after_selection_fails(self) -> None:
        candidate = "e" * 40
        pull: dict[str, Any] = {
            "number": 7,
            "user": {"login": "author"},
            "state": "open",
            "head": {"sha": candidate},
            "base": {"ref": "next", "repo": {"full_name": "openai/example"}},
        }
        approved = {
            "id": 1,
            "state": "APPROVED",
            "commit_id": candidate,
            "user": {"login": "human", "type": "User"},
            "author_association": "MEMBER",
            "body": policy.HUMAN_REVIEW_RULES["attestation_prefix"] + candidate,
        }
        for state in ("APPROVED", "DISMISSED", "CHANGES_REQUESTED"):
            with self.subTest(state=state):
                writes = self.publish(
                    event_name="merge_group",
                    branch="next",
                    policy_pull=pull,
                    policy_reviews=[{"number": 7, "head_sha": candidate}],
                    reviews=[{**approved, "state": state}],
                )
                self.assertEqual(
                    [w["state"] for w in writes],
                    ["success" if state == "APPROVED" else "failure"] * 2,
                )
        # Ordinary automated approvals may keep the queue live, but cannot replace
        # the independently required human policy approval.
        writes = self.publish(
            event_name="merge_group",
            branch="next",
            policy_pull=pull,
            policy_reviews=[{"number": 7, "head_sha": candidate}],
            reviews=[
                {**approved, "state": "DISMISSED"},
                {
                    **approved,
                    "id": 2,
                    "user": {"login": "automated", "type": "User"},
                    "body": "<!-- pr-review:automated-review:v1 -->",
                },
            ],
        )
        self.assertEqual([w["state"] for w in writes], ["failure", "failure"])

    def test_queue_policy_constituent_changes_fail_closed(self) -> None:
        candidate = "e" * 40
        pull: dict[str, Any] = {
            "number": 7,
            "user": {"login": "author"},
            "state": "open",
            "head": {"sha": candidate},
            "base": {"ref": "next", "repo": {"full_name": "openai/example"}},
        }
        approved = {
            "id": 1,
            "state": "APPROVED",
            "commit_id": candidate,
            "user": {"login": "human", "type": "User"},
            "author_association": "MEMBER",
            "body": policy.HUMAN_REVIEW_RULES["attestation_prefix"] + candidate,
        }
        for changed in [
            {**pull, "state": "closed"},
            {**pull, "head": {"sha": "f" * 40}},
            {**pull, "base": {**pull["base"], "ref": "main"}},
        ]:
            with self.subTest(changed=changed):
                writes = self.publish(
                    event_name="merge_group",
                    branch="next",
                    policy_pull=changed,
                    policy_reviews=[{"number": 7, "head_sha": candidate}],
                    reviews=[approved],
                )
                self.assertEqual([w["state"] for w in writes], ["failure", "failure"])

    def test_missing_policy_review_contract_fails_closed(self) -> None:
        self.assertEqual(
            [w["state"] for w in self.publish(branch="next", missing_review_contract=True)],
            ["failure", "failure"],
        )

    def test_legacy_review_contract_fails_closed_only_on_next(self) -> None:
        legacy = {
            key: value
            for key, value in policy.HUMAN_REVIEW_RULES.items()
            if key != "attestation_prefix"
        }
        legacy["version"] = 1
        for branch, expected in (("next", "failure"), ("main", "success")):
            with self.subTest(branch=branch):
                self.assertEqual(
                    [w["state"] for w in self.publish(branch=branch, review_contract=legacy)],
                    [expected, expected],
                )

    def test_statuses_attach_to_candidate_not_main(self) -> None:
        for event in ("pull_request", "merge_group"):
            with self.subTest(event=event):
                results = self.publish(event_name=event)
                self.assertEqual(len(results), 2)
                self.assertTrue(
                    all(r["sha"] == "b" * 40 and r["state"] == "success" for r in results)
                )

    def test_next_cannot_overwrite_main_results(self) -> None:
        for main_event in ("pull_request", "merge_group"):
            main = self.publish(event_name=main_event, failed_budget=True)
            self.assertEqual([r["state"] for r in main], ["success", "failure"])
            for event in ("pull_request", "merge_group"):
                with self.subTest(main_event=main_event, event=event):
                    # Both evaluations use the same commit. A next success
                    # must not replace the main target's required failure.
                    result = self.publish(event_name=event, branch="next", previous_statuses=main)
                    self.assertEqual([r["state"] for r in result], ["success", "success"])
                    self.assertTrue(
                        {r["context"] for r in result}.isdisjoint(r["context"] for r in main)
                    )

    def test_same_head_next_pr_does_not_block_required_main_statuses(self) -> None:
        for numbers in ([3, 4], [4, 3]):
            with self.subTest(numbers=numbers):
                results = self.publish(
                    run_overrides={"pull_requests": []},
                    fallback_pulls=[{"number": number} for number in numbers],
                    same_head_next_pr=True,
                    failed_budget=True,
                )
                self.assertEqual([r["state"] for r in results], ["success", "failure"])
                self.assertTrue(all(r["sha"] == "b" * 40 for r in results))
        next_results = self.publish(
            branch="next", run_overrides={"pull_requests": [{"number": 4}]}, same_head_next_pr=True
        )
        self.assertEqual([r["state"] for r in next_results], ["success", "success"])
        self.assertTrue(all(r["context"].startswith("Castiron next /") for r in next_results))

    def test_next_queue_approved_pin_survives_main_advancing(self) -> None:
        for changed in (False, True):
            with self.subTest(policy_changed=changed):
                results = self.publish(
                    event_name="merge_group", branch="next", policy_changed=changed
                )
                self.assertEqual([r["state"] for r in results], ["success", "success"])

    def test_next_pin_receipt_and_target_freshness(self) -> None:
        for event in ("pull_request", "merge_group"):
            cases: tuple[dict[str, Any], ...] = (
                {"selected_policy_matches": False},
                {"no_result": True},
                {"base_changed": True},
            )
            for kwargs in cases:
                with self.subTest(event=event, kwargs=kwargs):
                    results = self.publish(event_name=event, branch="next", **kwargs)
                    self.assertEqual([r["state"] for r in results], ["failure", "failure"])
            results = self.publish(event_name=event, branch="next", policy_sha="e" * 40)
            self.assertEqual([r["state"] for r in results], ["success", "success"])
        results = self.publish(event_name="merge_group", branch="next", queue_absent=True)
        self.assertEqual([r["state"] for r in results], ["failure", "failure"])

    def test_main_statuses_bind_target_policy_and_queue_membership(self) -> None:
        for event in ("pull_request", "merge_group"):
            with self.subTest(event=event):
                stale = self.publish(event_name=event, evaluated_branch="next")
                self.assertEqual([r["state"] for r in stale], ["failure", "failure"])
        for policy_changed, queue_absent in ((True, False), (False, True)):
            with self.subTest(policy_changed=policy_changed, queue_absent=queue_absent):
                result = self.publish(
                    event_name="merge_group",
                    policy_changed=policy_changed,
                    queue_absent=queue_absent,
                )
                self.assertEqual([r["state"] for r in result], ["failure", "failure"])
        self.assertEqual(self.publish(retarget_during_publication=True), [])

    def test_next_fork_and_unsupported_targets(self) -> None:
        result = self.publish(
            branch="next", run_overrides={"pull_requests": []}, fallback_pulls=[{"number": 3}]
        )
        self.assertEqual([r["state"] for r in result], ["success", "success"])
        for event in ("pull_request", "merge_group"):
            for branch in ("Next", "Main", "release", "next-other"):
                with self.subTest(event=event, branch=branch):
                    self.assertEqual(self.publish(event_name=event, branch=branch), [])

    def test_main_queue_membership_paginates(self) -> None:
        pages: list[dict[str, Any]] = [
            {
                "expected_cursor": None,
                "nodes": [],
                "pageInfo": {"hasNextPage": True, "endCursor": "page2"},
            },
            {
                "expected_cursor": "page2",
                "nodes": [{"headCommit": {"oid": "b" * 40}}],
                "pageInfo": {"hasNextPage": False, "endCursor": None},
            },
        ]
        result = self.publish(event_name="merge_group", queue_pages=pages)
        self.assertEqual([r["state"] for r in result], ["success", "success"])

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

    def test_main_rejects_mismatched_selector_receipt(self) -> None:
        results = self.publish(selected_policy_matches=False)
        self.assertTrue(results)
        self.assertTrue(all(result["state"] != "success" for result in results))

    def test_lookalike_workflow_cannot_publish(self) -> None:
        self.assertEqual(
            self.publish(
                run_overrides={
                    "path": ".github/workflows/castiron-custom-code.yml@evil.yml",
                    "workflow_id": 789,
                }
            ),
            [],
        )

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


@unittest.skipUnless(
    shutil.which("node"), "Node is needed to execute the review-revocation fixture"
)
class ReviewRevocationTests(unittest.TestCase):
    def payload(self) -> dict[str, Any]:
        head, base, queue = "a" * 40, "b" * 40, "c" * 40
        pull = {
            "number": 3,
            "user": {"login": "author"},
            "state": "open",
            "head": {"sha": head},
            "base": {"ref": "next", "sha": base, "repo": {"full_name": "openai/example"}},
        }
        run = {
            **source_run(head),
            "id": 20,
            "actor": {"login": "outsider", "type": "User"},
            "event": "pull_request_review",
            "status": "completed",
            "pull_requests": [{"number": 3, "head": {"sha": head}}],
        }

        def original(sha: str, event: str, identity: int) -> dict[str, Any]:
            return {**run, "head_sha": sha, "id": identity, "event": event}

        return {
            "run": run,
            "previous_statuses": [
                {
                    "context": name,
                    "state": "success",
                    "creator": {"login": "github-actions[bot]"},
                    "target_url": "https://github.com/openai/example/actions/runs/19",
                }
                for name in (
                    "Castiron next / budget-only change",
                    "Castiron next / custom-code budget",
                )
            ],
            "current": pull,
            "queue_nodes": [
                {"headCommit": {"oid": queue}, "pullRequest": {"number": 3, "headRefOid": head}}
            ],
            "runs_by_sha": {
                head: [original(head, "pull_request", 12)],
                queue: [original(queue, "merge_group", 14)],
            },
            "context": {
                "payload": {"workflow_run": dict(run)},
                "runId": 21,
                "repo": {"owner": "openai", "repo": "example"},
                "serverUrl": "https://github.com",
            },
        }

    def invoke(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        return run_publisher("Re-evaluate current PR and queue after review changes", payload)

    def test_revokes_pr_and_queue_before_requesting_normal_re_evaluation(self) -> None:
        result = self.invoke(self.payload())
        self.assertEqual([item.get("state") for item in result[:4]], ["pending"] * 4)
        self.assertEqual({item["sha"] for item in result[:4]}, {"a" * 40, "c" * 40})
        self.assertTrue(all(item["context"].startswith("Castiron next /") for item in result[:4]))
        self.assertEqual([item["run_id"] for item in result[4:]], [12, 14])
        self.assertNotIn("success", [item.get("state") for item in result])

    def approval(self) -> dict[str, Any]:
        return {
            "fullDatabaseId": "101",
            "state": "APPROVED",
            "body": policy.HUMAN_REVIEW_RULES["attestation_prefix"] + "a" * 40,
            "author": {"login": "reviewer", "__typename": "User"},
            "authorAssociation": "MEMBER",
            "commit": {"oid": "a" * 40},
            "updatedAt": "2026-10-22T01:00:00Z",
        }

    def recovery(self) -> dict[str, Any]:
        payload = self.payload()
        payload["review_nodes"] = [self.approval()]
        payload["run"]["actor"] = {"login": "reviewer", "type": "User"}
        for status in payload["previous_statuses"]:
            status["state"] = "failure"
        return payload

    def history(self, payload: dict[str, Any], writes: list[dict[str, Any]]) -> None:
        payload["statuses_by_sha"] = {
            sha: [
                {**item, "creator": {"login": "github-actions[bot]"}}
                for item in writes
                if item.get("sha") == sha
            ]
            for sha in ("a" * 40, "c" * 40)
        }
        payload["runs_by_id"] = {
            "21": {
                "id": 21,
                "workflow_id": 789,
                "status": "completed",
                "conclusion": "success",
                "repository": {"full_name": "openai/example"},
                "event": "workflow_run",
            }
        }

    def test_unrelated_comment_cannot_invalidate_valid_approval_or_request_recovery(self) -> None:
        for state in ("success", "failure", "pending"):
            payload = self.recovery()
            payload["run"]["actor"]["login"] = "outsider"
            payload["review_nodes"].append(
                {
                    **self.approval(),
                    "fullDatabaseId": "102",
                    "author": {"login": "outsider", "__typename": "User"},
                    "state": "COMMENTED",
                    "body": "hello",
                }
            )
            for status in payload["previous_statuses"]:
                status["state"] = state
            payload["forbid_queue"] = True
            self.assertEqual(self.invoke(payload), [])

    def test_ineligible_review_cannot_request_recovery(self) -> None:
        for overrides in (
            {"state": "COMMENTED"},
            {"body": ""},
            {"authorAssociation": "CONTRIBUTOR"},
            {"commit": {"oid": "b" * 40}},
            {"author": {"login": "author", "__typename": "User"}},
            {"author": {"login": "reviewer", "__typename": "Bot"}},
        ):
            with self.subTest(overrides=overrides):
                payload = self.recovery()
                payload["review_nodes"][0].update(overrides)
                self.assertEqual(self.invoke(payload), [])

    def test_repeated_invalid_signals_do_not_rerun_already_revoked_heads(self) -> None:
        payload = self.payload()
        writes = self.invoke(payload)
        self.history(payload, writes)
        self.assertEqual(self.invoke(payload), [])
        for statuses in payload["statuses_by_sha"].values():
            for status in statuses:
                status["state"] = "failure"
        self.assertEqual(self.invoke(payload), [])

    def test_approval_recovery_coalesces_and_edited_restoration_recovers_again(self) -> None:
        payload = self.recovery()
        writes = self.invoke(payload)
        self.assertEqual(len(writes), 6)
        self.assertTrue(all(len(item["description"]) <= 140 for item in writes[:4]))
        self.history(payload, writes)
        self.assertEqual(self.invoke(payload), [])
        payload["review_nodes"][0]["updatedAt"] = "2026-10-22T01:02:00Z"
        restored = self.invoke(payload)
        self.assertEqual(len(restored), 6)
        self.assertNotEqual(writes[0]["description"], restored[0]["description"])

    def test_new_revocation_supersedes_old_recovery_even_with_equal_edit_timestamp(self) -> None:
        payload = self.recovery()
        approved = self.invoke(payload)
        self.history(payload, approved)
        for statuses in payload["statuses_by_sha"].values():
            statuses[:0] = [
                {**status, "state": "success", "description": "Successful evaluation"}
                for status in statuses
            ]
        payload["review_nodes"][0]["body"] = ""
        revoked = self.invoke(payload)
        self.assertEqual(len(revoked), 6)
        self.history(payload, revoked)
        for sha, statuses in payload["statuses_by_sha"].items():
            statuses.extend(
                {**item, "creator": {"login": "github-actions[bot]"}}
                for item in approved
                if item.get("sha") == sha
            )
        payload["review_nodes"][0] = (
            self.approval()
        )  # Same ID, body and second-precision update time.
        self.assertEqual(len(self.invoke(payload)), 6)

    def test_full_review_id_handles_current_and_beyond_safe_integer_ids(self) -> None:
        payload = self.recovery()
        payload["review_nodes"][0].update(databaseId=None, fullDatabaseId="5614624241")
        self.assertEqual(len(self.invoke(payload)), 6)
        payload = self.payload()
        payload["review_nodes"] = [
            {**self.approval(), "databaseId": None, "fullDatabaseId": "9007199254740992"},
            {
                **self.approval(),
                "databaseId": None,
                "fullDatabaseId": "9007199254740993",
                "state": "COMMENTED",
            },
        ]
        self.assertEqual(len(self.invoke(payload)), 6)
        payload["review_nodes"][0]["fullDatabaseId"] = 9007199254740992
        with self.assertRaises(subprocess.CalledProcessError):
            self.invoke(payload)

    def test_publisher_failure_supersedes_recovery_without_observed_revocation(self) -> None:
        payload = self.recovery()
        approved = self.invoke(payload)
        self.history(payload, approved)
        for statuses in payload["statuses_by_sha"].values():
            statuses[:0] = [
                {**status, "state": "failure", "description": "Approval missing during publication"}
                for status in statuses
            ]
        # Publisher observed invalid body; review jobs only see its same-second restoration.
        # No new review identity/timestamp and no review-handler revocation marker exists.
        recovered = self.invoke(payload)
        self.assertEqual(len(recovered), 6)
        self.history(payload, recovered)
        self.assertEqual(self.invoke(payload), [])

    def test_deleted_marker_writer_is_untrusted_but_service_errors_propagate(self) -> None:
        payload = self.recovery()
        approved = self.invoke(payload)
        self.history(payload, approved)
        payload["run_errors"] = {"21": 404}
        self.assertEqual(len(self.invoke(payload)), 6)
        for status in (403, 429, 500):
            payload["run_errors"]["21"] = status
            with self.subTest(status=status), self.assertRaises(subprocess.CalledProcessError):
                self.invoke(payload)

    def test_failed_partial_dispatch_is_retried_before_signals_coalesce(self) -> None:
        for authorized in (False, True):
            for conclusion in ("failure", "cancelled", "timed_out"):
                payload = self.recovery() if authorized else self.payload()
                payload["fail_rerun"] = True
                # The fixture persists actual pending writes before the simulated API error.
                with tempfile.TemporaryDirectory() as directory:
                    capture = Path(directory) / "pending.json"
                    payload["capture_writes"] = str(capture)
                    with self.assertRaises(subprocess.CalledProcessError):
                        self.invoke(payload)
                    pending = json.loads(capture.read_text())
                self.assertEqual(len(pending), 4)
                self.history(payload, pending)
                payload.pop("capture_writes")
                payload.pop("fail_rerun")
                payload["runs_by_id"]["21"]["conclusion"] = conclusion
                payload["context"]["runId"] = 22
                retried = self.invoke(payload)
                self.assertEqual([item["run_id"] for item in retried if "run_id" in item], [12, 14])
                self.history(payload, retried)
                payload["runs_by_id"]["22"] = {**payload["runs_by_id"]["21"], "id": 22}
                self.assertEqual(self.invoke(payload), [])

    def test_untrusted_marker_cannot_suppress_recovery(self) -> None:
        for field, value in (
            ("workflow_id", 999),
            ("event", "pull_request"),
            ("repository", {"full_name": "attacker/example"}),
        ):
            payload = self.recovery()
            self.history(payload, self.invoke(payload))
            payload["runs_by_id"]["21"][field] = value
            self.assertEqual(len(self.invoke(payload)), 6)

    def test_dismissal_edit_away_and_later_comment_revoke_even_for_other_signal_actor(self) -> None:
        for changed in (
            {"state": "DISMISSED"},
            {"body": ""},
            {"state": "COMMENTED", "fullDatabaseId": "102"},
        ):
            payload = self.payload()
            payload["review_nodes"] = [{**self.approval(), **changed}]
            self.assertEqual(len(self.invoke(payload)), 6)
        payload = self.payload()
        payload["review_pages"] = [
            {
                "expected_cursor": None,
                "nodes": [{**self.approval(), "fullDatabaseId": "102", "state": "COMMENTED"}],
                "pageInfo": {"hasNextPage": True, "endCursor": "more"},
            },
            {
                "expected_cursor": "more",
                "nodes": [self.approval()],
                "pageInfo": {"hasNextPage": False},
            },
        ]
        self.assertEqual(len(self.invoke(payload)), 6)

    def test_missing_authoritative_edit_time_rejects_recovery(self) -> None:
        payload = self.recovery()
        payload["review_nodes"][0]["updatedAt"] = None
        with self.assertRaises(subprocess.CalledProcessError):
            self.invoke(payload)

    def test_review_signal_requires_canonical_workflow_identity_before_writes(self) -> None:
        for identity in (None, "456", 999):
            for path in (
                ".github/workflows/castiron-custom-code.yml",
                ".github/workflows/castiron-custom-code.yml@evil.yml",
            ):
                with self.subTest(identity=identity, path=path):
                    payload = self.payload()
                    payload["run"].update({"workflow_id": identity, "path": path})
                    payload["context"]["payload"]["workflow_run"] = dict(payload["run"])
                    self.assertEqual(self.invoke(payload), [])

    def test_rejects_forged_or_superseded_review_signals(self) -> None:
        for field, value in [
            ("path", ".github/workflows/other.yml"),
            ("run_attempt", 9),
            ("head_sha", "d" * 40),
            ("event", "pull_request"),
        ]:
            with self.subTest(field=field):
                payload = self.payload()
                payload["run"][field] = value
                with self.assertRaises(subprocess.CalledProcessError):
                    self.invoke(payload)
        payload = self.payload()
        payload["run"]["repository"] = {"full_name": "attacker/example"}
        with self.assertRaises(subprocess.CalledProcessError):
            self.invoke(payload)

    def test_head_change_keeps_observed_statuses_revoked_without_stale_reruns(self) -> None:
        payload = self.payload()
        changed = {**payload["current"], "head": {"sha": "d" * 40}}
        payload["current_sequence"] = [payload["current"], changed]
        payload["current"] = changed
        result = self.invoke(payload)
        self.assertEqual(len(result), 4)
        self.assertTrue(all(item["state"] == "pending" for item in result))
        self.assertNotIn("d" * 40, {item["sha"] for item in result})

    def test_queue_change_retries_and_invalidates_new_snapshot(self) -> None:
        payload = self.payload()
        old = list(payload["queue_nodes"])
        payload["queue_nodes"].append(
            {
                "headCommit": {"oid": "d" * 40},
                "pullRequest": {"number": 4, "headRefOid": "e" * 40},
            }
        )
        payload["runs_by_sha"]["d" * 40] = [
            {
                **payload["runs_by_sha"]["c" * 40][0],
                "head_sha": "d" * 40,
                "id": 16,
            }
        ]
        payload["queue_pages"] = [
            {
                "expected_cursor": None,
                "nodes": old,
                "pageInfo": {"hasNextPage": False},
            }
        ]
        result = self.invoke(payload)
        pending = [item for item in result if item.get("state") == "pending"]
        self.assertEqual({item["sha"] for item in pending}, {"a" * 40, "c" * 40, "d" * 40})
        self.assertEqual([item["run_id"] for item in result if "run_id" in item], [12, 14, 16])
        self.assertTrue(all(item.get("state") == "pending" for item in result[:-3]))

    def test_empty_review_pr_list_uses_authenticated_fork_discovery(self) -> None:
        for associated in ([], [{"number": 3}]):
            payload = self.payload()
            payload["run"].update(
                {
                    "pull_requests": [],
                    "head_repository": {"owner": {"login": "contributor"}},
                    "head_branch": "sdk",
                }
            )
            payload["associated_pulls"] = associated
            payload["fallback_pulls"] = [{"number": 3}]
            self.assertEqual(len(self.invoke(payload)), 6)
            payload["current"]["head"]["sha"] = "d" * 40
            payload["merge_sha"] = "e" * 40
            payload["merge_commit"] = {"parents": []}
            self.assertEqual(self.invoke(payload), [])

    def test_merge_sha_signal_requires_exact_live_merge_and_parents(self) -> None:
        payload = self.payload()
        payload["run"]["head_sha"] = payload["context"]["payload"]["workflow_run"]["head_sha"] = (
            "e" * 40
        )
        payload["merge_sha"] = "e" * 40
        payload["merge_commit"] = {"parents": [{"sha": "b" * 40}, {"sha": "a" * 40}]}
        self.assertEqual(len(self.invoke(payload)), 6)
        payload["merge_commit"]["parents"].reverse()
        self.assertEqual(self.invoke(payload), [])

    def test_closed_or_superseded_review_is_a_no_op(self) -> None:
        for changed in ({"state": "closed"}, {"head": {"sha": "f" * 40}}):
            payload = self.payload()
            payload["current"].update(changed)
            self.assertEqual(self.invoke(payload), [])

    def test_null_queue_association_does_not_block_revocation(self) -> None:
        payload = self.payload()
        payload["queue_nodes"].insert(0, {"headCommit": {"oid": "f" * 40}, "pullRequest": None})
        result = self.invoke(payload)
        self.assertEqual(len(result), 6)
        self.assertNotIn("f" * 40, {item.get("sha") for item in result})
        payload["queue_nodes"] = payload["queue_nodes"][:1]
        self.assertEqual(len(self.invoke(payload)), 3)

    def test_rerun_requires_the_reviewed_pr_not_just_shared_head(self) -> None:
        payload = self.payload()
        correct = payload["runs_by_sha"]["a" * 40][0]
        main = {
            **payload["current"],
            "number": 4,
            "base": {**payload["current"]["base"], "ref": "main"},
        }
        payload["pulls_by_number"] = {"4": main}
        other: dict[str, Any] = {
            **correct,
            "id": 30,
            "pull_requests": [{"number": 4, "head": {"sha": "a" * 40}}],
        }
        payload["runs_by_sha"]["a" * 40].append(other)
        result = self.invoke(payload)
        self.assertEqual([item["run_id"] for item in result if "run_id" in item], [12, 14])
        # Empty fork associations may rerun only if canonical discovery selects this next PR.
        fork: dict[str, Any] = {
            **correct,
            "pull_requests": [],
            "head_repository": {"owner": {"login": "contributor"}},
            "head_branch": "sdk",
        }
        payload["fallback_pulls"] = [{"number": 3}]
        payload["runs_by_sha"]["a" * 40] = [fork, other]
        result = self.invoke(payload)
        self.assertEqual([item["run_id"] for item in result if "run_id" in item], [12, 14])
        association_cases: tuple[list[dict[str, Any]], ...] = (
            [],
            [*correct["pull_requests"], *other["pull_requests"]],
        )
        for associations in association_cases:
            payload["associated_pulls"] = [{"number": 3}, {"number": 4}]
            payload["runs_by_sha"]["a" * 40] = [{**fork, "pull_requests": associations}, other]
            result = self.invoke(payload)
            self.assertEqual([item["run_id"] for item in result if "run_id" in item], [14])
            self.assertTrue(all(item["state"] == "pending" for item in result[:4]))

    def test_unprepared_queue_entry_still_revokes_pr_statuses(self) -> None:
        payload = self.payload()
        payload["queue_nodes"][0]["headCommit"] = None
        result = self.invoke(payload)
        self.assertEqual([item.get("state") for item in result], ["pending", "pending", None])
        self.assertEqual(result[-1]["run_id"], 12)

    def test_unrelated_review_does_not_restart_reporter(self) -> None:
        payload = self.payload()
        payload["files"] = [{"filename": "src/client.ts"}]
        self.assertEqual(self.invoke(payload), [])

    def test_no_success_or_foreign_run_can_be_published(self) -> None:
        payload = self.payload()
        payload["runs_by_sha"]["a" * 40][0]["repository"] = {"full_name": "other/repo"}
        result = self.invoke(payload)
        self.assertEqual(
            [item["run_id"] for item in result if item.get("operation") == "rerun"], [14]
        )
        self.assertTrue(all(item.get("state") != "success" for item in result))

    def test_signal_is_unprivileged_and_writers_serialize(self) -> None:
        producer = (WORKFLOW.parent / "castiron-custom-code.yml").read_text()
        self.assertIn("pull_request_review:\n    types: [submitted, edited, dismissed]", producer)
        signal = producer.split("  queue-signal:\n", 1)[1].split("  candidate-tests:\n", 1)[0]
        self.assertIn("permissions: {}", signal)
        self.assertNotIn("checkout@", signal)
        handler = WORKFLOW.read_text()
        revoke = handler.split("  review-change:\n", 1)[1].split("  compute:\n", 1)[0]
        self.assertNotIn("checkout@", revoke)
        self.assertNotIn("download-artifact", revoke)
        self.assertEqual(
            handler.count("group: castiron-budget-writes-${{ github.repository_id }}"), 2
        )


if __name__ == "__main__":
    unittest.main()
