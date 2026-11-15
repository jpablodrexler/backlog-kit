import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/brain/scripts/brain.py"


def run(brain, *args, ok=True):
    p = subprocess.run([sys.executable, "-I", str(SCRIPT), "--dir", str(brain), *args], capture_output=True, text=True, encoding="utf-8")
    if ok:
        assert p.returncode == 0, p.stdout + p.stderr
    return p


def note(brain, rel, title, summary, body, tags="[]"):
    f = Path(brain) / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(f"---\ntitle: {title}\nsummary: {summary}\ntags: {tags}\nupdated: 2026-11-11\n---\n\n{body}\n", encoding="utf-8")


class BrainTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.b = Path(self.tmp.name) / "brain"
        run(self.b, "init")
        note(self.b, "projects/acme/auth.md", "Auth flow", "Cómo funciona la autenticación", "Usamos tokens JWT con expiración corta.", "[auth, acme]")
        note(self.b, "topics/postgres.md", "Postgres tips", "Índices y vacuum", "Un índice parcial evitó el seq scan.", "[db]")

    def tearDown(self):
        self.tmp.cleanup()

    def test_init_is_idempotent_and_keeps_notes(self):
        out = run(self.b, "init").stdout
        self.assertIn("already existed", out)
        self.assertTrue((self.b / "projects/acme/auth.md").is_file())

    def test_search_ranks_title_over_body_and_ignores_accents(self):
        out = run(self.b, "search", "autenticacion").stdout
        self.assertTrue(out.startswith("projects/acme/auth.md"), out)
        out = run(self.b, "search", "indice").stdout
        self.assertIn("topics/postgres.md", out)

    def test_search_filters_and_json(self):
        data = json.loads(run(self.b, "search", "auth", "--area", "projects", "--json").stdout)
        self.assertEqual([d["path"] for d in data], ["projects/acme/auth.md"])
        self.assertEqual(run(self.b, "search", "auth", "--tag", "db").stdout.strip(), "no notes match")

    def test_index_and_check(self):
        run(self.b, "index")
        self.assertIn("(projects/acme/auth.md)", (self.b / "INDEX.md").read_text(encoding="utf-8"))
        self.assertEqual(run(self.b, "check", ok=False).returncode, 0)
        note(self.b, "topics/new.md", "New", "", "see [x](missing.md)")
        p = run(self.b, "check", ok=False)
        self.assertEqual(p.returncode, 1)
        for needle in ("missing `summary`", "broken link missing.md", "INDEX.md is stale"):
            self.assertIn(needle, p.stdout)

    def test_recent_and_missing_terms(self):
        self.assertIn("projects/acme/auth.md", run(self.b, "recent").stdout)
        self.assertNotEqual(run(self.b, "search", "x", ok=False).returncode, 0)


class DefaultDirTest(unittest.TestCase):
    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("brain", SCRIPT)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "home"
        self.od = Path(self.tmp.name) / "OneDrive - Work"
        self.home.mkdir()
        self.od.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_windows_uses_onedrive(self):
        d = self.m.brain_dir(env={"OneDrive": str(self.od)}, platform="win32", home=self.home)
        self.assertEqual(d, self.od / "brain")

    def test_windows_falls_back_to_home_onedrive_then_home(self):
        self.assertEqual(self.m.brain_dir(env={}, platform="win32", home=self.home), self.home / "brain")
        (self.home / "OneDrive").mkdir()
        self.assertEqual(self.m.brain_dir(env={}, platform="win32", home=self.home), self.home / "OneDrive" / "brain")

    def test_ignores_stale_onedrive_variable(self):
        env = {"OneDrive": str(self.od / "gone")}
        self.assertEqual(self.m.brain_dir(env=env, platform="win32", home=self.home), self.home / "brain")

    def test_other_platforms_and_explicit_choices_win(self):
        env = {"OneDrive": str(self.od)}
        self.assertEqual(self.m.brain_dir(env=env, platform="linux", home=self.home), self.home / "brain")
        self.assertEqual(self.m.brain_dir(env={**env, "BRAIN_DIR": "/x/b"}, platform="win32", home=self.home), Path("/x/b"))
        self.assertEqual(self.m.brain_dir("/y/b", env=env, platform="win32", home=self.home), Path("/y/b"))


class MemoryCommandTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.b = Path(self.tmp.name) / "brain"
        run(self.b, "init")

    def test_memory_lists_a_projects_claude_memory_without_touching_it(self):
        home = Path(self.tmp.name) / "claude"
        project = (Path(self.tmp.name) / "My App").resolve()
        enc = "".join(c if c.isalnum() else "-" for c in str(project))
        mem = home / "projects" / enc / "memory"
        mem.mkdir(parents=True)
        (mem / "MEMORY.md").write_text("- [Rule](feedback_rule.md) - hook\n", encoding="utf-8")
        (mem / "feedback_rule.md").write_text(
            "---\nname: rule-one\ndescription: Always run the skills as written\nmetadata:\n  type: feedback\n---\n\nBody of the rule.\n",
            encoding="utf-8")
        out = run(self.b, "memory", "--project", str(project), "--claude-home", str(home)).stdout
        self.assertIn("feedback_rule.md", out)
        self.assertIn("rule-one", out)
        self.assertIn("Always run the skills as written", out)
        self.assertIn("1 memory file", out)
        self.assertNotIn("Body of the rule", out)                      # lists, does not dump contents
        self.assertTrue((mem / "feedback_rule.md").is_file())          # read-only

    def test_memory_says_so_when_the_project_has_no_memory_folder(self):
        home = Path(self.tmp.name) / "claude"
        out = run(self.b, "memory", "--project", str(Path(self.tmp.name) / "none"), "--claude-home", str(home)).stdout
        self.assertIn("no memory folder", out)


