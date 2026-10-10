#!/usr/bin/env python3
"""
Remove "blocked on #N" notes from the Recommended implementation order once #N has shipped.

features-archive deletes the archived rows and rewrites the dependency blocks, but the order
list also carries free-text notes ("- `x` (#2) — P3, blocked on #1 (logs its names), small")
that go stale the moment the prerequisite is archived. This rewrites only those bullets, only
the "blocked on/by" clause, and only for prerequisites listed in features-implemented.md.

Usage:
    python3 clean_order_notes.py <repo-root> [--dry-run]

Prints JSON: {"changed": [{"line": n, "before": "...", "after": "..."}],
               "placeholder_restored": bool, "written": bool}.
It also restores the `_None yet._` placeholder when the list has no entries left (archiving
the last planned feature empties it, and an empty section with no placeholder is easy to
mistake for a truncated file). Idempotent: a second run changes nothing.
"""
import argparse
import os
import re
import sys
from pathlib import Path

_here = Path(__file__).resolve()
for _cand in (_here.parent, _here.parents[3] / "lib"):
    if (_cand / "backlog_kit.py").is_file():
        sys.path.insert(0, str(_cand))
        break
import backlog_kit as bk


PLACEHOLDER = "_None yet._"


def restore_placeholder(lines, heading, entry_regex):
    """Put `_None yet._` back under `heading` when its section has no entries and no placeholder."""
    start = next((i for i, ln in enumerate(lines) if ln.strip() == heading), None)
    if start is None:
        return False
    level = len(heading) - len(heading.lstrip("#"))
    end = len(lines)
    for i in range(start + 1, len(lines)):
        m = re.match(r"^(#+) ", lines[i])
        if m and len(m.group(1)) <= level:
            end = i
            break
    section = lines[start + 1:end]
    if any(re.match(entry_regex, ln) for ln in section) or any(ln.strip() == PLACEHOLDER for ln in section):
        return False
    idx = end
    while idx > start + 1 and lines[idx - 1].strip() == "":
        idx -= 1
    lines[idx:idx] = ["", PLACEHOLDER]
    return True


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
        bk.emit({"changed": [], "placeholder_restored": False, "written": False, "note": "features-planned.md not found"})
        return
    bounds = bk.order_section_bounds(lines)
    changed = []
    if bounds:
        for i in range(*bounds):
            new = bk.clean_blocked_notes(lines[i], implemented)
            if new != lines[i]:
                changed.append({"line": i + 1, "before": lines[i], "after": new})
                lines[i] = new
    restored = restore_placeholder(lines, "### Recommended implementation order",
                                   r"^\s*(?:-|\d+[.)])\s")
    # Archiving the last feature that had a dependency block empties that section too.
    restored_deps = restore_placeholder(lines, bk.HARD_DEPS_HEADING, r"^\s*\*\*Features?\s")
    restored = restored or restored_deps
    written = (bool(changed) or restored) and not a.dry_run
    if written:
        text = "\n".join(lines) + "\n"
        tmp = Path(p.features_planned).with_suffix(".md.tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, p.features_planned)
    bk.emit({"changed": changed, "placeholder_restored": restored, "written": written})


if __name__ == "__main__":
    main()
