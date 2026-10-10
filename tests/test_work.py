"""Tests for the work skills' deterministic helpers (branch_state, work_scope, detect_gates, gitread)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "lib"
sys.path.insert(0, str(LIB))
import gitread  # noqa: E402
import backlog_kit as bk  # noqa: E402


def sh(cwd, *cmd):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True).stdout


def git(cwd, *args):
    return sh(cwd, "git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args)


def run(script, root, *extra):
    out = subprocess.run([sys.executable, str(LIB / script), str(root), *extra],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def init_repo(path, bare=False):
    Path(path).mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q", "-b", "main", *(["--bare"] if bare else []))
    return path


def commit_file(repo, name, text="x", msg="c"):
    (Path(repo) / name).write_text(text)
    git(repo, "add", name)
    git(repo, "commit", "-q", "-m", msg)


class GitRead(unittest.TestCase):
    def test_write_commands_are_refused(self):
        with tempfile.TemporaryDirectory() as d:
            init_repo(d)
            for bad in (("commit", "-m", "x"), ("push",), ("merge", "x"), ("rebase",), ("add", "."),
                        ("reset", "--hard"), ("checkout", "-b", "x"), ("switch", "-c", "x"),
                        ("branch", "-D", "x"), ("branch", "--delete", "x"), ("tag", "v1"), ("stash",)):
                with self.subTest(cmd=bad):
                    with self.assertRaises(gitread.GitError):
                        gitread.git(d, *bad)

    def test_allowlist_contains_no_write_subcommand(self):
        forbidden = {"commit", "push", "merge", "rebase", "add", "reset", "checkout", "switch", "pull",
                     "stash", "cherry-pick", "apply", "am", "tag", "clean", "rm", "mv", "restore", "revert"}
        self.assertFalse(forbidden & gitread.ALLOWED)

    def test_changed_files_sees_untracked_and_spaces(self):
        with tempfile.TemporaryDirectory() as d:
            init_repo(d)
            commit_file(d, "tracked.txt")
            (Path(d) / "tracked.txt").write_text("changed")
            (Path(d) / "new file.txt").write_text("n")
            (Path(d) / "sub").mkdir()
            (Path(d) / "sub/a.py").write_text("n")
            self.assertEqual(gitread.changed_files(d), ["new file.txt", "sub/a.py", "tracked.txt"])














if __name__ == "__main__":
    unittest.main()


class ConfirmedModeSafety(unittest.TestCase):
    """features-next resolves a typed name with --select: blocked and implemented features must not pass."""

    def test_select_flags_blocked_and_refuses_implemented_or_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs/backlog").mkdir(parents=True)
            (root / "docs/backlog/features-planned.md").write_text(
                "# Planned Features\n\n## Feature List\n\n"
                "| # | Change name | Priority | Effort | Area | Implementation | Summary | Brief |\n"
                "| - | ----------- | -------- | ------ | ---- | -------------- | ------- | ----- |\n"
                "| 1 | `base` | P1 | S | X | ⬜ Pending | b | [brief](features/001-base.md) |\n"
                "| 2 | `needs-base` | P1 | S | X | ⬜ Pending | n | [brief](features/002-needs-base.md) |\n\n"
                "## Dependencies\n\n### Hard implementation dependencies\n\n"
                "**Feature 2 → Feature 1** (still pending)\n\nx\n\n### Recommended implementation order\n\n_None yet._\n")
            (root / "docs/backlog/features-implemented.md").write_text(
                "# Implemented Features\n\n## Feature List\n\n| # | Change name | Priority | Effort | Area | Details |\n"
                "| - | ----------- | -------- | ------ | ---- | ------- |\n| 7 | `done` | P1 | S | X | [brief](features/007-done.md) |\n")
            script = LIB.parent / "skills/features-next/scripts/rank_features.py"
            sel = lambda x: json.loads(subprocess.run([sys.executable, str(script), d, "--select", x, "--json"],
                                                      capture_output=True, text=True, check=True).stdout)
            self.assertFalse(sel("base")["blocked"])
            blocked = sel("needs-base")
            self.assertTrue(blocked["blocked"])
            self.assertEqual(blocked["blocked_on"], "1")
            self.assertIn("error", sel("done"))     # already implemented
            self.assertIn("error", sel("ghost"))    # unknown


