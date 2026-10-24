"""End-to-end checks of the backlog-kit scripts against throwaway repos.

Run: python3 -m unittest discover -s tests -v   (from the backlog-kit root)
"""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
S = KIT / "skills"
SCRIPTS = {
    "f_next_id": S / "feature-plan/scripts/next_id.py",
    "f_rank": S / "features-next/scripts/rank_features.py",
    "f_status": S / "features-status/scripts/status_report.py",
    "b_next_id": S / "bug-report/scripts/next_id.py",
    "b_rank": S / "bugs-next/scripts/rank_bugs.py",
    "b_status": S / "bugs-status/scripts/status_report.py",
    "adr": S / "decision-record/scripts/next_id.py",
}


def run(key, root, *extra, as_json=True):
    out = subprocess.run([sys.executable, str(SCRIPTS[key]), str(root), *extra],
                         capture_output=True, text=True, encoding="utf-8", check=True).stdout
    return json.loads(out) if as_json else out


def skeleton(root, backlog="docs/backlog"):
    """Create the two backlog files from the skeletons printed in feature-plan/SKILL.md (what the skill tells the model to write)."""
    text = (S / "feature-plan/SKILL.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```markdown\n(.*?)```", text, re.S)
    d = Path(root) / backlog
    d.mkdir(parents=True, exist_ok=True)
    (d / "features-planned.md").write_text(blocks[0], encoding="utf-8")
    (d / "features-implemented.md").write_text(blocks[1], encoding="utf-8")


def frow(n, name, prio="P2", schema="No", effort="3", area="Backend", sdd="⬜ Pending", impl="⬜ Pending", summary=None):
    return (f"| {n} | `{name}` | {prio} | {schema} | {effort} | {area} | {sdd} | {impl} | "
            f"{summary if summary is not None else 'Does ' + name} | [brief](features/{int(n):03d}-{name}.md) |")


def add_feature_row(root, rel, row):
    """Append a table row to a features file, right after the header separator's last row."""
    p = Path(root) / rel
    lines = p.read_text(encoding="utf-8").splitlines()
    idx = max(i for i, ln in enumerate(lines[: lines.index("## Column legend") if "## Column legend" in lines else len(lines)])
              if ln.startswith("|"))
    lines.insert(idx + 1, row)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


