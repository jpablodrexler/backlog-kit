"""0.2.9: holes in the work pipelines (manual tasks, tasks-ticked check, re-gating, re-entry)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "lib"))
import backlog_kit as bk  # noqa: E402


def task_state(tasks_md, workflow="openspec"):
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / ".backlog-kit.toml").write_text(f'[spec]\nworkflow = "{workflow}"\n')
        t = Path(d) / "openspec/changes/c1"
        t.mkdir(parents=True)
        if tasks_md is not None:
            (t / "tasks.md").write_text(tasks_md)
        out = subprocess.run([sys.executable, str(KIT / "lib/task_state.py"), d, "--change", "c1"],
                             capture_output=True, text=True, check=True).stdout
        return json.loads(out)


class TaskState(unittest.TestCase):
    def test_counts_done_blocking_and_manual(self):
        out = task_state("## 1. Build\n- [x] 1.1 Parser\n- [ ] 1.2 Wire it up\n"
                         "- [ ] 1.3 Generate the signing key (manual: `./scripts/make-key.sh`)\n  - [ ] 1.3.1 sub task\n")
        self.assertEqual((out["total"], out["done"]), (4, 1))
        self.assertEqual(out["blocking"], ["1.2 Wire it up", "1.3.1 sub task"])
        self.assertEqual(out["manual"], [{"title": "1.3 Generate the signing key", "command": "`./scripts/make-key.sh`"}])

    def test_all_done_means_nothing_blocking(self):
        out = task_state("- [x] a\n- [X] b\n")
        self.assertEqual(out["blocking"], [])

    def test_a_missing_file_is_reported_not_guessed(self):
        self.assertFalse(task_state(None)["found"])


class SpecFoldersAreNotCode(unittest.TestCase):
    def test_openspec_folders_are_kit_files_only_with_openspec(self):
        on = bk.load_config(tempfile.mkdtemp())
        on["spec"]["workflow"] = "openspec"
        self.assertTrue(bk.glob_match("openspec/changes/x/tasks.md", bk.kit_globs(on)))
        self.assertTrue(bk.glob_match("openspec/specs/a/spec.md", bk.kit_globs(on)))
        self.assertFalse(bk.glob_match("src/openspec.py", bk.kit_globs(on)))
        off = bk.load_config(tempfile.mkdtemp())
        self.assertFalse(bk.glob_match("openspec/changes/x/tasks.md", bk.kit_globs(off)))


def text(*parts):
    return (KIT.joinpath(*parts)).read_text()


class PipelineText(unittest.TestCase):





    def test_spec_compliance_has_a_guarded_manual_class_and_a_tasks_script(self):
        t = text("shared/spec-compliance.md")
        self.assertIn("task_state.py", t)
        self.assertIn("**Manual**", t)
        self.assertIn("never a way out of a gap you could close with a test", t)
        self.assertIn("<m> manual", t)


    def test_guardrails_define_reentry_after_a_blocker(self):
        t = text("shared/pipeline-guardrails.md")
        self.assertIn("Re-entry after a `*_BLOCKED`", t)
        self.assertIn("never from the start and never at the next phase", t)


if __name__ == "__main__":
    unittest.main()
