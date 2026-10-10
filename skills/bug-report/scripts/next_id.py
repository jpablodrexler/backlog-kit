#!/usr/bin/env python3
"""
Next free bug id (`<PREFIX>-NNN`, prefix from .backlog-kit.toml, default BUG)
plus the configured vocabulary. Scans both table files and the filenames in
the bugs/ folder, takes max+1, zero-padded to 3 digits. One global sequence,
never reused — not even for a Won't fix / Cannot reproduce entry.

Usage:
    python3 next_id.py <repo-root>
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
    root = sys.argv[1]
    cfg = bk.load_config(root)
    p = bk.Paths(root, cfg)
    prefix = re.escape(cfg["bugs"]["id_prefix"])
    nums = []
    for path in (p.bugs_open, p.bugs_fixed):
        if path.is_file():
            nums += [int(m) for m in re.findall(rf"{prefix}-(\d+)", path.read_text(encoding="utf-8"))]
    if p.bugs_dir.is_dir():
        for f in p.bugs_dir.glob(f"{cfg['bugs']['id_prefix']}-*.md"):
            m = re.match(rf"^{prefix}-(\d+)\.md$", f.name)
            if m:
                nums.append(int(m.group(1)))
    n = (max(nums) + 1) if nums else 1
    bk.emit({
        "next_id": f"{cfg['bugs']['id_prefix']}-{n:03d}",
        "vocab": {k: cfg["bugs"][k] for k in ("severities", "environments")},
    })


if __name__ == "__main__":
    main()
