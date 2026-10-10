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
                if d.name == "gitflow":      # the one skill that writes to git, and only when asked
                    continue
                self.assertIn("**Never run `git commit`, `git push` or open a PR.**", text,
                              "every skill must carry the canonical no-commit promise verbatim")

    def test_gitflow_is_the_only_writer_and_only_when_asked(self):
        text = (KIT / "skills/gitflow/SKILL.md").read_text()
        self.assertIn("**Only run a git write the user asked for in this invocation and confirmed.**", text)
        self.assertIn("Every git write here needs a yes", text)
        self.assertIn("no other backlog-kit skill commits", text.replace("No other", "no other"))
        for forbidden in ("gh pr merge", "--force", "--no-verify", "rebase"):
            self.assertIn(forbidden, text)          # named only to forbid; check each is in a prohibition line
            for ln in [l for l in text.splitlines() if forbidden in l]:
                self.assertRegex(ln.lower(), r"never|not|no |refuse|don't|stop", ln)
        # no other skill may mention being able to invoke it
        for d in SKILLS:
            if d.name == "gitflow":
                continue
            body = (d / "SKILL.md").read_text()
            for ln in [l for l in body.splitlines() if "`gitflow`" in l]:
                self.assertRegex(ln, r"never invoke it|[Dd]o not invoke", f"{d.name}: {ln[:80]}")

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

    def test_there_is_no_confirmed_mode_every_item_is_confirmed_by_the_user(self):
        # decision D8: the source projects confirm every item, also inside a batch.
        for path in list((KIT / "skills").glob("*/SKILL.md")) + list((KIT / "shared").glob("*.md")):
            with self.subTest(file=str(path.relative_to(KIT))):
                self.assertNotIn("--confirmed", path.read_text())
        for name in ("bug-fix", "feature-development"):
            text = (KIT / "skills" / name / "SKILL.md").read_text()
            self.assertIn("goes to the user, also when this skill runs inside a batch", text)
        for name in ("bugs-batch-fix", "features-batch-development"):
            text = (KIT / "skills" / name / "SKILL.md").read_text()
            self.assertIn("still asks the user to confirm each", text)
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
        self.assertEqual(backlog_kit.load_config(self.ROOT)["git"]["finish_skill"], "gitflow")
        self.assertIn("finish_skill", (self.ROOT / "backlog-kit.example.toml").read_text(encoding="utf-8"))


