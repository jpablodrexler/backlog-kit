"""Regression tests for defects found by comparing the kit with the skills it was extracted from."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
S = KIT / "skills"


def run(script, root, *args):
    out = subprocess.run([sys.executable, str(script), str(root), *args], capture_output=True, text=True, check=True).stdout
    return out


PLANNED = """# Planned Features

## Feature List

| # | Change name | Priority | Effort | Area | SDD Artifacts | Implementation | Summary | Brief |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4 | `shout` | P2 | S | Backend | ⬜ Pending | ⬜ Pending | s | [brief](features/004-shout.md) |

## Dependencies

### Hard implementation dependencies

%s

### Recommended implementation order

- `shout` (#4) — P2
"""
IMPLEMENTED = """# Implemented Features

## Feature List

| # | Change name | Priority | Effort | Area | Details |
| --- | --- | --- | --- | --- | --- |
| 3 | `parser` | P2 | S | Backend | [brief](features/003-parser.md) |
"""


def repo(deps="_None yet._", backlog="docs/backlog", toml='[spec]\nworkflow = "openspec"\n'):
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / ".backlog-kit.toml").write_text(toml + (f'[paths]\nbacklog_dir = "{backlog}"\n' if backlog != "docs/backlog" else ""))
    bl = root / backlog
    (bl / "features").mkdir(parents=True)
    (bl / "features-planned.md").write_text(PLANNED % deps)
    (bl / "features-implemented.md").write_text(IMPLEMENTED)
    (bl / "features/004-shout.md").write_text("# Feature 4 — shout\n\nx\n")
    (bl / "features/003-parser.md").write_text("# Feature 3 — parser\n\nx\n")
    return tmp, root


class SddArtifactsFromDisk(unittest.TestCase):
    def test_artifacts_on_disk_count_as_ready_even_if_the_cell_lags(self):
        tmp, root = repo()
        self.addCleanup(tmp.cleanup)
        ch = root / "openspec/changes/shout"
        (ch / "specs/shout").mkdir(parents=True)
        for f in ("proposal.md", "tasks.md", "specs/shout/spec.md"):
            (ch / f).write_text("x\n")
        ranked = json.loads(run(S / "features-next/scripts/rank_features.py", root, "--json"))
        self.assertTrue(ranked["top"]["artifacts_ready"])
        text = run(S / "features-status/scripts/status_report.py", root)
        self.assertIn("1 of 1 pending features already have spec artifacts", text)
        self.assertIn("`SDD Artifacts` cell is not `✅ Created`", text)

    def test_without_artifacts_it_is_not_ready(self):
        tmp, root = repo()
        self.addCleanup(tmp.cleanup)
        ranked = json.loads(run(S / "features-next/scripts/rank_features.py", root, "--json"))
        self.assertFalse(ranked["top"]["artifacts_ready"])

    def test_close_phase_prose_sets_the_cell(self):
        text = (S / "feature-development/SKILL.md").read_text()
        self.assertIn("`✅ Created`", text)
        self.assertIn("applyRequires", text)


class SpecLinkDepth(unittest.TestCase):
    def link(self, backlog):
        tmp, root = repo(backlog=backlog)
        self.addCleanup(tmp.cleanup)
        (root / "openspec/changes/archive/2026-10-09-parser").mkdir(parents=True)
        return json.loads(subprocess.run([sys.executable, str(S / "features-archive/scripts/spec_link.py"), str(root), "parser"],
                                         capture_output=True, text=True, check=True).stdout)

    def test_two_levels_deep(self):
        self.assertEqual(self.link("docs/backlog")["link"], "../../openspec/changes/archive/2026-10-09-parser/proposal.md")

    def test_three_levels_deep(self):
        self.assertEqual(self.link("Web/docs/backlog")["link"], "../../../openspec/changes/archive/2026-10-09-parser/proposal.md")

    def test_one_level_deep_and_not_yet_archived(self):
        out = self.link("backlog")
        self.assertEqual(out["link"], "../openspec/changes/archive/2026-10-09-parser/proposal.md")
        tmp, root = repo()
        self.addCleanup(tmp.cleanup)
        res = json.loads(subprocess.run([sys.executable, str(S / "features-archive/scripts/spec_link.py"), str(root), "nothing"],
                                        capture_output=True, text=True, check=True).stdout)
        self.assertFalse(res["exists"])


class ProseStaleDependencyNotes(unittest.TestCase):
    def status(self, deps):
        tmp, root = repo(deps=deps)
        self.addCleanup(tmp.cleanup)
        return run(S / "features-status/scripts/status_report.py", root)

    def test_prose_form_is_caught_when_the_prerequisite_shipped(self):
        text = self.status("`shout` needs the parser (#3), which is still pending.")
        self.assertIn("Stale dependency note", text)

    def test_features_n_and_m_form(self):
        self.assertIn("Stale dependency note", self.status("Features 3 and 9 are still pending, so `shout` waits."))

    def test_a_note_about_an_unshipped_feature_is_left_alone(self):
        self.assertNotIn("Stale dependency note", self.status("`shout` needs #9, which is still pending."))


class ClosedBugsKeepTheirWriteUp(unittest.TestCase):
    def test_wont_fix_without_resolution_or_file_is_flagged(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        bl = root / "docs/backlog"
        (bl / "bugs").mkdir(parents=True)
        (bl / "bugs-open.md").write_text("# Open Bugs\n\n## Bug List\n\n| Bug ID | Severity | Area | Environment | Status | Fix | Summary |\n| --- | --- | --- | --- | --- | --- | --- |\n"
                                        "| [BUG-001](bugs/BUG-001.md) | S3 | a | local | 🚫 Won't fix | | nope |\n| [BUG-002](bugs/BUG-002.md) | S3 | a | local | ❓ Cannot reproduce | | cannot |\n")
        (bl / "bugs-fixed.md").write_text("# Fixed Bugs\n\n## Bug List\n\n| Bug ID | Severity | Area | Environment | Fixed | Fix | Summary |\n| --- | --- | --- | --- | --- | --- | --- |\n")
        (bl / "bugs/BUG-001.md").write_text("# BUG-001 — a\n\n- **Steps to reproduce:** x\n")      # no Resolution line
        text = run(S / "bugs-status/scripts/status_report.py", root)
        self.assertIn("BUG-001 is closed", text)
        self.assertIn("BUG-002 has a table row but no", text)       # details file missing entirely


class SkillTextFixes(unittest.TestCase):
    def read(self, rel):
        return (KIT / rel).read_text()

    def test_decision_record_writes_nothing_before_confirmation(self):
        t = self.read("skills/decision-record/SKILL.md")
        self.assertIn("do not create anything yet", t)
        self.assertLess(t.index("do not create anything yet"), t.index("### 5. Confirm before writing"))
        self.assertIn("Nothing under `<decisions_dir>` is written before this step", t)

    def test_bugs_archive_never_leaves_two_resolution_lines(self):
        t = self.read("skills/bugs-archive/SKILL.md")
        self.assertIn("replace that one line instead", t)
        self.assertIn("never add a second", t)
        self.assertIn("offer to create it", t)

    def test_gate_loop_is_capped_and_configurable(self):
        t = self.read("shared/phase-gates.md")
        self.assertIn("`gate_max_rounds`", t)
        self.assertIn("still failing after <N> fix rounds", t)
        sys.path.insert(0, str(KIT / "lib"))
        import backlog_kit
        self.assertEqual(backlog_kit.load_config(KIT)["work"]["gate_max_rounds"], 3)

    def test_openspec_skills_are_preflighted(self):
        t = self.read("skills/feature-development/SKILL.md")
        self.assertIn("`openspec-propose`, `openspec-apply-change` and `openspec-archive-change` are among your available skills", t)

    def test_gitflow_cleanup_never_uses_force_delete(self):
        t = self.read("skills/gitflow/SKILL.md")
        self.assertIn("never `-D`", t)
        self.assertIn("just_started", t)
        self.assertIn("protected_branches", t)


if __name__ == "__main__":
    unittest.main()