class SeveralPcsTest(unittest.TestCase):
    """Two PCs sharing one synced brain: per-machine journal files and sync-conflict detection."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.b = Path(self.tmp.name) / "brain"
        run(self.b, "init")

    def test_journal_file_is_per_day_and_machine(self):
        out = run(self.b, "journal", "--date", "2026-11-15", "--host", "DESKTOP-TBBREK0").stdout.strip()
        self.assertEqual(out, "journal/2026-11-15-desktop-tbbrek0.md")
        other = run(self.b, "journal", "--date", "2026-11-15", "--host", "Gaming PC!").stdout.strip()
        self.assertEqual(other, "journal/2026-11-15-gaming-pc.md")
        self.assertNotEqual(out, other)                              # two machines never share a file

    def test_journal_defaults_to_today_on_this_machine(self):
        out = run(self.b, "journal").stdout.strip()
        self.assertRegex(out, r"^journal/\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md$")

    def test_check_flags_sync_conflict_copies_only(self):
        note(self.b, "projects/a/x.md", "X note", "The original", "text")
        note(self.b, "projects/a/x-DESKTOP-ABC1.md", "X note copy", "OneDrive copy", "text")
        note(self.b, "projects/a/y.md", "Y note", "The original y", "text")
        note(self.b, "projects/a/y (1).md", "Y note copy", "numbered copy", "text")
        note(self.b, "projects/a/z.md", "Z note", "The original z", "text")
        note(self.b, "projects/a/z (Ann's conflicted copy 2026-11-15).md", "Z note copy", "Dropbox copy", "text")
        # legitimate names that must not be flagged
        note(self.b, "journal/2026-11-15.md", "Journal old", "old style journal", "text")
        note(self.b, "journal/2026-11-15-my-pc.md", "Journal my pc", "per-machine journal", "text")
        note(self.b, "projects/a/api.md", "Api", "api note", "text")
        note(self.b, "projects/a/api-v2.md", "Api v2", "a different note", "text")
        run(self.b, "index")
        p = run(self.b, "check", ok=False)
        self.assertEqual(p.returncode, 1)
        self.assertIn("projects/a/x-DESKTOP-ABC1.md: looks like a sync conflict copy of projects/a/x.md", p.stdout)
        self.assertIn("projects/a/y (1).md: looks like a sync conflict copy of projects/a/y.md", p.stdout)
        self.assertIn("conflicted copy 2026-11-15).md: looks like a sync conflict copy of projects/a/z.md", p.stdout)
        for fine in ("journal/2026-11-15-my-pc.md", "api-v2.md"):
            self.assertNotIn(fine + ": looks like", p.stdout)

    def test_a_note_whose_original_is_gone_is_not_a_conflict(self):
        note(self.b, "projects/a/solo-DESKTOP-ABC1.md", "Solo", "no original beside it", "text")
        run(self.b, "index")
        self.assertIn("ok:", run(self.b, "check").stdout)

    def test_conflicted_index_copy_says_to_rebuild(self):
        run(self.b, "index")
        (self.b / "INDEX-DESKTOP-ABC1.md").write_text("# copy\n", encoding="utf-8")
        p = run(self.b, "check", ok=False)
        self.assertIn("INDEX-DESKTOP-ABC1.md: looks like a sync conflict copy of INDEX.md", p.stdout)
        self.assertIn("delete the copy and run `brain.py index`", p.stdout)

    def test_auto_save_prompt_uses_the_machine_journal(self):
        src = (ROOT / "skills/brain/scripts/session_end.py").read_text(encoding="utf-8")
        self.assertIn("{journal}", src)
        self.assertNotIn("journal/{today}.md", src)


if __name__ == "__main__":
    unittest.main()


@unittest.skipIf(sys.platform == "win32", "the test stands in for claude with a sh script")
class AutoSaveTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.brain, self.home = t / "brain", t / "claude"
        lines = [{"type": "user", "message": {"role": "user", "content": "Vamos a arreglar el login"}},
                 {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Cambié el token"}, {"type": "tool_use", "name": "Edit"}]}},
                 {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "content": "NOISE"}]}},
                 {"type": "user", "message": {"role": "user", "content": "<command-name>/x</command-name>"}},
                 {"type": "user", "message": {"role": "user", "content": "Gracias, guarda la decisión"}}]
        self.tr = t / "s.jsonl"
        self.tr.write_text("\n".join(json.dumps(l) for l in lines), encoding="utf-8")
        self.stub = t / "fake_claude.py"          # records how it was called instead of calling a model
        self.stub.write_text("import sys,json,os\nopen(os.environ['OUT'],'w').write(json.dumps({'argv':sys.argv[1:],'stdin':sys.stdin.read(),'cwd':os.getcwd()}))\n")
        self.out = t / "out.json"

    def tearDown(self):
        self.tmp.cleanup()

    def hook(self, extra_env=None, tr=None):
        import os
        stub = self.tmp.name + "/claude_stub.sh"
        Path(stub).write_text(f'#!/bin/sh\nexec "{sys.executable}" "{self.stub}" "$@"\n')
        Path(stub).chmod(0o755)
        env = {**os.environ, "BRAIN_DIR": str(self.brain), "BRAIN_AUTOSAVE_CLAUDE": stub, "BRAIN_AUTOSAVE_WAIT": "1",
               "OUT": str(self.out), **(extra_env or {})}
        env.pop("BRAIN_AUTOSAVE_RUNNING", None) if not extra_env else None
        arg = json.dumps({"session_id": "abc", "transcript_path": str(tr or self.tr), "cwd": "/w/acme", "reason": "other"})
        return subprocess.run([sys.executable, "-I", str(ROOT / "skills/brain/scripts/session_end.py")], input=arg, text=True,
                              capture_output=True, encoding="utf-8", env=env)

    def test_summarises_spoken_text_only(self):
        self.assertEqual(self.hook().returncode, 0)
        got = json.loads(self.out.read_text())
        self.assertIn("USER: Vamos a arreglar el login", got["stdin"])
        self.assertIn("CLAUDE: Cambié el token", got["stdin"])
        for noise in ("NOISE", "command-name", "tool_use"):
            self.assertNotIn(noise, got["stdin"])
        self.assertEqual(Path(got["cwd"]).resolve(), self.brain.resolve())
        self.assertIn("<!-- session: abc -->", got["argv"][1])
        self.assertIn("acceptEdits", got["argv"])

    def test_skips_short_sessions_and_child_runs(self):
        short = Path(self.tmp.name) / "short.jsonl"
        short.write_text(json.dumps({"type": "user", "message": {"content": "hola"}}))
        self.hook(tr=short)
        self.assertFalse(self.out.exists())
        self.hook({"BRAIN_AUTOSAVE_RUNNING": "1"})
        self.assertFalse(self.out.exists())

    def test_installer_adds_and_removes_only_its_hook(self):
        import os
        s = self.home / "settings.json"
        self.home.mkdir()
        s.write_text(json.dumps({"theme": "dark", "hooks": {"SessionEnd": [{"hooks": [{"type": "command", "command": "other"}]}]}}))
        env = {**os.environ, "CLAUDE_HOME": str(self.home)}
        cmd = [sys.executable, "-I", str(ROOT / "skills/brain/scripts/hook_install.py")]
        for _ in range(2):                                   # twice: must not duplicate
            subprocess.run(cmd, check=True, capture_output=True, env=env)
        d = json.loads(s.read_text())
        cmds = [h["command"] for g in d["hooks"]["SessionEnd"] for h in g["hooks"]]
        self.assertEqual(len(cmds), 2)
        self.assertEqual(d["theme"], "dark")
        subprocess.run(cmd + ["--remove"], check=True, capture_output=True, env=env)
        d = json.loads(s.read_text())
        self.assertEqual([h["command"] for g in d["hooks"]["SessionEnd"] for h in g["hooks"]], ["other"])
