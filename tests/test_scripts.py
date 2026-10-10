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

    def test_priority_scoring_is_the_fixed_scale_of_the_source_projects(self):
        run("f_scaffold", self.root)
        rel = "docs/backlog/features-planned.md"
        add_feature_row(self.root, rel, "| 1 | `a` | P2 | S | X | ⬜ Pending | a | [brief](features/001-a.md) |")
        add_feature_row(self.root, rel, "| 2 | `b` | P0 | L | X | ⬜ Pending | b | [brief](features/002-b.md) |")
        add_feature_row(self.root, rel, "| 3 | `c` | none | L | X | ⬜ Pending | c | [brief](features/003-c.md) |")
        out = run("f_rank", self.root, "--json")
        self.assertEqual(out["top"]["name"], "b")
        self.assertEqual(out["top"]["score"], 400)                                    # P0
        self.assertEqual([(r["name"], r["score"]) for r in out["runners_up"]], [("a", 200), ("c", 50)])

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
        # bugs-next resolves a typed id with --select; a closed / won't-fix / unknown id must not resolve.
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

    def test_status_flags_the_stale_notes_before_cleanup(self):
        out = run("f_status", self.root, "--json")
        notes = out["stale_order_notes"]
        self.assertEqual(len(notes), 3)
        self.assertTrue(all("blocked" in n["note"] for n in notes))

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
        self.assertEqual(run("f_status", self.root, "--json")["stale_order_notes"], [])


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


class SpecWorkflowHeaderMismatch(unittest.TestCase):
    """Found reviewing a real test repo: openspec configured, planned table created without `SDD Artifacts`."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        bl = self.root / "docs/backlog"
        (bl / "features").mkdir(parents=True)
        (self.root / ".backlog-kit.toml").write_text('[spec]\nworkflow = "openspec"\n')
        (bl / "features-planned.md").write_text(
            "# Planned Features\n\n## Feature List\n\n"
            "| # | Change name | Priority | Effort | Area | Implementation | Summary | Brief |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            "| 5 | `old-one` | P3 | S | Backend | ⬜ Pending | does a thing | [brief](features/005-old-one.md) |\n\n"
            "## Dependencies\n")
        (bl / "features/005-old-one.md").write_text("# Feature 5 — old-one\n\nx\n")
        (bl / "features-implemented.md").write_text(
            "# Implemented Features\n\n## Feature List\n\n| # | Change name | Priority | Effort | Area | Details |\n| --- | --- | --- | --- | --- | --- |\n"
            "| 1 | `done` | P3 | S | Backend | [brief](features/001-done.md) |\n")
        (bl / "features/001-done.md").write_text("# Feature 1 — done\n\nx\n")
        self.scaffold = KIT / "skills/feature-plan/scripts/scaffold.py"

    def tearDown(self):
        self.tmp.cleanup()

    def scaf(self, *extra):
        return json.loads(subprocess.run([sys.executable, str(self.scaffold), str(self.root), *extra],
                                         capture_output=True, text=True, check=True).stdout)

    def test_scaffold_reports_the_mismatch_without_touching_the_file(self):
        before = (self.root / "docs/backlog/features-planned.md").read_text()
        out = self.scaf()
        self.assertEqual(out["planned_header_mismatch"]["found"].count("SDD Artifacts"), 0)
        self.assertIn("SDD Artifacts", out["planned_header_mismatch"]["expected"])
        self.assertEqual((self.root / "docs/backlog/features-planned.md").read_text(), before)

    def test_status_names_the_mismatch_and_the_missing_spec_links(self):
        text = run("f_status", self.root, as_json=False)
        self.assertIn("does not match `spec.workflow`", text)
        self.assertIn("--fix-header", text)
        self.assertIn("#1 done", text)                      # implemented without a [spec] link
        self.assertIn("openspec", text)                     # no openspec/ folder

    def test_fix_header_is_lossless_and_idempotent(self):
        out = self.scaf("--fix-header")
        self.assertEqual(out["header_fixed"]["rows"], 1)
        text = (self.root / "docs/backlog/features-planned.md").read_text()
        self.assertIn("| # | Change name | Priority | Effort | Area | SDD Artifacts | Implementation | Summary | Brief |", text)
        self.assertIn("| 5 | `old-one` | P3 | S | Backend | ⬜ Pending | ⬜ Pending | does a thing | [brief](features/005-old-one.md) |", text)
        self.assertNotIn("planned_header_mismatch", self.scaf())
        self.assertEqual(run("f_status", self.root, "--json")["header_mismatch"], None)
        ranked = run("f_rank", self.root, "--json")
        self.assertEqual(ranked["top"]["brief_file"], "docs/backlog/features/005-old-one.md")

    def test_fix_header_also_drops_the_column_when_workflow_is_none(self):
        (self.root / ".backlog-kit.toml").write_text('[spec]\nworkflow = "none"\n')
        self.scaf("--fix-header")                            # nothing to do: header has no SDD column and none wanted
        (self.root / ".backlog-kit.toml").write_text('[spec]\nworkflow = "openspec"\n')
        self.scaf("--fix-header")
        (self.root / ".backlog-kit.toml").write_text('[spec]\nworkflow = "none"\n')
        self.assertIn("planned_header_mismatch", self.scaf())
        self.scaf("--fix-header")
        text = (self.root / "docs/backlog/features-planned.md").read_text()
        self.assertNotIn("SDD Artifacts", text)
        self.assertIn("| 5 | `old-one` | P3 | S | Backend | ⬜ Pending | does a thing | [brief](features/005-old-one.md) |", text)


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

    def test_status_lists_candidates_as_information(self):
        root = self.build(self.BRIEFS)
        text = run("f_status", root, as_json=False)
        self.assertIn("Possible unrecorded dependency: #4 `shout-flag` → #3 `arg-parser`", text)
