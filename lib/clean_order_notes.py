#!/usr/bin/env python3
"""
Remove "blocked on #N" notes from the Recommended implementation order once #N has shipped.

features-archive deletes the archived rows and rewrites the dependency blocks, but the order
list also carries free-text notes ("- `x` (#2) — P3, blocked on #1 (logs its names), small")
that go stale the moment the prerequisite is archived. This rewrites only those bullets, only
the "blocked on/by" clause, and only for prerequisites listed in features-implemented.md.

Usage:
    python3 clean_order_notes.py <repo-root> [--dry-run]

Prints JSON: {"changed": [{"line": n, "before": "...", "after": "..."}], "written": bool}.
Idempotent: a second run changes nothing.
"""
import argparse
import os
import sys
from pathlib import Path

_here = Path(__file__).resolve()
for _cand in (_here.parent, _here.parents[3] / "lib"):
    if (_cand / "backlog_kit.py").is_file():
        sys.path.insert(0, str(_cand))
        break
import backlog_kit as bk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    cfg = bk.load_config(a.repo_root)
    p = bk.Paths(a.repo_root, cfg)
    _, impl_rows = bk.table_rows(p.features_implemented, "## Feature List")
    implemented = {r.get("#", "").strip() for r in impl_rows if r.get("#", "").strip()}
    lines = bk.read_lines(p.features_planned)
    if lines is None:
        bk.emit({"changed": [], "written": False, "note": "features-planned.md not found"})
        return
    bounds = bk.order_section_bounds(lines)
    changed = []
    if bounds:
        for i in range(*bounds):
            new = bk.clean_blocked_notes(lines[i], implemented)
            if new != lines[i]:
                changed.append({"line": i + 1, "before": lines[i], "after": new})
                lines[i] = new
    written = bool(changed) and not a.dry_run
    if written:
        text = "\n".join(lines) + "\n"
        tmp = Path(p.features_planned).with_suffix(".md.tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, p.features_planned)
    bk.emit({"changed": changed, "written": written})


if __name__ == "__main__":
    main()
