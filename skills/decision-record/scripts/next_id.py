#!/usr/bin/env python3
"""
Next free ADR number — scans the configured decisions dir for the 4-digit
`NNNN-` filename prefix and takes max+1. One global sequence, never reused,
even for a later-superseded record.

Usage:
    python3 next_id.py <repo-root>
Prints JSON: {"next_number": "0004", "directory_exists": true, "directory": "docs/decisions"}
"""
import re
import sys
from pathlib import Path

_here = Path(__file__).resolve()
for _cand in (_here.parent, _here.parents[3] / "lib"):
    if (_cand / "backlog_kit.py").is_file():
        sys.path.insert(0, str(_cand))
        break
import backlog_kit as bk


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    cfg = bk.load_config(sys.argv[1])
    d = bk.Paths(sys.argv[1], cfg).decisions
    nums = []
    if d.exists():
        for f in d.glob("*.md"):
            m = re.match(r"^(\d{4})-", f.name)
            if m:
                nums.append(int(m.group(1)))
    n = (max(nums) + 1) if nums else 1
    bk.emit({"next_number": f"{n:04d}", "directory_exists": d.exists(),
             "directory": cfg["paths"]["decisions_dir"]})


if __name__ == "__main__":
    main()
