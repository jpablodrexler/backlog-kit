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

    def test_status_flags_a_file_saved_in_a_legacy_codepage_instead_of_crashing(self):
        skeleton(self.root)
        add_feature_row(self.root, self.REL, frow(1, "a", "P1"))
        planned = Path(self.root) / "docs/backlog/features-planned.md"
        planned.write_bytes(planned.read_bytes() + "\n<!-- a \u00b7 b -->\n".encode("cp1252"))
        out = run("f_status", self.root, as_json=False)
        self.assertIn("Total features", out)
        self.assertIn("docs/backlog/features-planned.md is not valid UTF-8 at line(s)", out)

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

    def test_status_flags_a_file_saved_in_a_legacy_codepage_instead_of_crashing(self):
        bug_skeleton(self.root)
        self.add_bug("BUG-001", "S1", "prod")
        opened = self.root / "docs/backlog/bugs-open.md"
        opened.write_bytes(opened.read_bytes() + "\n<!-- a \u00b7 b -->\n".encode("cp1252"))
        out = run("b_status", self.root, as_json=False)
        self.assertRegex(out, r"\| ⬜ Open\s+\| 1 \|")
        self.assertIn("docs/backlog/bugs-open.md is not valid UTF-8 at line(s)", out)

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


class BacklogReport(unittest.TestCase):
    """The velocity report: bug dates from the Fixed column, feature dates from git history."""

    IMPLEMENTED = ("# Implemented\n\n## Feature List\n\n| # | Change name | Priority | Schema Change | Effort | Area | Details |\n"
                   "| --- | --- | --- | --- | --- | --- | --- |\n")
    PLANNED = ("# Planned\n\n## Feature List\n\n| # | Change name | Priority | Schema Change | Effort | Area | SDD Artifacts | Implementation | Summary | Brief |\n"
               "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
               "| 3 | `gamma` | P2 | No | 8 | UI | — | ⬜ Pending | s | [brief](features/003-gamma.md) |\n"
               "| 4 | `delta` | P2 | No | 5 | UI | — | 🔶 In Progress | s | [brief](features/004-delta.md) |\n")
    FIXED = ("# Fixed\n\n## Bug List\n\n| Bug ID | Severity | Area | Environment | Fixed | Fix |\n| --- | --- | --- | --- | --- | --- |\n"
             "| BUG-001 | S2 | UI | web | 2026-10-21 | x |\n")

    def run_report(self, root, *extra):
        script = Path(__file__).resolve().parents[1] / "skills/backlog-report/scripts/backlog_report.py"
        out = subprocess.run([sys.executable, str(script), str(root), "--today", "2026-11-04", "--json", *extra],
                             capture_output=True, text=True, encoding="utf-8", check=True).stdout
        return json.loads(out)

    def test_dates_points_velocity_and_projection(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = root / "docs/backlog"
            b.mkdir(parents=True)
            (b / "features-planned.md").write_text(self.PLANNED, encoding="utf-8")
            (b / "bugs-fixed.md").write_text(self.FIXED, encoding="utf-8")

            def commit(day, msg):
                env = {**os.environ, "GIT_AUTHOR_DATE": f"{day}T10:00:00Z", "GIT_COMMITTER_DATE": f"{day}T10:00:00Z"}
                subprocess.run(["git", "-C", d, "add", "-A"], check=True, capture_output=True, env=env)
                subprocess.run(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "commit", "-qm", msg],
                               check=True, capture_output=True, env=env)
            subprocess.run(["git", "-C", d, "init", "-q", "-b", "main"], check=True, capture_output=True)
            (b / "features-implemented.md").write_text(self.IMPLEMENTED + "| 1 | `alpha` | P1 | No | 3 | UI | [brief](features/001-alpha.md) |\n", encoding="utf-8")
            commit("2026-10-13", "a")
            with open(b / "features-implemented.md", "a", encoding="utf-8") as fh:
                fh.write("| 2 | `beta` | P1 | No | 5 | UI | [brief](features/002-beta.md) |\n")
            commit("2026-10-28", "b")
            with open(b / "features-implemented.md", "a", encoding="utf-8") as fh:
                fh.write("| 5 | `eps` | P1 | No | 2 | UI | [brief](features/005-eps.md) |\n")   # not committed

            r = self.run_report(root, "--weeks", "4")
            self.assertEqual([w["week"] for w in r["weeks"]], ["2026-10-12", "2026-10-19", "2026-10-26", "2026-11-02"])
            self.assertEqual([w["points"] for w in r["weeks"]], [3, 0, 5, 2])
            self.assertEqual([w["bugs"] for w in r["weeks"]], [0, 1, 0, 0])
            self.assertEqual((r["features_delivered"], r["points_delivered"], r["bugs_fixed"]), (3, 10, 1))
            self.assertEqual(r["bugs_by_severity"], {"S2": 1})
            self.assertEqual(r["velocity"], {"points_per_week": 2.7, "over_weeks": 3, "weekly_points": [3, 0, 5],     # (3 + 0 + 5) / 3
                                             "weeks_with_deliveries": 2, "last_delivery": "2026-11-04"})
            self.assertEqual(r["bugs_per_week"], 0.3)                                                               # one bug in three weeks
            self.assertEqual(r["pending"], {"features": 2, "points": 13, "unestimated": 0, "weeks_at_that_pace": 4.8})
            self.assertEqual([w["code"] for w in r["warnings"]], ["uncommitted"])
            self.assertTrue(any(i["id"] == "#5" and i["uncommitted"] for i in r["delivered"]))
            # a period that starts after the first commits leaves them out
            self.assertEqual(self.run_report(root, "--since", "2026-10-26")["features_delivered"], 2)

    def test_missing_files_are_reported_not_guessed(self):
        with tempfile.TemporaryDirectory() as d:
            r = self.run_report(d)
            self.assertEqual(r["available"], {"features": False, "pending": False, "bugs": False})
            self.assertIsNone(r["velocity"]["points_per_week"])
            self.assertEqual(r["features_delivered"], 0)
            self.assertEqual(r["warnings"], [])

    def committed_backlog(self, d, rows, day="2026-07-21"):
        """A repo whose implemented table was committed in one go on `day`."""
        import os
        b = Path(d) / "docs/backlog"
        b.mkdir(parents=True)
        (b / "features-planned.md").write_text(self.PLANNED, encoding="utf-8")
        (b / "bugs-fixed.md").write_text(self.FIXED, encoding="utf-8")
        (b / "features-implemented.md").write_text(self.IMPLEMENTED + rows, encoding="utf-8")
        env = {**os.environ, "GIT_AUTHOR_DATE": f"{day}T10:00:00Z", "GIT_COMMITTER_DATE": f"{day}T10:00:00Z"}
        git = lambda *a: subprocess.run(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *a],
                                        check=True, capture_output=True, env=env)
        git("init", "-q", "-b", "main"); git("add", "-A"); git("commit", "-qm", "load the backlog")

    BULK_ROWS = "".join(f"| {n} | `f{n}` | P1 | No | {e} | UI | [brief](features/{n:03d}-f{n}.md) |\n"
                        for n, e in ((1, "—"), (2, "—"), (3, "—"), (4, "—"), (5, "3"), (6, "5")))

    def test_a_bulk_load_and_missing_points_are_flagged_and_there_is_no_fake_zero(self):
        with tempfile.TemporaryDirectory() as d:
            self.committed_backlog(d, self.BULK_ROWS)
            r = self.run_report(d, "--since", "2026-07-20")
            codes = [w["code"] for w in r["warnings"]]
            self.assertIn("bulk_date", codes)                       # 6 of 6 features carry the same date
            self.assertIn("unestimated", codes)                     # 4 of 6 have no points
            self.assertNotIn("pending_unestimated", codes)          # both pending features have points
            self.assertEqual(r["points_delivered"], 8)
            v = r["velocity"]
            self.assertIsNone(v["points_per_week"])                 # nothing was archived in the last four complete weeks
            self.assertEqual((v["weeks_with_deliveries"], v["last_delivery"]), (0, "2026-07-21"))

    def test_the_text_report_says_when_nothing_was_archived_recently(self):
        with tempfile.TemporaryDirectory() as d:
            self.committed_backlog(d, self.BULK_ROWS)
            script = Path(__file__).resolve().parents[1] / "skills/backlog-report/scripts/backlog_report.py"
            out = subprocess.run([sys.executable, str(script), d, "--today", "2026-11-04", "--since", "2026-07-20"],
                                 capture_output=True, text=True, encoding="utf-8", check=True).stdout
            self.assertIn("no feature was archived in the last 4 complete week(s); the last one was on 2026-07-21", out)
            self.assertNotIn("0.0 points/week", out)
            self.assertIn("### Reliability", out)
            self.assertIn("4 of 6 delivered features have no story points", out)

    def test_a_shallow_clone_is_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            src, dst = Path(d) / "src", Path(d) / "dst"
            src.mkdir()
            self.committed_backlog(str(src), self.BULK_ROWS)
            (src / "extra.txt").write_text("x", encoding="utf-8")
            subprocess.run(["git", "-C", str(src), "add", "-A"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(src), "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "commit", "-qm", "more"],
                           check=True, capture_output=True)
            subprocess.run(["git", "clone", "-q", "--depth", "1", src.as_uri(), str(dst)], check=True, capture_output=True)
            self.assertIn("shallow_clone", [w["code"] for w in self.run_report(dst, "--since", "2026-07-20")["warnings"]])
            self.assertNotIn("shallow_clone", [w["code"] for w in self.run_report(src, "--since", "2026-07-20")["warnings"]])


class BugsTriage(unittest.TestCase):
    OPEN = ("# Open Bugs\n\n## Bug List\n\n| Bug ID | Severity | Area | Environment | Status | Fix | Summary |\n| --- | --- | --- | --- | --- | --- | --- |\n"
            "| [BUG-010](bugs/BUG-010.md) | S2 | /settings | deployed | ⬜ Open | | Saving settings shows a blank page after submit. |\n"
            "| [BUG-011](bugs/BUG-011.md) | S2 | /settings | deployed | ⬜ Open | | Settings page is blank after saving the form. |\n"
            "| [BUG-012](bugs/BUG-012.md) | S3 | nav | local | ⬜ Open | | Broken. |\n"
            "| [BUG-013](bugs/BUG-013.md) | S3 | import | local | ⬜ Open | | Import creates duplicate rows again for every file. |\n\n"
            "## Recommended fix order\n\n- BUG-010 — x\n- BUG-011 — y\n- BUG-012 — z\n")
    FIXED = ("# Fixed Bugs\n\n## Bug List\n\n| Bug ID | Severity | Area | Environment | Fixed | Fix | Summary |\n| --- | --- | --- | --- | --- | --- | --- |\n"
             "| [BUG-001](bugs/BUG-001.md) | S2 | import | deployed | 2026-10-01 | abc | Import creates duplicate rows for every file. |\n")

    def brief(self, n, repro="1. Open it.", expected="It saves.", actual="Blank page."):
        return f"# BUG-{n} — t\n\n- **Steps to reproduce:**\n  {repro}\n- **Expected:** {expected}\n- **Actual:** {actual}\n- **Environment:** local\n"

    def test_findings(self):
        with tempfile.TemporaryDirectory() as d:
            b = Path(d) / "docs/backlog"
            (b / "bugs").mkdir(parents=True)
            (b / "bugs-open.md").write_text(self.OPEN, encoding="utf-8")
            (b / "bugs-fixed.md").write_text(self.FIXED, encoding="utf-8")
            (b / "bugs/BUG-010.md").write_text(self.brief("010"), encoding="utf-8")
            (b / "bugs/BUG-011.md").write_text(self.brief("011"), encoding="utf-8")
            (b / "bugs/BUG-012.md").write_text(self.brief("012", repro="<unknown — needs repro>", actual=""), encoding="utf-8")
            (b / "bugs/BUG-013.md").write_text(self.brief("013"), encoding="utf-8")
            script = Path(__file__).resolve().parents[1] / "skills/bugs-triage/scripts/triage.py"
            out = subprocess.run([sys.executable, str(script), d, "--json"], capture_output=True, text=True, encoding="utf-8", check=True).stdout
            f = json.loads(out)["findings"]
            self.assertEqual(f["missing_repro"], ["BUG-012"])
            self.assertEqual(f["missing_expected"], ["BUG-012"])
            self.assertEqual(f["vague_summary"], ["BUG-012"])
            self.assertEqual([x["bugs"] for x in f["duplicates"]], [["BUG-010", "BUG-011"]])
            self.assertEqual([(x["bug"], x["looks_like_fixed"]) for x in f["regressions"]], [("BUG-013", "BUG-001")])
            self.assertEqual(f["not_in_fix_order"], ["BUG-013"])

    def test_missing_backlog_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            script = Path(__file__).resolve().parents[1] / "skills/bugs-triage/scripts/triage.py"
            out = subprocess.run([sys.executable, str(script), d], capture_output=True, text=True, encoding="utf-8", check=True).stdout
            self.assertIn("nothing to triage", out)


class BacklogImport(unittest.TestCase):
    ISSUES = [
        {"number": 21, "title": "Export the task list as CSV", "body": "Users want CSV.", "url": "https://github.com/o/r/issues/21", "state": "open",
         "labels": [{"name": "enhancement"}, {"name": "priority: high"}, {"name": "points: 5"}, {"name": "area: backend"}]},
        {"number": 22, "title": "Login loops after password reset", "body": "Steps", "url": "https://github.com/o/r/issues/22", "state": "open",
         "labels": [{"name": "bug"}, {"name": "priority/critical"}]},
        {"number": 23, "title": "A pull request", "url": "https://github.com/o/r/pull/23", "state": "open", "pull_request": {}, "labels": []},
        {"number": 24, "title": "Closed one", "url": "https://github.com/o/r/issues/24", "state": "closed", "labels": []},
        {"number": 2, "title": "Dark mode", "url": "https://github.com/o/r/issues/2", "state": "open", "labels": []},
        {"iid": 5, "title": "Gitlab shaped bug", "description": "d", "web_url": "https://gitlab.com/o/r/-/issues/5", "state": "opened", "labels": ["defect", "severity::major"]},
    ]

    def plan(self, root, issues, *extra):
        script = Path(__file__).resolve().parents[1] / "skills/backlog-import/scripts/plan_import.py"
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "issues.json"
            f.write_text(json.dumps(issues), encoding="utf-8")
            out = subprocess.run([sys.executable, str(script), str(root), str(f), "--json", *extra], capture_output=True, text=True, encoding="utf-8", check=True).stdout
        return json.loads(out)

    def test_classification_labels_and_skips(self):
        with tempfile.TemporaryDirectory() as d:
            b = Path(d) / "docs/backlog/features"
            b.mkdir(parents=True)
            (b / "002-dark-mode.md").write_text("# Feature 2 — dark-mode\n\nImported from https://github.com/o/r/issues/2\n", encoding="utf-8")
            r = self.plan(d, self.ISSUES)
            by = {i["number"]: i for i in r["importable"]}
            self.assertEqual(sorted(by), [5, 21, 22])
            self.assertEqual((by[21]["kind"], by[21]["priority"], by[21]["points"], by[21]["area"]), ("feature", "P1", "5", "backend"))
            self.assertEqual((by[22]["kind"], by[22]["severity"]), ("bug", "S1"))          # no severity label: taken from the priority
            self.assertEqual((by[5]["kind"], by[5]["severity"]), ("bug", "S2"))            # GitLab shape, severity::major
            self.assertEqual(by[21]["suggested_name"], "export-task-list-csv")
            reasons = {s["number"]: s["reason"] for s in r["skipped"]}
            self.assertEqual(reasons[23], "pull request")
            self.assertEqual(reasons[24], "closed")
            self.assertEqual(reasons[2], "already imported as 002-dark-mode")
            self.assertNotIn(2, by)

    def test_an_issue_url_does_not_match_a_longer_number(self):
        with tempfile.TemporaryDirectory() as d:
            b = Path(d) / "docs/backlog/bugs"
            b.mkdir(parents=True)
            (b / "BUG-001.md").write_text("Imported from https://github.com/o/r/issues/210\n", encoding="utf-8")
            r = self.plan(d, [{"number": 21, "title": "Short one", "url": "https://github.com/o/r/issues/21", "state": "open", "labels": []}])
            self.assertEqual([i["number"] for i in r["importable"]], [21])

    def test_limit_reports_what_is_left(self):
        with tempfile.TemporaryDirectory() as d:
            issues = [{"number": n, "title": f"Thing {n}", "url": f"https://github.com/o/r/issues/{n}", "state": "open", "labels": []} for n in range(1, 6)]
            r = self.plan(d, issues, "--limit", "2")
            self.assertEqual(([i["number"] for i in r["importable"]], r["not_shown"]), ([1, 2], 3))


class FeaturesTriage(unittest.TestCase):
    PLANNED = ("# Planned\n\n## Feature List\n\n| # | Change name | Priority | Schema Change | Effort | Area | SDD Artifacts | Implementation | Summary | Brief |\n"
               "| - | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
               "| 2 | `alpha` | P1 | No | | UI | — | ⬜ Pending | Export the task list as a CSV file. | [brief](features/002-alpha.md) |\n"
               "| 3 | `beta` | P1 | No | 13 | UI | — | ⬜ Pending | Export the task list as CSV file download. | [brief](features/003-beta.md) |\n"
               "| 4 | `gamma` | P2 | No | M | API | — | ⬜ Pending | Rate limit the API per key. | [brief](features/004-gamma.md) |\n"
               "| 5 | `delta` | P2 | No | 3 | API | — | 🔶 In Progress | Webhook retries. | [brief](features/005-delta.md) |\n"
               "| 6 | `eps` | P2 | No | 2 | API | — | ⬜ Pending | Audit log. | [brief](features/006-eps.md) |\n\n"
               "## Dependencies\n\n### Hard implementation dependencies\n\n**Feature 6 → Feature 1** (hard)\n\n**Feature 4 → Feature 99** (hard)\n\n"
               "### Recommended implementation order\n\n- `alpha` (#2)\n- `beta` (#3)\n")
    IMPLEMENTED = ("# Implemented\n\n## Feature List\n\n| # | Change name | Priority | Schema Change | Effort | Area | Details |\n| - | --- | --- | --- | --- | --- | --- |\n"
                   "| 1 | `base` | P1 | No | 3 | API | [brief](features/001-base.md) |\n")
    STORY = "# Feature {n} — x\n\n**As a** dev, **I want** x, **so that** y.\n\n## Acceptance Criteria\n\n- AC1: Given a, when b, then c.\n"

    def test_findings(self):
        with tempfile.TemporaryDirectory() as d:
            b = Path(d) / "docs/backlog"
            (b / "features").mkdir(parents=True)
            (b / "features-planned.md").write_text(self.PLANNED, encoding="utf-8")
            (b / "features-implemented.md").write_text(self.IMPLEMENTED, encoding="utf-8")
            for n, slug in ((2, "alpha"), (3, "beta"), (4, "gamma"), (5, "delta"), (6, "eps")):
                body = self.STORY.format(n=n)
                if n == 4:
                    body = "# Feature 4 — gamma\n\nJust do the thing.\n"      # no story, no acceptance criteria
                (b / "features" / f"{n:03d}-{slug}.md").write_text(body, encoding="utf-8")
            script = Path(__file__).resolve().parents[1] / "skills/features-triage/scripts/triage.py"
            out = subprocess.run([sys.executable, str(script), d, "--json"], capture_output=True, text=True, encoding="utf-8", check=True).stdout
            r = json.loads(out)
            f = r["findings"]
            nums = lambda key: [x["number"] for x in f[key]]
            self.assertFalse(r["branches_checked"])                                   # not a git repository
            self.assertEqual(nums("unestimated"), ["2"])
            self.assertEqual(nums("legacy_size"), ["4"])
            self.assertEqual(nums("oversized"), ["3"])
            self.assertEqual(nums("missing_story"), ["4"])
            self.assertEqual(nums("missing_acceptance"), ["4"])
            self.assertEqual([(x["number"], x["prerequisite"]) for x in f["now_unblocked"]], [("6", "1")])
            self.assertEqual([(x["number"], x["prerequisite"]) for x in f["dangling_dependency"]], [("4", "99")])
            self.assertEqual([x["features"] for x in f["duplicates"]], [["2", "3"]])
            self.assertEqual(nums("not_in_order"), ["4", "6"])
            self.assertEqual(f["stale_in_progress"], [])

    def test_stale_in_progress_needs_a_branch(self):
        with tempfile.TemporaryDirectory() as d:
            b = Path(d) / "docs/backlog"
            (b / "features").mkdir(parents=True)
            (b / "features-planned.md").write_text(self.PLANNED, encoding="utf-8")
            (b / "features-implemented.md").write_text(self.IMPLEMENTED, encoding="utf-8")
            git = lambda *a: subprocess.run(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *a], check=True, capture_output=True)
            git("init", "-q", "-b", "main"); git("add", "-A"); git("commit", "-qm", "x")
            script = Path(__file__).resolve().parents[1] / "skills/features-triage/scripts/triage.py"
            run = lambda: json.loads(subprocess.run([sys.executable, str(script), d, "--json"], capture_output=True, text=True, encoding="utf-8", check=True).stdout)
            self.assertEqual([x["name"] for x in run()["findings"]["stale_in_progress"]], ["delta"])
            git("branch", "feature/delta")
            self.assertEqual(run()["findings"]["stale_in_progress"], [])


if __name__ == "__main__":
    unittest.main()
