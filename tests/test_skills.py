"""Lint the SKILL.md files: structure, script references, the public promise, no stack coupling.

Run: python3 -m unittest discover -s tests -v   (from the backlog-kit root)
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
def sdir(name):
    """A skill's folder, whether it is core (skills/) or an extra (extras/)."""
    return KIT / "extras" / name if (KIT / "extras" / name).is_dir() else KIT / "skills" / name


SKILLS = sorted(list((KIT / "skills").iterdir()) + list((KIT / "extras").iterdir()))
# Terms that mean a skill has leaked the project it was extracted from.
LEAK = re.compile(r"supabase|angular|vercel|optimus|pablo|cypress|\bRLS\b|\.cy\.ts|drexler|jp-photo", re.I)
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def frontmatter(text):
    m = FRONTMATTER.match(text)
    assert m, "missing frontmatter"
    out = {}
    lines = m.group(1).splitlines()
    i = 0
    while i < len(lines):
        k = re.match(r"^(\w+):\s*(.*)$", lines[i])
        i += 1
        if not k:
            continue
        key, val = k.group(1), k.group(2).strip()
        if val in (">", ">-", "|", "|-"):          # a folded / literal block scalar: the indented lines that follow
            block = []
            while i < len(lines) and (lines[i].startswith(" ") or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            val = " ".join(x for x in block if x)
        out[key] = val
    return out


class SkillLint(unittest.TestCase):
    def test_every_skill_dir_has_valid_frontmatter(self):
        for d in SKILLS:
            with self.subTest(skill=d.name):
                fm = frontmatter((d / "SKILL.md").read_text(encoding="utf-8"))
                self.assertEqual(fm["name"], d.name)
                self.assertGreater(len(fm["description"]), 80)
                self.assertRegex(fm["description"], r"TRIGGER|Use when", "description must say when to trigger")

    def test_referenced_scripts_exist(self):
        for d in SKILLS:
            text = (d / "SKILL.md").read_text(encoding="utf-8")
            for rel in set(re.findall(r"python3 (scripts/\w+\.py)", text)):
                with self.subTest(skill=d.name, script=rel):
                    self.assertTrue((d / rel).is_file())
            for rel in set(re.findall(r"python3 (\.\./[\w-]+/scripts/\w+\.py)", text)):
                with self.subTest(skill=d.name, script=rel):
                    self.assertTrue((d / rel).resolve().is_file())

    def test_public_promise_never_commits(self):
        for d in SKILLS:
            with self.subTest(skill=d.name):
                text = (d / "SKILL.md").read_text(encoding="utf-8")
                if d.name == "gitflow":      # the one skill that writes to git, and only when asked
                    continue
                self.assertIn("**Never run `git commit`, `git push` or open a PR.**", text,
                              "every skill must carry the canonical no-commit promise verbatim")

    def test_gitflow_is_the_only_pusher_and_keeps_the_originals_confirmations(self):
        text = (KIT / "skills/gitflow/SKILL.md").read_text(encoding="utf-8")
        for needle in ("Never force-push", "Never merge a PR automatically",
                       "Never tag without explicit user confirmation",
                       "Never delete `main` or `develop`",
                       "Cleanup branches never deletes anything without the user explicitly confirming"):
            self.assertIn(needle, text)
        # the other skills only create/switch/sync a branch through gitflow and never commit
        for d in SKILLS:
            if d.name == "gitflow":
                continue
            body = (d / "SKILL.md").read_text(encoding="utf-8")
            for ln in [l for l in body.splitlines() if "`gitflow`" in l]:
                if d.name in ("feature-development", "bug-fix", "features-batch-development", "bugs-batch-fix", "dependency-upgrade", "spec-compliance-check"):
                    continue        # D23: the pipelines call gitflow's start and sync as the originals do
                self.assertRegex(ln, r"never invoke it|[Dd]o not invoke", f"{d.name}: {ln[:80]}")

    def test_only_gitread_may_shell_out(self):
        # Scripts that can shell out could run git write commands and break the promise.
        # Exactly one module is allowed to, and its allowlist is checked below.
        files = list(list((KIT / "skills").rglob("*.py")) + list((KIT / "extras").rglob("*.py"))) + list((KIT / "lib").glob("*.py")) + list((KIT / "tools").glob("*.py"))
        for f in files:
            with self.subTest(file=str(f.relative_to(KIT))):
                body = f.read_text(encoding="utf-8")
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






    def test_there_is_no_confirmed_mode(self):
        # decision D8: the source projects confirm every item, also inside a batch.
        for path in list((KIT / "skills").glob("*/SKILL.md")) + list((KIT / "extras").glob("*/SKILL.md")) + list((KIT / "shared").glob("*.md")):
            with self.subTest(file=str(path.relative_to(KIT))):
                self.assertNotIn("--confirmed", path.read_text(encoding="utf-8"))

    def test_vendored_copies_are_current(self):
        proc = subprocess.run([sys.executable, str(KIT / "tools/vendor.py"), "--check"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_placeholder_script_and_reference_paths_resolve(self):
        for d in SKILLS:
            text = (d / "SKILL.md").read_text(encoding="utf-8")
            for rel in set(re.findall(r"<scripts>/(\w+\.py)", text + "".join(
                    f.read_text(encoding="utf-8") for f in (d / "reference").glob("*.md") if (d / "reference").is_dir()))):
                with self.subTest(skill=d.name, script=rel):
                    self.assertTrue((d / "scripts" / rel).is_file())
            for rel in set(re.findall(r"`(reference/[\w-]+\.md)`", text)):
                with self.subTest(skill=d.name, reference=rel):
                    self.assertTrue((d / rel).is_file())

    def test_no_stack_leakage(self):
        for f in list((KIT / "skills").rglob("*")) + list((KIT / "extras").rglob("*")) + list((KIT / "lib").glob("*")) + list((KIT / "shared").glob("*")) + list((KIT / "tools").glob("*")):
            if f.is_file() and f.suffix in {".md", ".py"}:
                with self.subTest(file=str(f.relative_to(KIT))):
                    # the author line of the frontmatter names the owner; nothing else may
                    hit = LEAK.search(f.read_text(encoding="utf-8").replace("author: Juan Pablo Drexler", ""))
                    self.assertIsNone(hit, f"stack-specific term leaked: {hit.group(0) if hit else ''}")

    def test_no_script_imports_outside_stdlib_or_lib(self):
        stdlib_ok = {"argparse", "json", "re", "sys", "pathlib", "copy", "tomllib", "subprocess",
                     "datetime", "os",
                     "backlog_kit", "gitread", "work_scope", "branch_state", "detect_gates", "batch_plan", "batch_report"}
        for f in list((KIT / "skills").rglob("*.py")) + list((KIT / "extras").rglob("*.py")):
            with self.subTest(file=str(f.relative_to(KIT))):
                mods = set(re.findall(r"^(?:import|from)\s+(\w+)", f.read_text(encoding="utf-8"), re.M))
                self.assertLessEqual(mods, stdlib_ok, f"non-stdlib import: {mods - stdlib_ok}")


if __name__ == "__main__":
    unittest.main()


class PackagingTest(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]

    def test_plugin_manifest_and_marketplace_are_valid(self):
        import json
        plugin = json.loads((self.ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        market = json.loads((self.ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["name"], "backlog-kit")
        self.assertRegex(plugin["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual([p["name"] for p in market["plugins"]], [plugin["name"]])

    def test_docs_list_every_skill(self):
        names = sorted(p.name for p in (self.ROOT / "skills").iterdir() if (p / "SKILL.md").is_file())
        readme = (self.ROOT / "README.md").read_text(encoding="utf-8")
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

    def test_installer_extras_flag_with_and_without_names(self):
        import subprocess, sys, tempfile
        base = [sys.executable, str(self.ROOT / "tools" / "install.py")]
        core = len(list((self.ROOT / "skills").glob("*/SKILL.md")))
        extras = len(list((self.ROOT / "extras").glob("*/SKILL.md")))
        for args, expected in (([], core), (["--extras"], core + extras), (["--extras", "docs-sync,code-reviewer"], core + 2)):
            with tempfile.TemporaryDirectory() as d:
                self.assertEqual(subprocess.run(base + [d] + args, capture_output=True).returncode, 0, args)
                self.assertEqual(len(list((Path(d) / ".claude/skills").glob("*/SKILL.md"))), expected, args)


class ReleaseHygieneTest(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]

    def test_changelog_top_entry_matches_the_plugin_version(self):
        import json
        version = json.loads((self.ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        top = re.search(r"^## \[?(\d+\.\d+\.\d+)", (self.ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), re.M)
        self.assertIsNotNone(top)
        self.assertEqual(top.group(1), version)

    def test_ci_runs_the_drift_check_and_the_tests(self):
        ci = (self.ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("tools/vendor.py --check", ci)
        self.assertIn("unittest discover -s tests", ci)

    def test_readme_states_its_limits_and_the_loop(self):
        readme = (self.ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Limitations", readme)
        self.assertIn("has been tested against real git repositories, not yet against GitHub", readme)
        self.assertIn("## The loop", readme)


class GeneralizedSkillsTest(unittest.TestCase):
    """The seven skills generalized from the source projects."""
    ROOT = Path(__file__).resolve().parents[1]
    REVIEWERS = ("code-reviewer", "security-reviewer", "database-reviewer")
    STANDALONE = ("architecture-reviewer", "product-scope-roaster", "dependency-upgrade", "docs-sync")

    def text(self, name):
        parts = [(sdir(name) / "SKILL.md").read_text(encoding="utf-8")]
        for ref in sorted((sdir(name) / "reference").glob("*.md")) if (sdir(name) / "reference").is_dir() else []:
            parts.append(ref.read_text(encoding="utf-8"))
        return "\n".join(parts)



    def test_every_new_skill_writes_only_where_it_says_and_never_commits(self):
        for name in self.REVIEWERS + self.STANDALONE:
            with self.subTest(skill=name):
                self.assertIn("**Never run `git commit`, `git push` or open a PR.**", self.text(name))
                self.assertFalse((sdir(name) / "scripts").exists(), "no scripts: nothing here may shell out")

    def test_whole_system_skills_only_advise(self):
        for name in ("architecture-reviewer", "product-scope-roaster"):
            with self.subTest(skill=name):
                t = self.text(name)
                self.assertRegex(t, r"(?i)never (file|apply|edit)")
                self.assertIn("backlog_dir", t)

    def test_architecture_follow_ups_can_record_decisions(self):
        self.assertIn("`decision-record`", self.text("architecture-reviewer"))











class ListMergeCandidates(unittest.TestCase):
    """The original cleanup helper, reading git through the allowlisted gitread."""

    def test_lists_local_topic_branches_without_a_remote(self):
        import json, subprocess, sys, tempfile
        script = KIT / "skills/gitflow/scripts/list_merge_candidates.py"
        with tempfile.TemporaryDirectory() as d:
            def g(*a):
                subprocess.run(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *a],
                               check=True, capture_output=True)
            g("init", "-q", "-b", "main")
            g("commit", "-q", "--allow-empty", "-m", "x")
            g("branch", "feature/a"); g("branch", "hotfix/v1.0.1"); g("branch", "other/z")
            out = json.loads(subprocess.run([sys.executable, str(script), d, "--no-fetch", "--json"],
                                            capture_output=True, text=True, encoding="utf-8", check=True).stdout)
            self.assertEqual([c["branch"] for c in out["candidates"]], ["feature/a", "hotfix/v1.0.1"])
            self.assertEqual(out["candidates"][0]["where"], ["local"])


class ReviewerFrames(unittest.TestCase):
    """D30/D31: the reviewers carry the frame; the checklists are the project's, found by their `Read when:` line."""

    def test_each_reviewer_reads_the_project_checklists_and_warns_when_there_are_none(self):
        for name, kind in (("code-reviewer", "code"), ("security-reviewer", "security"), ("database-reviewer", "database")):
            with self.subTest(skill=name):
                text = (sdir(name) / "SKILL.md").read_text(encoding="utf-8")
                # their checks live in a section of the project's docs
                self.assertIn(f"`{kind.capitalize()} review checks`", text)
                self.assertIn({"code": "docs/frontend.md", "security": "docs/security.md", "database": "docs/database.md"}[kind], text)
                self.assertIn("no project checklist", " ".join(text.lower().split()))
                self.assertIn("**Never run `git commit`, `git push` or open a PR.**", text)


class MigrateCheck(unittest.TestCase):
    def test_reports_replaced_skills_references_backlog_and_missing_folders(self):
        import subprocess, sys, tempfile
        script = KIT / "tools/migrate_check.py"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            def g(*a):
                subprocess.run(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True, capture_output=True)
            g("init", "-q", "-b", "main")
            (root / ".claude/skills/bug-fix").mkdir(parents=True)
            (root / ".claude/skills/bug-fix/SKILL.md").write_text("x", encoding="utf-8")
            (root / ".claude/skills/web-docs-sync").mkdir(parents=True)
            (root / ".claude/skills/web-docs-sync/SKILL.md").write_text("x", encoding="utf-8")
            (root / ".claude/skills/stack-helper").mkdir(parents=True)
            (root / ".claude/skills/stack-helper/SKILL.md").write_text("see `web-docs-sync` and bug-fix", encoding="utf-8")
            (root / "sub/docs/backlog").mkdir(parents=True)
            (root / "sub/docs/backlog/bugs-open.md").write_text("# Bugs\n", encoding="utf-8")
            g("add", "-A")
            out = subprocess.run([sys.executable, str(script), d], capture_output=True, text=True, encoding="utf-8", check=True).stdout
            self.assertIn("- bug-fix", out)
            self.assertIn("web-docs-sync  (the kit calls it `docs-sync`)", out)
            self.assertNotIn("- stack-helper", out.split("## 2.")[0])
            self.assertIn(".claude/skills/stack-helper/SKILL.md", out)
            self.assertIn('backlog_dir = "sub/docs/backlog"', out)
            self.assertIn("## 5. Base branch", out)
            self.assertIn("no local develop branch", out)
            g("commit", "-q", "-m", "x")
            g("branch", "develop")
            out = subprocess.run([sys.executable, str(script), d], capture_output=True, text=True, encoding="utf-8", check=True).stdout
            self.assertIn("WARNING develop does not contain the kit's skills", out)
            (root / ".claude/skills/features-next/scripts").mkdir(parents=True)
            (root / ".claude/skills/features-next/scripts/backlog_kit.py").write_text("x", encoding="utf-8")
            g("add", "-A"); g("commit", "-q", "-m", "y"); g("branch", "-f", "develop")
            out = subprocess.run([sys.executable, str(script), d], capture_output=True, text=True, encoding="utf-8", check=True).stdout
            self.assertIn("develop contains the kit's skills", out)


class HandBackContract(unittest.TestCase):
    """The shared hand-back paragraph exists and every skill that spawns subagents tells the orchestrator to append it."""

    def test_paragraph_and_references(self):
        for name in ("feature-development", "bug-fix"):
            with self.subTest(skill=name):
                text = (sdir(name) / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("**Hand-back.** Your hand-back is the final text of your response", text)
                self.assertIn("never send placeholder text", text)
        for name in ("feature-development", "bug-fix"):
            text = " ".join((sdir(name) / "SKILL.md").read_text(encoding="utf-8").split())
            self.assertIn("look at the working tree for what the subagent actually did", text)


class KitConventions(unittest.TestCase):
    """Every docs/ path a skill mentions is a location the kit's conventions table defines."""

    def test_skill_paths_are_in_the_conventions_table(self):
        import re
        table = (KIT / "shared/conventions.md").read_text(encoding="utf-8")
        known = {k.rstrip("/") for k in re.findall(r"`(docs/[^`]+)`", table)}
        known |= {"docs/*.md", "docs/<topic>.md", "docs/decisions/*.md"}
        dirs = {k for k in known if k in ("docs/backlog", "docs/decisions", "docs/explorations", "docs/reports")}
        # a "`a.md`, `b.md`" cell lists several paths; the regex above already catches each one
        pat = re.compile(r"docs/[A-Za-z0-9_.*<>-]+(?:/[A-Za-z0-9_.*<>-]+)*")
        files = [f for d in ("skills", "extras") for f in (KIT / d).rglob("*.md") if "reference/conventions.md" not in str(f)]
        for f in files:
            for m in pat.findall(f.read_text(encoding="utf-8")):
                path = m.rstrip(".")
                ok = path in known or any(path.startswith(k + "/") for k in dirs)
                with self.subTest(file=str(f.relative_to(KIT)), path=path):
                    self.assertTrue(ok, f"{path} is not in shared/conventions.md")

    def test_checked_against_column_is_in_the_table_and_the_example(self):
        for rel in ("shared/conventions.md", "docs/conventions.md"):
            with self.subTest(file=rel):
                text = (KIT / rel).read_text(encoding="utf-8")
                self.assertIn("| Path | What it holds | Checked against |", text)
        self.assertIn("Checked against", (KIT / "extras/docs-sync/SKILL.md").read_text(encoding="utf-8"))

    def test_docs_sync_carries_the_table(self):
        self.assertTrue((KIT / "extras/docs-sync/reference/conventions.md").is_file())
        self.assertIn("## Kit conventions", (KIT / "shared/conventions.md").read_text(encoding="utf-8"))


class ViewportCheck(unittest.TestCase):
    def test_pipelines_require_every_configured_viewport_to_be_reported(self):
        for rel in ("shared/review-gate.md",):
            with self.subTest(file=rel):
                text = " ".join(" ".join(l.lstrip("> ") for l in (KIT / rel).read_text(encoding="utf-8").splitlines()).split())
                self.assertIn("Check **each** configured viewport in turn", text)
                self.assertIn("a viewport you did not check is never reported as verified", text)


class ReviewGate(unittest.TestCase):
    def test_pipelines_run_reviews_in_their_own_subagents_and_verify_the_reports(self):
        gate = (KIT / "shared/review-gate.md").read_text(encoding="utf-8")
        for needle in ("G6 — Verify before accepting", "SKILL_USED:", "FILES_CHANGED:", "REVIEW_GATE: DONE"):
            self.assertIn(needle, gate)
        for rel in ("skills/bug-fix", "skills/feature-development"):
            with self.subTest(skill=rel):
                self.assertTrue((KIT / rel / "reference/review-gate.md").is_file())
                text = (KIT / rel / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("reference/review-gate.md", text)
                self.assertIn("REVIEW_GATE: DONE", text)
        phase2 = (KIT / "skills/feature-development/reference/phase-2-implement-review.md").read_text(encoding="utf-8")
        self.assertNotIn("Invoke `code-reviewer`", phase2)


class SkillAuthor(unittest.TestCase):
    def test_every_skill_names_its_author(self):
        for f in sorted(list((KIT / "skills").glob("*/SKILL.md")) + list((KIT / "extras").glob("*/SKILL.md"))):
            with self.subTest(skill=f.parent.name):
                head = f.read_text(encoding="utf-8").split("\n---\n", 1)[0]
                self.assertIn("  author: Juan Pablo Drexler", head)
