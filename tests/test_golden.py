"""Golden scenarios: the scripts run over a small, realistic backlog (tests/fixtures/backlog) and their JSON output
must match tests/golden/*.json exactly. A change in ranking, counting or date logic shows up here as a diff.

Regenerate after an intended change:  UPDATE_GOLDEN=1 python3 -m unittest tests.test_golden
Then read the diff of tests/golden/ before committing it.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
FIXTURE = KIT / "tests/fixtures/backlog"
GOLDEN = KIT / "tests/golden"
TODAY = "2026-11-04"

SCENARIOS = {
    "features-next": ["skills/features-next/scripts/rank_features.py", "{root}", "--json"],
    "bugs-next": ["skills/bugs-next/scripts/rank_bugs.py", "{root}", "--json"],
    "features-status": ["skills/features-status/scripts/status_report.py", "{root}", "--json"],
    "bugs-status": ["skills/bugs-status/scripts/status_report.py", "{root}", "--json"],
    "backlog-report": ["skills/backlog-report/scripts/backlog_report.py", "{root}", "--today", TODAY, "--weeks", "6", "--json"],
    "bugs-triage": ["skills/bugs-triage/scripts/triage.py", "{root}", "--json"],
    "next-feature-id": ["skills/feature-plan/scripts/next_id.py", "{root}"],
}


class GoldenScenarios(unittest.TestCase):
    def run_script(self, args, root):
        cmd = [sys.executable, str(KIT / args[0])] + [a.replace("{root}", str(root)) for a in args[1:]]
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError:
            return proc.stdout.strip().splitlines()      # a script that prints text, not JSON

    def test_scripts_match_their_golden_output(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            shutil.copytree(FIXTURE, root)
            for name, args in SCENARIOS.items():
                with self.subTest(scenario=name):
                    got = self.run_script(args, root)
                    path = GOLDEN / f"{name}.json"
                    text = json.dumps(got, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
                    if os.environ.get("UPDATE_GOLDEN"):
                        GOLDEN.mkdir(exist_ok=True)
                        path.write_text(text, encoding="utf-8")
                        continue
                    self.assertTrue(path.is_file(), f"{path.name} is missing: run with UPDATE_GOLDEN=1")
                    self.assertEqual(json.loads(path.read_text(encoding="utf-8")), got)

    def test_the_fixture_is_clean(self):
        # The golden files describe a healthy backlog: no data-integrity issue in either status report.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            shutil.copytree(FIXTURE, root)
            feats = self.run_script(SCENARIOS["features-status"], root)
            bugs = self.run_script(SCENARIOS["bugs-status"], root)
            for key in ("duplicate_numbers", "missing_feature_files", "orphan_feature_files", "bad_feature_headings",
                        "bad_planned_summaries", "missing_brief_links", "stale_dependency_notes"):
                self.assertEqual(feats[key], [], key)
            for key in ("duplicate_ids", "rows_missing_file", "files_without_row", "files_bad_h1", "fixed_missing_resolution"):
                self.assertEqual(bugs[key], [], key)


if __name__ == "__main__":
    unittest.main()
