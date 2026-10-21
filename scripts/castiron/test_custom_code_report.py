# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.
from __future__ import annotations

import base64
import hashlib
import json
import os
import struct
import subprocess
import unittest
from unittest import mock

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
        self.assertEqual(set(report.tree_entries(self.repo, second)), {b"a"})
        self.assertEqual(
            set(report.tree_entries(self.repo, second, include_workflows=True)),
            {b"a", b".github/workflows/test.yml", b".github/actions/test/action.yml"},
        )
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

    def test_next_checkpoint_uses_its_namespaced_ref(self) -> None:
        generated, base = self.baseline()
        self.git("checkout", "--detach", generated)
        metadata = {
            "schema_version": "castiron-checkpoint/v2",
            "release_target": "next",
            "record": {"generation_id": GENERATION, "source_branch": "test"},
        }
        encoded = base64.b64encode(json.dumps(metadata).encode()).decode()
        checkpoint = self.commit(f"codegen\n\nGeneration metadata: {encoded}")
        ref = "refs/remotes/origin/codegen/castiron/next/test"
        self.git("update-ref", ref, checkpoint)
        stats = report.read_stats(self.repo, base) | {
            "codegen_sha": checkpoint,
            "codegen_hash": report.hash_codegen_commit(self.repo, checkpoint),
        }
        result = report.resolve_checkpoint(
            self.repo, stats, fetch=False, require_hash=True, target_branch="next"
        )
        self.assertEqual(result["commit"], checkpoint)
        self.git("update-ref", "refs/remotes/origin/codegen/test", checkpoint)
        self.git("update-ref", "-d", ref)
        with self.assertRaises(report.ReportError):
            report.resolve_checkpoint(
                self.repo, stats, fetch=False, require_hash=True, target_branch="next"
            )

    def test_next_checkpoint_cannot_authorize_main_reports(self) -> None:
        import custom_code_budget as budget

        generated, base = self.baseline()
        self.write(
            ".castiron-ratchet.json", '{"schema_version": 1, "max_custom_patch_lines": 10000}\n'
        )
        base = self.commit("policy")
        self.git("checkout", "--detach", generated)
        metadata = {
            "schema_version": "castiron-checkpoint/v2",
            "release_target": "next",
            "record": {"generation_id": GENERATION, "source_branch": "test"},
        }
        encoded = base64.b64encode(json.dumps(metadata).encode()).decode()
        checkpoint = self.commit(f"codegen\n\nGeneration metadata: {encoded}")
        self.git("update-ref", "refs/remotes/origin/codegen/castiron/next/test", checkpoint)
        self.git("checkout", "--detach", base)
        stats = report.read_stats(self.repo, base) | {
            "codegen_sha": checkpoint,
            "codegen_hash": report.hash_codegen_commit(self.repo, checkpoint),
        }
        self.write(".castiron.stats.yml", "".join(f"{k}: {v}\n" for k, v in stats.items()))
        head = self.commit("next checkpoint")
        for target, expected in (("main", "error"), ("next", "ok")):
            with self.subTest(target=target):
                result = report.write_report(
                    self.repo,
                    base,
                    head,
                    self.repo / "report-output",
                    fetch=False,
                    require_head_hash=True,
                    public=False,
                    target_branch=target,
                )
                self.assertEqual(result["status"], expected)
                measured, _ = budget.evaluate(
                    self.repo,
                    base,
                    head,
                    public=False,
                    target_branch=target,
                )
                self.assertEqual(measured["target_branch"], target)
                self.assertEqual(
                    measured["checks"]["budget"]["state"],
                    "success" if target == "next" else "failure",
                )
        output = self.repo / "budget-output"
        budget.write_result(output, measured)
        self.assertEqual(json.loads((output / "budget.json").read_text())["target_branch"], "next")
        self.assertIn("Target next:", (output / "summary.md").read_text())
        snapshot = report.create_public_snapshot(
            self.repo,
            self.git("rev-parse", f"{checkpoint}^{{tree}}"),
            GENERATION,
            stats["codegen_hash"],
            "codegen/castiron/next/test",
            None,
        )
        self.git("update-ref", "refs/remotes/origin/codegen/castiron/next/test", snapshot)
        stats["public_codegen_sha"] = snapshot
        self.write(".castiron.stats.yml", "".join(f"{k}: {v}\n" for k, v in stats.items()))
        public_head = self.commit("public next snapshot")
        with self.assertRaisesRegex(report.ReportError, "cannot authorize a main"):
            report.build_report(self.repo, base, public_head, public=True)
        accepted, _ = report.build_report(
            self.repo, base, public_head, public=True, target_branch="next"
        )
        self.assertEqual(accepted["status"], "ok")

    def test_public_next_namespace_root_remains_reserved(self) -> None:
        generated, _ = self.baseline()
        branch = "codegen/castiron/next"
        snapshot = report.create_public_snapshot(
            self.repo,
            self.git("rev-parse", f"{generated}^{{tree}}"),
            GENERATION,
            report.hash_codegen_commit(self.repo, generated),
            branch,
            None,
        )
        metadata = report.public_metadata(self.repo, snapshot)
        self.assertEqual(metadata["Target"], "next")
        for target in ("main", "next"):
            with self.subTest(target=target):
                metadata["Target"] = target
                with self.assertRaisesRegex(report.ReportError, "cannot authorize a main"):
                    report.validate_public_target(
                        self.repo, snapshot, metadata, target_branch="main", fetch=False
                    )
                report.validate_public_target(
                    self.repo, snapshot, metadata, target_branch="next", fetch=False
                )

    def test_prepare_public_next_root_and_descendant(self) -> None:
        generated, base = self.baseline()
        self.git("branch", "codegen/test", generated)
        self.git("checkout", "--detach", generated)
        metadata = {
            "schema_version": "castiron-checkpoint/v2",
            "release_target": "next",
            "record": {"generation_id": GENERATION, "source_branch": "test"},
        }
        encoded = base64.b64encode(json.dumps(metadata).encode()).decode()
        checkpoint = self.commit(f"codegen\n\nGeneration metadata: {encoded}")
        self.git("branch", "codegen/castiron/next/test", checkpoint)
        self.git("checkout", "--detach", base)
        stats = report.read_stats(self.repo, base) | {
            "codegen_sha": checkpoint,
            "codegen_hash": report.hash_codegen_commit(self.repo, checkpoint),
        }
        self.write(".castiron.stats.yml", "".join(f"{k}: {v}\n" for k, v in stats.items()))
        head = self.commit("next checkpoint")
        self.git("remote", "add", "origin", str(self.repo))
        public = self.repo / "public"
        self.git("clone", "--no-local", str(self.repo), str(public))
        report.git(public, "checkout", "--detach", base)
        public_remote = self.repo / "public.git"
        report.git(public, "init", "--bare", str(public_remote))
        report.git(public, "remote", "set-url", "origin", str(public_remote))
        report.git(public, "push", "origin", f"{base}:refs/heads/main")
        for branch in ("castiron/next", "castiron/next/test"):
            with self.subTest(branch=branch):
                snapshot = report.prepare_public_snapshot(
                    self.repo, base, head, public, base, branch
                )
                self.assertEqual(snapshot["branch"], f"codegen/{branch}")
                public_metadata = report.public_metadata(public, snapshot["commit"])
                self.assertEqual(public_metadata["Target"], "next")
                with self.assertRaisesRegex(report.ReportError, "cannot authorize a main"):
                    report.validate_public_target(
                        public,
                        snapshot["commit"],
                        public_metadata,
                        target_branch="main",
                        fetch=False,
                    )
        with self.assertRaises(report.ReportError):
            report.prepare_public_snapshot(self.repo, base, head, public, base, "castiron/nextish")

    def test_legacy_public_snapshot_requires_trusted_main_adoption(self) -> None:
        generated, base = self.baseline()
        branch = "codegen/castiron/promotions/pr-42"
        content_hash = report.hash_codegen_commit(self.repo, generated)
        tree = self.git("rev-parse", f"{generated}^{{tree}}")
        message = (
            "Castiron generated snapshot\n\n"
            "Castiron-Public-Codegen-Version: 1\n"
            f"Castiron-Public-Codegen-Generation-ID: {GENERATION}\n"
            f"Castiron-Public-Codegen-Hash: {content_hash}\n"
            f"Castiron-Public-Codegen-Branch: {branch}\n"
        )
        legacy = self.git("commit-tree", tree, "-m", message)
        self.git("update-ref", f"refs/remotes/origin/{branch}", legacy)
        self.git("update-ref", "refs/remotes/origin/main", base)
        stats = report.read_stats(self.repo, base) | {"public_codegen_sha": legacy}
        self.write(".castiron.stats.yml", "".join(f"{k}: {v}\n" for k, v in stats.items()))
        head = self.commit("untrusted legacy snapshot adoption")
        with self.assertRaisesRegex(report.ReportError, "no verified main adoption"):
            report.resolve_public_baseline(self.repo, head, fetch=False, require_hash=True)
        report.resolve_public_baseline(
            self.repo, head, fetch=False, require_hash=True, target_branch="next"
        )
        # A side branch can add then remove the reference before merging. None
        # of its intermediate stats were ever adopted on main's first-parent line.
        base_tree = self.git("rev-parse", f"{base}^{{tree}}")
        removed = self.git("commit-tree", base_tree, "-p", head, "-m", "remove reference")
        self.write(
            ".castiron.stats.yml",
            self.git("show", f"{base}:.castiron.stats.yml") + "\n# main metadata retained\n",
        )
        self.git("add", ".castiron.stats.yml")
        merged = self.git(
            "commit-tree",
            self.git("write-tree"),
            "-p",
            base,
            "-p",
            removed,
            "-m",
            "merge clean tip with main metadata update",
        )
        self.git("update-ref", "refs/remotes/origin/main", merged)
        with self.assertRaisesRegex(report.ReportError, "no verified main adoption"):
            report.resolve_public_baseline(self.repo, head, fetch=False, require_hash=True)
        # A merge that actually adopts the snapshot on main is sufficient.
        adopted = self.git(
            "commit-tree",
            self.git("rev-parse", f"{head}^{{tree}}"),
            "-p",
            merged,
            "-p",
            head,
            "-m",
            "adopt snapshot on main",
        )
        self.git("update-ref", "refs/remotes/origin/main", adopted)
        report.resolve_public_baseline(self.repo, head, fetch=False, require_hash=True)
        for spelling in (f'"{legacy}"', f"   {legacy}"):
            with self.subTest(spelling=spelling):
                self.write(
                    ".castiron.stats.yml",
                    "".join(
                        f"{key}: {spelling if key == 'public_codegen_sha' else value}\n"
                        for key, value in stats.items()
                    ),
                )
                self.git("add", ".castiron.stats.yml")
                formatted = self.git(
                    "commit-tree", self.git("write-tree"), "-p", base, "-m", "formatted adoption"
                )
                self.git("update-ref", "refs/remotes/origin/main", formatted)
                report.resolve_public_baseline(self.repo, formatted, fetch=False, require_hash=True)

        # Replacing a comment with the field preserves the SHA occurrence count.
        original_stats = self.git("show", f"{base}:.castiron.stats.yml") + "\n"
        self.write(".castiron.stats.yml", original_stats + f"# candidate: {legacy}\n")
        self.git("add", ".castiron.stats.yml")
        mentioned = self.git(
            "commit-tree", self.git("write-tree"), "-p", base, "-m", "mention candidate"
        )
        self.git("update-ref", "refs/remotes/origin/main", mentioned)
        self.assertFalse(report.legacy_snapshot_on_main(self.repo, legacy, fetch=False))
        with self.assertRaisesRegex(report.ReportError, "no verified main adoption"):
            report.resolve_public_baseline(self.repo, head, fetch=False, require_hash=True)
        self.write(".castiron.stats.yml", original_stats + f"public_codegen_sha: {legacy}\n")
        self.git("add", ".castiron.stats.yml")
        adopted = self.git(
            "commit-tree", self.git("write-tree"), "-p", mentioned, "-m", "adopt candidate"
        )
        self.git("update-ref", "refs/remotes/origin/main", adopted)
        report.resolve_public_baseline(self.repo, adopted, fetch=False, require_hash=True)

        # Explicit next metadata cannot be grandfathered, even with an old locator.
        explicit_next = self.git(
            "commit-tree", tree, "-m", message + "Castiron-Public-Codegen-Target: next\n"
        )
        self.git("update-ref", f"refs/remotes/origin/{branch}", explicit_next)
        stats["public_codegen_sha"] = explicit_next
        self.write(".castiron.stats.yml", "".join(f"{k}: {v}\n" for k, v in stats.items()))
        head = self.commit("explicit next target")
        self.git("update-ref", "refs/remotes/origin/main", head)
        with self.assertRaisesRegex(report.ReportError, "cannot authorize a main"):
            report.resolve_public_baseline(self.repo, head, fetch=False, require_hash=True)

    def test_legacy_bootstrap_baseline_uses_verified_main_lineage(self) -> None:
        generated, base = self.baseline()
        tree = self.git("rev-parse", f"{generated}^{{tree}}")
        content_hash = report.hash_codegen_commit(self.repo, generated)
        branch = "codegen/castiron/promotions/pr-1"

        def legacy_snapshot(generation: str, parent: str | None = None) -> str:
            message = (
                "Castiron generated snapshot\n\n"
                "Castiron-Public-Codegen-Version: 1\n"
                f"Castiron-Public-Codegen-Generation-ID: {generation}\n"
                f"Castiron-Public-Codegen-Hash: {content_hash}\n"
                f"Castiron-Public-Codegen-Branch: {branch}\n"
            )
            return self.git("commit-tree", tree, *(["-p", parent] if parent else []), "-m", message)

        bootstrap = legacy_snapshot(GENERATION)
        generation = "650e8400-e29b-41d4-a716-446655440000"
        adopted = legacy_snapshot(generation, bootstrap)
        self.git("update-ref", f"refs/remotes/origin/{branch}", adopted)
        stats = report.read_stats(self.repo, base) | {
            "generation_id": generation,
            "public_codegen_sha": adopted,
        }
        self.write(".castiron.stats.yml", "".join(f"{k}: {v}\n" for k, v in stats.items()))
        head = self.commit("adopt first public checkpoint")
        self.git("update-ref", "refs/remotes/origin/main", head)
        result, _ = report.build_report(self.repo, base, head, public=True, require_head_hash=True)
        self.assertEqual(result["before"]["commit"], bootstrap)
        self.assertEqual(result["after"]["commit"], adopted)
        self.assertFalse(report.legacy_snapshot_on_main(self.repo, bootstrap, fetch=False))

        # An unadopted legacy head cannot authorize its own bootstrap lineage.
        with self.assertRaisesRegex(report.ReportError, "no verified main adoption"):
            report.resolve_public_baseline(
                self.repo, base, fetch=False, require_hash=False, lineage=bootstrap
            )

    def test_public_next_namespace_root_is_reserved(self) -> None:
        generated, _ = self.baseline()
        tree = self.git("rev-parse", f"{generated}^{{tree}}")
        content_hash = report.hash_codegen_commit(self.repo, generated)
        for branch, target in (
            ("codegen/castiron/next", "next"),
            ("codegen/castiron/next/child", "next"),
            ("codegen/castiron/next-door", "main"),
        ):
            with self.subTest(branch=branch):
                snapshot = report.create_public_snapshot(
                    self.repo, tree, GENERATION, content_hash, branch, None
                )
                metadata = report.public_metadata(self.repo, snapshot)
                self.assertEqual(metadata["Target"], target)
                # A misleading explicit target cannot authorize the reserved root.
                metadata["Target"] = "main"
                if target == "next":
                    with self.assertRaisesRegex(report.ReportError, "cannot authorize a main"):
                        report.validate_public_target(
                            self.repo, snapshot, metadata, target_branch="main", fetch=False
                        )
                else:
                    report.validate_public_target(
                        self.repo, snapshot, metadata, target_branch="main", fetch=False
                    )

    def test_legacy_main_adoption_accepts_stats_formatting(self) -> None:
        generated, base = self.baseline()
        branch = "codegen/castiron/promotions/pr-42"
        content_hash = report.hash_codegen_commit(self.repo, generated)
        message = (
            "Castiron generated snapshot\n\n"
            "Castiron-Public-Codegen-Version: 1\n"
            f"Castiron-Public-Codegen-Generation-ID: {GENERATION}\n"
            f"Castiron-Public-Codegen-Hash: {content_hash}\n"
            f"Castiron-Public-Codegen-Branch: {branch}\n"
        )
        snapshot = self.git(
            "commit-tree", self.git("rev-parse", f"{generated}^{{tree}}"), "-m", message
        )
        self.git("update-ref", f"refs/remotes/origin/{branch}", snapshot)
        for value in (f"'{snapshot}'", f'"{snapshot}"', f"   {snapshot}"):
            with self.subTest(value=value):
                self.git("checkout", "--detach", "-q", base)
                stats = self.git("show", f"{base}:.castiron.stats.yml")
                self.write(".castiron.stats.yml", stats + f"\n# pending snapshot: {snapshot}\n")
                commented = self.commit("mention snapshot without adopting it")
                self.git("update-ref", "refs/remotes/origin/main", commented)
                self.assertFalse(report.legacy_snapshot_on_main(self.repo, snapshot, fetch=False))
                self.write(".castiron.stats.yml", stats + f"\npublic_codegen_sha: {value}\n")
                adopted = self.commit("adopt formatted snapshot")
                self.git("update-ref", "refs/remotes/origin/main", adopted)
                resolved = report.resolve_public_baseline(
                    self.repo, adopted, fetch=False, require_hash=True
                )
                self.assertEqual(resolved["commit"], snapshot)

    def test_legacy_bootstrap_parent_uses_main_adopted_lineage(self) -> None:
        generated, base = self.baseline()
        tree = self.git("rev-parse", f"{generated}^{{tree}}")
        content_hash = report.hash_codegen_commit(self.repo, generated)
        child_generation = "550e8400-e29b-41d4-a716-446655440001"
        for parent_branch, parent_target, allowed in (
            ("codegen/castiron/bootstrap", "", True),
            ("codegen/castiron/bootstrap", "next", False),
            ("codegen/castiron/next", "", False),
            ("codegen/castiron/next/bootstrap", "", False),
        ):
            with self.subTest(branch=parent_branch, target=parent_target):
                for reserved in self.git(
                    "for-each-ref",
                    "--format=%(refname)",
                    "refs/remotes/origin/codegen/castiron/next",
                ).splitlines():
                    self.git("update-ref", "-d", reserved)
                self.git("checkout", "--detach", "-q", base)
                self.git("update-ref", "refs/remotes/origin/main", base)
                parent_message = (
                    "Castiron generated snapshot\n\n"
                    "Castiron-Public-Codegen-Version: 1\n"
                    f"Castiron-Public-Codegen-Generation-ID: {GENERATION}\n"
                    f"Castiron-Public-Codegen-Hash: {content_hash}\n"
                    f"Castiron-Public-Codegen-Branch: {parent_branch}\n"
                )
                if parent_target:
                    parent_message += f"Castiron-Public-Codegen-Target: {parent_target}\n"
                parent = self.git("commit-tree", tree, "-m", parent_message)
                self.git("update-ref", f"refs/remotes/origin/{parent_branch}", parent)
                child_branch = "codegen/castiron/promotions/test"
                child_message = (
                    "Castiron generated snapshot\n\n"
                    "Castiron-Public-Codegen-Version: 1\n"
                    f"Castiron-Public-Codegen-Generation-ID: {child_generation}\n"
                    f"Castiron-Public-Codegen-Hash: {content_hash}\n"
                    f"Castiron-Public-Codegen-Branch: {child_branch}\n"
                )
                child = self.git("commit-tree", tree, "-p", parent, "-m", child_message)
                self.git("update-ref", f"refs/remotes/origin/{child_branch}", child)
                stats = report.read_stats(self.repo, base) | {
                    "generation_id": child_generation,
                    "public_codegen_sha": child,
                }
                self.write(".castiron.stats.yml", "".join(f"{k}: {v}\n" for k, v in stats.items()))
                head = self.commit("adopt only the legacy descendant")
                with self.assertRaisesRegex(report.ReportError, "no verified main adoption"):
                    report.build_report(self.repo, base, head, public=True, require_head_hash=True)
                self.git("update-ref", "refs/remotes/origin/main", head)
                if allowed:
                    result, _ = report.build_report(
                        self.repo, base, head, public=True, require_head_hash=True
                    )
                    self.assertEqual(result["status"], "ok")
                    self.assertEqual(
                        report.resolve_public_baseline(
                            self.repo, base, fetch=False, require_hash=False, lineage=child
                        )["commit"],
                        parent,
                    )
                    # Adoption of a descendant never authorizes a direct parent reference.
                    direct = report.read_stats(self.repo, base) | {"public_codegen_sha": parent}
                    self.write(
                        ".castiron.stats.yml", "".join(f"{k}: {v}\n" for k, v in direct.items())
                    )
                    direct_head = self.commit("reference an unadopted parent directly")
                    with self.assertRaisesRegex(report.ReportError, "no verified main adoption"):
                        report.resolve_public_baseline(
                            self.repo, direct_head, fetch=False, require_hash=True, lineage=child
                        )
                else:
                    with self.assertRaisesRegex(report.ReportError, "cannot authorize a main"):
                        report.build_report(
                            self.repo, base, head, public=True, require_head_hash=True
                        )

    def test_legacy_checkpoint_cannot_use_next_namespace(self) -> None:
        generated, base = self.baseline()
        self.git("checkout", "--detach", generated)
        metadata = {"generation_id": GENERATION, "source_branch": "castiron/next/test"}
        encoded = base64.b64encode(json.dumps(metadata).encode()).decode()
        checkpoint = self.commit(f"codegen\n\nGeneration metadata: {encoded}")
        self.git("update-ref", "refs/remotes/origin/codegen/castiron/next/test", checkpoint)
        stats = report.read_stats(self.repo, base) | {
            "codegen_sha": checkpoint,
            "codegen_hash": report.hash_codegen_commit(self.repo, checkpoint),
        }
        for target in ("main", "next"):
            with (
                self.subTest(target=target),
                self.assertRaisesRegex(report.ReportError, "reserved next"),
            ):
                report.resolve_checkpoint(
                    self.repo, stats, fetch=False, require_hash=True, target_branch=target
                )

    def test_invalid_checkpoint_envelopes_are_rejected(self) -> None:
        _, base = self.baseline()
        record = {"generation_id": GENERATION, "source_branch": "test"}
        envelope = {
            "schema_version": "castiron-checkpoint/v2",
            "release_target": "next",
            "record": record,
        }
        for metadata in (
            envelope | {"schema_version": "unknown"},
            envelope | {"release_target": "main"},
            envelope | {"extra": True},
            envelope | {"record": record | {"release_target": "next"}},
            record | {"release_target": "next"},
        ):
            with self.subTest(metadata=metadata):
                encoded = base64.b64encode(json.dumps(metadata).encode()).decode()
                checkpoint = self.commit(f"codegen\n\nGeneration metadata: {encoded}")
                stats = report.read_stats(self.repo, base) | {"codegen_sha": checkpoint}
                with self.assertRaisesRegex(report.ReportError, "envelope"):
                    report.resolve_checkpoint(
                        self.repo, stats, fetch=False, require_hash=True, target_branch="next"
                    )

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

    def test_pending_legacy_promotion_is_upgraded_without_authorizing_legacy_reports(self) -> None:
        generated, source_base = self.baseline()
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
        (public / ".castiron.stats.yml").write_text((self.repo / ".castiron.stats.yml").read_text())
        report.git(public, "add", ".")
        report.git(public, "commit", "-qm", "public baseline")
        initial = report.git(public, "rev-parse", "HEAD").decode().strip()
        branch = "castiron/promotions/legacy-retry"
        codegen_branch = f"codegen/{branch}"

        def legacy_snapshot(
            tree: str, generation: str, content_hash: str, parent: str | None
        ) -> str:
            message = (
                "Castiron generated snapshot\n\nCastiron-Public-Codegen-Version: 1\n"
                f"Castiron-Public-Codegen-Generation-ID: {generation}\n"
                f"Castiron-Public-Codegen-Hash: {content_hash}\n"
                f"Castiron-Public-Codegen-Branch: {codegen_branch}\n"
            )
            parents = ["-p", parent] if parent is not None else []
            return report.git(public, "commit-tree", tree, *parents, "-m", message).decode().strip()

        base_tree = report.copy_generated_tree(self.repo, generated, public, initial)
        legacy_base = legacy_snapshot(
            base_tree, GENERATION, report.hash_codegen_commit(self.repo, generated), None
        )
        with (public / ".castiron.stats.yml").open("a") as stats:
            stats.write(f"public_codegen_sha: {legacy_base}\n")
        report.git(public, "add", ".castiron.stats.yml")
        report.git(public, "commit", "-qm", "adopt legacy baseline")
        public_base = report.git(public, "rev-parse", "HEAD").decode().strip()
        public_remote = self.repo / "public.git"
        report.git(public, "clone", "--bare", str(public), str(public_remote))
        report.git(public, "remote", "add", "origin", str(public_remote))
        report.git(public, "push", "origin", f"{legacy_base}:refs/heads/{codegen_branch}")

        generation = "650e8400-e29b-41d4-a716-446655440000"
        self.git("checkout", "--detach", generated)
        self.write("generated.py", "regenerated\n")
        self.git("add", "generated.py")
        metadata = base64.b64encode(
            json.dumps({"generation_id": generation, "source_branch": "test"}).encode()
        ).decode()
        self.git("commit", "-qm", f"updated codegen\n\nGeneration metadata: {metadata}")
        updated = self.git("rev-parse", "HEAD")
        self.git("push", "origin", f"{updated}:refs/heads/codegen/test")
        content_hash = report.hash_codegen_commit(self.repo, updated)
        self.write(
            ".castiron.stats.yml",
            f"schema_version: 1\ngeneration_id: {generation}\ncodegen_sha: {updated}\ncodegen_hash: {content_hash}\n",
        )
        self.git("add", ".castiron.stats.yml")
        self.git("commit", "-qm", "updated integrated SDK")
        source_head = self.git("rev-parse", "HEAD")
        tree = report.copy_generated_tree(self.repo, updated, public, public_base)
        pending = legacy_snapshot(tree, generation, content_hash, legacy_base)
        report.git(public, "push", "origin", f"{pending}:refs/heads/{codegen_branch}")
        self.assertTrue(report.legacy_snapshot_on_main(public, legacy_base, fetch=True))
        self.assertFalse(report.legacy_snapshot_on_main(public, pending, fetch=False))
        (public / "generated.py").write_text("regenerated\n")
        report.git(public, "add", "generated.py")

        message = report.git(public, "show", "-s", "--format=%B", pending).decode()
        for invalid_message, error in (
            (message + "Castiron-Public-Codegen-Target: next\n", "next checkpoint"),
            (message.replace(content_hash, "f" * 64), "invalid provenance"),
            (
                message.replace(codegen_branch, "codegen/another-promotion"),
                "no verified main adoption",
            ),
        ):
            with self.subTest(error=error):
                invalid = (
                    report.git(
                        public, "commit-tree", tree, "-p", legacy_base, "-m", invalid_message
                    )
                    .decode()
                    .strip()
                )
                report.git(
                    public, "push", "--force", "origin", f"{invalid}:refs/heads/{codegen_branch}"
                )
                with self.assertRaisesRegex(report.ReportError, error):
                    report.prepare_public_snapshot(
                        self.repo, source_base, source_head, public, public_base, branch
                    )
        report.git(public, "push", "--force", "origin", f"{pending}:refs/heads/{codegen_branch}")
        upgraded = report.prepare_public_snapshot(
            self.repo, source_base, source_head, public, public_base, branch
        )
        self.assertNotEqual(upgraded["commit"], pending)
        self.assertEqual(upgraded["base_commit"], legacy_base)
        self.assertEqual(upgraded["previous"], pending)
        self.assertEqual(
            report.git(public, "rev-parse", upgraded["commit"] + "^1").decode().strip(), pending
        )
        self.assertEqual(report.public_metadata(public, upgraded["commit"])["Target"], "main")
        self.assertEqual(report.hash_codegen_commit(public, upgraded["commit"]), content_hash)
        with self.assertRaisesRegex(report.ReportError, "no verified main adoption"):
            report.validate_public_target(
                public,
                pending,
                report.public_metadata(public, pending),
                target_branch="main",
                fetch=False,
            )
        report.git(public, "push", "origin", f"{upgraded['commit']}:refs/heads/{codegen_branch}")
        report.git(public, "commit", "-qm", "upgraded public SDK")
        head = report.git(public, "rev-parse", "HEAD").decode().strip()
        result, _ = report.build_report(
            public, public_base, head, fetch=True, require_head_hash=True, public=True
        )
        self.assertEqual(result["after"]["generation_id"], generation)

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
        self.assertEqual(snapshot["base_commit"], snapshot["commit"])
        self.assertNotEqual(snapshot["commit"], generated)
        self.assertEqual(snapshot["base_commit"], snapshot["commit"])
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
        self.assertEqual(again["base_commit"], snapshot["base_commit"])
        self.assertEqual(again["commit"], snapshot["commit"])
        self.assertEqual(again["base_commit"], snapshot["base_commit"])
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
