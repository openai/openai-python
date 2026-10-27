# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
"""Current-main policy selection and review authorization regressions."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
import unittest.mock as mock  # noqa: PLR0402 - keep unittest imports consistent
from collections.abc import Callable
from pathlib import Path
from typing import Any

import custom_code_budget as budget
import custom_code_policy as selector
from custom_code_test_support import GitTestCase

REPO = "openai/example"


class ReviewedPinTests(GitTestCase):
    def setUp(self) -> None:  # pyright: ignore[reportImplicitOverride]
        super().setUp()
        self.git("remote", "add", "origin", f"https://github.com/{REPO}.git")
        self.policy = {"schema_version": 1, "max_custom_patch_lines": 4000}
        self.write_policy(self.policy)
        checker = self.repo / "scripts/castiron/custom_code_budget.py"
        checker.parent.mkdir(parents=True)
        checker.write_text("NEXT_POLICY_VERSION = 1\n")
        checker.with_name("custom_code_policy.py").write_text(
            'PIN_REVIEW_POLICY = "effective-policy-v1"\n'
        )
        self.main = self.commit("main policy")
        self.git("update-ref", "refs/remotes/origin/main", self.main)
        self.pin = {"repository": REPO, "main_sha": self.main}
        self.write_policy({**self.policy, "next_policy": self.pin})
        self.base = self.commit("reviewed next pin")
        self.git("checkout", "-q", "-b", "next", self.base)
        (self.repo / "sdk.txt").write_text("candidate SDK bytes")
        self.head = self.commit("sdk change")

    def test_review_command_uses_git_policies_and_rejects_stale_main(self) -> None:
        git: Callable[..., bytes] = selector.report.git

        def local_fetch(repo: Path, *args: str, **kwargs: Any) -> bytes:
            if args[0] == "fetch":
                return git(
                    repo,
                    "fetch",
                    "--quiet",
                    str(self.repo),
                    f"{self.main}:refs/remotes/origin/main",
                    self.base,
                    self.head,
                )
            return git(repo, *args, **kwargs)

        with (
            tempfile.TemporaryDirectory() as directory,
            mock.patch.object(selector.report, "git", side_effect=local_fetch),
        ):
            for stale in (False, True):
                with (
                    self.subTest(stale=stale),
                    mock.patch("sys.stdout", new_callable=io.StringIO) as output,
                ):
                    args = [
                        "review-required",
                        "--repo",
                        str(Path(directory) / str(stale)),
                        "--repository",
                        REPO,
                        "--base",
                        self.base,
                        "--head",
                        self.head,
                        "--main",
                        self.base if stale else self.main,
                    ]
                    if stale:
                        with self.assertRaisesRegex(ValueError, "authenticated main changed"):
                            selector.main(args)
                        self.assertEqual(output.getvalue(), "")
                    else:
                        self.assertEqual(selector.main(args), 0)
                        self.assertEqual(json.loads(output.getvalue()), {"requires_human": False})

    def write_policy(self, value: dict[str, Any]) -> None:
        (self.repo / ".castiron-ratchet.json").write_text(json.dumps(value))

    def select(
        self, base: str | None = None, head: str | None = None, main: str | None = None, **kw: Any
    ) -> dict[str, Any]:
        return selector.select_policy(
            self.repo,
            REPO,
            "next",
            base or self.base,
            head or self.head,
            main or self.main,
            **kw,
        )

    def review_api(self, reviews: list[dict[str, Any]]) -> Callable[[str, str], Any]:
        def api(method: str, path: str) -> Any:
            if "/commits/" in path:
                return [{"number": 3}]
            if "/reviews?" in path:
                return reviews
            return {
                "number": 3,
                "state": "open",
                "head": {"sha": self.head},
                "base": {"ref": "next", "repo": {"full_name": REPO}},
                "user": {"login": "author"},
            }

        return api

    def test_policy_review_fork_fallback_keeps_live_exact_head_checks(self) -> None:
        original = self.review_api([self.approved()])
        current = original("GET", "repos/openai/example/pulls/3")
        cases: list[tuple[dict[str, Any], bool]] = [
            ({}, True),
            ({"state": "closed"}, False),
            ({"head": {"sha": "f" * 40}}, False),
            ({"base": {"ref": "main", "repo": {"full_name": REPO}}}, False),
            ({"base": {"ref": "next", "repo": {"full_name": "other/repo"}}}, False),
        ]
        for change, accepted in cases:
            with self.subTest(change=change):

                def api(method: str, path: str, change: dict[str, Any] = change) -> Any:
                    if "/commits/" in path:
                        return []
                    if "/pulls?" in path:
                        if path.endswith("page=1"):
                            return [{"head": {"sha": "a" * 40}}] * 100
                        return [current]
                    if path.endswith("/pulls/3"):
                        return {**current, **change}
                    return original(method, path)

                with mock.patch.object(selector.report, "api", side_effect=api):
                    if accepted:
                        self.assertEqual(selector.require_human_policy_review(REPO, self.head), 3)
                    else:
                        with self.assertRaisesRegex(ValueError, "one open next PR"):
                            selector.require_human_policy_review(REPO, self.head)

    def approved(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "id": 10,
            "state": "APPROVED",
            "commit_id": self.head,
            "user": {"type": "User", "login": "reviewer"},
            "author_association": "MEMBER",
            "body": selector.HUMAN_REVIEW_RULES["attestation_prefix"] + self.head,
            **kwargs,
        }

    def test_fork_policy_review_uses_the_discovered_pull(self) -> None:
        self.git("checkout", "-q", "--detach", self.base)
        self.write_policy({**self.policy, "next_policy": self.pin, "max_custom_patch_lines": 5000})
        self.head = self.commit("fork increases policy budget")
        review = self.review_api([self.approved()])
        run: dict[str, Any] = {
            "head_sha": self.head,
            "head_repository": {
                "id": 17,
                "full_name": "forker/example",
                "owner": {"login": "forker"},
            },
            "head_branch": "policy",
            "pull_requests": [],
        }

        def api(method: str, path: str) -> Any:
            if "/commits/" in path:
                return []
            if "/pulls?" in path:
                self.assertIn("head=forker%3Apolicy", path)
                return [{"number": 3}]
            result = review(method, path)
            if path == f"repos/{REPO}/pulls/3":
                result["head"].update(ref="policy", repo=run["head_repository"])
            return result

        with mock.patch.object(selector.report, "api", side_effect=api):
            current = selector.report.current_pull(REPO, run)
            assert current is not None
            number, branch = current
            self.assertEqual(branch, "next")
            result = self.select(base=self.main, pull_numbers={self.head: number})
            self.assertEqual(result["policy_reviews"], [{"number": 3, "head_sha": self.head}])
            with self.assertRaisesRegex(ValueError, "one open next PR"):
                selector.require_human_policy_review(REPO, self.main, number)

    def test_only_base_pin_selects_checker(self) -> None:
        (self.repo / "scripts/castiron/custom_code_budget.py").write_text(
            'raise RuntimeError("candidate code must never execute")\n'
        )
        self.head = self.commit("malicious candidate code")
        self.assertEqual(self.select()["policy_sha"], self.main)
        self.assertEqual(self.select()["schema_version"], 1)

    def test_old_reviewed_pin_survives_main_advancing(self) -> None:
        self.git("checkout", "-q", "--detach", self.main)
        (self.repo / "main-new.txt").write_text("later main")
        later = self.commit("main later")
        self.git("update-ref", "refs/remotes/origin/main", later)
        self.assertEqual(self.select(main=later)["policy_sha"], self.main)

    def test_wrong_repository_and_unadopted_pin_rejected(self) -> None:
        for pin in (
            {"repository": "other/repo", "main_sha": self.main},
            {"repository": REPO, "main_sha": self.head},
        ):
            self.git("checkout", "-q", "--detach", self.base)
            self.write_policy({**self.policy, "next_policy": pin})
            base = self.commit("bad pin")
            with self.assertRaises((ValueError, selector.report.ReportError)):
                self.select(base=base, head=base)

    def test_side_branch_merge_does_not_adopt_policy(self) -> None:
        self.git("checkout", "-q", "--detach", self.main)
        (self.repo / "side").write_text("side")
        side = self.commit("side policy")
        self.git("checkout", "-q", "--detach", self.main)
        (self.repo / "parent").write_text("main")
        self.commit("main")
        self.git("merge", "--no-ff", "-qm", "merge side", side)
        main = self.git("rev-parse", "HEAD")
        self.git("update-ref", "refs/remotes/origin/main", main)
        self.write_policy({**self.policy, "next_policy": {"repository": REPO, "main_sha": side}})
        base = self.commit("next pins side")
        with self.assertRaisesRegex(ValueError, "first-parent"):
            self.select(base=base, head=base, main=main)

    def test_absent_pin_ordinary_change_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "initialization"):
            self.select(base=self.main, head=self.head)

    def test_absent_pin_preserves_value_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "trusted next base has no reviewed policy pin"):
            selector.next_policy_sha(self.repo, REPO, self.main, self.main)

    def test_malformed_base_pin_cannot_bootstrap(self) -> None:
        self.git("checkout", "-q", "--detach", self.main)
        self.write_policy({**self.policy, "next_policy": {}})
        base = self.commit("malformed")
        with self.assertRaisesRegex(ValueError, "exactly"):
            self.select(base=base, head=self.base)

    def test_bootstrap_requires_exact_policy_only_with_native_review(self) -> None:
        self.head = self.base
        with mock.patch.object(selector, "require_human_policy_review") as review:
            result = self.select(base=self.main)
            self.assertTrue(result["bootstrap"])
            self.assertEqual(result["policy_reviews"], [])
            self.assertEqual(result["human_review_rules"], selector.HUMAN_REVIEW_RULES)
            self.assertEqual(result["policy_sha"], self.main)
            review.assert_not_called()
        with self.assertRaisesRegex(ValueError, "policy-only"):
            self.select(base=self.main, head=self.git("rev-parse", "next"))

    def test_queue_bootstrap_isolated_per_constituent(self) -> None:
        self.git("checkout", "-q", "--detach", self.main)
        (self.repo / "unrelated.txt").write_text("independent SDK change")
        sdk_head = self.commit("unrelated PR on unpinned next")
        self.git("merge", "--no-ff", "-qm", "queue initialization and SDK", self.base)
        group = self.git("rev-parse", "HEAD")
        with mock.patch.object(selector, "require_human_policy_review", return_value=3) as review:
            result = self.select(base=self.main, head=group, pull_heads=[self.base, sdk_head])
            self.assertTrue(result["bootstrap"])
            self.assertEqual(result["policy_sha"], self.main)
            self.assertEqual(result["policy_reviews"], [])
            review.assert_not_called()
        for heads in (None, [group]):
            with self.subTest(heads=heads), self.assertRaisesRegex(ValueError, "policy-only"):
                self.select(base=self.main, head=group, pull_heads=heads)
        with self.assertRaisesRegex(ValueError, "verified constituent"):
            self.select(base=self.main, head=group, pull_heads=[])
        with self.assertRaisesRegex(ValueError, "verified policy-only constituent"):
            self.select(base=self.main, head=group, pull_heads=[sdk_head])

    def test_queue_pin_update_isolated_per_constituent(self) -> None:
        self.git("checkout", "-q", "--detach", self.main)
        (self.repo / "main-new.txt").write_text("later main")
        later = self.commit("main later")
        self.git("update-ref", "refs/remotes/origin/main", later)
        self.git("checkout", "-q", "--detach", self.base)
        self.write_policy({**self.policy, "next_policy": {"repository": REPO, "main_sha": later}})
        pin_head = self.commit("isolated pin update")
        self.git("merge", "--no-ff", "-qm", "queue group", self.head)
        group = self.git("rev-parse", "HEAD")
        with mock.patch.object(selector, "require_human_policy_review", return_value=3) as review:
            result = self.select(head=group, main=later, pull_heads=[pin_head, self.head])
            self.assertEqual(result["policy_sha"], self.main)
            self.assertEqual(result["policy_reviews"], [])
            review.assert_not_called()
        # A combined SDK/pin change in one PR is still forbidden.
        with self.assertRaisesRegex(ValueError, "policy-only"):
            self.select(head=group, main=later)
        with self.assertRaisesRegex(ValueError, "policy-only"):
            self.select(head=group, main=later, pull_heads=[group])

    def advanced_pin_base(self) -> tuple[str, str]:
        self.git("checkout", "-q", "--detach", self.main)
        (self.repo / "later-main.txt").write_text("later main")
        later = self.commit("later approved main")
        self.git("update-ref", "refs/remotes/origin/main", later)
        self.git("checkout", "-q", "--detach", self.base)
        self.write_policy({**self.policy, "next_policy": {"repository": REPO, "main_sha": later}})
        return later, self.commit("reviewed pin update on next")

    def test_stale_sdk_branch_uses_current_protected_pin(self) -> None:
        later, base = self.advanced_pin_base()
        with mock.patch.object(selector, "require_human_policy_review") as review:
            result = self.select(base=base, main=later)
            self.assertEqual(result["policy_sha"], later)
            self.assertEqual(result["policy_reviews"], [])
            review.assert_not_called()

    def test_queue_stale_sdk_constituent_inherits_protected_pin(self) -> None:
        later, base = self.advanced_pin_base()
        self.git("merge", "--no-ff", "-qm", "queue SDK branch", self.head)
        group = self.git("rev-parse", "HEAD")
        with mock.patch.object(selector, "require_human_policy_review") as review:
            result = self.select(base=base, head=group, main=later, pull_heads=[self.head])
            self.assertEqual(result["policy_sha"], later)
            self.assertEqual(result["policy_reviews"], [])
            review.assert_not_called()

    def test_stale_actual_pin_edit_still_requires_isolation(self) -> None:
        later, base = self.advanced_pin_base()
        self.git("checkout", "-q", "--detach", self.base)
        self.write_policy({**self.policy, "next_policy": {"repository": REPO, "main_sha": later}})
        edited = self.commit("PR independently edits pin")
        with mock.patch.object(selector, "require_human_policy_review", return_value=3) as review:
            result = self.select(base=base, head=edited, main=later)
            self.assertEqual(result["policy_reviews"], [])
            review.assert_not_called()
        (self.repo / "mixed-sdk.txt").write_text("SDK change")
        mixed = self.commit("mix policy and SDK")
        with self.assertRaisesRegex(ValueError, "policy-only"):
            self.select(base=base, head=mixed, main=later)
        with self.assertRaisesRegex(ValueError, "policy-only"):
            self.select(base=base, head=mixed, main=later, pull_heads=[mixed])

    def test_stale_sdk_budget_after_target_decrease_needs_no_review(self) -> None:
        self.git("checkout", "-q", "--detach", self.base)
        self.write_policy({**self.policy, "next_policy": self.pin, "max_custom_patch_lines": 3000})
        base = self.commit("lower protected next budget")
        self.git("merge", "--no-ff", "-qm", "queue stale SDK branch", self.head)
        group = self.git("rev-parse", "HEAD")
        for head, heads in ((self.head, None), (group, [self.head])):
            with (
                self.subTest(head=head),
                mock.patch.object(selector, "require_human_policy_review") as review,
            ):
                result = self.select(base=base, head=head, pull_heads=heads)
                self.assertEqual(result["policy_sha"], self.main)
                self.assertEqual(result["base_sha"], base)
                self.assertEqual(result["policy_reviews"], [])
                self.assertEqual(budget.read_budget(self.repo, base), 3000)
                review.assert_not_called()

    def test_actual_budget_increase_is_reviewed_even_if_target_increased_further(self) -> None:
        self.git("checkout", "-q", "--detach", self.base)
        self.write_policy({**self.policy, "next_policy": self.pin, "max_custom_patch_lines": 6000})
        base = self.commit("reviewed target budget increase")
        self.git("checkout", "-q", "--detach", self.base)
        self.write_policy({**self.policy, "next_policy": self.pin, "max_custom_patch_lines": 5000})
        edited = self.commit("PR actually raises budget")
        for heads in (None, [edited]):
            with (
                mock.patch.object(
                    selector,
                    "require_human_policy_review",
                    side_effect=ValueError("human required"),
                ),
                self.assertRaisesRegex(ValueError, "human"),
            ):
                self.select(base=base, head=edited, pull_heads=heads)
        (self.repo / "mixed-sdk.txt").write_text("SDK change")
        mixed = self.commit("mix SDK and actual budget increase")
        with self.assertRaisesRegex(ValueError, "policy-only"):
            self.select(base=base, head=mixed)

    def test_selector_outputs_transport_review_receipt_as_json(self) -> None:
        event = self.repo / "event.json"
        event.write_text("{}")
        out, output = self.repo / "selection.json", self.repo / "outputs"
        selected = {
            "schema_version": 1,
            "policy_reviews": [{"number": 3, "head_sha": self.head}],
            "human_review_rules": selector.HUMAN_REVIEW_RULES,
            "bootstrap": False,
        }
        args = [
            "budget",
            "select-policy",
            "--repo",
            str(self.repo / "objects.git"),
            "--repository",
            REPO,
            "--event-path",
            str(event),
            "--trusted-sha",
            self.main,
            "--out",
            str(out),
        ]
        with (
            mock.patch.object(sys, "argv", args),
            mock.patch.dict(selector.os.environ, {"GITHUB_OUTPUT": str(output)}),
            mock.patch.object(selector, "select_github_policy", return_value=selected),
        ):
            self.assertEqual(selector.main(), 0)
        values = dict(line.split("=", 1) for line in output.read_text().splitlines())
        self.assertEqual(json.loads(values["policy_reviews"]), selected["policy_reviews"])
        self.assertEqual(json.loads(values["human_review_rules"]), selector.HUMAN_REVIEW_RULES)
        self.assertFalse(json.loads(values["bootstrap"]))
        self.assertEqual(json.loads(out.read_text())["schema_version"], 1)

    def test_follow_up_comments_preserve_policy_approval(self) -> None:
        approval = self.approved()
        for state in ("COMMENTED", "PENDING"):
            follow_up = self.approved(id=11, state=state, body="A non-blocking follow-up")
            for reviews in ([approval, follow_up], [follow_up, approval]):
                with (
                    self.subTest(state=state, reviews=reviews),
                    mock.patch.object(selector.report, "api", side_effect=self.review_api(reviews)),
                ):
                    self.assertEqual(selector.require_human_policy_review(REPO, self.head), 3)

    def test_comments_do_not_restore_revoked_policy_approval(self) -> None:
        comment = self.approved(id=12, state="COMMENTED", body="A follow-up comment")
        cases = [
            [self.approved(), self.approved(id=11, state="CHANGES_REQUESTED"), comment],
            [self.approved(state="DISMISSED"), comment],
            [self.approved(body="Attestation removed"), comment],
            [comment],
        ]
        for reviews in cases:
            with (
                self.subTest(reviews=reviews),
                mock.patch.object(selector.report, "api", side_effect=self.review_api(reviews)),
                self.assertRaisesRegex(ValueError, "human"),
            ):
                selector.require_human_policy_review(REPO, self.head)

    def test_forged_bot_stale_dismissed_untrusted_reviews_rejected(self) -> None:
        self.git("checkout", "-q", "--detach", self.base)
        self.write_policy(
            {
                **self.policy,
                "next_policy": self.pin,
                "max_custom_patch_lines": self.policy["max_custom_patch_lines"] + 1,
            }
        )
        self.head = self.commit("bootstrap pin with budget increase")
        cases = [
            [],
            [self.approved(body="")],
            [self.approved(body="Looks good to me")],
            [self.approved(body=selector.HUMAN_REVIEW_RULES["attestation_prefix"] + "f" * 40)],
            [self.approved(state="COMMENTED", body="APPROVED by a human")],
            [self.approved(user={"type": "Bot", "login": "reviewer[bot]"})],
            [self.approved(commit_id="a" * 40)],
            [self.approved(author_association="NONE")],
            [
                self.approved(
                    user={"type": "User", "login": "dpiet-oai"},
                    body="<!-- pr-review:automated-review:v1 -->",
                )
            ],
            [
                self.approved(
                    user={"type": "User", "login": "markstuart-oai"},
                    body="Reviewed `f4c5de3e28ea4c21c2a3d230d06341c3c25a0004`. No actionable findings in the two workflow changes. Adding `next` retains the existing CodeQL and exported-API jobs, uses the actual PR or merge-group comparison base, and leaves merge-group triggers and main-only release/credential guards intact.\n\nSource-only review; I did not execute candidate code or workflows. Current-head CodeQL and exported-API checks passed. Some hosted ecosystem and Node-version tests are still pending. Branch protection settings and the author's branch-creation claims were not independently verified; required CI and review gates still apply.",
                )
            ],
            [self.approved(body="Automated source review.")],
            [self.approved(body="This does not substitute for human approval.")],
            [self.approved(body="This does not constitute human approval.")],
            [self.approved(body="This is not a human approving review.")],
            [self.approved(), self.approved(id=11, state="DISMISSED")],
        ]
        for reviews in cases:
            with (
                self.subTest(reviews=reviews),
                mock.patch.object(selector.report, "api", side_effect=self.review_api(reviews)),
                self.assertRaisesRegex(ValueError, "human"),
            ):
                self.select(base=self.main)

    def test_bootstrap_budget_increase_keeps_human_proof_for_pr_and_queue(self) -> None:
        self.git("checkout", "-q", "--detach", self.base)
        self.write_policy(
            {
                **self.policy,
                "next_policy": self.pin,
                "max_custom_patch_lines": self.policy["max_custom_patch_lines"] + 1,
            }
        )
        self.head = self.commit("bootstrap pin with budget increase")
        for heads in (None, [self.head]):
            with (
                mock.patch.object(selector.report, "api", side_effect=self.review_api([])),
                self.assertRaisesRegex(ValueError, "human"),
            ):
                self.select(base=self.main, pull_heads=heads)
            with mock.patch.object(
                selector.report, "api", side_effect=self.review_api([self.approved()])
            ):
                result = self.select(base=self.main, pull_heads=heads)
                self.assertEqual(result["policy_reviews"], [{"number": 3, "head_sha": self.head}])

    def test_authorless_review_does_not_block_valid_approval(self) -> None:
        self.git("checkout", "-q", "--detach", self.base)
        policy = selector.read_policy(self.repo, self.base)
        self.write_policy(
            {**policy, "max_custom_patch_lines": policy["max_custom_patch_lines"] + 1}
        )
        self.head = self.commit("increase budget")
        reviews = [self.approved(id=9, user=None), self.approved()]
        with mock.patch.object(selector.report, "api", side_effect=self.review_api(reviews)):
            self.assertEqual(
                self.select()["policy_reviews"],
                [{"number": 3, "head_sha": self.head}],
            )

    def test_budget_increase_without_pin_change_requires_human(self) -> None:
        self.git("checkout", "-q", "--detach", self.base)
        policy = selector.read_policy(self.repo, self.base)
        self.write_policy(
            {**policy, "max_custom_patch_lines": policy["max_custom_patch_lines"] + 1}
        )
        self.head = self.commit("increase budget without changing pin")
        for reviews in ([], [self.approved(body="Automated source review.")]):
            with (
                mock.patch.object(selector.report, "api", side_effect=self.review_api(reviews)),
                self.assertRaisesRegex(ValueError, "human"),
            ):
                self.select()
        with mock.patch.object(
            selector.report, "api", side_effect=self.review_api([self.approved()])
        ):
            self.assertEqual(self.select()["policy_sha"], self.main)

    def test_changed_authenticated_main_ref_rejected(self) -> None:
        self.git("update-ref", "refs/remotes/origin/main", self.head)
        with self.assertRaisesRegex(ValueError, "changed"):
            self.select()

    def test_go_ratchet_activation_requires_human_for_pr_and_queue(self) -> None:
        self.git("checkout", "-q", "--detach", self.base)
        self.write_policy({**selector.read_policy(self.repo, self.base), "ratchet": "go"})
        self.head = self.commit("activate Go ratchet without changing pin or ceiling")
        for pull_heads in (None, [self.head]):
            for reviews in ([], [self.approved(body="Automated source review.")]):
                with (
                    self.subTest(pull_heads=pull_heads, reviews=reviews),
                    mock.patch.object(selector.report, "api", side_effect=self.review_api(reviews)),
                    self.assertRaisesRegex(ValueError, "human"),
                ):
                    self.select(pull_heads=pull_heads)
            with mock.patch.object(
                selector.report, "api", side_effect=self.review_api([self.approved()])
            ):
                selected = self.select(pull_heads=pull_heads)
                self.assertEqual(selected["policy_sha"], self.main)
                self.assertEqual(selected["policy_reviews"], [{"number": 3, "head_sha": self.head}])

    def test_wrong_origin_rejected(self) -> None:
        self.git("remote", "set-url", "origin", "https://github.com/attacker/example.git")
        with self.assertRaisesRegex(ValueError, "origin"):
            self.select()

    def test_same_repository_github_url_spellings_are_accepted(self) -> None:
        for origin in (
            f"https://github.com/{REPO}.git",
            f"https://github.com/{REPO}",
            f"git@github.com:{REPO}.git",
        ):
            with self.subTest(origin=origin):
                self.git("remote", "set-url", "origin", origin)
                self.assertEqual(self.select()["policy_sha"], self.main)

    def test_policy_update_uses_old_base_checker_and_requires_human(self) -> None:
        self.git("checkout", "-q", "--detach", self.main)
        self.write_policy({**self.policy, "max_custom_patch_lines": 5000})
        newer = self.commit("new reviewed main policy")
        self.git("update-ref", "refs/remotes/origin/main", newer)
        self.git("checkout", "-q", "--detach", self.base)
        self.write_policy({**self.policy, "next_policy": {"repository": REPO, "main_sha": newer}})
        self.head = self.commit("request new pin")
        with mock.patch.object(
            selector.report, "api", side_effect=self.review_api([self.approved()])
        ):
            self.assertEqual(self.select(main=newer)["policy_sha"], self.main)
        with (
            mock.patch.object(selector.report, "api", side_effect=self.review_api([])),
            self.assertRaisesRegex(ValueError, "human"),
        ):
            self.select(main=newer)

    def test_pin_effective_policy_review_for_pr_and_queue(self) -> None:
        cases = (
            ({**self.policy, "max_custom_patch_lines": 4000}, False),
            ({**self.policy, "max_custom_patch_lines": 3999}, False),
            ({**self.policy, "max_custom_patch_lines": 5000}, True),
            ({**self.policy, "ratchet": "go"}, True),
            ({"schema_version": 2, "max_custom_patch_lines": 0, "generated_files": "strict"}, True),
        )
        for proposed, requires_human in cases:
            self.git("checkout", "-q", "--detach", self.main)
            self.write_policy(proposed)
            newer = self.commit("adopt proposed effective policy")
            self.git("update-ref", "refs/remotes/origin/main", newer)
            for bootstrap in (False, True):
                base = self.main if bootstrap else self.base
                self.git("checkout", "-q", "--detach", base)
                self.write_policy(
                    {**self.policy, "next_policy": {"repository": REPO, "main_sha": newer}}
                )
                self.head = self.commit("request pin without changing local budget")
                for heads in (None, [self.head]):
                    with self.subTest(proposed=proposed, bootstrap=bootstrap, heads=heads):
                        needs_proof = requires_human and not bootstrap
                        with mock.patch.object(
                            selector,
                            "require_human_policy_review",
                            side_effect=ValueError("human review missing"),
                        ) as review:
                            if needs_proof:
                                with self.assertRaisesRegex(ValueError, "human"):
                                    self.select(base=base, main=newer, pull_heads=heads)
                                review.assert_called_once_with(REPO, self.head, None)
                            else:
                                result = self.select(base=base, main=newer, pull_heads=heads)
                                review.assert_not_called()
                                self.assertEqual(result["policy_reviews"], [])
                        if needs_proof:
                            with mock.patch.object(
                                selector.report,
                                "api",
                                side_effect=self.review_api([self.approved()]),
                            ):
                                result = self.select(base=base, main=newer, pull_heads=heads)
                                self.assertEqual(
                                    result["policy_reviews"], [{"number": 3, "head_sha": self.head}]
                                )

    def test_legacy_checker_pin_review_receipt_for_pr_and_queue(self) -> None:
        declarations = (
            None,
            'PIN_REVIEW_POLICY = "unknown"\n',
            'PIN_REVIEW_POLICY = "effective-policy-v1"\n' * 2,
        )
        for declaration in declarations:
            self.git("checkout", "-q", "--detach", self.main)
            checker = self.repo / "scripts/castiron/custom_code_policy.py"
            if declaration is None:
                checker.unlink()
            else:
                checker.write_text(declaration)
            legacy = self.commit("legacy review contract")
            checker.write_text('PIN_REVIEW_POLICY = "effective-policy-v1"\n')
            newer = self.commit("modern review contract")
            self.git("update-ref", "refs/remotes/origin/main", newer)
            self.git("checkout", "-q", "--detach", legacy)
            self.write_policy(
                {**self.policy, "next_policy": {"repository": REPO, "main_sha": legacy}}
            )
            base = self.commit("protected legacy checker")
            self.write_policy(
                {**self.policy, "next_policy": {"repository": REPO, "main_sha": newer}}
            )
            self.head = self.commit("forward same-budget pin")
            for heads in (None, [self.head]):
                with self.subTest(declaration=declaration, heads=heads):
                    with (
                        mock.patch.object(selector.report, "api", side_effect=self.review_api([])),
                        self.assertRaisesRegex(ValueError, "human"),
                    ):
                        self.select(base=base, main=newer, pull_heads=heads)
                    with mock.patch.object(
                        selector.report, "api", side_effect=self.review_api([self.approved()])
                    ):
                        result = self.select(base=base, main=newer, pull_heads=heads)
                        self.assertEqual(result["policy_sha"], legacy)
                        self.assertEqual(
                            result["policy_reviews"], [{"number": 3, "head_sha": self.head}]
                        )

    def test_rollback_pin_keeps_human_proof_for_pr_and_queue(self) -> None:
        self.git("checkout", "-q", "--detach", self.main)
        (self.repo / "checker-fix.txt").write_text("reviewed checker fix")
        newer = self.commit("newer main checker with unchanged policy")
        self.git("update-ref", "refs/remotes/origin/main", newer)
        self.git("checkout", "-q", "--detach", self.base)
        self.write_policy({**self.policy, "next_policy": {"repository": REPO, "main_sha": newer}})
        advanced_base = self.commit("adopt newer checker")
        self.write_policy({**self.policy, "next_policy": self.pin})
        self.head = self.commit("roll back checker without changing budget")
        for heads in (None, [self.head]):
            with (
                mock.patch.object(selector.report, "api", side_effect=self.review_api([])),
                self.assertRaisesRegex(ValueError, "human"),
            ):
                self.select(base=advanced_base, main=newer, pull_heads=heads)
            with mock.patch.object(
                selector.report, "api", side_effect=self.review_api([self.approved()])
            ):
                result = self.select(base=advanced_base, main=newer, pull_heads=heads)
                self.assertEqual(result["policy_sha"], newer)
                self.assertEqual(result["policy_reviews"], [{"number": 3, "head_sha": self.head}])

    def test_stale_pin_compares_current_protected_policy_for_pr_and_queue(self) -> None:
        for protected_policy in (
            self.policy,
            {**self.policy, "max_custom_patch_lines": 3999},
            {"schema_version": 2, "max_custom_patch_lines": 0, "generated_files": "strict"},
        ):
            self.git("checkout", "-q", "--detach", self.main)
            (self.repo / "checker-fix.txt").write_text("intermediate checker")
            intermediate = self.commit("intermediate main checker")
            self.write_policy(protected_policy)
            (self.repo / "checker-fix.txt").write_text("protected checker")
            current = self.commit("current main checker")
            (self.repo / "checker-fix.txt").write_text("forward checker")
            forward = self.commit("forward main checker")
            self.git("update-ref", "refs/remotes/origin/main", forward)
            self.git("checkout", "-q", "--detach", self.base)
            self.write_policy(
                {**self.policy, "next_policy": {"repository": REPO, "main_sha": current}}
            )
            protected_base = self.commit("advance protected next pin")
            for proposed in (intermediate, current, forward):
                self.git("checkout", "-q", "--detach", self.base)
                self.write_policy(
                    {**self.policy, "next_policy": {"repository": REPO, "main_sha": proposed}}
                )
                self.head = self.commit("stale policy-only PR")
                for heads in (None, [self.head]):
                    with self.subTest(policy=protected_policy, proposed=proposed, heads=heads):
                        with mock.patch.object(
                            selector.report, "api", side_effect=self.review_api([])
                        ):
                            if proposed == intermediate:
                                with self.assertRaisesRegex(ValueError, "human"):
                                    self.select(base=protected_base, main=forward, pull_heads=heads)
                            else:
                                result = self.select(
                                    base=protected_base, main=forward, pull_heads=heads
                                )
                                self.assertEqual(result["policy_reviews"], [])
                        with mock.patch.object(
                            selector.report, "api", side_effect=self.review_api([self.approved()])
                        ):
                            result = self.select(
                                base=protected_base, main=forward, pull_heads=heads
                            )
                            self.assertEqual(result["policy_sha"], current)
                            self.assertEqual(
                                result["policy_reviews"],
                                [{"number": 3, "head_sha": self.head}]
                                if proposed == intermediate
                                else [],
                            )

    def test_initial_older_pin_keeps_human_proof_for_pr_and_queue(self) -> None:
        self.git("checkout", "-q", "--detach", self.main)
        (self.repo / "checker-fix.txt").write_text("reviewed bootstrap checker fix")
        newer = self.commit("newer main checker with unchanged policy")
        self.git("update-ref", "refs/remotes/origin/main", newer)
        for pin_sha in (self.main, newer):
            self.git("checkout", "-q", "--detach", self.main)
            self.write_policy(
                {**self.policy, "next_policy": {"repository": REPO, "main_sha": pin_sha}}
            )
            self.head = self.commit("initial checker pin")
            for heads in (None, [self.head]):
                with mock.patch.object(selector.report, "api", side_effect=self.review_api([])):
                    if pin_sha == self.main:
                        with self.assertRaisesRegex(ValueError, "human"):
                            self.select(base=self.main, main=newer, pull_heads=heads)
                    else:
                        result = self.select(base=self.main, main=newer, pull_heads=heads)
                        self.assertEqual(result["policy_reviews"], [])
                        self.assertEqual(result["policy_sha"], newer)
                with mock.patch.object(
                    selector.report, "api", side_effect=self.review_api([self.approved()])
                ):
                    result = self.select(base=self.main, main=newer, pull_heads=heads)
                    self.assertEqual(result["policy_sha"], newer)
                    self.assertTrue(result["bootstrap"])
                    self.assertEqual(
                        result["policy_reviews"],
                        [{"number": 3, "head_sha": self.head}] if pin_sha == self.main else [],
                    )

    def test_bootstrap_uses_active_main_policy_for_pr_and_queue(self) -> None:
        self.git("checkout", "-q", "--detach", self.main)
        self.write_policy(
            {"schema_version": 2, "max_custom_patch_lines": 0, "generated_files": "strict"}
        )
        current = self.commit("main activates strict zero policy")
        self.git("update-ref", "refs/remotes/origin/main", current)
        for proposed in (self.main, current):
            self.git("checkout", "-q", "--detach", self.main)
            self.write_policy(
                {**self.policy, "next_policy": {"repository": REPO, "main_sha": proposed}}
            )
            self.head = self.commit("initial pin with unchanged legacy local ceiling")
            for heads in (None, [self.head]):
                with self.subTest(proposed=proposed, heads=heads):
                    with mock.patch.object(selector.report, "api", side_effect=self.review_api([])):
                        if proposed == self.main:
                            with self.assertRaisesRegex(ValueError, "human"):
                                self.select(base=self.main, main=current, pull_heads=heads)
                        else:
                            result = self.select(base=self.main, main=current, pull_heads=heads)
                            self.assertEqual(result["policy_reviews"], [])
                            self.assertEqual(result["policy_sha"], current)
                    with mock.patch.object(
                        selector.report, "api", side_effect=self.review_api([self.approved()])
                    ):
                        result = self.select(base=self.main, main=current, pull_heads=heads)
                        self.assertTrue(result["bootstrap"])
                        self.assertEqual(result["policy_sha"], current)
                        self.assertEqual(
                            result["policy_reviews"],
                            [{"number": 3, "head_sha": self.head}] if proposed == self.main else [],
                        )

    def test_incapable_policy_is_not_executed(self) -> None:
        self.git("checkout", "-q", "--detach", self.main)
        (self.repo / "scripts/castiron/custom_code_budget.py").write_text(
            "raise RuntimeError('must not execute')\n"
        )
        incapable = self.commit("old checker without pin protocol")
        self.git("update-ref", "refs/remotes/origin/main", incapable)
        self.write_policy(
            {**self.policy, "next_policy": {"repository": REPO, "main_sha": incapable}}
        )
        base = self.commit("pin incapable checker")
        with self.assertRaisesRegex(ValueError, "does not support"):
            self.select(base=base, head=base, main=incapable)

    def test_main_selection_unchanged(self) -> None:
        result = selector.select_policy(self.repo, REPO, "main", self.main, self.head, self.main)
        self.assertEqual(result["policy_sha"], self.main)
        self.assertFalse(result["bootstrap"])

    def prepare_snapshot(self) -> None:
        self.git("checkout", "-q", "--detach", self.main)
        self.base = self.main  # unpinned legacy next
        self.strict = {
            "schema_version": 2,
            "max_custom_patch_lines": 0,
            "generated_files": "strict",
        }
        self.write_policy(self.strict)
        self.write("sdk.txt", "approved main output\n")
        self.write(
            ".castiron.stats.yml",
            "schema_version: 1\ngeneration_id: 550e8400-e29b-41d4-a716-446655440000\ncodegen_sha: "
            + "a" * 40
            + "\npublic_codegen_sha: "
            + "a" * 40
            + "\n",
        )
        self.main = self.commit("strict main snapshot")
        self.git("update-ref", "refs/remotes/origin/main", self.main)
        self.write_policy(
            {**self.strict, "next_policy": {"repository": REPO, "main_sha": self.main}}
        )
        tree_commit = self.commit("adopt exact main snapshot")
        self.head = self.git(
            "commit-tree",
            f"{tree_commit}^{{tree}}",
            "-p",
            self.base,
            "-p",
            self.main,
            "-m",
            "canonical snapshot",
        )
        self.git("checkout", "--detach", "-q", self.head)

    def test_exact_main_snapshot_pr_and_queue(self) -> None:
        self.prepare_snapshot()
        for queue in (False, True):
            with (
                self.subTest(queue=queue),
                mock.patch.object(
                    selector.report, "api", side_effect=AssertionError("no human proof needed")
                ),
            ):
                receipt = self.select(pull_heads=[self.head] if queue else None)
                self.assertEqual(receipt["main_snapshot"], self.main)
                self.assertEqual(receipt["policy_sha"], self.main)
                self.assertEqual(receipt["policy_reviews"], [])

    def test_snapshot_rejects_additional_bytes_modes_or_metadata(self) -> None:
        self.prepare_snapshot()
        valid = self.head
        for kind in ("content", "mode", "extra", "stats", "symlink"):
            for queue in (False, True):
                with self.subTest(kind=kind, queue=queue):
                    self.git("reset", "--hard", valid)
                    if kind == "content":
                        self.write("sdk.txt", "unreviewed output\n")
                    elif kind == "mode":
                        (self.repo / "sdk.txt").chmod(0o755)
                    elif kind == "extra":
                        self.write("extra.txt", "extra")
                    elif kind == "stats":
                        self.write(".castiron.stats.yml", "schema_version: 1\n")
                    else:
                        (self.repo / "sdk.txt").unlink()
                        (self.repo / "sdk.txt").symlink_to(".castiron.stats.yml")
                    self.head = self.commit("invalid adoption")
                    with self.assertRaises(ValueError):
                        self.select(pull_heads=[self.head] if queue else None)

    def test_snapshot_rejects_main_movement_and_nonancestor_target(self) -> None:
        self.prepare_snapshot()
        old_main = self.main
        candidate = self.head
        self.git("checkout", "-q", "--detach", old_main)
        self.write("sdk.txt", "new approved main\n")
        self.main = self.commit("main advances")
        self.git("update-ref", "refs/remotes/origin/main", self.main)
        with self.assertRaises(ValueError):
            self.select(head=candidate)
        self.main = old_main
        self.git("update-ref", "refs/remotes/origin/main", self.main)
        self.git("checkout", "-q", "--detach", self.base)
        self.write("private-only.txt", "unmerged next history")
        self.base = self.commit("divergent next")
        with self.assertRaises(ValueError):
            self.select(head=candidate)

    def test_snapshot_rejects_private_history_but_accepts_verified_queue_wrapper(self) -> None:
        self.prepare_snapshot()
        constituent = self.head
        wrapper = self.git(
            "commit-tree",
            f"{constituent}^{{tree}}",
            "-p",
            self.base,
            "-p",
            constituent,
            "-m",
            "queue wrapper",
        )
        self.assertEqual(
            self.select(head=wrapper, pull_heads=[constituent])["main_snapshot"], self.main
        )
        with self.assertRaises(ValueError):
            self.select(head=wrapper)  # A wrapper is not an independently verified PR head.
        self.write("private.txt", "private-only historical bytes")
        self.commit("private historical commit")
        (self.repo / "private.txt").unlink()
        reverted = self.commit("revert private historical bytes")
        self.assertEqual(
            self.git("rev-parse", f"{reverted}^{{tree}}"),
            self.git("rev-parse", f"{constituent}^{{tree}}"),
        )
        for heads in (None, [reverted]):
            with self.subTest(queue=heads is not None), self.assertRaises(ValueError):
                self.select(head=reverted, pull_heads=heads)

    def test_snapshot_rejects_multiple_queue_constituents(self) -> None:
        self.prepare_snapshot()
        with self.assertRaisesRegex(ValueError, "one exact"):
            self.select(pull_heads=[self.head, self.head])


if __name__ == "__main__":
    unittest.main()
