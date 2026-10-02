# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
from __future__ import annotations

import base64
import hashlib
import json
import os
import struct
import subprocess
import unittest
import unittest.mock as mock

import custom_code_report as report

from custom_code_test_support import GENERATION, GitTestCase


class CustomCodeTests(GitTestCase):
    def test_git_preserves_authentication_without_inherited_repository_routing(self) -> None:
        environment = {
            "GIT_CONFIG_GLOBAL": "/ordinary/gitconfig",
            "GIT_ASKPASS": "/ordinary/askpass",
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "credential.helper",
            "GIT_CONFIG_VALUE_0": "example",
            "GIT_DIR": "/wrong/repository",
            "GIT_COMMON_DIR": "/wrong/common",
            "GIT_INDEX_FILE": "/wrong/index",
        }
        with (
            mock.patch.dict(os.environ, environment),
            mock.patch.object(
                report.subprocess,
                "run",
                return_value=subprocess.CompletedProcess([], 0, stdout=b"ok"),
            ) as run,
        ):
            self.assertEqual(report.git(self.repo, "status"), b"ok")
        actual = run.call_args.kwargs["env"]
        for name, value in environment.items():
            if name in {"GIT_DIR", "GIT_COMMON_DIR", "GIT_INDEX_FILE"}:
                self.assertNotIn(name, actual)
            else:
                self.assertEqual(actual[name], value)
        self.assertEqual(actual["GIT_NO_REPLACE_OBJECTS"], "1")

    @unittest.skipUnless(os.environ.get("CASTIRON_TEST_BIN"), "Castiron compiler contract test")
    def test_rust_and_python_hashes_match(self) -> None:
        self.write("a", "first\n")
        self.write("nested/b", "second\n")
        self.write(".github/workflows/ignored.yml", "ignored\n")
        for change in ("initial", "mode", "bytes"):
            if change == "mode":
                (self.repo / "a").chmod(0o755)
            elif change == "bytes":
                self.write("nested/b", "changed\n")
            commit = self.commit(change)
            rust = subprocess.check_output(
                [
                    os.environ["CASTIRON_TEST_BIN"],
                    "sdk",
                    "codegen-hash",
                    "--repo",
                    str(self.repo),
                    "--commit",
                    commit,
                ],
                text=True,
            ).strip()
            self.assertEqual(rust, report.hash_codegen_commit(self.repo, commit))

    def test_reporting_script_can_be_a_mixed_file(self) -> None:
        path = "scripts/castiron/custom_code_report.py"
        self.write(path, "# generated reporter\n")
        _, base = self.baseline()
        self.write(path, "# generated reporter\n# local customization\n")
        head = self.commit()
        result, _ = report.build_report(self.repo, base, head, require_head_hash=True)
        changed = next(file for file in result["files"] if file["path"] == path)
        self.assertEqual(changed["category"], "newly_customized")

    def test_hash_vector_and_exclusions(self) -> None:
        self.write("a", "hello\n")
        first = self.commit()
        encoded = (
            report.DOMAIN
            + struct.pack(">Q", 1)
            + struct.pack(">Q", 1)
            + b"a100644"
            + struct.pack(">Q", 6)
            + b"hello\n"
        )
        expected = hashlib.sha256(encoded).hexdigest()
        self.assertEqual(report.hash_codegen_commit(self.repo, first), expected)
        self.write(".github/workflows/test.yml", "ignored\n")
        self.write(".github/actions/test/action.yml", "ignored\n")
        second = self.commit()
        self.assertEqual(report.hash_codegen_commit(self.repo, second), expected)
        os.chmod(self.repo / "a", 0o755)
        self.assertNotEqual(report.hash_codegen_commit(self.repo, self.commit()), expected)
        self.write(".github/CODEOWNERS", "not ignored\n")
        self.assertNotEqual(report.hash_codegen_commit(self.repo, self.commit()), expected)

    def test_classifications(self) -> None:
        a, b, c = (report.Entry(b"100644", value * 40) for value in "abc")
        cases = [
            ((a, a, b, b), None),
            ((a, a, a, b), "newly_customized"),
            ((a, b, a, a), "removed"),
            ((a, b, a, c), "existing_changed"),
            ((a, b, a, b), "unchanged"),
            ((a, b, c, b), "baseline_changed"),
            ((a, b, None, b), "no_longer_generated"),
            ((a, a, None, a), "no_longer_generated"),
            ((a, a, None, None), None),
            ((None, b, a, b), "newly_generation_owned"),
            ((None, a, a, a), "newly_generation_owned"),
            ((a, a, b, a), "baseline_changed"),
            ((a, b, b, b), "baseline_changed"),
            ((a, a, a, None), "newly_customized"),
        ]
        for values, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(report.classify(*values), expected)

    def test_report_ignores_handwritten_files_and_shows_custom_patch(self) -> None:
        generated, base = self.baseline()
        self.write("generated.py", "generated\n# custom\n")
        self.write("handwritten.py", "handwritten\n")
        head = self.commit()
        result, patch = report.build_report(self.repo, base, head, require_head_hash=True)
        self.assertEqual(result["counts"]["newly_customized"], 1)
        self.assertEqual(result["files"][0]["path"], "generated.py")
        self.assertIn(b"+# custom", patch)
        self.assertNotIn(b"handwritten", patch)
        self.assertEqual(result["after"]["commit"], generated)
        body = report.render_report(result, repository="openai/example", run_id=42, run_attempt=2)
        self.assertIn("<summary>Inspect the custom-code diff</summary>", body)
        self.assertIn("gh run download 42 --repo openai/example", body)
        self.assertIn("--name castiron-custom-code-42-2", body)
        self.assertIn(f"--head {head}", body)
        self.assertIn("current full custom patch", body)

    def test_bad_hash_and_lost_checkpoint_fail(self) -> None:
        generated, base = self.baseline()
        stats = self.repo / ".castiron.stats.yml"
        stats.write_text(
            stats.read_text().replace(report.hash_codegen_commit(self.repo, generated), "f" * 64)
        )
        with self.assertRaisesRegex(report.ReportError, "codegen_hash mismatch"):
            report.build_report(self.repo, base, self.commit())
        self.git("update-ref", "-d", "refs/remotes/origin/codegen/test")
        with self.assertRaises(report.ReportError):
            report.resolve_baseline(self.repo, base, fetch=False, require_hash=True)

    def test_stats_symlink_is_rejected(self) -> None:
        self.baseline()
        path = self.repo / ".castiron.stats.yml"
        original = path.read_text()
        path.unlink()
        path.symlink_to(original)
        with self.assertRaisesRegex(report.ReportError, "regular Git file"):
            report.read_stats(self.repo, self.commit())

    def test_public_snapshot_rejects_private_governance_and_unpublished_paths(self) -> None:
        entry = report.Entry(b"100644", "a" * 40)
        blocked = [
            b".castiron/private.json",
            b".github/CODEOWNERS",
            b".gitmodules",
            b"CODEOWNERS",
            b"SECURITY.md",
            b"docs/SECURITY.md",
        ]
        for path in blocked:
            with (
                self.subTest(path=path),
                mock.patch.object(
                    report, "tree_entries", side_effect=[{path: entry}, {path: entry}]
                ),
                mock.patch.object(report, "read_blobs") as read,
            ):
                with self.assertRaisesRegex(report.ReportError, "private or governance"):
                    report.copy_generated_tree(self.repo, "a" * 40, self.repo, "b" * 40)
                read.assert_not_called()
        with (
            mock.patch.object(report, "tree_entries", side_effect=[{b"unreleased.py": entry}, {}]),
            mock.patch.object(report, "read_blobs") as read,
        ):
            with self.assertRaisesRegex(
                report.ReportError, "absent from the approved public SDK tree"
            ):
                report.copy_generated_tree(self.repo, "a" * 40, self.repo, "b" * 40)
            read.assert_not_called()

    def test_zero_new_files_summary_reports_existing_changes(self) -> None:
        _, clean = self.baseline()
        self.write("generated.py", "generated\n# existing customization\n")
        base = self.commit()
        self.write("generated.py", "generated\n# existing customization updated\n")
        result, _ = report.build_report(self.repo, base, self.commit())
        body = report.render_report(result)
        self.assertIn("✅ No new custom-code files detected.", body)
        self.assertIn("1 mixed file remains; 1 existing customization changed.", body)
        self.assertNotIn("0 newly customized", body)
        empty, _ = report.build_report(self.repo, clean, clean)
        self.assertIn(
            "0 mixed files remain; 0 existing customizations changed.", report.render_report(empty)
        )

    def test_new_mixed_file_headline_includes_changed_generated_baselines(self) -> None:
        _, base = self.baseline()
        result, _ = report.build_report(self.repo, base, base)
        for category in ("baseline_changed", "newly_generation_owned"):
            result["files"] = [
                {
                    "path": "generated.py",
                    "category": category,
                    "custom_before": False,
                    "custom_after": True,
                    "added": "1",
                    "removed": "1",
                }
            ]
            body = report.render_report(result)
            self.assertNotIn("No new custom-code files", body)
            self.assertIn("1 newly customized", body)

    def test_removals_include_changed_baselines_but_not_handwritten_only_files(self) -> None:
        _, base = self.baseline()
        result, _ = report.build_report(self.repo, base, base)
        result["files"] = [
            {
                "path": category,
                "category": category,
                "custom_before": True,
                "custom_after": False,
                "added": "0",
                "removed": "0",
            }
            for category in ("baseline_changed", "no_longer_generated")
        ]
        self.assertIn("1 customizations removed", report.render_report(result))
        result["files"].append(
            {
                "path": "new.py",
                "category": "newly_customized",
                "custom_before": False,
                "custom_after": True,
                "added": "1",
                "removed": "0",
            }
        )
        self.assertIn("1 customizations removed", report.render_report(result))

    def test_public_snapshot_has_no_private_history_and_reports_without_private_remote(
        self,
    ) -> None:
        self.write("private-only.txt", "must never be published\n")
        private_ancestor = self.commit("private history")
        (self.repo / "private-only.txt").unlink()
        generated, base = self.baseline()
        self.git("branch", "codegen/test", generated)
        private_remote = self.repo / "private.git"
        self.git("clone", "--bare", str(self.repo), str(private_remote))
        self.git("remote", "add", "origin", str(private_remote))

        public = self.repo / "public"
        public.mkdir()
        report.git(public, "init", "-q", "-b", "main")
        report.git(public, "config", "user.name", "Public test")
        report.git(public, "config", "user.email", "public@example.test")
        (public / "generated.py").write_text("generated\n")
        (public / ".castiron.stats.yml").write_text(
            (self.repo / ".castiron.stats.yml").read_text().split("codegen_hash:")[0]
        )
        report.git(public, "add", ".")
        report.git(public, "commit", "-qm", "already public")
        public_base = report.git(public, "rev-parse", "HEAD").decode().strip()
        public_remote = self.repo / "public.git"
        report.git(public, "clone", "--bare", str(public), str(public_remote))
        report.git(public, "remote", "add", "origin", str(public_remote))
        snapshot = report.prepare_public_snapshot(
            self.repo, base, base, public, public_base, "castiron/promotions/pr-1"
        )
        self.assertNotEqual(snapshot["commit"], generated)
        self.assertEqual(report.git(public, "rev-list", "--count", snapshot["commit"]), b"1\n")
        self.assertEqual(report.hash_codegen_commit(public, snapshot["commit"]), snapshot["hash"])
        with self.assertRaises(report.ReportError):
            report.git(public, "cat-file", "-e", private_ancestor)
        self.assertNotIn(
            b"private-only.txt", report.git(public, "ls-tree", "-r", snapshot["commit"])
        )
        report.git(
            public, "push", "origin", f"{snapshot['commit']}:refs/heads/{snapshot['branch']}"
        )
        (public / "generated.py").write_text("generated\n# custom\n")
        report.git(public, "add", ".")
        report.git(public, "commit", "-qm", "public customization")
        public_head = report.git(public, "rev-parse", "HEAD").decode().strip()
        result, patch = report.build_report(
            public, public_base, public_head, fetch=True, require_head_hash=True, public=True
        )
        self.assertEqual(result["counts"]["newly_customized"], 1)
        self.assertIn(b"+# custom", patch)
        self.assertIn(" --public", report.render_report(result))
        self.assertFalse(result["before"]["hash_recorded"])
        again = report.prepare_public_snapshot(
            self.repo, base, base, public, public_base, "castiron/promotions/pr-1"
        )
        self.assertEqual(again["commit"], snapshot["commit"])
        tree = report.git(public, "rev-parse", f"{snapshot['commit']}^{{tree}}").decode().strip()
        message = report.git(public, "show", "-s", "--format=%B", snapshot["commit"])
        chained = (
            report.git(
                public,
                "commit-tree",
                tree,
                "-p",
                snapshot["commit"],
                "-F",
                "-",
                input_bytes=message,
            )
            .decode()
            .strip()
        )
        report.git(
            public, "push", "--force", "origin", f"{chained}:refs/heads/{snapshot['branch']}"
        )
        reused = report.prepare_public_snapshot(
            self.repo, base, base, public, public_base, "castiron/promotions/pr-1"
        )
        self.assertEqual(reused["commit"], chained)

        # A fresh generation may introduce files. Its public parent must be a
        # previously public snapshot, never the private checkpoint parent.
        next_generation = "650e8400-e29b-41d4-a716-446655440000"
        self.git("checkout", "--detach", generated)
        self.write("generated.py", "regenerated\n")
        self.write("new.py", "new generated file\n")
        self.git("add", "--", "generated.py", "new.py")
        metadata = base64.b64encode(
            json.dumps(
                {
                    "generation_id": next_generation,
                    "source_branch": "test",
                }
            ).encode()
        ).decode()
        self.git("commit", "-qm", f"next codegen\n\nGeneration metadata: {metadata}")
        next_codegen = self.git("rev-parse", "HEAD")
        self.git("push", "origin", f"{next_codegen}:refs/heads/codegen/test")
        self.write(
            ".castiron.stats.yml",
            (
                f"schema_version: 1\ngeneration_id: {next_generation}\n"
                f"codegen_sha: {next_codegen}\n"
                f"codegen_hash: {report.hash_codegen_commit(self.repo, next_codegen)}\n"
            ),
        )
        self.git("add", "--", ".castiron.stats.yml")
        self.git("commit", "-qm", "next integrated SDK")
        next_head = self.git("rev-parse", "HEAD")
        # An unreviewed path in private HEAD is not enough to publish it.
        with self.assertRaisesRegex(report.ReportError, "approved public SDK tree"):
            report.prepare_public_snapshot(
                self.repo, base, next_head, public, public_base, "castiron/promotions/pr-1"
            )
        # Model normal promotion applying its reviewed patch to the public index.
        (public / "generated.py").write_text("regenerated\n")
        (public / "new.py").write_text("new generated file\n")
        report.git(public, "add", "--", "generated.py", "new.py")
        advanced = report.prepare_public_snapshot(
            self.repo, base, next_head, public, public_base, "castiron/promotions/pr-1"
        )
        self.assertEqual(
            report.git(public, "rev-parse", advanced["commit"] + "^1").decode().strip(), chained
        )
        self.assertEqual(report.hash_codegen_commit(public, advanced["commit"]), advanced["hash"])
        with self.assertRaises(report.ReportError):
            report.git(public, "cat-file", "-e", next_codegen)
        report.git(
            public, "push", "origin", f"{advanced['commit']}:refs/heads/{advanced['branch']}"
        )
        (public / "generated.py").write_text("regenerated\n")
        (public / "new.py").write_text("new generated file\n")
        report.git(public, "add", "--", ".castiron.stats.yml", "generated.py", "new.py")
        report.git(public, "commit", "-qm", "next public SDK")
        next_public = report.git(public, "rev-parse", "HEAD").decode().strip()
        compared, _ = report.build_report(
            public, public_base, next_public, fetch=True, require_head_hash=True, public=True
        )
        self.assertEqual(compared["before"]["generation_id"], GENERATION)
        self.assertEqual(compared["after"]["generation_id"], next_generation)

        # Once A lands, handwritten-only promotion B may reuse A's exact
        # snapshot. Its original branch is a locator, not exclusive ownership.
        report.git(public, "push", "origin", f"{next_public}:refs/heads/main")
        self.write("generated.py", "regenerated\n# handwritten change\n")
        self.git("add", "--", "generated.py")
        self.git("commit", "-qm", "handwritten change")
        custom_head = self.git("rev-parse", "HEAD")
        (public / "generated.py").write_text("regenerated\n# handwritten change\n")
        report.git(public, "add", "--", "generated.py")
        other_branch = "castiron/promotions/pr-2"
        other = report.prepare_public_snapshot(
            self.repo, next_head, custom_head, public, next_public, other_branch
        )
        self.assertEqual(other["commit"], advanced["commit"])
        self.assertEqual(
            report.public_metadata(public, other["commit"])["Branch"], advanced["branch"]
        )
        report.git(public, "push", "origin", f"{other['commit']}:refs/heads/{other['branch']}")
        retried = report.prepare_public_snapshot(
            self.repo, next_head, custom_head, public, next_public, other_branch
        )
        self.assertEqual(retried["commit"], other["commit"])

        # A merge-queue commit also resolves the baseline from its own stats,
        # independently of the name or parents of the integrated SDK commit.
        merged_tree = report.git(public, "write-tree").decode().strip()
        pr_head = (
            report.git(
                public,
                "commit-tree",
                merged_tree,
                "-p",
                next_public,
                "-m",
                "public handwritten change",
            )
            .decode()
            .strip()
        )
        merged = (
            report.git(
                public,
                "commit-tree",
                merged_tree,
                "-p",
                next_public,
                "-p",
                pr_head,
                "-m",
                "merge queue",
            )
            .decode()
            .strip()
        )
        merged_report, _ = report.build_report(
            public, next_public, merged, fetch=True, require_head_hash=True, public=True
        )
        self.assertEqual(merged_report["after"]["commit"], advanced["commit"])
        self.assertEqual(merged_report["counts"]["newly_customized"], 1)


if __name__ == "__main__":
    unittest.main()
