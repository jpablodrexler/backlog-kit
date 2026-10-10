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


class OrderNoteCleanup(unittest.TestCase):
    """Stale free-text "blocked on #N" notes in the Recommended implementation order."""

    PLANNED = """# Planned Features

## Feature List

| # | Change name | Priority | Effort | Area | Implementation | Summary | Brief |
| - | ----------- | -------- | ------ | ---- | -------------- | ------- | ----- |
| 2 | `log` | P3 | S | Backend | ⬜ Pending | s | [brief](features/002-log.md) |
| 3 | `dash` | P3 | M | Full-stack | ⬜ Pending | s | [brief](features/003-dash.md) |
| 4 | `multi` | P3 | M | Backend | ⬜ Pending | s | [brief](features/004-multi.md) |

## Dependencies

### Hard implementation dependencies

_None yet._

### Recommended implementation order

- `log` (#2) — P3, blocked on #1 (logs the names its resolver produces), small
- `dash` (#3) — blocked on #1, P3, medium
- `multi` (#4) — P3, blocked on #1 and #3 (needs both), medium
- `other` (#9) — P3, blocked on #8, small
"""
    IMPL = """# Implemented Features

## Feature List

| # | Change name | Priority | Effort | Area | Details |
| - | ----------- | -------- | ------ | ---- | ------- |
| 1 | `resolver` | P2 | S | Backend | [brief](features/001-resolver.md) |
"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        bl = self.root / "docs/backlog"
        bl.mkdir(parents=True)
        (bl / "features-planned.md").write_text(self.PLANNED)
        (bl / "features-implemented.md").write_text(self.IMPL)
        self.script = KIT / "skills/features-archive/scripts/clean_order_notes.py"

    def tearDown(self):
        self.tmp.cleanup()

    def clean(self, *extra):
        out = subprocess.run([sys.executable, str(self.script), str(self.root), *extra], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout)

    def text(self):
        return (self.root / "docs/backlog/features-planned.md").read_text()

    def test_removes_shipped_prerequisites_and_nothing_else(self):
        res = self.clean()
        self.assertTrue(res["written"])
        t = self.text()
        self.assertIn("- `log` (#2) — P3, small\n", t)
        self.assertIn("- `dash` (#3) — P3, medium\n", t)
        self.assertIn("- `multi` (#4) — P3, blocked on #3, medium\n", t)       # #3 still pending, kept
        self.assertIn("- `other` (#9) — P3, blocked on #8, small\n", t)        # unrelated note untouched
        self.assertEqual(t.split("### Recommended")[0], self.PLANNED.split("### Recommended")[0])

    def test_is_idempotent_and_dry_run_writes_nothing(self):
        self.assertFalse(self.clean("--dry-run")["written"])
        self.assertEqual(self.text(), self.PLANNED)
        self.clean()
        again = self.clean()
        self.assertEqual(again["changed"], [])
        self.assertFalse(again["written"])


class OrderPlaceholder(unittest.TestCase):
    def test_emptied_order_list_gets_its_placeholder_back_once(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bl = root / "docs/backlog"
            bl.mkdir(parents=True)
            (bl / "features-planned.md").write_text(
                "# Planned Features\n\n## Feature List\n\n| # | Change name | Priority | Effort | Area | Implementation | Summary | Brief |\n"
                "| - | - | - | - | - | - | - | - |\n\n## Dependencies\n\n### Recommended implementation order\n\nNot a schedule.\n")
            (bl / "features-implemented.md").write_text("# Implemented Features\n\n## Feature List\n\n| # | Change name | Priority | Effort | Area | Details |\n| - | - | - | - | - | - |\n")
            script = KIT / "skills/features-archive/scripts/clean_order_notes.py"
            first = json.loads(subprocess.run([sys.executable, str(script), d], capture_output=True, text=True, check=True).stdout)
            self.assertTrue(first["placeholder_restored"] and first["written"])
            text = (bl / "features-planned.md").read_text()
            self.assertTrue(text.rstrip().endswith("Not a schedule.\n\n_None yet._"), text)
            second = json.loads(subprocess.run([sys.executable, str(script), d], capture_output=True, text=True, check=True).stdout)
            self.assertFalse(second["placeholder_restored"] or second["written"])


class DependencyScan(unittest.TestCase):
    """dep_scan: unrecorded hard dependencies implied by briefs (a vague brief once hid one)."""

    HEAD = ("# Planned Features\n\n## Feature List\n\n"
            "| # | Change name | Priority | Effort | Area | Implementation | Summary | Brief |\n| --- | --- | --- | --- | --- | --- | --- | --- |\n")

    def build(self, briefs, deps="_None yet._", code=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        bl = root / "docs/backlog"
        (bl / "features").mkdir(parents=True)
        rows = ""
        for n, (name, text) in briefs.items():
            (bl / "features" / f"{n:03d}-{name}.md").write_text(f"# Feature {n} — {name}\n\n{text}\n")
            rows += f"| {n} | `{name}` | P2 | S | Backend | ⬜ Pending | s | [brief](features/{n:03d}-{name}.md) |\n"
        (bl / "features-planned.md").write_text(
            self.HEAD + rows + f"\n## Dependencies\n\n### Hard implementation dependencies\n\n{deps}\n\n### Recommended implementation order\n\n_None yet._\n")
        (bl / "features-implemented.md").write_text("# Implemented Features\n\n## Feature List\n\n| # | Change name | Priority | Effort | Area | Details |\n| --- | --- | --- | --- | --- | --- |\n")
        for rel, text in (code or {}).items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text)
        return root

    def scan(self, root, *extra, stdin=None):
        script = KIT / "skills/feature-development/scripts/dep_scan.py"
        out = subprocess.run([sys.executable, str(script), str(root), *extra], capture_output=True, text=True, input=stdin, check=True).stdout
        return json.loads(out)["candidates"]

    BRIEFS = {
        3: ("arg-parser", "Extract argument handling into a new `args.js` exporting `parseArgs(argv)`. Add unit tests for `parseArgs`."),
        4: ("shout-flag", "Make `--shout` meaningful: `parseArgs` returns `shout: true`, and index.js prints upper case."),
    }

    def test_symbol_introduced_by_another_pending_feature_is_a_candidate(self):
        root = self.build(self.BRIEFS)
        c = self.scan(root, "--feature", "4")
        self.assertEqual([(x["dependent"], x["prerequisite"], x["kind"]) for x in c], [("4", "3", ["symbol"])])
        self.assertIn("parseArgs", c[0]["evidence"][0])

    def test_the_defining_feature_and_tests_only_mentions_are_not_dependents(self):
        root = self.build(self.BRIEFS)
        self.assertEqual(self.scan(root, "--feature", "3"), [])   # defines parseArgs; the "tests" sentence adds nothing

    def test_already_recorded_dependency_is_not_reported(self):
        root = self.build(self.BRIEFS, deps="**Feature 4 → Feature 3** (still pending)\n\nneeds parseArgs.")
        self.assertEqual(self.scan(root), [])

    def test_symbol_that_already_exists_in_the_repo_is_not_reported(self):
        root = self.build(self.BRIEFS, code={"src/args.js": "function parseArgs() {}\n"})
        self.assertEqual(self.scan(root, "--feature", "4"), [])

    def test_explicit_mention_of_another_feature_is_a_candidate(self):
        root = self.build({3: ("arg-parser", "Add `args.js`."), 5: ("lang-flag", "Needs the arg-parser feature to be in place first.")})
        c = self.scan(root, "--feature", "5")
        self.assertEqual(c[0]["kind"], ["mention"])

    def test_flags_and_short_tokens_are_ignored(self):
        root = self.build({3: ("a", "Add `--shout` and `ab`."), 4: ("b", "Uses `--shout` and `ab`.")})
        self.assertEqual(self.scan(root), [])

    def test_a_draft_not_yet_in_the_backlog_can_be_scanned_from_stdin(self):
        root = self.build({3: self.BRIEFS[3]})
        c = self.scan(root, "--new", "--name", "lang-flag", "--number", "5", stdin="Make `--lang` work: `parseArgs` reads the value.")
        self.assertEqual([(x["dependent"], x["prerequisite"]) for x in c], [("5", "3")])
