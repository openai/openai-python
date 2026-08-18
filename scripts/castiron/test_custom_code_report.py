from __future__ import annotations

import os
import json
import base64
import struct
import hashlib
import tempfile
import unittest
import subprocess
from pathlib import Path
from unittest import mock

import custom_code_report as report

GENERATION = "550e8400-e29b-41d4-a716-446655440000"


class CustomCodeTests(unittest.TestCase):
    # Keep the vendored test stdlib-only on Python 3.10 (no typing.override yet).
    def setUp(self) -> None:  # pyright: ignore[reportImplicitOverride]
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Castiron test")
        self.git("config", "user.email", "castiron@example.test")

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(self.repo), *args], check=True, capture_output=True, text=True
        ).stdout.strip()

    def write(self, path: str, body: str) -> None:
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body)

    def commit(self, message: str = "fixture") -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message)
        return self.git("rev-parse", "HEAD")

    def baseline(self) -> tuple[str, str]:
        self.write("generated.py", "generated\n")
        metadata = {
            "generation_id": GENERATION,
            "source_branch": "test",
            "target": "openai-python",
            "language": "python",
        }
        encoded = base64.b64encode(json.dumps(metadata).encode()).decode()
        generated = self.commit(f"codegen\n\nGeneration metadata: {encoded}")
        self.git("update-ref", "refs/remotes/origin/codegen/test", generated)
        self.write(
            ".castiron.stats.yml",
            f"schema_version: 1\ngeneration_id: {GENERATION}\ncodegen_sha: {generated}\ncodegen_hash: {report.hash_codegen_commit(self.repo, generated)}\n",
        )
        return generated, self.commit("integrated")

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
            with self.assertRaisesRegex(report.ReportError, "not present on public main"):
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
        with self.assertRaisesRegex(report.ReportError, "does not match the pilot generation"):
            report.prepare_public_snapshot(
                self.repo, base, base, public, public_base, "castiron/promotions/pr-1"
            )

    def test_comment_updates_existing_bot_comment_and_skips_stale(self) -> None:
        _, base = self.baseline()
        result, _ = report.build_report(self.repo, base, base)
        calls: list[tuple[str, str, object]] = []

        def fake_api(method: str, path: str, payload: object = None) -> object:
            calls.append((method, path, payload))
            if "/pulls/" in path:
                return {"state": "open", "head": {"sha": base}, "base": {"sha": base}}
            if "/actions/runs/" in path:
                return {
                    "event": "pull_request",
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
        pull = {"state": "open", "head": {"sha": base}, "base": {"sha": base}}
        run = {
            "event": "pull_request",
            "head_sha": base,
            "run_attempt": 2,
            "pull_requests": [{"number": 1}],
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
        with mock.patch.object(report, "api", side_effect=[pull, {**run, "pull_requests": []}]):
            with self.assertRaisesRegex(report.ReportError, "does not match report PR"):
                report.publish_comment(result, "openai/example", 1, 2, 2)
        changed = {**pull, "head": {"sha": "f" * 40}}
        with mock.patch.object(report, "api", side_effect=[pull, run, [], changed]) as api:
            self.assertEqual(
                report.publish_comment(result, "openai/example", 1, 2, 2), "Skipped stale report"
            )
            self.assertEqual(api.call_count, 4)


if __name__ == "__main__":
    unittest.main()
