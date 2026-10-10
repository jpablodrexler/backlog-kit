"""0.2.8: the review phase and the reviewer skills agree on one input contract."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
REVIEWERS = ("code-reviewer", "security-reviewer", "database-reviewer")


def scope(cfg_text, *files, create=()):
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / ".backlog-kit.toml").write_text(cfg_text)
        for f in create:
            p = Path(d) / f
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("x\n")
        out = subprocess.run([sys.executable, str(KIT / "lib/work_scope.py"), d, "--files", *files],
                             capture_output=True, text=True, check=True).stdout
        return json.loads(out)


class WorkScopeReviewLists(unittest.TestCase):
    CFG = '[[reviews]]\nname = "db"\nskill = "database-reviewer"\nwhen = ["db/**", "package-lock.json"]\n'

    def test_a_review_gets_every_matching_file_not_the_first_twenty(self):
        files = [f"db/m{i:03d}.sql" for i in range(35)]
        out = scope(self.CFG, *files, "src/a.py", create=files)
        self.assertEqual(out["reviews"][0]["matched_files"], sorted(files))

    def test_deleted_and_bulk_files_are_named(self):
        out = scope(self.CFG, "db/old.sql", "db/new.sql", "package-lock.json", create=["db/new.sql", "package-lock.json"])
        r = out["reviews"][0]
        self.assertEqual(r["deleted_files"], ["db/old.sql"])
        self.assertEqual(r["bulk_files"], ["package-lock.json"])


class ReviewerContract(unittest.TestCase):
    def test_every_reviewer_takes_the_same_inputs(self):
        for name in REVIEWERS:
            t = (KIT / "skills" / name / "SKILL.md").read_text()
            for needle in ("`deleted_files` (optional)", "`bulk_files` (optional)", "Default `adhoc` when absent",
                           "`self_review` (optional)", "git diff HEAD -- <file>", "<file>[:<line>]", "Self-reviewed: yes"):
                with self.subTest(skill=name, needle=needle):
                    self.assertIn(needle, t)

    def test_a_file_list_alone_selects_non_interactive_mode(self):
        t = (KIT / "skills/code-reviewer/SKILL.md").read_text()
        self.assertIn("If the caller gave a file list, it is the non-interactive mode", t)



if __name__ == "__main__":
    unittest.main()
