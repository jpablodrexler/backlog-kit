"""Tests for the batch skills' helpers: batch_plan (resolve + order) and batch_report (resumable report)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "lib"


def run(script, *args, env=None, check=True):
    proc = subprocess.run([sys.executable, str(LIB / script), *map(str, args)], capture_output=True, text=True,
                          env={**os.environ, **(env or {})})
    if check:
        assert proc.returncode == 0, proc.stderr + proc.stdout
    return json.loads(proc.stdout)


BUGS_OPEN = """# Open Bugs

## Bug List

| Bug ID | Severity | Area | Environment | Status | Fix | Summary |
| ------ | -------- | ---- | ----------- | ------ | --- | ------- |
| [BUG-001](bugs/BUG-001.md) | S3 | a | local | ⬜ Open | | minor one |
| [BUG-002](bugs/BUG-002.md) | S1 | b | prod | ⬜ Open | | blocker |
| [BUG-003](bugs/BUG-003.md) | S2 | c | local | 🔶 In Progress | | major in progress |
| [BUG-004](bugs/BUG-004.md) | S2 | d | local | 🚫 Won't fix | | nope |
| [BUG-005](bugs/BUG-005.md) | S2 | e | local | ❓ Cannot reproduce | | cannot |

## Recommended fix order

_No open bugs to order._
"""
BUGS_FIXED = """# Fixed Bugs

## Bug List

| Bug ID | Severity | Area | Environment | Fixed | Fix | Summary |
| ------ | -------- | ---- | ----------- | ----- | --- | ------- |
| [BUG-009](bugs/BUG-009.md) | S2 | z | local | 2026-01-01 | | old |
"""
FEATURES_PLANNED = """# Planned Features

## Feature List

| # | Change name | Priority | Effort | Area | Implementation | Summary | Brief |
| - | ----------- | -------- | ------ | ---- | -------------- | ------- | ----- |
| 1 | `alpha` | P2 | M | X | ⬜ Pending | a | [brief](features/001-alpha.md) |
| 2 | `beta` | P1 | S | X | ⬜ Pending | b | [brief](features/002-beta.md) |
| 3 | `gamma` | P3 | L | X | 🔶 In Progress | c | [brief](features/003-gamma.md) |

## Dependencies

### Hard implementation dependencies

%s

### Recommended implementation order

%s
"""
FEATURES_IMPL = """# Implemented Features

## Feature List

| # | Change name | Priority | Effort | Area | Details |
| - | ----------- | -------- | ------ | ---- | ------- |
| 7 | `done-one` | P1 | S | X | [brief](features/007-done-one.md) |
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs/backlog").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        (self.root / "docs/backlog" / rel).write_text(text)

    def bugs(self):
        self.write("bugs-open.md", BUGS_OPEN)
        self.write("bugs-fixed.md", BUGS_FIXED)

    def features(self, deps="_None yet._", order="_None yet._"):
        self.write("features-planned.md", FEATURES_PLANNED % (deps, order))
        (self.root / "docs/backlog/features").mkdir(exist_ok=True)
        for n, name in ((1, "alpha"), (2, "beta"), (3, "gamma")):
            (self.root / "docs/backlog/features" / f"{n:03d}-{name}.md").write_text(f"# Feature {n} — {name}\n\nx\n")
        self.write("features-implemented.md", FEATURES_IMPL)


