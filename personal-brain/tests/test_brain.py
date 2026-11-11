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


if __name__ == "__main__":
    unittest.main()
