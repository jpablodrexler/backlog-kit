"""Tests for the work skills' deterministic helpers (branch_state, work_scope, detect_gates, gitread)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "lib"
sys.path.insert(0, str(LIB))
import gitread  # noqa: E402
import backlog_kit as bk  # noqa: E402


def sh(cwd, *cmd):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True).stdout


def git(cwd, *args):
    return sh(cwd, "git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args)


def run(script, root, *extra):
    out = subprocess.run([sys.executable, str(LIB / script), str(root), *extra],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def init_repo(path, bare=False):
    Path(path).mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q", "-b", "main", *(["--bare"] if bare else []))
    return path


def commit_file(repo, name, text="x", msg="c"):
    (Path(repo) / name).write_text(text)
    git(repo, "add", name)
    git(repo, "commit", "-q", "-m", msg)


class GitRead(unittest.TestCase):
    def test_write_commands_are_refused(self):
        with tempfile.TemporaryDirectory() as d:
            init_repo(d)
            for bad in (("commit", "-m", "x"), ("push",), ("merge", "x"), ("rebase",), ("add", "."),
                        ("reset", "--hard"), ("checkout", "-b", "x"), ("switch", "-c", "x"),
                        ("branch", "-D", "x"), ("branch", "--delete", "x"), ("tag", "v1"), ("stash",)):
                with self.subTest(cmd=bad):
                    with self.assertRaises(gitread.GitError):
                        gitread.git(d, *bad)

    def test_allowlist_contains_no_write_subcommand(self):
        forbidden = {"commit", "push", "merge", "rebase", "add", "reset", "checkout", "switch", "pull",
                     "stash", "cherry-pick", "apply", "am", "tag", "clean", "rm", "mv", "restore", "revert"}
        self.assertFalse(forbidden & gitread.ALLOWED)

    def test_changed_files_sees_untracked_and_spaces(self):
        with tempfile.TemporaryDirectory() as d:
            init_repo(d)
            commit_file(d, "tracked.txt")
            (Path(d) / "tracked.txt").write_text("changed")
            (Path(d) / "new file.txt").write_text("n")
            (Path(d) / "sub").mkdir()
            (Path(d) / "sub/a.py").write_text("n")
            self.assertEqual(gitread.changed_files(d), ["new file.txt", "sub/a.py", "tracked.txt"])


class KitFiles(unittest.TestCase):
    def test_work_scope_ignores_backlog_kit_bookkeeping(self):
        with tempfile.TemporaryDirectory() as d:
            init_repo(d)
            for rel in ("docs/backlog/bugs-open.md", "docs/reports/bug-batch/R.md", "docs/decisions/0001-x.md",
                        ".backlog-kit.toml", ".claude/skills/bug-fix/SKILL.md", "src/Real.java"):
                f = Path(d) / rel
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text("[git]\n" if rel == ".backlog-kit.toml" else "x")   # a valid, empty-ish config
            out = run("work_scope.py", d)
            self.assertEqual(out["changed_files"], ["src/Real.java"])
            self.assertEqual(out["kit_files_ignored"], 5)

    def test_explicit_files_are_never_filtered(self):
        with tempfile.TemporaryDirectory() as d:
            out = run("work_scope.py", d, "--files", "docs/backlog/x.md")
            self.assertEqual(out["changed_files"], ["docs/backlog/x.md"])

    def test_known_failures_pass_through(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".backlog-kit.toml").write_text(
                '[[gates]]\nname = "unit"\nrun = "mvn test"\nknown_failures = ["HealthIndicatorTest"]\n')
            out = run("work_scope.py", d, "--files", "a.java")
            self.assertEqual(out["gates"][0]["known_failures"], ["HealthIndicatorTest"])


class GateCoverage(unittest.TestCase):
    def scope(self, toml, *files):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".backlog-kit.toml").write_text(toml)
            return run("work_scope.py", d, "--files", *files)

    def test_changed_files_outside_every_gate_are_reported(self):
        out = self.scope('[[gates]]\nname = "be"\nrun = "mvn test"\ncwd = "backend"\n',
                         "backend/src/A.java", "frontend/src/x.ts", "README.md")
        self.assertEqual(sorted(out["uncovered_files"]), ["README.md", "frontend/src/x.ts"])

    def test_a_gate_at_the_root_covers_everything_its_when_matches(self):
        out = self.scope('[[gates]]\nname = "all"\nrun = "make test"\n', "a/b.py", "c.py")
        self.assertEqual(out["uncovered_files"], [])

    def test_when_globs_narrow_coverage(self):
        out = self.scope('[[gates]]\nname = "sql"\nrun = "x"\nwhen = ["db/**"]\n', "db/m.sql", "src/a.py")
        self.assertEqual(out["uncovered_files"], ["src/a.py"])

    def test_no_gates_configured_reports_nothing_uncovered(self):
        self.assertEqual(self.scope("", "a.py")["uncovered_files"], [])


class Globs(unittest.TestCase):
    def test_matching(self):
        m = bk.glob_match
        self.assertTrue(m("src/app/x.ts", ["src/**"]))
        self.assertTrue(m("db/migrations/001.sql", ["**/migrations/**"]))
        self.assertTrue(m("c.sql", ["**/*.sql"]))
        self.assertFalse(m("a/b/c.sql", ["*.sql"]))
        self.assertTrue(m("anything", []))
        self.assertTrue(m("anything/at/all", ["**"]))


class WorkScope(unittest.TestCase):
    def test_gates_and_reviews_follow_when_globs(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".backlog-kit.toml").write_text(
                '[[gates]]\nname = "unit"\nrun = "echo u"\n\n'
                '[[gates]]\nname = "migrations"\nrun = "echo m"\nwhen = ["db/**"]\nask_before = "Hit staging?"\n\n'
                '[[reviews]]\nname = "security"\nfocus = "auth"\nwhen = ["**/auth/**"]\n')
            out = run("work_scope.py", d, "--files", "src/app.py", "web/auth/login.py")
            gates = {g["name"]: g for g in out["gates"]}
            self.assertTrue(gates["unit"]["applies"])
            self.assertFalse(gates["migrations"]["applies"])
            self.assertEqual(gates["migrations"]["ask_before"], "Hit staging?")
            self.assertEqual([r["name"] for r in out["reviews"] if r["applies"]], ["security"])
            # configured reviews replace the built-in default entirely
            self.assertEqual([r["name"] for r in out["reviews"]], ["security"])

    def test_default_has_a_general_review_and_no_gates(self):
        with tempfile.TemporaryDirectory() as d:
            out = run("work_scope.py", d, "--files", "a.txt")
            self.assertFalse(out["gates_configured"])
            self.assertEqual([r["name"] for r in out["reviews"]], ["code"])
            self.assertTrue(out["reviews"][0]["applies"])


class BranchState(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.t = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def state(self, repo, branch="fix/bug-1-x", *extra):
        return run("branch_state.py", repo, "--branch", branch, *extra)

    def test_create_when_nothing_exists(self):
        r = init_repo(self.t / "r")
        commit_file(r, "a.txt")
        s = self.state(r)
        self.assertEqual((s["action"], s["start_point"]), ("create", "main"))

    def test_dirty_tree_on_another_branch_blocks(self):
        r = init_repo(self.t / "r")
        commit_file(r, "a.txt")
        (Path(r) / "a.txt").write_text("dirty")
        self.assertEqual(self.state(r)["action"], "blocked")

    def test_kit_bookkeeping_files_do_not_count_as_dirty(self):
        r = init_repo(self.t / "r")
        commit_file(r, "a.txt")
        (Path(r) / "docs/backlog/bugs").mkdir(parents=True)
        (Path(r) / "docs/backlog/bugs-open.md").write_text("x")
        (Path(r) / "docs/backlog/bugs/BUG-001.md").write_text("x")
        (Path(r) / ".backlog-kit.toml").write_text("[git]\n")
        (Path(r) / ".claude/skills/bug-fix").mkdir(parents=True)
        (Path(r) / ".claude/skills/bug-fix/SKILL.md").write_text("x")
        (Path(r) / "docs/reports/bug-batch").mkdir(parents=True)
        (Path(r) / "docs/reports/bug-batch/BUG_BATCH_REPORT_2026-01-01.md").write_text("x")
        s = self.state(r)
        self.assertEqual(s["action"], "create")
        self.assertFalse(s["dirty"])
        self.assertEqual(s["kit_files_changed"], 5)

    def test_real_uncommitted_work_still_blocks_and_is_named(self):
        r = init_repo(self.t / "r")
        commit_file(r, "a.txt")
        (Path(r) / "docs/backlog").mkdir(parents=True)
        (Path(r) / "docs/backlog/bugs-open.md").write_text("x")
        (Path(r) / "src").mkdir()
        (Path(r) / "src/Main.java").write_text("half-done work")
        s = self.state(r)
        self.assertEqual(s["action"], "blocked")
        self.assertEqual(s["dirty_files"], ["src/Main.java"])
        self.assertIn("src/Main.java", s["reason"])

    def test_resume_beats_dirty_check(self):
        r = init_repo(self.t / "r")
        commit_file(r, "a.txt")
        git(r, "switch", "-c", "fix/bug-1-x")
        (Path(r) / "a.txt").write_text("in-progress fix")
        self.assertEqual(self.state(r)["action"], "resume")

    def test_checkout_existing_local_branch(self):
        r = init_repo(self.t / "r")
        commit_file(r, "a.txt")
        git(r, "branch", "fix/bug-1-x")
        self.assertEqual(self.state(r)["action"], "checkout")

    def test_remote_scenarios(self):
        origin = init_repo(self.t / "origin", bare=True)
        a = self.t / "a"
        git(self.t, "clone", "-q", str(origin), str(a))
        commit_file(a, "base.txt")
        git(a, "push", "-q", "origin", "main")
        b = self.t / "b"
        git(self.t, "clone", "-q", str(origin), str(b))

        git(a, "switch", "-c", "fix/bug-1-x")
        commit_file(a, "fix.txt")
        git(a, "push", "-q", "-u", "origin", "fix/bug-1-x")

        # pushed from another machine, no local copy -> track it
        self.assertEqual(self.state(b, "fix/bug-1-x", "--fetch")["action"], "track-remote")

        # create local tracking branch, then the other machine pushes more -> fast-forward paths
        git(b, "switch", "-q", "-c", "fix/bug-1-x", "--track", "origin/fix/bug-1-x")
        git(b, "switch", "-q", "main")
        commit_file(a, "more.txt")
        git(a, "push", "-q")
        self.assertEqual(self.state(b, "fix/bug-1-x", "--fetch")["action"], "checkout-ff")
        git(b, "switch", "-q", "fix/bug-1-x")
        self.assertEqual(self.state(b, "fix/bug-1-x")["action"], "fast-forward")

        # local-only commit as well -> diverged -> blocked, never merged
        commit_file(b, "local.txt")
        s = self.state(b, "fix/bug-1-x")
        self.assertEqual(s["action"], "blocked")
        self.assertIn("diverged", s["reason"])

    def test_batch_mode(self):
        r = init_repo(self.t / "r")
        commit_file(r, "a.txt")
        self.assertEqual(self.state(r, "x", "--batch")["action"], "blocked")  # on main
        git(r, "switch", "-c", "fix/shared-batch")
        (Path(r) / "a.txt").write_text("dirty is fine in batch mode")
        self.assertEqual(self.state(r, "x", "--batch")["action"], "batch-ok")

    def test_configured_base_branch(self):
        r = init_repo(self.t / "r")
        commit_file(r, "a.txt")
        git(r, "branch", "-m", "main", "trunkish")
        (Path(r) / ".backlog-kit.toml").write_text('[git]\nbase_branch = "trunkish"\n')
        git(r, "add", ".backlog-kit.toml")
        git(r, "commit", "-q", "-m", "cfg")
        self.assertEqual(self.state(r)["start_point"], "trunkish")


class DetectGates(unittest.TestCase):
    def test_node_in_subfolder_and_python_at_root(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "frontend").mkdir()
            (root / "frontend/package.json").write_text(json.dumps({"scripts": {"test": "x", "build": "y", "start": "z"}}))
            (root / "pytest.ini").write_text("[pytest]\n")
            out = run("detect_gates.py", d)
            runs = {(g["run"], g["cwd"]) for g in out["gates"]}
            self.assertIn(("npm test", "frontend"), runs)
            self.assertIn(("npm run build", "frontend"), runs)
            self.assertIn(("pytest", "."), runs)
            self.assertNotIn("start", json.dumps(out["gates"]))
            self.assertIn("[[gates]]", out["toml"])

    def test_finds_modules_two_levels_deep(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "Product/backend").mkdir(parents=True)
            (root / "Product/backend/pom.xml").write_text("<project/>")
            (root / "Product/frontend").mkdir(parents=True)
            (root / "Product/frontend/package.json").write_text(json.dumps({"scripts": {"test": "x", "build": "y"}}))
            runs = {(g["run"], g["cwd"]) for g in run("detect_gates.py", d)["gates"]}
            self.assertIn(("mvn -q test", "Product/backend"), runs)
            self.assertIn(("npm test", "Product/frontend"), runs)

    def test_nested_module_covered_by_ancestor_is_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "pom.xml").write_text("<project><modules/></project>")
            (root / "core").mkdir()
            (root / "core/pom.xml").write_text("<project/>")
            gates = run("detect_gates.py", d)["gates"]
            self.assertEqual([(g["run"], g["cwd"]) for g in gates], [("mvn -q test", ".")])

    def test_depth_is_bounded(self):
        with tempfile.TemporaryDirectory() as d:
            deep = Path(d) / "a/b/c/d"
            deep.mkdir(parents=True)
            (deep / "pom.xml").write_text("<project/>")
            self.assertEqual(run("detect_gates.py", d)["gates"], [])

    def test_nothing_detected(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(run("detect_gates.py", d)["gates"], [])

    def test_skips_node_modules(self):
        with tempfile.TemporaryDirectory() as d:
            nm = Path(d) / "node_modules/pkg"
            nm.mkdir(parents=True)
            (nm / "package.json").write_text(json.dumps({"scripts": {"test": "x"}}))
            self.assertEqual(run("detect_gates.py", d)["gates"], [])


if __name__ == "__main__":
    unittest.main()


class ConfirmedModeSafety(unittest.TestCase):
    """features-next resolves a typed name with --select: blocked and implemented features must not pass."""

    def test_select_flags_blocked_and_refuses_implemented_or_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs/backlog").mkdir(parents=True)
            (root / "docs/backlog/features-planned.md").write_text(
                "# Planned Features\n\n## Feature List\n\n"
                "| # | Change name | Priority | Effort | Area | Implementation | Summary | Brief |\n"
                "| - | ----------- | -------- | ------ | ---- | -------------- | ------- | ----- |\n"
                "| 1 | `base` | P1 | S | X | ⬜ Pending | b | [brief](features/001-base.md) |\n"
                "| 2 | `needs-base` | P1 | S | X | ⬜ Pending | n | [brief](features/002-needs-base.md) |\n\n"
                "## Dependencies\n\n### Hard implementation dependencies\n\n"
                "**Feature 2 → Feature 1** (still pending)\n\nx\n\n### Recommended implementation order\n\n_None yet._\n")
            (root / "docs/backlog/features-implemented.md").write_text(
                "# Implemented Features\n\n## Feature List\n\n| # | Change name | Priority | Effort | Area | Details |\n"
                "| - | ----------- | -------- | ------ | ---- | ------- |\n| 7 | `done` | P1 | S | X | [brief](features/007-done.md) |\n")
            script = LIB.parent / "skills/features-next/scripts/rank_features.py"
            sel = lambda x: json.loads(subprocess.run([sys.executable, str(script), d, "--select", x, "--json"],
                                                      capture_output=True, text=True, check=True).stdout)
            self.assertFalse(sel("base")["blocked"])
            blocked = sel("needs-base")
            self.assertTrue(blocked["blocked"])
            self.assertEqual(blocked["blocked_on"], "1")
            self.assertIn("error", sel("done"))     # already implemented
            self.assertIn("error", sel("ghost"))    # unknown


class ExampleConfig(unittest.TestCase):
    """The shipped example must parse, and its `when` globs must select what its comments claim."""

    def scope(self, *files):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".backlog-kit.toml").write_bytes((LIB.parent / "examples/angular-supabase.toml").read_bytes())
            out = run("work_scope.py", d, "--files", *files)
        return ({g["name"] for g in out["gates"] if g["applies"]},
                {r["name"] for r in out["reviews"] if r["applies"]}, out)

    def test_plain_component_change(self):
        gates, reviews, _ = self.scope("frontend/src/app/expenses/expenses.ts")
        self.assertEqual(gates, {"component tests", "mocked e2e", "production build"})
        self.assertEqual(reviews, {"code"})

    def test_template_change_adds_layout_review(self):
        _, reviews, _ = self.scope("frontend/src/app/expenses/expenses.html")
        self.assertEqual(reviews, {"code", "layout"})

    def test_migration_adds_database_security_reviews_and_live_e2e(self):
        gates, reviews, out = self.scope("supabase/migrations/20260101_x.sql")
        self.assertIn("live e2e", gates)
        self.assertEqual(reviews, {"code", "database", "security"})
        self.assertTrue(next(g for g in out["gates"] if g["name"] == "live e2e")["ask_before"])

    def test_auth_change_triggers_security_and_live_e2e(self):
        gates, reviews, _ = self.scope("frontend/src/app/core/auth.service.ts")
        self.assertIn("live e2e", gates)
        self.assertIn("security", reviews)

    def test_dependency_manifest_triggers_security_only(self):
        gates, reviews, _ = self.scope("frontend/package.json")
        self.assertNotIn("live e2e", gates)
        self.assertIn("security", reviews)