class PlanBugs(Base):
    def plan(self, *args):
        return run("batch_plan.py", self.root, "--kind", "bugs", *args)

    def test_all_orders_by_severity_when_no_fix_order(self):
        self.bugs()
        out = self.plan("--all")
        # BUG-003 is already in progress, so it leads; then severity (S1 before S3)
        self.assertEqual([i["id"] for i in out["items"]], ["BUG-003", "BUG-002", "BUG-001"])
        self.assertEqual(out["order_basis"], "severity")

    def test_all_order_list_only_breaks_ties_within_a_severity(self):
        self.bugs()
        p = self.root / "docs/backlog/bugs-open.md"
        p.write_text(p.read_text().replace("| [BUG-001](bugs/BUG-001.md) | S3 |", "| [BUG-006](bugs/BUG-006.md) | S3 | a | local | ⬜ Open | | another minor |\n| [BUG-001](bugs/BUG-001.md) | S3 |")
                     .replace("_No open bugs to order._", "- BUG-001 — first\n- BUG-006 — second"))
        out = self.plan("--all")
        self.assertEqual([i["id"] for i in out["items"]], ["BUG-003", "BUG-002", "BUG-001", "BUG-006"])

    def test_all_ignores_a_stale_order_list_that_contradicts_severity(self):
        self.bugs()
        p = self.root / "docs/backlog/bugs-open.md"
        p.write_text(p.read_text().replace("_No open bugs to order._", "- BUG-001 — first\n- BUG-002 — second"))
        out = self.plan("--all")
        self.assertEqual([i["id"] for i in out["items"]], ["BUG-003", "BUG-002", "BUG-001"])
        self.assertTrue(any("disagrees with the run order" in w for w in out["warnings"]))
        self.assertTrue(any("BUG-003" in w and "Not in the" in w for w in out["warnings"]))

    def test_named_normalizes_and_flags_problems(self):
        self.bugs()
        out = self.plan("--ids", "bug-1, 2, BUG-009, BUG-004, BUG-005, BUG-099, BUG-001")
        self.assertEqual([i["id"] for i in out["items"]], ["BUG-001", "BUG-002"])
        kinds = {p["input"]: p["kind"] for p in out["problems"]}
        self.assertEqual(kinds["BUG-009"], "already-closed")
        self.assertEqual(kinds["BUG-004"], "wont-fix")
        self.assertEqual(kinds["BUG-005"], "cannot-repro")
        self.assertEqual(kinds["BUG-099"], "unresolved")
        self.assertEqual(kinds["BUG-001"], "duplicate")

    def test_empty_backlog_is_not_an_error(self):
        self.write("bugs-open.md", BUGS_OPEN.split("| [BUG-001]")[0] + "\n## Recommended fix order\n\n_No open bugs to order._\n")
        self.write("bugs-fixed.md", BUGS_FIXED)
        out = self.plan("--all")
        self.assertTrue(out["empty"])


class PlanFeatures(Base):
    def plan(self, *args):
        return run("batch_plan.py", self.root, "--kind", "features", *args)

    def test_all_ranks_in_progress_then_priority(self):
        self.features()
        out = self.plan("--all")
        # gamma is in progress (P3), beta is P1, alpha is P2
        self.assertEqual([i["id"] for i in out["items"]], ["gamma", "beta", "alpha"])
        self.assertEqual(out["order_basis"], "priority")
        self.assertEqual(out["warnings"], [])

    def test_all_table_order_breaks_ties(self):
        self.features()
        p = self.root / "docs/backlog/features-planned.md"
        p.write_text(p.read_text().replace("| P1 |", "| P2 |").replace("🔶 In Progress", "⬜ Pending"))
        out = self.plan("--all")
        self.assertEqual([i["id"] for i in out["items"]], ["alpha", "beta", "gamma"])

    def test_all_puts_prerequisite_before_a_higher_priority_dependent(self):
        # beta (P1) needs gamma (P3, in progress anyway); alpha (P2) is unrelated
        self.features(deps="**Feature 2 → Feature 3** (still pending)\n\n`beta` needs `gamma`.")
        p = self.root / "docs/backlog/features-planned.md"
        p.write_text(p.read_text().replace("🔶 In Progress", "⬜ Pending"))
        out = self.plan("--all")
        ids = [i["id"] for i in out["items"]]
        self.assertEqual(ids, ["alpha", "gamma", "beta"])   # alpha (P2) outranks the P3 prerequisite; gamma then precedes beta
        self.assertEqual(out["warnings"], [])

    def test_all_stale_order_list_does_not_reorder_tiers(self):
        self.features(deps="**Feature 2 → Feature 3** (still pending)\n\nx",
                      order="- `beta` (#2) — first\n- `gamma` (#3) — second\n- `alpha` (#1) — third")
        out = self.plan("--all")
        self.assertEqual([i["id"] for i in out["items"]], ["gamma", "beta", "alpha"])
        self.assertTrue(any("disagrees with the run order" in w for w in out["warnings"]))

    def test_all_order_list_breaks_ties_within_a_tier(self):
        self.features(order="- `gamma` (#3) — x\n- `alpha` (#1) — y\n- `beta` (#2) — z")
        p = self.root / "docs/backlog/features-planned.md"
        p.write_text(p.read_text().replace("| P1 |", "| P2 |").replace("| P3 |", "| P2 |").replace("🔶 In Progress", "⬜ Pending"))
        out = self.plan("--all")
        self.assertEqual([i["id"] for i in out["items"]], ["gamma", "alpha", "beta"])
        self.assertEqual(out["warnings"], [])

    def test_named_by_number_and_name_with_problems(self):
        self.features()
        out = self.plan("--ids", "#2, alpha, 7, nope, beta")
        self.assertEqual([i["id"] for i in out["items"]], ["beta", "alpha"])
        kinds = {p["input"]: p["kind"] for p in out["problems"]}
        self.assertEqual(kinds["7"], "already-implemented")
        self.assertEqual(kinds["nope"], "unresolved")
        self.assertEqual(kinds["beta"], "duplicate")

    def test_named_warns_when_prerequisite_not_in_run(self):
        self.features(deps="**Feature 1 → Feature 2** (still pending)\n\nx")
        out = self.plan("--ids", "alpha")
        self.assertTrue(any("not in this run" in w for w in out["warnings"]))

    def test_dependency_cycle_is_reported_not_fatal(self):
        self.features(deps="**Feature 1 → Feature 2** (still pending)\n\nx\n\n**Feature 2 → Feature 1** (still pending)\n\ny")
        out = self.plan("--all")
        self.assertEqual(len(out["items"]), 3)
        self.assertTrue(any("cycle" in w for w in out["warnings"]))


