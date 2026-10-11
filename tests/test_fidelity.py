"""The pilot's guarantees: the ledgers are complete, and the kit's scripts agree with the originals."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
BASE = KIT / "fidelity/base"

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


class LedgersAreComplete(unittest.TestCase):
    @unittest.skipUnless(BASE.is_dir(), "originals not fetched (see fidelity/SOURCES.md)")
    def test_every_difference_from_the_originals_is_on_record(self):
        proc = subprocess.run([sys.executable, str(KIT / "tools/fidelity.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_every_decision_a_ledger_cites_exists(self):
        decided = {l.split("|")[1].strip() for l in (KIT / "fidelity/decisions.md").read_text().splitlines() if l.startswith("| D")}
        import re
        for ledger in (KIT / "fidelity/ledgers").glob("*.md"):
            for d in re.findall(r"\b(D\d+)\b", ledger.read_text()):
                with self.subTest(ledger=ledger.name, decision=d):
                    self.assertIn(d, decided)


@unittest.skipUnless(BASE.is_dir(), "originals not fetched (see fidelity/SOURCES.md)")
class ScriptsAgreeWithTheOriginals(unittest.TestCase):
    """The kit's rank scripts are the originals plus a few edited lines; on the same backlog they must agree."""

    def test_features_next_ranks_like_the_original(self):
        with tempfile.TemporaryDirectory() as d:
            root = project(d)
            orig = run(BASE / "pablo-web/features-next/scripts/rank_features.py", root, "--json")
            kit = run(KIT / "skills/features-next/scripts/rank_features.py", root, "--json")
            kit.pop("has_sdd")
            self.assertEqual(orig, kit)
            self.assertEqual(kit["top"]["name"], "gamma")                  # in progress beats everything
            self.assertEqual([c["name"] for c in kit["blocked"]], ["eps"])

    def test_bugs_next_ranks_like_the_original(self):
        with tempfile.TemporaryDirectory() as d:
            root = project(d)
            kit = run(KIT / "skills/bugs-next/scripts/rank_bugs.py", root, "--json")
            # The only intended differences: the rest of the file layout (paths come from the config) and the
            # schema flag, which the original read with a regex; with no schema bug, scores and order agree.
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