class ReleaseHygieneTest(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]

    def test_changelog_top_entry_matches_the_plugin_version(self):
        import json
        version = json.loads((self.ROOT / ".claude-plugin/plugin.json").read_text())["version"]
        top = re.search(r"^## \[?(\d+\.\d+\.\d+)", (self.ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), re.M)
        self.assertIsNotNone(top)
        self.assertEqual(top.group(1), version)

    def test_ci_runs_the_drift_check_and_the_tests(self):
        ci = (self.ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("tools/vendor.py --check", ci)
        self.assertIn("unittest discover -s tests", ci)

    def test_readme_states_its_limits_and_the_loop(self):
        readme = (self.ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Limitations", readme)
        self.assertIn("has been tested against real git repositories, not yet against GitHub", readme)
        self.assertIn("## The loop", readme)


class GeneralizedSkillsTest(unittest.TestCase):
    """The seven skills generalized from the source projects (0.2.6)."""
    ROOT = Path(__file__).resolve().parents[1]
    REVIEWERS = ("code-reviewer", "security-reviewer", "database-reviewer")
    STANDALONE = ("architecture-reviewer", "product-scope-roaster", "dependency-upgrade", "docs-sync")

    def text(self, name):
        parts = [(self.ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")]
        for ref in sorted((self.ROOT / "skills" / name / "reference").glob("*.md")) if (self.ROOT / "skills" / name / "reference").is_dir() else []:
            parts.append(ref.read_text(encoding="utf-8"))
        return "\n".join(parts)

    def test_reviewers_have_a_non_interactive_mode_that_matches_the_review_phase(self):
        for name in self.REVIEWERS:
            with self.subTest(skill=name):
                t = self.text(name)
                self.assertIn("REVIEW: <n> critical, <n> warning, <n> suggestion", t)
                self.assertRegex(t, r"(?i)non-interactive")
                self.assertIn("- [ ]", t)
                self.assertIn("🔴", t)
                self.assertRegex(t, r"\[\[reviews\]\][^`]*skill\s*=\s*\"" + re.escape(name) + r"\"|skill = \"" + re.escape(name) + r"\"")
                self.assertIn("reports_dir", t)
                self.assertIn("<reports_dir>/review/", t)

    def test_reviewers_show_a_reviews_block_a_project_can_paste(self):
        for name in self.REVIEWERS:
            with self.subTest(skill=name):
                self.assertRegex(self.text(name), r"```toml\n\[\[reviews\]\]\nname\s*=")

    def test_every_new_skill_writes_only_where_it_says_and_never_commits(self):
        for name in self.REVIEWERS + self.STANDALONE:
            with self.subTest(skill=name):
                self.assertIn("**Never run `git commit`, `git push` or open a PR.**", self.text(name))
                self.assertFalse((self.ROOT / "skills" / name / "scripts").exists(), "no scripts: nothing here may shell out")

    def test_whole_system_skills_only_advise(self):
        for name in ("architecture-reviewer", "product-scope-roaster"):
            with self.subTest(skill=name):
                t = self.text(name)
                self.assertRegex(t, r"(?i)never (file|apply|edit)")
                self.assertIn("reports_dir", t)

    def test_architecture_follow_ups_can_record_decisions(self):
        self.assertIn("`decision-record`", self.text("architecture-reviewer"))

    def test_dependency_upgrade_never_writes_outside_the_repo_or_uses_destructive_git(self):
        t = self.text("dependency-upgrade")
        self.assertIn("snapshots/", t)
        self.assertNotIn("outside the repo (not a git operation)", t)
        self.assertRegex(t, r"Never run a destructive git command")
        self.assertIn("never switches branches", t)

    def test_dependency_upgrade_snapshots_stay_out_of_git_status_and_cover_edited_files(self):
        t = self.text("dependency-upgrade")
        self.assertIn("git rev-parse --git-dir", t)
        self.assertIn("<git-dir>/backlog-kit/dependency-upgrade/snapshots/", t)
        self.assertNotIn("<reports_dir>/dependency-upgrade/snapshots", t)
        self.assertIn("before editing any file, copy it into the group's snapshot folder", t)

    def test_dependency_upgrade_declares_groups_that_cannot_be_rolled_back(self):
        t = self.text("dependency-upgrade")
        self.assertIn("Declare source-rewriting groups", t)
        self.assertIn("NOT ROLLED BACK", t)
        self.assertIn("do not attempt a partial restore", t)

    def test_dependency_upgrade_rechecks_vulnerabilities_and_never_says_clean_unchecked(self):
        t = self.text("dependency-upgrade")
        self.assertIn("## 6. Re-check vulnerabilities", t)
        self.assertIn('"not checked", never "clean"', t)
        self.assertIn("Vulnerability check (read-only)", t)

    def test_dependency_upgrade_table_has_the_corrected_commands(self):
        t = self.text("dependency-upgrade")
        self.assertIn("Do not use `versions:use-latest-versions`", t)
        self.assertIn("-DgenerateBackupPoms=false", t)
        self.assertIn("dotnet restore --locked-mode", t)
        self.assertIn("`--save-exact`", t)
        self.assertIn("a major needs the constraint edited", t)
        self.assertIn("a major needs `Cargo.toml` edited first", t)
        self.assertIn("**Yarn flavour**", t)
        self.assertIn("**Workspaces**", t)

    def test_dependency_upgrade_restores_the_originals_levers(self):
        t = self.text("dependency-upgrade")
        for needle in ("**Version-managing parents come first.**", "ask_before", "Say \"candidate\", never \"unused\"",
                       "current branch is the base branch"):
            self.assertIn(needle, t)

    def test_docs_sync_edits_docs_only_and_documents_the_map(self):
        t = self.text("docs-sync")
        for key in ("[[docs.map]]", "doc", "section", "source", "check"):
            self.assertIn(key, t)
        self.assertIn("DOCS: nothing to sync", t)
        sys.path.insert(0, str(self.ROOT / "lib"))
        import backlog_kit
        self.assertEqual(backlog_kit.load_config(self.ROOT)["docs"]["map"], [])
        example = (self.ROOT / "backlog-kit.example.toml").read_text(encoding="utf-8")
        self.assertIn("[[docs.map]]", example)

    def test_docs_map_entries_load_from_toml(self):
        import tempfile
        sys.path.insert(0, str(self.ROOT / "lib"))
        import backlog_kit
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".backlog-kit.toml").write_text('[[docs.map]]\ndoc = "docs/a.md"\nsource = ["src/**"]\ncheck = "x"\n')
            cfg = backlog_kit.load_config(d)
            self.assertEqual(cfg["docs"]["map"][0]["doc"], "docs/a.md")
            self.assertEqual(cfg["docs"]["sync_skill"], "")

    def test_example_config_points_reviews_at_shipped_skills(self):
        example = (self.ROOT / "backlog-kit.example.toml").read_text(encoding="utf-8")
        for name in self.REVIEWERS:
            self.assertIn(f'skill = "{name}"', example)
            self.assertTrue((self.ROOT / "skills" / name / "SKILL.md").is_file())