class FeatureFlow(unittest.TestCase):
    REL = "docs/backlog/features-planned.md"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_the_skeleton_in_the_skill_is_what_the_scripts_read_and_numbering_starts_at_one(self):
        skeleton(self.root)
        self.assertEqual(run("f_next_id", self.root)["next_number"], 1)
        header = (self.root / self.REL).read_text(encoding="utf-8").splitlines()
        self.assertIn("| # | Change name | Priority | Schema Change | Effort | Area | SDD Artifacts | Implementation | Summary | Brief |", header)
        self.assertIn("## Deployment (migration) dependencies (applied)", (self.root / "docs/backlog/features-implemented.md").read_text(encoding="utf-8"))

    def test_rank_blocks_on_live_prerequisite_and_prefers_in_progress(self):
        skeleton(self.root)
        for r in (frow(1, "alpha", "P1"), frow(2, "beta", "P0", effort="1"), frow(3, "gamma", "P3", effort="5", area="Frontend", impl="🔶 In Progress")):
            add_feature_row(self.root, self.REL, r)
        fdir = self.root / "docs/backlog/features"
        fdir.mkdir()
        for n, name in ((1, "alpha"), (2, "beta"), (3, "gamma")):
            (fdir / f"{n:03d}-{name}.md").write_text(f"# Feature {n} — {name}\n\nbrief\n", encoding="utf-8")

        out = run("f_rank", self.root, "--json")
        self.assertEqual(out["top"]["name"], "gamma", "an in-progress feature outranks a higher-priority pending one")

        # beta (P0) hard-depends on alpha, which is still pending -> beta is blocked
        p = self.root / self.REL
        p.write_text(p.read_text(encoding="utf-8").replace(
            "### Hard implementation dependencies\n\n_None yet._",
            "### Hard implementation dependencies\n\n**Feature 2 → Feature 1** (still pending)\n\n`beta` needs `alpha`."), encoding="utf-8")
        out = run("f_rank", self.root, "--json")
        self.assertEqual([b["number"] for b in out["blocked"]], ["2"])
        self.assertNotIn("beta", [out["top"]["name"]] + [r["name"] for r in out["runners_up"]])

        sel = run("f_rank", self.root, "--select", "beta", "--json")
        self.assertTrue(sel["blocked"])
        self.assertEqual(sel["blocked_on"], "1")

    def test_priority_scoring_is_the_fixed_scale_of_the_source_projects(self):
        skeleton(self.root)
        add_feature_row(self.root, self.REL, frow(1, "a", "P2", schema="Yes"))
        add_feature_row(self.root, self.REL, frow(2, "b", "P0", schema="Yes"))
        add_feature_row(self.root, self.REL, frow(3, "c", "none", schema="Yes"))
        out = run("f_rank", self.root, "--json")
        self.assertEqual(out["top"]["name"], "b")
        self.assertEqual(out["top"]["score"], 400)                                    # P0
        self.assertEqual([(r["name"], r["score"]) for r in out["runners_up"]], [("a", 200), ("c", 50)])

    def test_no_schema_change_and_ready_artifacts_earn_their_bonuses(self):
        skeleton(self.root)
        add_feature_row(self.root, self.REL, frow(1, "a", "P1", schema="Yes"))
        add_feature_row(self.root, self.REL, frow(2, "b", "P1", schema="No"))
        add_feature_row(self.root, self.REL, frow(3, "c", "P1", schema="Yes", sdd="✅ Created"))
        out = run("f_rank", self.root, "--json")
        self.assertEqual([out["top"]["name"]] + [r["name"] for r in out["runners_up"]], ["c", "b", "a"])
        self.assertEqual([out["top"]["score"]] + [r["score"] for r in out["runners_up"]], [320, 305, 300])

    def test_status_reports_integrity_issues(self):
        skeleton(self.root)
        add_feature_row(self.root, self.REL, frow(1, "a", "P1", summary="x" * 300))
        out = run("f_status", self.root, as_json=False)
        self.assertIn("Total features", out)
        self.assertIn("bad Summary", out)
        self.assertIn("no docs/backlog/features/001-a.md file", out)

    def test_status_counts_story_points_and_still_reads_old_sizes(self):
        skeleton(self.root)
        add_feature_row(self.root, self.REL, frow(1, "a", "P1", effort="8"))
        add_feature_row(self.root, self.REL, frow(2, "b", "P1", effort="3"))
        add_feature_row(self.root, self.REL, frow(3, "c", "P1", effort="L"))      # an unconverted size counts as 5
        out = run("f_status", self.root, "--json")
        self.assertEqual(out["effort_breakdown"], {"1": 0, "2": 0, "3": 1, "5": 1, "8": 1, "13": 0, "none": 0})
        self.assertEqual(out["pending_points"], 16)
        text = run("f_status", self.root, as_json=False)
        self.assertIn("| 8            | 1 |", text)
        self.assertIn("**Total pending points** | **16**", text)

    def test_effort_to_points_tool_converts_both_tables_and_the_legend_once(self):
        skeleton(self.root)
        add_feature_row(self.root, self.REL, frow(1, "a", "P1", effort="S"))
        add_feature_row(self.root, self.REL, frow(2, "b", "P1", effort="XL"))
        add_feature_row(self.root, self.REL, frow(3, "c", "P1", effort="5"))
        impl = self.root / "docs/backlog/features-implemented.md"
        impl.write_text(impl.read_text(encoding="utf-8").replace(
            "| - | ------------ | -------- | -------------- | ------ | ---- | -------------------- |",
            "| - | ------------ | -------- | -------------- | ------ | ---- | -------------------- |\n| 9 | `done` | P2 | No | M | Backend | x |"), encoding="utf-8")
        tool = KIT / "tools/effort_to_points.py"
        dry = subprocess.run([sys.executable, str(tool), str(self.root), "--dry-run"], capture_output=True, text=True, encoding="utf-8", check=True).stdout
        self.assertIn("would convert 3 cell(s)", dry)
        self.assertIn("| S |", (self.root / self.REL).read_text(encoding="utf-8"))        # dry run wrote nothing
        out = subprocess.run([sys.executable, str(tool), str(self.root)], capture_output=True, text=True, encoding="utf-8", check=True).stdout
        self.assertIn("converted 3 cell(s)", out)
        planned = (self.root / self.REL).read_text(encoding="utf-8")
        self.assertRegex(planned, r"\| 1 \| `a` \| P1 \| No \| 1 \|")
        self.assertRegex(planned, r"\| 2 \| `b` \| P1 \| No \| 8 \|")
        self.assertRegex(planned, r"\| 3 \| `c` \| P1 \| No \| 5 \|")
        self.assertIn("story points on the Fibonacci scale", planned)
        self.assertRegex(impl.read_text(encoding="utf-8"), r"\| 9 \| `done` \| P2 \| No \| 3 \|")
        again = subprocess.run([sys.executable, str(tool), str(self.root)], capture_output=True, text=True, encoding="utf-8", check=True).stdout
        self.assertIn("converted 0 cell(s)", again)

    def test_status_checks_story_briefs_but_leaves_paragraph_briefs_alone(self):
        skeleton(self.root)
        for n, name in ((1, "old"), (2, "story"), (3, "good")):
            add_feature_row(self.root, self.REL, frow(n, name, "P1"))
        fdir = self.root / "docs/backlog/features"
        fdir.mkdir()
        (fdir / "001-old.md").write_text("# Feature 1 — old\n\nA dense paragraph brief.\n", encoding="utf-8")
        story = "# Feature {n} — {name}\n\n**As a** caregiver, **I want** x, **so that** y.\n"
        (fdir / "002-story.md").write_text(story.format(n=2, name="story"), encoding="utf-8")
        (fdir / "003-good.md").write_text(story.format(n=3, name="good") + "\n## Acceptance Criteria\n- AC1: Given a, when b, then c.\n", encoding="utf-8")
        out = run("f_status", self.root, "--json")
        self.assertEqual([b["name"] for b in out["stories_without_acceptance_criteria"]], ["story"])
        self.assertFalse(out["definition_of_done"])
        (self.root / "docs/backlog/definition-of-done.md").write_text("- [ ] tests pass\n", encoding="utf-8")
        self.assertTrue(run("f_status", self.root, "--json")["definition_of_done"])

    def test_custom_backlog_dir(self):
        (self.root / ".backlog-kit.toml").write_text('[paths]\nbacklog_dir = "planning"\n', encoding="utf-8")
        skeleton(self.root, "planning")
        add_feature_row(self.root, "planning/features-planned.md", frow(4, "d", "P1"))
        (self.root / "planning/features").mkdir()
        (self.root / "planning/features/004-d.md").write_text("# Feature 4 — d\n\nbrief\n", encoding="utf-8")
        self.assertEqual(run("f_next_id", self.root)["next_number"], 5)
        self.assertEqual(run("f_rank", self.root, "--json")["top"]["brief_file"], "planning/features/004-d.md")


