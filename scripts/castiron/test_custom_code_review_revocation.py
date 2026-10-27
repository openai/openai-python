# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
"""Exercise review revocation and target freshness against offline GitHub state."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any

import custom_code_policy as policy
from custom_code_test_support import WORKFLOW, run_publisher, source_head, source_run


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
            "head": source_head(head),
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
            "policies_by_sha": {
                base: {"schema_version": 1, "max_custom_patch_lines": 0},
                head: {"schema_version": 1, "max_custom_patch_lines": 1},
            },
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

    def test_retries_policy_failure_when_main_advances_before_revocation(self) -> None:
        payload = self.payload()
        payload["main_sha_sequence"] = ["d" * 40, "e" * 40]
        payload["main_sha"] = "e" * 40
        payload["policy_error_sequence"] = [True, False]
        result = self.invoke(payload)
        self.assertEqual([item.get("state") for item in result[:4]], ["pending"] * 4)
        self.assertEqual({item["sha"] for item in result[:4]}, {"a" * 40, "c" * 40})
        self.assertEqual([item["run_id"] for item in result[4:]], [12, 14])

    def test_uses_live_target_when_pull_base_snapshot_lags(self) -> None:
        for requires_human in (False, True):
            with self.subTest(requires_human=requires_human):
                payload = self.payload()
                payload["target_sha"] = "e" * 40
                payload["expected_policy_base"] = "e" * 40
                payload["requires_human"] = requires_human
                result = self.invoke(payload)
                if requires_human:
                    self.assertEqual([item.get("state") for item in result[:4]], ["pending"] * 4)
                    self.assertEqual([item["run_id"] for item in result[4:]], [12, 14])
                else:
                    self.assertEqual(result, [])

    def test_retries_when_live_target_advances_during_evaluation(self) -> None:
        for requires_human in (False, True):
            with self.subTest(requires_human=requires_human):
                payload = self.payload()
                payload["target_sha_sequence"] = ["d" * 40, "e" * 40]
                payload["target_sha"] = "e" * 40
                payload["expected_policy_bases"] = ["d" * 40, "e" * 40]
                payload["requires_human"] = requires_human
                result = self.invoke(payload)
                if requires_human:
                    self.assertEqual(
                        [item["run_id"] for item in result if "run_id" in item], [12, 14]
                    )
                    self.assertTrue(
                        all(item.get("state") == "pending" for item in result if "state" in item)
                    )
                else:
                    self.assertEqual(result, [])

    def test_refreshes_executable_policy_when_main_changes_review_requirement(self) -> None:
        payload = self.payload()
        payload["main_sha_sequence"] = ["d" * 40, "e" * 40]
        payload["main_sha"] = "e" * 40
        payload["requires_human_by_main"] = {"d" * 40: False, "e" * 40: True}
        result = self.invoke(payload)
        self.assertEqual([item.get("state") for item in result[:4]], ["pending"] * 4)
        self.assertEqual({item["sha"] for item in result[:4]}, {"a" * 40, "c" * 40})
        self.assertEqual([item["run_id"] for item in result[4:]], [12, 14])

    def test_rejects_invalid_trusted_policy_downloads(self) -> None:
        for override in [
            {"type": "symlink"},
            {"encoding": "none"},
            {"size": 1048577},
            {"size": 0},
            {"content": ""},
        ]:
            with self.subTest(override=override):
                payload = self.payload()
                payload["policy_file_override"] = override
                with self.assertRaises(subprocess.CalledProcessError):
                    self.invoke(payload)

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

    def test_later_comment_preserves_green_pr_and_queue_statuses(self) -> None:
        for state in ("COMMENTED", "PENDING"):
            for paginated in (False, True):
                with self.subTest(state=state, paginated=paginated):
                    payload = self.recovery()
                    approval = self.approval()
                    comment = {
                        **approval,
                        "fullDatabaseId": "102",
                        "state": state,
                        "body": "Follow-up discussion",
                    }
                    payload["review_nodes"] = [approval, comment]
                    if paginated:
                        payload.pop("review_nodes")
                        payload["review_pages"] = [
                            {
                                "expected_cursor": None,
                                "nodes": [comment],
                                "pageInfo": {"hasNextPage": True, "endCursor": "more"},
                            },
                            {
                                "expected_cursor": "more",
                                "nodes": [approval],
                                "pageInfo": {"hasNextPage": False},
                            },
                        ]
                    for status in payload["previous_statuses"]:
                        status["state"] = "success"
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
                "state": "CHANGES_REQUESTED",
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

    def test_dismissal_edit_away_and_blocking_review_revoke_even_for_other_signal_actor(
        self,
    ) -> None:
        for changed in (
            {"state": "DISMISSED"},
            {"body": ""},
            {"state": "CHANGES_REQUESTED", "fullDatabaseId": "102"},
        ):
            payload = self.payload()
            payload["review_nodes"] = [{**self.approval(), **changed}]
            self.assertEqual(len(self.invoke(payload)), 6)
        payload = self.payload()
        payload["review_pages"] = [
            {
                "expected_cursor": None,
                "nodes": [
                    {**self.approval(), "fullDatabaseId": "102", "state": "CHANGES_REQUESTED"}
                ],
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
                    "head_repository": source_run("a" * 40)["head_repository"],
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

    def test_shared_head_revokes_the_run_source_pr(self) -> None:
        payload = self.payload()
        payload["run"]["pull_requests"] = []
        payload["run"]["head_repository"]["id"] = 101
        payload["current"]["head"].update(
            ref="sdk", repo={"id": 101, "full_name": "contributor/example"}
        )
        payload["associated_pulls"] = [{"number": number} for number in (3, 4, 5)]
        payload["pulls_by_number"] = {
            str(number): {
                **payload["current"],
                "number": number,
                "head": {**payload["current"]["head"], **change},
            }
            for number, change in ((4, {"ref": "other"}), (5, {"repo": {"id": 102}}))
        }
        result = self.invoke(payload)
        self.assertEqual([item.get("state") for item in result[:4]], ["pending"] * 4)
        self.assertEqual({item["sha"] for item in result[:4]}, {"a" * 40, "c" * 40})

    def test_branch_only_merge_signal_requires_current_merge_and_base(self) -> None:
        payload = self.payload()
        payload["run"]["pull_requests"] = []
        payload["run"]["head_sha"] = payload["context"]["payload"]["workflow_run"]["head_sha"] = (
            "e" * 40
        )
        payload["fallback_pulls"] = [{"number": 3}]
        payload["merge_commit"] = {"parents": [{"sha": "b" * 40}, {"sha": "a" * 40}]}
        payload["merge_sha"] = "f" * 40
        self.assertEqual(self.invoke(payload), [])

        payload["merge_sha"] = "e" * 40
        self.assertEqual(len(self.invoke(payload)), 6)
        payload["current"]["base"]["sha"] = "d" * 40
        payload["comparisons"] = {
            f"{'d' * 40}...{'a' * 40}": {"merge_base_commit": {"sha": "b" * 40}}
        }
        self.assertEqual(self.invoke(payload), [])

    def test_merge_sha_signal_survives_base_advance_and_rejects_wrong_parents(self) -> None:
        payload = self.payload()
        payload["run"]["head_sha"] = payload["context"]["payload"]["workflow_run"]["head_sha"] = (
            "e" * 40
        )
        payload["current"]["base"]["sha"] = "d" * 40
        payload["comparisons"] = {
            f"{'d' * 40}...{'a' * 40}": {"merge_base_commit": {"sha": "b" * 40}}
        }
        payload["merge_commit"] = {"parents": [{"sha": "b" * 40}, {"sha": "a" * 40}]}
        self.assertEqual(len(self.invoke(payload)), 6)
        payload["comparisons"][f"{'b' * 40}...{'d' * 40}"] = {
            "merge_base_commit": {"sha": "f" * 40}
        }
        self.assertEqual(self.invoke(payload), [])
        payload["merge_commit"]["parents"].reverse()
        self.assertEqual(self.invoke(payload), [])

    def test_trusted_policy_decision_controls_revocation(self) -> None:
        payload = self.payload()
        payload["requires_human"] = False
        self.assertEqual(self.invoke(payload), [])
        payload["requires_human"] = True
        self.assertEqual(len(self.invoke(payload)), 6)

    def test_policy_failure_or_malformed_decision_cannot_write_statuses(self) -> None:
        for result in ({"policy_error": True}, {"requires_human": "false"}):
            with self.subTest(result=result), tempfile.TemporaryDirectory() as directory:
                payload = {**self.payload(), **result}
                capture = Path(directory) / "writes.json"
                payload["capture_writes"] = str(capture)
                with self.assertRaises(subprocess.CalledProcessError):
                    self.invoke(payload)
                self.assertEqual(json.loads(capture.read_text()), [])

    def test_revoked_go_ratchet_activation_invalidates_pr_and_queue_statuses(self) -> None:
        for changed in ({"state": "DISMISSED"}, {"body": ""}):
            with self.subTest(changed=changed):
                payload = self.payload()
                payload["policies_by_sha"]["a" * 40] = {
                    **payload["policies_by_sha"]["b" * 40],
                    "ratchet": "go",
                }
                payload["review_nodes"] = [{**self.approval(), **changed}]
                writes = self.invoke(payload)
                self.assertCountEqual(
                    [(item["sha"], item["state"]) for item in writes if "state" in item],
                    [("a" * 40, "pending")] * 2 + [("c" * 40, "pending")] * 2,
                )
                self.assertCountEqual(
                    [item["run_id"] for item in writes if "run_id" in item], [12, 14]
                )

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
            "head_repository": source_run("a" * 40)["head_repository"],
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

    def main_advance_payload(self) -> dict[str, Any]:
        payload = self.payload()
        main = "d" * 40
        run = {
            **source_run(main, "push"),
            "head_branch": "main",
            "head_repository": {"full_name": "openai/example"},
        }
        payload["run"] = run
        payload["main_sha"] = main
        payload["context"]["payload"]["workflow_run"] = dict(run)
        payload["runs_by_sha"]["c" * 40][0]["head_branch"] = "gh-readonly-queue/next/pr-3-example"
        return payload

    def invoke_main_advance(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        return run_publisher("Re-evaluate live next queue after main advances", payload)

    def test_main_advance_revokes_success_before_normal_queue_rerun(self) -> None:
        result = self.invoke_main_advance(self.main_advance_payload())
        self.assertEqual([item.get("state") for item in result[:2]], ["pending", "pending"])
        self.assertEqual({item["sha"] for item in result[:2]}, {"c" * 40})
        self.assertTrue(all(item["context"].startswith("Castiron next /") for item in result[:2]))
        self.assertEqual([item["run_id"] for item in result[2:]], [14])
        self.assertNotIn("success", [item.get("state") for item in result])

    def test_old_main_push_does_not_invalidate_newer_qualified_candidates(self) -> None:
        payload = self.main_advance_payload()
        payload["main_sha"] = "e" * 40
        self.assertEqual(self.invoke_main_advance(payload), [])

    def test_main_advance_rejects_foreign_or_non_main_signals(self) -> None:
        for field, value in (
            ("head_repository", {"full_name": "other/repo"}),
            ("repository", {"full_name": "other/repo"}),
            ("head_branch", "next"),
            ("event", "pull_request"),
        ):
            with self.subTest(field=field):
                payload = self.main_advance_payload()
                payload["run"][field] = value
                with self.assertRaises(subprocess.CalledProcessError):
                    self.invoke_main_advance(payload)
        payload = self.main_advance_payload()
        payload["run"]["workflow_id"] = 999
        self.assertEqual(self.invoke_main_advance(payload), [])

    def test_main_advance_invalidates_every_queue_page_before_dispatch(self) -> None:
        payload = self.main_advance_payload()
        payload["queue_pages"] = [
            {
                "expected_cursor": None,
                "nodes": [{"headCommit": None}, {"headCommit": {"oid": "c" * 40}}],
                "pageInfo": {"hasNextPage": True, "endCursor": "second"},
            },
            {
                "expected_cursor": "second",
                "nodes": [{"headCommit": {"oid": "e" * 40}}, {"headCommit": None}],
                "pageInfo": {"hasNextPage": False, "endCursor": None},
            },
        ]
        result = self.invoke_main_advance(payload)
        self.assertEqual([item.get("state") for item in result[:4]], ["pending"] * 4)
        self.assertEqual({item["sha"] for item in result[:4]}, {"c" * 40, "e" * 40})
        self.assertEqual([item["run_id"] for item in result[4:]], [14])

    def test_main_advance_still_rejects_malformed_non_null_heads(self) -> None:
        for head in ({}, {"oid": None}, {"oid": "g" * 40}):
            with self.subTest(head=head):
                payload = self.main_advance_payload()
                payload["queue_nodes"][0]["headCommit"] = head
                with self.assertRaises(subprocess.CalledProcessError):
                    self.invoke_main_advance(payload)

    def test_main_advance_does_not_rerun_wrong_queue_or_foreign_workflows(self) -> None:
        for field, value in (
            ("repository", {"full_name": "other/repo"}),
            ("workflow_id", 999),
            ("head_branch", "gh-readonly-queue/main/pr-3-example"),
        ):
            with self.subTest(field=field):
                payload = self.main_advance_payload()
                payload["runs_by_sha"]["c" * 40][0][field] = value
                result = self.invoke_main_advance(payload)
                self.assertEqual([item.get("state") for item in result], ["pending", "pending"])

    def test_main_advance_leaves_newer_running_evaluation_to_publish(self) -> None:
        payload = self.main_advance_payload()
        runs = payload["runs_by_sha"]["c" * 40]
        runs.append({**runs[0], "id": 15, "status": "in_progress"})
        result = self.invoke_main_advance(payload)
        self.assertEqual([item.get("state") for item in result], ["pending", "pending"])

    def test_main_advance_with_empty_queue_has_no_writes(self) -> None:
        payload = self.main_advance_payload()
        payload["queue_nodes"] = []
        payload["queue_absent"] = True
        self.assertEqual(self.invoke_main_advance(payload), [])

    def test_signal_is_unprivileged_and_writers_serialize(self) -> None:
        producer = (WORKFLOW.parent / "castiron-custom-code.yml").read_text()
        self.assertIn("pull_request_review:\n    types: [submitted, edited, dismissed]", producer)
        signal = producer.split("  queue-signal:\n", 1)[1].split("  candidate-tests:\n", 1)[0]
        self.assertIn("permissions: {}", signal)
        self.assertIn("push:\n    branches: [main]", producer)
        main_change = (
            WORKFLOW.read_text().split("  main-change:\n", 1)[1].split("  compute:\n", 1)[0]
        )
        self.assertNotIn("checkout@", main_change)
        self.assertNotIn("download-artifact", main_change)
        self.assertNotIn("checkout@", signal)
        handler = WORKFLOW.read_text()
        revoke = handler.split("  review-change:\n", 1)[1].split("  compute:\n", 1)[0]
        self.assertNotIn("checkout@", revoke)
        self.assertNotIn("ref: ${{ github.event", revoke)
        self.assertIn("path.join(root, 'custom_code_policy.py'), 'review-required'", revoke)
        self.assertNotIn("download-artifact", revoke)
        self.assertEqual(
            handler.count("group: castiron-budget-writes-${{ github.repository_id }}"), 3
        )

    def test_direct_head_review_discovery_rejects_shared_commit_from_other_sources(
        self,
    ) -> None:
        for field, value in (
            ("id", 99),
            ("full_name", "other/example"),
            ("ref", "other-branch"),
        ):
            with self.subTest(field=field):
                payload = self.payload()
                payload["run"]["pull_requests"] = []
                head = source_head("a" * 40)
                if field == "ref":
                    head[field] = value
                else:
                    head["repo"][field] = value
                other = {**payload["current"], "number": 4, "head": head}
                payload["pulls_by_number"] = {"4": other}
                for discovery in ("associated_pulls", "fallback_pulls"):
                    payload["associated_pulls"] = []
                    payload[discovery] = [{"number": 4}, {"number": 3}]
                    result = self.invoke(payload)
                    self.assertEqual(len(result), 6)
                    self.assertEqual(
                        [item["run_id"] for item in result if "run_id" in item], [12, 14]
                    )

    def test_foreign_only_associations_retry_revocation_and_reporter_discovery(self) -> None:
        for explicit in (False, True):
            with self.subTest(explicit=explicit):
                payload = self.payload()
                payload["run"]["pull_requests"] = [{"number": 4}] if explicit else []
                payload["runs_by_sha"]["a" * 40][0]["pull_requests"] = []
                payload["associated_pulls"] = [{"number": 4}]
                payload["fallback_pulls"] = [{"number": 3}]
                own = payload["current"]
                foreign: dict[str, Any] = {
                    **own,
                    "number": 4,
                    "head": {**own["head"], "ref": "other"},
                }
                payload["pulls_by_number"] = {"4": foreign}
                payload["review_nodes"] = [{**self.approval(), "state": "DISMISSED"}]
                writes = self.invoke(payload)
                self.assertEqual(
                    [w["state"] for w in writes if "state" in w],
                    [] if explicit else ["pending"] * 4,
                )
                self.assertEqual(
                    [w["run_id"] for w in writes if "run_id" in w], [] if explicit else [12, 14]
                )
        # A fallback reached through unrelated commit associations is still branch-only:
        # an old synthetic merge must not gain the association-only exemption.
        payload["run"]["pull_requests"] = []
        payload["run"]["head_sha"] = payload["context"]["payload"]["workflow_run"]["head_sha"] = (
            "e" * 40
        )
        payload["merge_sha"] = "d" * 40
        payload["merge_commit"] = {"parents": [{"sha": "b" * 40}, {"sha": "a" * 40}]}
        payload["pulls_by_number"]["4"]["head"]["sha"] = "f" * 40
        self.assertEqual(self.invoke(payload), [])

    def test_merge_review_filters_foreign_sources_before_branch_fallback(self) -> None:
        for field, value in (("ref", "other"), ("id", 99), ("full_name", "other/example")):
            for explicit in (False, True):
                with self.subTest(field=field, explicit=explicit):
                    payload = self.payload()
                    payload["run"]["head_sha"] = "e" * 40
                    payload["context"]["payload"]["workflow_run"]["head_sha"] = "e" * 40
                    payload["run"]["pull_requests"] = [{"number": 4}] if explicit else []
                    payload["associated_pulls"] = [{"number": 4}]
                    payload["fallback_pulls"] = [{"number": 3}]
                    payload["merge_sha"] = "e" * 40
                    payload["merge_commit"] = {"parents": [{"sha": "b" * 40}, {"sha": "a" * 40}]}
                    head = source_head("a" * 40)
                    if field == "ref":
                        head[field] = value
                    else:
                        head["repo"][field] = value
                    payload["pulls_by_number"] = {
                        "4": {**payload["current"], "number": 4, "head": head}
                    }
                    writes = self.invoke(payload)
                    self.assertEqual(
                        [w["state"] for w in writes if "state" in w],
                        [] if explicit else ["pending"] * 4,
                    )
                    self.assertEqual(
                        [w["run_id"] for w in writes if "run_id" in w],
                        [] if explicit else [12, 14],
                    )
                    # Filtering a foreign association must not exempt fallback from freshness.
                    payload["merge_sha"] = "f" * 40
                    self.assertEqual(self.invoke(payload), [])

    def test_review_requires_complete_source_identity(self) -> None:
        for overrides in (
            {"head_repository": None},
            {"head_repository": {"id": 10}},
            {"head_repository": {"full_name": "contributor/example"}},
            {"head_branch": None},
            {"head_branch": "refs/pull/3/merge"},
        ):
            for merge in (False, True):
                with self.subTest(overrides=overrides, merge=merge):
                    payload = self.payload()
                    if merge:
                        payload["run"]["head_sha"] = "e" * 40
                        payload["context"]["payload"]["workflow_run"]["head_sha"] = "e" * 40
                        payload["merge_commit"] = {
                            "parents": [{"sha": "b" * 40}, {"sha": "a" * 40}]
                        }
                    payload["run"].update(overrides)
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

    def test_historical_merge_revocation_after_base_advance(self) -> None:
        for discovery in ("run", "commit", "branch"):
            for revoked in ({"state": "DISMISSED"}, {"body": ""}):
                with self.subTest(discovery=discovery, revoked=revoked):
                    payload = self.payload()
                    payload["review_nodes"] = [{**self.approval(), **revoked}]
                    payload["run"]["head_sha"] = "e" * 40
                    payload["context"]["payload"]["workflow_run"]["head_sha"] = "e" * 40
                    payload["current"]["base"]["sha"] = "f" * 40
                    payload["comparisons"] = {
                        f"{'f' * 40}...{'a' * 40}": {"merge_base_commit": {"sha": "b" * 40}}
                    }
                    payload["merge_sha"] = "d" * 40
                    payload["merge_commit"] = {"parents": [{"sha": "b" * 40}, {"sha": "a" * 40}]}
                    if discovery != "run":
                        payload["run"]["pull_requests"] = []
                        payload["associated_pulls"] = (
                            [{"number": 3}] if discovery == "commit" else []
                        )
                        payload["fallback_pulls"] = [{"number": 3}]
                    result = self.invoke(payload)
                    if discovery == "branch":
                        self.assertEqual(result, [])
                    else:
                        self.assertEqual(
                            [item.get("state") for item in result[:4]], ["pending"] * 4
                        )
                        self.assertEqual({item["sha"] for item in result[:4]}, {"a" * 40, "c" * 40})
                        self.assertEqual([item["run_id"] for item in result[4:]], [12, 14])

    def test_rerun_ignores_same_sha_main_from_another_source(self) -> None:
        for changes in (
            {"ref": "other"},
            {"repo": {**source_head("a" * 40)["repo"], "id": 11}},
            {"repo": {**source_head("a" * 40)["repo"], "full_name": "other/repo"}},
            {"repo": None},
        ):
            with self.subTest(changes=changes):
                payload = self.payload()
                reporter = payload["runs_by_sha"]["a" * 40][0]
                reporter["pull_requests"] = []
                current = payload["current"]
                main = {
                    **current,
                    "number": 4,
                    "head": {**current["head"], **changes},
                    "base": {**current["base"], "ref": "main"},
                }
                payload["pulls_by_number"] = {"4": main}
                payload["associated_pulls"] = [{"number": 3}, {"number": 4}]
                result = self.invoke(payload)
                self.assertEqual([item["run_id"] for item in result if "run_id" in item], [12, 14])

    def test_rerun_rejects_missing_reporter_source_identity(self) -> None:
        for changes in (
            {"head_repository": None},
            {"head_repository": {"full_name": "contributor/example"}},
            {"head_repository": {"id": 10}},
            {"head_branch": ""},
        ):
            with self.subTest(changes=changes):
                payload = self.payload()
                payload["runs_by_sha"]["a" * 40][0].update(changes)
                result = self.invoke(payload)
                self.assertEqual([item["run_id"] for item in result if "run_id" in item], [14])
                self.assertTrue(all(item["state"] == "pending" for item in result[:4]))


if __name__ == "__main__":
    unittest.main()
