"""End-to-end checks of the backlog-kit scripts against throwaway repos.

Run: python3 -m unittest discover -s tests -v   (from the backlog-kit root)
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
S = KIT / "skills"
SCRIPTS = {
    "f_scaffold": S / "feature-plan/scripts/scaffold.py",
    "f_next_id": S / "feature-plan/scripts/next_id.py",
    "f_rank": S / "features-next/scripts/rank_features.py",
    "f_status": S / "features-status/scripts/status_report.py",
    "b_scaffold": S / "bug-report/scripts/scaffold.py",
    "b_next_id": S / "bug-report/scripts/next_id.py",
    "b_rank": S / "bugs-next/scripts/rank_bugs.py",
    "b_status": S / "bugs-status/scripts/status_report.py",
    "adr": S / "decision-record/scripts/next_id.py",
}


def run(key, root, *extra, as_json=True):
    out = subprocess.run([sys.executable, str(SCRIPTS[key]), str(root), *extra],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out) if as_json else out


def add_feature_row(root, rel, row):
    """Append a table row to a features file, right after the header separator's last row."""
    p = Path(root) / rel
    lines = p.read_text().splitlines()
    idx = max(i for i, ln in enumerate(lines[: lines.index("## Column legend") if "## Column legend" in lines else len(lines)])
              if ln.startswith("|"))
    lines.insert(idx + 1, row)
    p.write_text("\n".join(lines) + "\n")


