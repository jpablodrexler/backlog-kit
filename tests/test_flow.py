"""flow_plan.py against real throwaway git repos (a bare origin plus a clone)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
SCRIPT = KIT / "skills/gitflow/scripts/flow_plan.py"
ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

IMPLEMENTED = """# Implemented Features

## Feature List

| # | Change name | Priority | Effort | Area | Details |
| --- | ----------- | -------- | ------ | ---- | ------- |
"""
FIXED = """# Fixed Bugs

## Bug List

| Bug ID | Severity | Area | Environment | Fixed | Fix | Summary |
| ------ | -------- | ---- | ----------- | ----- | --- | ------- |
"""


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, env=ENV, check=True).stdout


class FlowBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.origin, self.repo = t / "origin.git", t / "work"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.origin)], check=True)
        subprocess.run(["git", "clone", "-q", str(self.origin), str(self.repo)], check=True, capture_output=True)
        (self.repo / "docs/backlog").mkdir(parents=True)
        (self.repo / "docs/backlog/features-implemented.md").write_text(IMPLEMENTED)
        (self.repo / "docs/backlog/bugs-fixed.md").write_text(FIXED)
        (self.repo / "app.py").write_text("print('hi')\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "init")
        git(self.repo, "branch", "-M", "main")
        git(self.repo, "push", "-q", "-u", "origin", "main")
        git(self.repo, "remote", "set-head", "origin", "main")

    def tearDown(self):
        self.tmp.cleanup()

    def plan(self, action, *extra):
        out = subprocess.run([sys.executable, str(SCRIPT), str(self.repo), "--action", action, *extra],
                             capture_output=True, text=True, check=True).stdout
        return json.loads(out)

    def topic(self, name="feature/arg-parser"):
        git(self.repo, "switch", "-q", "-c", name, "--no-track", "origin/main")

    def finish_work(self):
        (self.repo / "app.py").write_text("print('hello')\n")
        (self.repo / "docs/backlog/features-implemented.md").write_text(
            IMPLEMENTED + "| 3 | `arg-parser` | P2 | S | Backend | [brief](features/003-arg-parser.md) |\n")
        (self.repo / "docs/reports/review").mkdir(parents=True)
        (self.repo / "docs/reports/review/code-arg-parser.md").write_text("clean\n")


class CommitPlan(FlowBase):
    def test_refuses_on_the_base_branch(self):
        (self.repo / "app.py").write_text("x\n")
        out = self.plan("commit")
        self.assertTrue(out["on_base"])
        self.assertTrue(any("base branch" in b for b in out["blockers"]))

    def test_nothing_to_commit_is_a_blocker(self):
        self.topic()
        self.assertIn("nothing to commit", self.plan("commit")["blockers"])

    def test_lists_files_by_kind_flags_secrets_and_names_closed_items(self):
        self.topic()
        self.finish_work()
        (self.repo / ".env").write_text("TOKEN=1\n")
        (self.repo / ".env.example").write_text("TOKEN=\n")
        (self.repo / "docs/backlog/bugs-fixed.md").write_text(FIXED + "| [BUG-007](bugs/BUG-007.md) | S2 | x | local | 2026-10-10 | | The thing broke. |\n")
        out = self.plan("commit")
        self.assertEqual(out["blockers"], [])
        files = {f["path"]: f for f in out["files"]}
        self.assertTrue(files[".env"]["suspicious"])
        self.assertFalse(files[".env.example"]["suspicious"])
        self.assertEqual(files["app.py"]["kind"], "code")
        self.assertEqual(files["docs/reports/review/code-arg-parser.md"]["kind"], "kit")
        self.assertIn({"kind": "feature", "number": "3", "name": "arg-parser"}, out["backlog_closed"])
        self.assertEqual([c["id"] for c in out["backlog_closed"] if c["kind"] == "bug"], ["BUG-007"])
        self.assertTrue(any("secrets" in w for w in out["warnings"]))


class CommitStatIncludesNewFiles(FlowBase):
    def test_untracked_only_change_still_has_a_stat(self):
        self.topic()
        (self.repo / "brand_new.py").write_text("a\nb\n")
        out = self.plan("commit")
        self.assertEqual(out["untracked_files"], ["brand_new.py"])
        self.assertIn("brand_new.py (new file, 2 lines)", out["diff_stat"])


class FinishPlan(FlowBase):
    def commit_all(self):
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "Add parseArgs (feature 3)")

    def test_blocks_on_dirty_tree_and_on_no_commits(self):
        self.topic()
        out = self.plan("finish")
        self.assertTrue(any("no commits ahead" in b for b in out["blockers"]))
        self.finish_work()
        self.assertTrue(any("uncommitted" in b for b in self.plan("finish")["blockers"]))

    def test_describes_the_pr_from_the_real_branch(self):
        self.topic()
        self.finish_work()
        self.commit_all()
        out = self.plan("finish")
        self.assertEqual(out["blockers"], [])
        self.assertEqual(out["title"], "Feature arg-parser")
        self.assertEqual(out["commit_count"], 1)
        self.assertEqual(out["reports"], ["docs/reports/review/code-arg-parser.md"])
        self.assertIn("app.py", out["files"])
        self.assertEqual(out["backlog_closed"][0]["name"], "arg-parser")
        self.assertFalse(out["pushed"])
        git(self.repo, "push", "-q", "-u", "origin", "feature/arg-parser")
        self.assertTrue(self.plan("finish")["pushed"])

    def test_fix_branch_title_and_moved_base_warning(self):
        self.topic("fix/bug-007")
        self.finish_work()
        self.commit_all()
        other = Path(self.tmp.name) / "other"
        subprocess.run(["git", "clone", "-q", str(self.origin), str(other)], check=True, capture_output=True)
        (other / "new.txt").write_text("x\n")
        git(other, "add", "-A")
        git(other, "commit", "-q", "-m", "elsewhere")
        git(other, "push", "-q", "origin", "main")
        out = self.plan("finish", "--fetch")
        self.assertEqual(out["title"], "Fix bug-007")
        self.assertTrue(any("lacks" in w for w in out["warnings"]))
        self.assertEqual(self.plan("sync", "--fetch")["behind_base"], 1)


class CleanupPlan(FlowBase):
    def test_distinguishes_merged_from_unmerged_topic_branches(self):
        for name, merge in (("feature/done", True), ("feature/open", False), ("fix/old", True)):
            git(self.repo, "switch", "-q", "-c", name, "--no-track", "origin/main")
            (self.repo / f"{name.replace('/', '-')}.txt").write_text("x\n")
            git(self.repo, "add", "-A")
            git(self.repo, "commit", "-q", "-m", name)
            if merge:
                git(self.repo, "switch", "-q", "main")
                git(self.repo, "merge", "-q", "--no-ff", "-m", "merge " + name, name)
                git(self.repo, "push", "-q", "origin", "main")
            git(self.repo, "switch", "-q", "main")
        git(self.repo, "branch", "scratch")      # not a topic prefix: never a candidate
        out = self.plan("cleanup")
        by = {c["branch"]: c for c in out["candidates"]}
        self.assertEqual(sorted(by), ["feature/done", "feature/open", "fix/old"])
        self.assertTrue(by["feature/done"]["merged_into_base"] and by["fix/old"]["merged_into_base"])
        self.assertFalse(by["feature/open"]["merged_into_base"])
        self.assertEqual(by["feature/open"]["ahead_of_base"], 1)

    def test_a_branch_just_started_is_not_reported_as_merged(self):
        git(self.repo, "branch", "feature/fresh")                  # sits on the base tip
        out = self.plan("cleanup")
        c = next(c for c in out["candidates"] if c["branch"] == "feature/fresh")
        self.assertTrue(c["just_started"])
        self.assertFalse(c["merged_into_base"])
        self.assertIn("main", out["protected_branches"])
        self.assertEqual(c["last_author"], "t")

    def test_the_current_branch_is_never_a_candidate(self):
        self.topic("feature/mine")
        self.assertEqual(self.plan("cleanup")["candidates"], [])


class ScriptIsReadOnly(unittest.TestCase):
    def test_flow_plan_only_uses_allowlisted_git(self):
        body = SCRIPT.read_text()
        self.assertNotRegex(body, r"\bsubprocess\b")
        for word in ("commit", "push", "reset", "checkout"):
            self.assertNotRegex(body, rf'gitread\.git\([^)]*"{word}"')


if __name__ == "__main__":
    unittest.main()


class StartPlan(FlowBase):
    def plan_start(self, branch):
        out = subprocess.run([sys.executable, str(SCRIPT), str(self.repo), "--action", "start", "--branch", branch],
                             capture_output=True, text=True, check=True).stdout
        return json.loads(out)

    def test_on_the_base_branch_no_question(self):
        out = self.plan_start("feature/x")
        self.assertFalse(out["needs_question"])

    def test_already_on_another_topic_branch_asks(self):
        self.topic("feature/old")
        (self.repo / "wip.py").write_text("x\n")
        out = self.plan_start("feature/new")
        self.assertTrue(out["needs_question"])
        self.assertFalse(out["current_pushed"])
        self.assertTrue(out["dirty"])

    def test_restarting_the_branch_you_are_on_is_not_a_question(self):
        self.topic("feature/same")
        self.assertFalse(self.plan_start("feature/same")["needs_question"])

    def test_skill_text_has_the_question_and_the_merge_redirect(self):
        t = (KIT / "skills/gitflow/SKILL.md").read_text()
        self.assertIn("**If `needs_question` is true**", t)
        self.assertIn("rename it to `<branch>`", t)
        self.assertIn("A request to merge or pull a branch into a topic branch is `sync`", t)
        self.assertIn("`feature #3` goes into the PR body as `feature 3`", t)
