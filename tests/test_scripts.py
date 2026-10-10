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
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out) if as_json else out


def skeleton(root, backlog="docs/backlog"):
    """Create the two backlog files from the skeletons printed in feature-plan/SKILL.md (what the skill tells the model to write)."""
    text = (S / "feature-plan/SKILL.md").read_text()
    blocks = re.findall(r"```markdown\n(.*?)```", text, re.S)
    d = Path(root) / backlog
    d.mkdir(parents=True, exist_ok=True)
    (d / "features-planned.md").write_text(blocks[0])
    (d / "features-implemented.md").write_text(blocks[1])


def frow(n, name, prio="P2", schema="No", effort="M", area="Backend", sdd="⬜ Pending", impl="⬜ Pending", summary=None):
    return (f"| {n} | `{name}` | {prio} | {schema} | {effort} | {area} | {sdd} | {impl} | "
            f"{summary if summary is not None else 'Does ' + name} | [brief](features/{int(n):03d}-{name}.md) |")


def add_feature_row(root, rel, row):
    """Append a table row to a features file, right after the header separator's last row."""
    p = Path(root) / rel
    lines = p.read_text().splitlines()
    idx = max(i for i, ln in enumerate(lines[: lines.index("## Column legend") if "## Column legend" in lines else len(lines)])
              if ln.startswith("|"))
    lines.insert(idx + 1, row)
    p.write_text("\n".join(lines) + "\n")


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
        header = (self.root / self.REL).read_text().splitlines()
        self.assertIn("| # | Change name | Priority | Schema Change | Effort | Area | SDD Artifacts | Implementation | Summary | Brief |", header)
        self.assertIn("## Deployment (migration) dependencies (applied)", (self.root / "docs/backlog/features-implemented.md").read_text())

    def test_rank_blocks_on_live_prerequisite_and_prefers_in_progress(self):
        skeleton(self.root)
        for r in (frow(1, "alpha", "P1"), frow(2, "beta", "P0", effort="S"), frow(3, "gamma", "P3", effort="L", area="Frontend", impl="🔶 In Progress")):
            add_feature_row(self.root, self.REL, r)
        fdir = self.root / "docs/backlog/features"
        fdir.mkdir()
        for n, name in ((1, "alpha"), (2, "beta"), (3, "gamma")):
            (fdir / f"{n:03d}-{name}.md").write_text(f"# Feature {n} — {name}\n\nbrief\n")

        out = run("f_rank", self.root, "--json")
        self.assertEqual(out["top"]["name"], "gamma", "an in-progress feature outranks a higher-priority pending one")

        # beta (P0) hard-depends on alpha, which is still pending -> beta is blocked
        p = self.root / self.REL
        p.write_text(p.read_text().replace(
            "### Hard implementation dependencies\n\n_None yet._",
            "### Hard implementation dependencies\n\n**Feature 2 → Feature 1** (still pending)\n\n`beta` needs `alpha`."))
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

    def test_custom_backlog_dir(self):
        (self.root / ".backlog-kit.toml").write_text('[paths]\nbacklog_dir = "planning"\n')
        skeleton(self.root, "planning")
        add_feature_row(self.root, "planning/features-planned.md", frow(4, "d", "P1"))
        (self.root / "planning/features").mkdir()
        (self.root / "planning/features/004-d.md").write_text("# Feature 4 — d\n\nbrief\n")
        self.assertEqual(run("f_next_id", self.root)["next_number"], 5)
        self.assertEqual(run("f_rank", self.root, "--json")["top"]["brief_file"], "planning/features/004-d.md")


def bug_skeleton(root, backlog="docs/backlog"):
    """Create bugs-open.md / bugs-fixed.md from the skeletons printed in bug-report/SKILL.md."""
    text = (S / "bug-report/SKILL.md").read_text()
    blocks = re.findall(r"```markdown\n(.*?)```", text, re.S)
    d = Path(root) / backlog
    d.mkdir(parents=True, exist_ok=True)
    (d / "bugs-open.md").write_text(blocks[0])
    (d / "bugs-fixed.md").write_text(blocks[1])


class BugFlow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def add_bug(self, bug_id, sev, env, status="⬜ Open"):
        p = self.root / "docs/backlog/bugs-open.md"
        text = p.read_text().replace("\n\n_No open bugs._", "")
        lines = text.splitlines()
        sep = next(i for i, ln in enumerate(lines) if ln.startswith("| ---"))
        end = sep + 1
        while end < len(lines) and lines[end].startswith("|"):
            end += 1
        lines.insert(end, f"| [{bug_id}](bugs/{bug_id}.md) | {sev} | /x | {env} | {status} | | summary {bug_id} |")
        p.write_text("\n".join(lines) + "\n")
        bdir = self.root / "docs/backlog/bugs"
        bdir.mkdir(exist_ok=True)
        (bdir / f"{bug_id}.md").write_text(f"# {bug_id} — title\n\n- **Expected:** x\n")

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
        (self.root / "docs/backlog/bugs/BUG-009.md").write_text("# BUG-009 — orphan\n")
        out = run("b_status", self.root, as_json=False)
        self.assertRegex(out, r"\| ⬜ Open\s+\| 1 \|")
        self.assertIn("BUG-009.md exists but BUG-009 has no table row", out)


class AdrNumbering(unittest.TestCase):
    def test_next_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run("adr", tmp)["next_number"], "0001")
            d = Path(tmp) / "docs/decisions"
            d.mkdir(parents=True)
            (d / "0031-x.md").write_text("x")
            self.assertEqual(run("adr", tmp)["next_number"], "0032")


if __name__ == "__main__":
    unittest.main()


