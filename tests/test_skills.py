"""Lint the SKILL.md files: structure, script references, the public promise, no stack coupling.

Run: python3 -m unittest discover -s tests -v   (from the backlog-kit root)
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
SKILLS = sorted((KIT / "skills").iterdir())
# Terms that mean a skill has leaked the project it was extracted from.
LEAK = re.compile(r"supabase|angular|vercel|optimus|pablo|cypress|\bRLS\b|\.cy\.ts|drexler|jp-photo", re.I)
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def frontmatter(text):
    m = FRONTMATTER.match(text)
    assert m, "missing frontmatter"
    return dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M))


class SkillLint(unittest.TestCase):
    def test_every_skill_dir_has_valid_frontmatter(self):
        for d in SKILLS:
            with self.subTest(skill=d.name):
                fm = frontmatter((d / "SKILL.md").read_text())
                self.assertEqual(fm["name"], d.name)
                self.assertGreater(len(fm["description"]), 80)
                self.assertIn("TRIGGER", fm["description"], "description must say when to trigger")

    def test_referenced_scripts_exist(self):
        for d in SKILLS:
            text = (d / "SKILL.md").read_text()
            for rel in set(re.findall(r"python3 (scripts/\w+\.py)", text)):
                with self.subTest(skill=d.name, script=rel):
                    self.assertTrue((d / rel).is_file())
            for rel in set(re.findall(r"python3 (\.\./[\w-]+/scripts/\w+\.py)", text)):
                with self.subTest(skill=d.name, script=rel):
                    self.assertTrue((d / rel).resolve().is_file())

    def test_public_promise_never_commits(self):
        for d in SKILLS:
            with self.subTest(skill=d.name):
                text = (d / "SKILL.md").read_text()
                self.assertIn("**Never run `git commit`, `git push` or open a PR.**", text,
                              "every skill must carry the canonical no-commit promise verbatim")

    def test_only_gitread_may_shell_out(self):
        # Scripts that can shell out could run git write commands and break the promise.
        # Exactly one module is allowed to, and its allowlist is checked below.
        files = list((KIT / "skills").rglob("*.py")) + list((KIT / "lib").glob("*.py")) + list((KIT / "tools").glob("*.py"))
        for f in files:
            with self.subTest(file=str(f.relative_to(KIT))):
                body = f.read_text()
                if f.name == "gitread.py":
                    continue
                self.assertNotRegex(body, r"\bsubprocess\b|os\.system|os\.popen")

    def test_gitread_allowlist_has_no_write_subcommand(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("gitread", KIT / "lib/gitread.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        forbidden = {"commit", "push", "merge", "rebase", "add", "reset", "checkout", "switch", "pull",
                     "stash", "cherry-pick", "apply", "am", "tag", "clean", "rm", "mv", "restore", "revert"}
        self.assertFalse(forbidden & mod.ALLOWED, forbidden & mod.ALLOWED)

    def test_work_skills_forbid_non_ff_merges_in_prose(self):
        for name in ("bug-fix", "feature-development"):
            text = (KIT / "skills" / name / "reference" / "pipeline-guardrails.md").read_text()
            self.assertIn("git merge --ff-only", text)
            self.assertRegex(text, r"(?i)no `git merge` without `--ff-only`")

    def test_created_branches_never_track_the_base_branch(self):
        for name, f in (("bug-fix", "phase-branch.md"), ("feature-development", "phase-branch.md"),
                        ("bugs-batch-fix", "batch-runner.md"), ("features-batch-development", "batch-runner.md")):
            text = (KIT / "skills" / name / "reference" / f).read_text()
            create = [ln for ln in text.splitlines() if ln.lstrip("> ").startswith("|") and "git switch -c" in ln and "--track" not in ln]
            self.assertTrue(create, f"{name}: no `create` row found")
            for ln in create:
                self.assertIn("--no-track", ln, f"{name}: `git switch -c` must use --no-track: {ln[:80]}")

    def test_gates_phase_forbids_system_changes_and_does_not_block_on_one_gate(self):
        text = (KIT / "shared/phase-gates.md").read_text()
        self.assertIn("Never install system packages", text)
        self.assertIn("NOT RUN (environment)", text)
        self.assertIn("GATES: PARTIAL", text)
        self.assertIn("never wave it through", text)
        self.assertIn("`npm ci`, not `npm install`", text)

    def test_confirmed_mode_is_wired_through_and_bounded(self):
        # the batch runner passes it, the work skills accept it, the selectors honour it only with an id
        for name in ("bugs-batch-fix", "features-batch-development"):
            runner = (KIT / "skills" / name / "reference" / "batch-runner.md").read_text()
            self.assertIn("--skip-branch-setup --confirmed", runner)
            self.assertIn("one approval of *what* gets worked on", runner)
        for name in ("bug-fix", "feature-development"):
            text = (KIT / "skills" / name / "SKILL.md").read_text()
            self.assertIn("--confirmed", text)
            self.assertIn("removes only Phase 0's per-", text)      # it removes ONE prompt, not the others
            self.assertIn("still goes to the user", text)
        for name, tail in (("bugs-next", "BUG_ID"), ("features-next", "CHANGE_NAME")):
            text = (KIT / "skills" / name / "SKILL.md").read_text()
            self.assertIn("### Confirmed mode", text)
            self.assertIn("can never be used to *choose*", text)     # no id -> ignored, normal flow
            self.assertIn("— mandatory", text)                       # the normal confirmation is still there
            self.assertIn(f"**no** `{tail}:` line", text)            # a stale id stops instead of guessing
        self.assertIn("**blocked by a prerequisite", (KIT / "skills/features-next/SKILL.md").read_text())
        guard = (KIT / "shared/pipeline-guardrails.md").read_text()
        self.assertIn("The one exception is `--confirmed`", guard)
        self.assertIn("never lets anything be chosen on the user's behalf", guard)

    def test_a_confirmed_mode_refusal_has_an_explicit_outcome(self):
        runner = (KIT / "shared/batch-runner.md").read_text()
        self.assertIn("or refused the item at selection", runner)
        self.assertIn("a later resume of the same list retries it", runner)
        self.assertIn("Refused at selection", (KIT / "skills/features-batch-development/SKILL.md").read_text())
        self.assertIn("Refused at selection", (KIT / "skills/bugs-batch-fix/SKILL.md").read_text())

    def test_uncovered_changes_are_called_out_not_folded_into_pass(self):
        gates = (KIT / "shared/phase-gates.md").read_text()
        self.assertIn("uncovered_files", gates)
        self.assertIn("NOT VERIFIED BY ANY GATE", gates)
        for name in ("bug-fix", "feature-development"):
            self.assertIn("NOT VERIFIED BY ANY GATE", (KIT / "skills" / name / "SKILL.md").read_text())

    def test_vendored_copies_are_current(self):
        proc = subprocess.run([sys.executable, str(KIT / "tools/vendor.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_placeholder_script_and_reference_paths_resolve(self):
        for d in SKILLS:
            text = (d / "SKILL.md").read_text()
            for rel in set(re.findall(r"<scripts>/(\w+\.py)", text + "".join(
                    f.read_text() for f in (d / "reference").glob("*.md") if (d / "reference").is_dir()))):
                with self.subTest(skill=d.name, script=rel):
                    self.assertTrue((d / "scripts" / rel).is_file())
            for rel in set(re.findall(r"`(reference/[\w-]+\.md)`", text)):
                with self.subTest(skill=d.name, reference=rel):
                    self.assertTrue((d / rel).is_file())

    def test_no_stack_leakage(self):
        for f in list((KIT / "skills").rglob("*")) + list((KIT / "lib").glob("*")) + list((KIT / "shared").glob("*")) + list((KIT / "tools").glob("*")):
            if f.is_file() and f.suffix in {".md", ".py"}:
                with self.subTest(file=str(f.relative_to(KIT))):
                    hit = LEAK.search(f.read_text())
                    self.assertIsNone(hit, f"stack-specific term leaked: {hit.group(0) if hit else ''}")

    def test_no_script_imports_outside_stdlib_or_lib(self):
        stdlib_ok = {"argparse", "json", "re", "sys", "pathlib", "copy", "tomllib", "subprocess",
                     "datetime", "os",
                     "backlog_kit", "gitread", "work_scope", "branch_state", "detect_gates", "batch_plan", "batch_report"}
        for f in (KIT / "skills").rglob("*.py"):
            with self.subTest(file=str(f.relative_to(KIT))):
                mods = set(re.findall(r"^(?:import|from)\s+(\w+)", f.read_text(), re.M))
                self.assertLessEqual(mods, stdlib_ok, f"non-stdlib import: {mods - stdlib_ok}")


if __name__ == "__main__":
    unittest.main()


class PackagingTest(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]

    def test_plugin_manifest_and_marketplace_are_valid(self):
        import json
        plugin = json.loads((self.ROOT / ".claude-plugin" / "plugin.json").read_text())
        market = json.loads((self.ROOT / ".claude-plugin" / "marketplace.json").read_text())
        self.assertEqual(plugin["name"], "backlog-kit")
        self.assertRegex(plugin["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual([p["name"] for p in market["plugins"]], [plugin["name"]])

    def test_docs_list_every_skill(self):
        names = sorted(p.name for p in (self.ROOT / "skills").iterdir() if (p / "SKILL.md").is_file())
        readme = (self.ROOT / "README.md").read_text()
        for n in names:
            self.assertIn(f"`{n}`", readme, f"README does not mention {n}")

    def test_installer_copies_and_refuses_to_clobber(self):
        import subprocess, sys, tempfile
        with tempfile.TemporaryDirectory() as d:
            cmd = [sys.executable, str(self.ROOT / "tools" / "install.py"), d]
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            self.assertTrue((Path(d) / ".claude/skills/bug-fix/SKILL.md").is_file())
            self.assertNotEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            self.assertEqual(subprocess.run(cmd + ["--force", "--only", "bug-fix"], capture_output=True).returncode, 0)


class SpecComplianceProseTest(unittest.TestCase):
    def test_close_phase_checks_requirement_prose_not_only_scenarios(self):
        text = (Path(__file__).resolve().parents[1] / "skills/feature-development/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("prose conflict", text)
        self.assertIn("never edit a scenario's expected behaviour to match the code", text.replace("Never edit", "never edit"))
        self.assertIn("Never archive a change with a known prose conflict", text)


class FinishSkillPointerTest(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]

    def test_hand_off_can_name_the_projects_finish_skill_but_never_runs_it(self):
        for rel in ("skills/feature-development/SKILL.md", "skills/bug-fix/SKILL.md",
                    "skills/bugs-batch-fix/SKILL.md", "skills/features-batch-development/SKILL.md", "shared/batch-runner.md"):
            text = (self.ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("[git] finish_skill", text, rel)
            self.assertRegex(text, r"never invoke it( yourself)?", rel)

    def test_finish_skill_is_a_documented_default(self):
        sys.path.insert(0, str(self.ROOT / "lib"))
        import backlog_kit
        self.assertEqual(backlog_kit.load_config(self.ROOT)["git"]["finish_skill"], "")
        self.assertIn("finish_skill", (self.ROOT / "backlog-kit.example.toml").read_text(encoding="utf-8"))