def bug_skeleton(root, backlog="docs/backlog"):
    """Create bugs-open.md / bugs-fixed.md from the skeletons printed in bug-report/SKILL.md."""
    text = (S / "bug-report/SKILL.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```markdown\n(.*?)```", text, re.S)
    d = Path(root) / backlog
    d.mkdir(parents=True, exist_ok=True)
    (d / "bugs-open.md").write_text(blocks[0], encoding="utf-8")
    (d / "bugs-fixed.md").write_text(blocks[1], encoding="utf-8")


class BugFlow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def add_bug(self, bug_id, sev, env, status="⬜ Open"):
        p = self.root / "docs/backlog/bugs-open.md"
        text = p.read_text(encoding="utf-8").replace("\n\n_No open bugs._", "")
        lines = text.splitlines()
        sep = next(i for i, ln in enumerate(lines) if ln.startswith("| ---"))
        end = sep + 1
        while end < len(lines) and lines[end].startswith("|"):
            end += 1
        lines.insert(end, f"| [{bug_id}](bugs/{bug_id}.md) | {sev} | /x | {env} | {status} | | summary {bug_id} |")
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        bdir = self.root / "docs/backlog/bugs"
        bdir.mkdir(exist_ok=True)
        (bdir / f"{bug_id}.md").write_text(f"# {bug_id} — title\n\n- **Expected:** x\n", encoding="utf-8")

    def test_numbering_follows_the_skeleton_in_the_skill(self):
        bug_skeleton(self.root)
        self.assertEqual(run("b_next_id", self.root)["next_id"], "BUG-001")
        self.add_bug("BUG-007", "S2", "local")
        self.assertEqual(run("b_next_id", self.root)["next_id"], "BUG-008")

    def test_rank_in_progress_then_severity_then_prod(self):
        bug_skeleton(self.root)
        self.add_bug("BUG-001", "S1", "local")
        self.add_bug("BUG-002", "S2", "deployed")
        self.add_bug("BUG-003", "S4", "local", status="🔶 In Progress")
        out = run("b_rank", self.root, "--json")
        self.assertEqual(out["top"]["id"], "BUG-003")
        self.assertEqual([r["id"] for r in out["runners_up"]], ["BUG-001", "BUG-002"])

    def test_select_revalidates_so_a_stale_confirmed_id_is_refused(self):
        # bugs-next resolves a typed id with --select; a closed / won't-fix / unknown id must not resolve.
        bug_skeleton(self.root)
        self.add_bug("BUG-001", "S2", "local")
        self.add_bug("BUG-002", "S2", "local", status="🚫 Won't fix")
        self.add_bug("BUG-003", "S2", "local", status="❓ Cannot reproduce")
        ok = run("b_rank", self.root, "--select", "BUG-001", "--json")
        self.assertEqual(ok["selected"]["id"], "BUG-001")
        for stale in ("BUG-002", "BUG-003", "BUG-099"):
            self.assertIn("error", run("b_rank", self.root, "--select", stale, "--json"), stale)

    def test_status_counts_and_integrity(self):
        bug_skeleton(self.root)
        self.add_bug("BUG-001", "S1", "prod")
        (self.root / "docs/backlog/bugs/BUG-009.md").write_text("# BUG-009 — orphan\n", encoding="utf-8")
        out = run("b_status", self.root, as_json=False)
        self.assertRegex(out, r"\| ⬜ Open\s+\| 1 \|")
        self.assertIn("BUG-009.md exists but BUG-009 has no table row", out)


class AdrNumbering(unittest.TestCase):
    def test_next_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run("adr", tmp)["next_number"], "0001")
            d = Path(tmp) / "docs/decisions"
            d.mkdir(parents=True)
            (d / "0031-x.md").write_text("x", encoding="utf-8")
            self.assertEqual(run("adr", tmp)["next_number"], "0032")


if __name__ == "__main__":
    unittest.main()


