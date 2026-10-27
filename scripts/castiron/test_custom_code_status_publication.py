# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
"""Execute the trusted workflow against offline GitHub state."""

from __future__ import annotations

import json
import shutil
import unittest
from typing import Any

import custom_code_policy as policy
from custom_code_test_support import run_publisher, source_head, source_run


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
        associated_pulls: list[dict[str, int]] | None = None,
        run_overrides: dict[str, Any] | None = None,
        previous_statuses: list[dict[str, Any]] | None = None,
        branch: str = "main",
        evaluated_branch: str | None = None,
        policy_changed: bool = False,
        authenticated_main_sha: str | None = None,
        bootstrap: str = "false",
        main_snapshot: str = "",
        policy_sha: str | None = None,
        selected_policy_matches: bool = True,
        queue_absent: bool = False,
        queue_pages: list[dict[str, Any]] | None = None,
        retarget_during_publication: bool = False,
        source_changes_during_publication: dict[str, Any] | None = None,
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
            "associated_pulls": associated_pulls,
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
                "head": source_head("c" * 40 if head_changed else head),
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
                "SELECTED_BOOTSTRAP": bootstrap,
                "MAIN_SNAPSHOT": main_snapshot,
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
        payload["env"]["AUTHENTICATED_MAIN_SHA"] = (
            payload["main_sha"] if authenticated_main_sha is None else authenticated_main_sha
        )
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
        if source_changes_during_publication is not None:
            current = payload["current"]
            payload["current_sequence"] = [
                current,
                {**current, "head": {**current["head"], **source_changes_during_publication}},
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
                    branch="next",
                    policy_reviews=[{"number": 3, "head_sha": head}],
                    reviews=reviews,
                )
                self.assertEqual([w["state"] for w in writes], [expected, expected])

    def test_final_publisher_preserves_approval_across_comments(self) -> None:
        head = "b" * 40
        approval = {
            "id": 10,
            "state": "APPROVED",
            "commit_id": head,
            "user": {"login": "human", "type": "User"},
            "author_association": "MEMBER",
            "body": policy.HUMAN_REVIEW_RULES["attestation_prefix"] + head,
        }
        comment = {**approval, "id": 11, "state": "COMMENTED", "body": "A follow-up comment"}
        cases = [
            ([approval, comment], "success"),
            ([comment, approval], "success"),
            ([comment], "failure"),
            ([{**approval, "state": "DISMISSED"}, comment], "failure"),
            ([{**approval, "body": "Attestation removed"}, comment], "failure"),
            (
                [
                    approval,
                    {**approval, "id": 12, "state": "CHANGES_REQUESTED"},
                    {**comment, "id": 13},
                ],
                "failure",
            ),
            (
                [
                    {**approval, "state": "CHANGES_REQUESTED"},
                    {**approval, "id": 12},
                    {**comment, "id": 13},
                ],
                "success",
            ),
        ]
        for reviews, expected in cases:
            with self.subTest(reviews=reviews):
                writes = self.publish(
                    branch="next",
                    policy_reviews=[{"number": 3, "head_sha": head}],
                    reviews=reviews,
                )
                self.assertEqual([w["state"] for w in writes], [expected] * 2)

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
        replacement = {**approval, "id": 9007199254740993, "state": "CHANGES_REQUESTED"}
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

    def test_next_publication_binds_authenticated_main(self) -> None:
        # The reviewed checker pin may remain old. The evaluation's main snapshot
        # must still be current so an old publisher cannot undo invalidation.
        for event in ("pull_request", "merge_group"):
            for authenticated_main, expected in (
                ("a" * 40, "failure"),
                ("d" * 40, "success"),
                ("", "failure"),
                ("invalid", "failure"),
            ):
                with self.subTest(event=event, authenticated_main=authenticated_main):
                    writes = self.publish(
                        event_name=event,
                        branch="next",
                        policy_changed=True,
                        authenticated_main_sha=authenticated_main,
                    )
                    self.assertEqual([item["state"] for item in writes], [expected] * 2)

    def test_main_snapshot_publication_rechecks_live_main(self) -> None:
        for event in ("pull_request", "merge_group"):
            for moved in (False, True):
                with self.subTest(event=event, moved=moved):
                    writes = self.publish(
                        event_name=event,
                        branch="next",
                        policy_sha="e" * 40,
                        main_snapshot="e" * 40,
                        policy_changed=moved,
                    )
                    self.assertEqual(
                        [w["state"] for w in writes],
                        ["failure", "failure"] if moved else ["success", "success"],
                    )

    def test_bootstrap_rechecks_authenticated_main(self) -> None:
        for event in ("pull_request", "merge_group"):
            for bootstrap, changed, expected in (
                ("true", False, "success"),
                ("true", True, "failure"),
                ("false", True, "success"),
                ("", False, "failure"),
                ("invalid", False, "failure"),
            ):
                with self.subTest(event=event, bootstrap=bootstrap, changed=changed):
                    writes = self.publish(
                        event_name=event,
                        branch="next",
                        bootstrap=bootstrap,
                        policy_changed=changed,
                    )
                    self.assertEqual([item["state"] for item in writes], [expected] * 2)

    def test_freshness_is_rechecked_after_review_pagination(self) -> None:
        head = "b" * 40
        approval = {
            "fullDatabaseId": "1",
            "state": "APPROVED",
            "body": policy.HUMAN_REVIEW_RULES["attestation_prefix"] + head,
            "author": {"login": "human", "__typename": "User"},
            "authorAssociation": "MEMBER",
            "commit": {"oid": head},
        }
        current: dict[str, Any] = {
            "number": 3,
            "user": {"login": "author"},
            "state": "open",
            "head": source_head(head),
            "base": {"ref": "next", "sha": "a" * 40, "repo": {"full_name": "openai/example"}},
        }
        advanced = {**current, "base": {**current["base"], "sha": "c" * 40}}
        changed_source = {**current, "head": {**current["head"], "ref": "other-source"}}
        for event, mutation, expected in (
            ("pull_request", {}, ["success"] * 2),
            ("merge_group", {}, ["success"] * 2),
            ("pull_request", {"main_sha": "d" * 40}, ["failure"] * 2),
            ("merge_group", {"main_sha": "d" * 40}, ["failure"] * 2),
            ("pull_request", {"current": advanced}, ["failure"] * 2),
            ("merge_group", {"current": advanced}, ["failure"] * 2),
            ("merge_group", {"queue_absent": True}, ["failure"] * 2),
            ("pull_request", {"current": changed_source}, []),
        ):
            with self.subTest(event=event, mutation=mutation):
                result = self.publish(
                    event_name=event,
                    branch="next",
                    bootstrap="true",
                    policy_reviews=[{"number": 3, "head_sha": head}],
                    review_pages=[
                        {
                            "expected_cursor": None,
                            "nodes": [],
                            "pageInfo": {"hasNextPage": True, "endCursor": "last"},
                        },
                        {
                            "expected_cursor": "last",
                            "nodes": [approval],
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                            "after_read": mutation,
                        },
                    ],
                )
                self.assertEqual([item["state"] for item in result], expected)

    def test_queue_policy_approval_dismissal_after_selection_fails(self) -> None:
        candidate = "e" * 40
        for queue_head in (source_head(candidate), {"sha": candidate}):
            with self.subTest(queue_head=queue_head):
                pull: dict[str, Any] = {
                    "number": 7,
                    "user": {"login": "author"},
                    "state": "open",
                    "head": queue_head,
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
        for queue_head in (source_head(candidate), {"sha": candidate}):
            with self.subTest(queue_head=queue_head):
                pull: dict[str, Any] = {
                    "number": 7,
                    "user": {"login": "author"},
                    "state": "open",
                    "head": queue_head,
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

    def test_statuses_recheck_source_identity_immediately_before_writing(self) -> None:
        source = source_head("b" * 40)
        self.assertEqual(len(self.publish(source_changes_during_publication={})), 2)
        for changes in (
            {"ref": "other"},
            {"repo": {**source["repo"], "id": 11}},
            {"repo": {**source["repo"], "full_name": "other/example"}},
            {"repo": None},
        ):
            with self.subTest(changes=changes):
                self.assertEqual(self.publish(source_changes_during_publication=changes), [])

    def test_statuses_reject_a_run_from_a_different_source(self) -> None:
        for source in (
            {"head_branch": "other"},
            {"head_repository": {"id": 11, "full_name": "other/repo"}},
            {"head_repository": None},
        ):
            with self.subTest(source=source):
                self.assertEqual(self.publish(run_overrides=source), [])

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

    def test_foreign_only_associations_retry_source_branch(self) -> None:
        foreign = {
            "number": 4,
            "state": "open",
            "head": {**source_head("b" * 40), "ref": "other"},
            "base": {"ref": "main", "repo": {"full_name": "openai/example"}},
        }
        for explicit in (False, True):
            with self.subTest(explicit=explicit):
                writes = self.publish(
                    run_overrides={"pull_requests": [{"number": 4}] if explicit else []},
                    associated_pulls=[{"number": 4}],
                    fallback_pulls=[{"number": 3}],
                    policy_pull=foreign,
                )
                self.assertEqual(
                    [w["state"] for w in writes], [] if explicit else ["success", "success"]
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
            branch="next",
            run_overrides={"pull_requests": [{"number": 4}]},
            same_head_next_pr=True,
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
                run_overrides={"pull_requests": []},
                fallback_pulls=[{"number": 3}, {"number": 4}],
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

    def test_publication_guard_allows_current_retry_and_ignores_unrelated_statuses(
        self,
    ) -> None:
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
            {
                "description": "[evaluation 999:9:999:9]",
                "target_url": "https://example.com/999",
            },
        ):
            with self.subTest(overrides=overrides):
                results = self.publish(previous_statuses=[{**previous, **overrides}])
                self.assertEqual(len(results), 2)
                self.assertTrue(all(r["state"] == "success" for r in results))
                self.assertTrue(all(len(r["description"]) <= 140 for r in results))
