#!/usr/bin/env python3
"""
Print the `[spec]` link a features-archive row needs, computed from the real directory layout.

The link is relative to the backlog directory, so it depends on how deep `paths.backlog_dir` is
and where `spec.changes_dir` lives; a hand-written `../../` is only right for one layout.

Usage:
    python3 spec_link.py <repo-root> <change-name>
Prints JSON: {"link": "../../openspec/changes/archive/2026-10-09-x/proposal.md", "exists": true,
              "archive_dir": "2026-10-09-x"}
`exists` is false when the change has not been archived yet (the link is then built from today's date).
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve()
for _cand in (_here.parent, _here.parents[3] / "lib"):
    if (_cand / "backlog_kit.py").is_file():
        sys.path.insert(0, str(_cand))
        break
import backlog_kit as bk


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    root, name = sys.argv[1], sys.argv[2]
    bk.emit(bk.spec_link(root, bk.load_config(root), name))


if __name__ == "__main__":
    main()
