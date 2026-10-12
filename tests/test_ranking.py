"""The rank scripts order a backlog the way the backlog rules say."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]

PLANNED = """# Planned Features

## Feature List

| # | Change name | Priority | Schema Change | Effort | Area | SDD Artifacts | Implementation | Summary | Brief |
| - | ----------- | -------- | ------------- | ------ | ---- | ------------- | -------------- | ------- | ----- |
| 1 | `alpha` | P2 | No | M | Backend | ⬜ Pending | ⬜ Pending | a | [brief](features/001-alpha.md) |
| 2 | `beta` | P1 | Yes | S | Frontend | ✅ Created | ⬜ Pending | b | [brief](features/002-beta.md) |
| 3 | `gamma` | P2 | No | L | Backend | ⬜ Pending | 🔶 In Progress | c | [brief](features/003-gamma.md) |
| 4 | `delta` | P2 | Yes | S | Backend | ⬜ Pending | ⬜ Pending | d | [brief](features/004-delta.md) |
| 5 | `eps` | P1 | No | S | Backend | ⬜ Pending | ⬜ Pending | e | [brief](features/005-eps.md) |

## Dependencies

### Hard implementation dependencies

**Feature 5 → Feature 2** (still pending)

blocked until beta ships

### Recommended implementation order

- `delta` (#4)
- `alpha` (#1)
"""
IMPLEMENTED = """# Implemented Features

## Feature List

| # | Change name | Priority | Schema Change | Effort | Area | Details |
| - | ----------- | -------- | ------------- | ------ | ---- | ------- |
| 7 | `old` | P1 | No | S | Backend | [brief](features/007-old.md) |
"""
BUGS = """# Open Bugs

## Bug List

| Bug ID | Severity | Area | Environment | Status | Fix | Summary |
| ------ | -------- | ---- | ----------- | ------ | --- | ------- |
| [BUG-001](bugs/BUG-001.md) | S2 | Backend | local | ⬜ Open | | one |
| [BUG-002](bugs/BUG-002.md) | S2 | Backend | prod | ⬜ Open | | two |
| [BUG-003](bugs/BUG-003.md) | S3 | Backend | local | 🔶 In Progress | | three |
| [BUG-004](bugs/BUG-004.md) | S2 | Backend | local | ⬜ Open | | four |

## Recommended fix order

- BUG-004 — x
- BUG-001 — y
"""


def project(tmp):
    root = Path(tmp)
    (root / "docs/backlog/features").mkdir(parents=True)
    (root / "docs/backlog/bugs").mkdir(parents=True)
    (root / "docs/backlog/features-planned.md").write_text(PLANNED)
    (root / "docs/backlog/features-implemented.md").write_text(IMPLEMENTED)
    (root / "docs/backlog/bugs-open.md").write_text(BUGS)
    for n in range(1, 5):
        (root / f"docs/backlog/bugs/BUG-00{n}.md").write_text(f"# BUG-00{n}\n\n- **Notes:** none\n")
    return root


def run(script, root, *args):
    return json.loads(subprocess.run([sys.executable, str(script), str(root), *args], capture_output=True, text=True, check=True).stdout)


class RankScripts(unittest.TestCase):
    def test_features_next_ranks_in_progress_first(self):
        with tempfile.TemporaryDirectory() as d:
            root = project(d)
            kit = run(KIT / "skills/features-next/scripts/rank_features.py", root, "--json")
            self.assertEqual(kit["top"]["name"], "gamma")                  # in progress beats everything
            self.assertEqual([c["name"] for c in kit["blocked"]], ["eps"])

    def test_bugs_next_ranks_by_tier_and_order(self):
        with tempfile.TemporaryDirectory() as d:
            root = project(d)
            kit = run(KIT / "skills/bugs-next/scripts/rank_bugs.py", root, "--json")
            self.assertEqual([kit["top"]["id"]] + [r["id"] for r in kit["runners_up"]], ["BUG-003", "BUG-002", "BUG-004", "BUG-001"])
            self.assertEqual(kit["top"]["score"], 1000 + 200 + 5)
            self.assertEqual([r["score"] for r in kit["runners_up"]], [325, 315, 315])

    def test_a_bug_marked_schema_change_loses_the_tier_4_bonus(self):
        with tempfile.TemporaryDirectory() as d:
            root = project(d)
            (root / "docs/backlog/bugs/BUG-001.md").write_text("# BUG-001\n\n- **Schema change:** yes — adds a column\n")
            kit = run(KIT / "skills/bugs-next/scripts/rank_bugs.py", root, "--json")
            scores = {r["id"]: r["score"] for r in [kit["top"]] + kit["runners_up"]}
            self.assertEqual(scores["BUG-001"], scores["BUG-004"] - 5)       # same tier and order bonus, but no tier 4



if __name__ == "__main__":
    unittest.main()
