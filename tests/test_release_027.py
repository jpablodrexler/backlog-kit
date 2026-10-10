"""0.2.7: safety and correctness fixes found by the second comparison round."""
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "lib"))
sys.path.insert(0, str(KIT / "tests"))
import backlog_kit as bk  # noqa: E402
import gitread  # noqa: E402
from test_flow import FlowBase, git  # noqa: E402


class DotfileGlobs(unittest.TestCase):
    def test_a_leading_dot_in_a_name_is_kept(self):
        self.assertTrue(bk.glob_match(".github/workflows/ci.yml", [".github/**"]))
        self.assertFalse(bk.glob_match(".github/workflows/ci.yml", ["github/**"]))
        self.assertTrue(bk.glob_match("./src/a.py", ["src/**"]))
        self.assertTrue(bk.glob_match("src\\a.py", ["src/**"]))
        self.assertTrue(bk.glob_match(".env", [".env"]))

    def test_a_single_string_is_one_pattern(self):
        self.assertTrue(bk.glob_match("db/m.sql", "db/**"))


class GitReadAllowlist(unittest.TestCase):
    def test_branch_cannot_create_a_ref_and_diff_cannot_write_a_file(self):
        for bad in (("branch", "sneaky"), ("branch", "sneaky", "HEAD"), ("branch", "--merged", "main", "extra"),
                    ("diff", "--output=/tmp/x"), ("diff", "--output", "/tmp/x"), ("log", "--output=/tmp/x"),
                    ("diff", "--ext-diff")):
            with self.subTest(cmd=bad):
                with self.assertRaises(gitread.GitError):
                    gitread._run(".", *bad)

    def test_listing_forms_stay_allowed(self):
        for ok in (("branch", "--show-current"), ("branch", "--merged", "origin/main"),
                   ("branch", "-r", "--merged", "main"), ("branch", "--format=%(refname:short)")):
            with self.subTest(cmd=ok):
                gitread._check_branch(ok[1:])


class FlowPlanSafety(FlowBase):
    def test_commit_plan_lists_what_is_already_staged(self):
        self.topic()
        (self.repo / "other.py").write_text("x\n")
        git(self.repo, "add", "other.py")
        (self.repo / "app.py").write_text("changed\n")
        out = self.plan("commit")
        self.assertEqual(out["staged"], ["other.py"])
        self.assertTrue(any("already staged" in w for w in out["warnings"]))

    def test_non_ascii_paths_are_reported_as_they_are(self):
        self.topic()
        (self.repo / "café.txt").write_text("x\n")
        out = self.plan("commit")
        self.assertIn("café.txt", [f["path"] for f in out["files"]])
        self.assertIn("café.txt", out["untracked_files"])

    def test_cleanup_does_not_trust_a_local_copy_when_the_remote_has_an_extra_commit(self):
        self.topic("feature/x")
        (self.repo / "a.txt").write_text("a\n")
        git(self.repo, "add", "-A"); git(self.repo, "commit", "-q", "-m", "a")
        git(self.repo, "push", "-q", "-u", "origin", "feature/x")
        git(self.repo, "switch", "-q", "main")
        git(self.repo, "merge", "-q", "--no-ff", "-m", "merge x", "feature/x")
        git(self.repo, "push", "-q", "origin", "main")
        # somebody pushes one more commit to the remote branch after the merge
        git(self.repo, "switch", "-q", "feature/x")
        (self.repo / "b.txt").write_text("b\n")
        git(self.repo, "add", "-A"); git(self.repo, "commit", "-q", "-m", "b")
        git(self.repo, "push", "-q", "origin", "feature/x")
        git(self.repo, "reset", "-q", "--hard", "HEAD~1")
        git(self.repo, "switch", "-q", "main")
        c = {x["branch"]: x for x in self.plan("cleanup", "--fetch")["candidates"]}["feature/x"]
        self.assertTrue(c["remote_has_unmerged_commits"])
        self.assertFalse(c["merged_into_base"])

    def test_an_invalid_start_branch_name_is_a_blocker(self):
        out = self.plan("start", "--branch", "feature/bad name")
        self.assertTrue(any("not a valid branch name" in b for b in out["blockers"]))
        self.assertEqual(self.plan("start", "--branch", "feature/ok")["blockers"], [])


class SkillTextFixes(unittest.TestCase):
    def test_gitflow_commits_explicit_paths_only(self):
        t = (KIT / "skills/gitflow/SKILL.md").read_text()
        self.assertIn("-- <the same paths>", t)
        self.assertIn("remote_has_unmerged_commits", t)

    def test_bug_fix_separates_archive_blocked_from_close_blocked(self):
        t = (KIT / "skills/bug-fix/SKILL.md").read_text()
        self.assertIn("`ARCHIVE_BLOCKED — bugs-archive could not be run", t)
        self.assertIn("On `ARCHIVE_BLOCKED`", t)


if __name__ == "__main__":
    unittest.main()