class Report(Base):
    ENV = {"BACKLOG_KIT_NOW": "2026-10-06 14:02"}

    def init(self, items="BUG-001,BUG-002,BUG-003", kind="bugs", env=None):
        return run("batch_report.py", "init", self.root, "--kind", kind, "--branch", "fix/bug-batch-2026-10-06",
                   "--items", items, env=env or self.ENV)["path"]

    def test_init_set_finish_roundtrip(self):
        path = self.init()
        self.assertTrue(path.endswith("docs/reports/bug-batch/BUG_BATCH_REPORT_2026-10-06.md"))
        shown = run("batch_report.py", "show", path)
        self.assertEqual([i["status"] for i in shown["items"]], ["not-started"] * 3)
        self.assertEqual(shown["branch"], "fix/bug-batch-2026-10-06")

        run("batch_report.py", "set", path, "--id", "BUG-001", "--status", "in-progress")
        self.assertIn("🔄 In progress", Path(path).read_text())
        run("batch_report.py", "set", path, "--id", "BUG-001", "--status", "closed", "--summary", "Root cause X; changed Y.",
            env={"BACKLOG_KIT_NOW": "2026-10-06 14:31"})
        text = Path(path).read_text()
        self.assertIn("- [x] **BUG-001** — ✅ Closed 14:31 — Root cause X; changed Y.", text)
        run("batch_report.py", "set", path, "--id", "BUG-002", "--status", "blocked", "--summary", "needs a human")
        run("batch_report.py", "set", path, "--id", "BUG-003", "--status", "cannot-reproduce")

        summary = run("batch_report.py", "finish", path)
        self.assertEqual((summary["done"], summary["cannot_reproduce"], summary["blocked_or_skipped"], summary["not_reached"]), (1, 1, 1, 0))
        self.assertIn("**Closed:** 1/3", Path(path).read_text())
        run("batch_report.py", "finish", path)  # idempotent: footer refreshed, not duplicated
        self.assertEqual(Path(path).read_text().count("## Run Summary"), 1)

    def test_set_unknown_id_fails_without_touching_file(self):
        path = self.init()
        before = Path(path).read_text()
        proc = subprocess.run([sys.executable, str(LIB / "batch_report.py"), "set", path, "--id", "BUG-099", "--status", "closed"],
                              capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(Path(path).read_text(), before)

    def test_same_day_second_run_gets_suffix(self):
        a = self.init()
        b = self.init()
        self.assertTrue(b.endswith("BUG_BATCH_REPORT_2026-10-06-2.md"))
        self.assertNotEqual(a, b)

    def test_feature_report_uses_completed_and_its_own_dir(self):
        path = self.init("alpha,beta", kind="features")
        self.assertIn("feature-batch/FEATURE_BATCH_REPORT_", path)
        run("batch_report.py", "set", path, "--id", "alpha", "--status", "completed", "--summary", "Done.")
        self.assertIn("✅ Completed", Path(path).read_text())
        self.assertEqual(run("batch_report.py", "finish", path)["done"], 1)

    def test_find_resume_classes(self):
        path = self.init("BUG-001,BUG-002,BUG-003,BUG-004,BUG-005")
        run("batch_report.py", "set", path, "--id", "BUG-001", "--status", "closed", "--summary", "s")
        find = lambda items: run("batch_report.py", "find", self.root, "--kind", "bugs", "--items", items)

        exact = find("BUG-001,BUG-002,BUG-003,BUG-004,BUG-005")
        self.assertEqual(exact["match"], "exact")
        self.assertEqual(exact["branch"], "fix/bug-batch-2026-10-06")
        self.assertEqual(exact["done"], ["BUG-001"])
        self.assertEqual(exact["remaining"], ["BUG-002", "BUG-003", "BUG-004", "BUG-005"])

        self.assertEqual(find("BUG-001,BUG-002,BUG-003,BUG-004,BUG-005,BUG-006")["match"], "near")   # 5/6 = 0.83
        self.assertEqual(find("BUG-001,BUG-002,BUG-009")["match"], "partial")
        self.assertEqual(find("BUG-040,BUG-041")["match"], "none")

    def test_finished_report_is_not_resumable(self):
        path = self.init("BUG-001")
        run("batch_report.py", "set", path, "--id", "BUG-001", "--status", "closed", "--summary", "s")
        out = run("batch_report.py", "find", self.root, "--kind", "bugs", "--items", "BUG-001")
        self.assertEqual(out["match"], "none")

    def test_blocked_item_keeps_a_report_resumable(self):
        # Found in dogfood run 2: a feature refused for an unshipped prerequisite must be retried on resume.
        path = self.init("BUG-001,BUG-002")
        run("batch_report.py", "set", path, "--id", "BUG-002", "--status", "closed", "--summary", "s")
        run("batch_report.py", "set", path, "--id", "BUG-001", "--status", "blocked", "--summary", "x")
        out = run("batch_report.py", "find", self.root, "--kind", "bugs", "--items", "BUG-001,BUG-002")
        self.assertEqual(out["match"], "exact")
        self.assertEqual(out["remaining"], ["BUG-001"])
        self.assertEqual(out["done"], ["BUG-002"])

    def test_interrupted_in_progress_item_is_resumable(self):
        path = self.init("BUG-001,BUG-002")
        run("batch_report.py", "set", path, "--id", "BUG-001", "--status", "in-progress")
        out = run("batch_report.py", "find", self.root, "--kind", "bugs", "--items", "BUG-001,BUG-002")
        self.assertEqual(out["match"], "exact")
        self.assertEqual(out["remaining"], ["BUG-001", "BUG-002"])


if __name__ == "__main__":
    unittest.main()


class PlanFeaturesBriefAndNumberedOrder(Base):
    def plan(self, *args):
        return run("batch_plan.py", self.root, "--kind", "features", *args)

    def test_a_missing_brief_is_reported_before_the_run_starts(self):
        self.features()
        (self.root / "docs/backlog/features/002-beta.md").unlink()
        out = self.plan("--all")
        self.assertEqual([(p["kind"], p["input"]) for p in out["problems"]], [("missing-brief", "beta")])

    def test_numbered_order_lists_are_read_like_bulleted_ones(self):
        self.features(order="1. `gamma` (#3) — x\n2. `alpha` (#1) — y\n3. `beta` (#2) — z")
        p = self.root / "docs/backlog/features-planned.md"
        p.write_text(p.read_text().replace("| P1 |", "| P2 |").replace("| P3 |", "| P2 |").replace("🔶 In Progress", "⬜ Pending"))
        out = self.plan("--all")
        self.assertEqual([i["id"] for i in out["items"]], ["gamma", "alpha", "beta"])
        self.assertEqual(out["warnings"], [])


class ResumeNeedsTheSameList(Base):
    def test_near_and_partial_report_what_differs(self):
        rep = run("batch_report.py", "init", self.root, "--kind", "bugs", "--items", "BUG-001,BUG-002,BUG-003,BUG-004,BUG-005", "--branch", "fix/b")
        out = run("batch_report.py", "find", self.root, "--kind", "bugs", "--items", "BUG-001,BUG-002,BUG-003,BUG-004,BUG-005,BUG-006")
        self.assertEqual(out["match"], "near")
        self.assertEqual((out["added"], out["dropped"]), (["BUG-006"], []))
        text = (Path(__file__).resolve().parents[1] / "shared/batch-runner.md").read_text()
        self.assertIn("don't reuse the old list silently", text)