class FeatureFlow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_scaffold_is_idempotent_and_numbering_starts_at_one(self):
        first = run("f_scaffold", self.root)
        self.assertEqual(len(first["created"]), 2)
        again = run("f_scaffold", self.root)
        self.assertEqual(again["created"], [])
        self.assertEqual(run("f_next_id", self.root)["next_number"], 1)

    def test_rank_blocks_on_live_prerequisite_and_prefers_in_progress(self):
        run("f_scaffold", self.root)
        rel = "docs/backlog/features-planned.md"
        rows = [
            "| 1 | `alpha` | P1 | M | Backend | ⬜ Pending | Does alpha | [brief](features/001-alpha.md) |",
            "| 2 | `beta` | P0 | S | Backend | ⬜ Pending | Does beta | [brief](features/002-beta.md) |",
            "| 3 | `gamma` | P3 | L | Frontend | 🔶 In Progress | Does gamma | [brief](features/003-gamma.md) |",
        ]
        for r in rows:
            add_feature_row(self.root, rel, r)
        fdir = self.root / "docs/backlog/features"
        fdir.mkdir()
        for n, name in ((1, "alpha"), (2, "beta"), (3, "gamma")):
            (fdir / f"{n:03d}-{name}.md").write_text(f"# Feature {n} — {name}\n\nbrief\n")

        out = run("f_rank", self.root, "--json")
        self.assertEqual(out["top"]["name"], "gamma", "an in-progress feature outranks a higher-priority pending one")

        # beta (P0) hard-depends on alpha, which is still pending -> beta is blocked
        p = self.root / rel
        p.write_text(p.read_text().replace(
            "### Hard implementation dependencies\n\n_None yet._",
            "### Hard implementation dependencies\n\n**Feature 2 → Feature 1** (still pending)\n\n`beta` needs `alpha`."))
        out = run("f_rank", self.root, "--json")
        self.assertEqual([b["number"] for b in out["blocked"]], ["2"])
        self.assertNotIn("beta", [out["top"]["name"]] + [r["name"] for r in out["runners_up"]])

        sel = run("f_rank", self.root, "--select", "beta", "--json")
        self.assertTrue(sel["blocked"])
        self.assertEqual(sel["blocked_on"], "1")

    def test_priority_scoring_follows_configured_order(self):
        (self.root / ".backlog-kit.toml").write_text('[features]\npriorities = ["urgent", "normal"]\nefforts = ["S", "L"]\n')
        run("f_scaffold", self.root)
        rel = "docs/backlog/features-planned.md"
        add_feature_row(self.root, rel, "| 1 | `a` | normal | S | X | ⬜ Pending | a | [brief](features/001-a.md) |")
        add_feature_row(self.root, rel, "| 2 | `b` | urgent | L | X | ⬜ Pending | b | [brief](features/002-b.md) |")
        out = run("f_rank", self.root, "--json")
        self.assertEqual(out["top"]["name"], "b")
        self.assertEqual(out["top"]["score"], 200)  # 2 tiers -> urgent = 200

    def test_openspec_workflow_adds_column_and_ready_bonus(self):
        (self.root / ".backlog-kit.toml").write_text('[spec]\nworkflow = "openspec"\n')
        run("f_scaffold", self.root)
        self.assertIn("SDD Artifacts", run("f_next_id", self.root)["planned_header"])
        rel = "docs/backlog/features-planned.md"
        add_feature_row(self.root, rel, "| 1 | `a` | P1 | M | X | ⬜ Pending | ⬜ Pending | a | [brief](features/001-a.md) |")
        add_feature_row(self.root, rel, "| 2 | `b` | P1 | M | X | ✅ Created | ⬜ Pending | b | [brief](features/002-b.md) |")
        out = run("f_rank", self.root, "--json")
        self.assertEqual(out["top"]["name"], "b")

    def test_status_reports_integrity_issues(self):
        run("f_scaffold", self.root)
        add_feature_row(self.root, "docs/backlog/features-planned.md",
                        "| 1 | `a` | P1 | M | X | ⬜ Pending | " + "x" * 300 + " | [brief](features/001-a.md) |")
        out = run("f_status", self.root, as_json=False)
        self.assertIn("Total features", out)
        self.assertIn("bad Summary", out)
        self.assertIn("no docs/backlog/features/001-a.md file", out)

    def test_custom_backlog_dir(self):
        (self.root / ".backlog-kit.toml").write_text('[paths]\nbacklog_dir = "planning"\n')
        run("f_scaffold", self.root)
        self.assertTrue((self.root / "planning/features-planned.md").is_file())
        self.assertFalse((self.root / "docs").exists())


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

    def test_numbering_and_scaffold(self):
        run("b_scaffold", self.root)
        self.assertEqual(run("b_next_id", self.root)["next_id"], "BUG-001")
        self.add_bug("BUG-007", "S2", "local")
        self.assertEqual(run("b_next_id", self.root)["next_id"], "BUG-008")

    def test_custom_prefix(self):
        (self.root / ".backlog-kit.toml").write_text('[bugs]\nid_prefix = "ISSUE"\n')
        run("b_scaffold", self.root)
        self.assertEqual(run("b_next_id", self.root)["next_id"], "ISSUE-001")

    def test_rank_in_progress_then_severity_then_prod(self):
        run("b_scaffold", self.root)
        self.add_bug("BUG-001", "S1", "local")
        self.add_bug("BUG-002", "S2", "prod")
        self.add_bug("BUG-003", "S4", "local", status="🔶 In Progress")
        out = run("b_rank", self.root, "--json")
        self.assertEqual(out["top"]["id"], "BUG-003")
        self.assertEqual([r["id"] for r in out["runners_up"]], ["BUG-001", "BUG-002"])

    def test_select_revalidates_so_a_stale_confirmed_id_is_refused(self):
        # bugs-next --confirmed resolves the id with --select; a closed / won't-fix / unknown id must not resolve.
        run("b_scaffold", self.root)
        self.add_bug("BUG-001", "S2", "local")
        self.add_bug("BUG-002", "S2", "local", status="🚫 Won't fix")
        self.add_bug("BUG-003", "S2", "local", status="❓ Cannot reproduce")
        ok = run("b_rank", self.root, "--select", "BUG-001", "--json")
        self.assertEqual(ok["selected"]["id"], "BUG-001")
        for stale in ("BUG-002", "BUG-003", "BUG-099"):
            self.assertIn("error", run("b_rank", self.root, "--select", stale, "--json"), stale)

    def test_status_counts_and_integrity(self):
        run("b_scaffold", self.root)
        self.add_bug("BUG-001", "S1", "prod")
        (self.root / "docs/backlog/bugs/BUG-009.md").write_text("# BUG-009 — orphan\n")
        out = run("b_status", self.root, as_json=False)
        self.assertIn("| ⬜ Open | 1 |", out)
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
