#!/usr/bin/env python3
# VENDORED from lib/task_state.py — do not edit here; edit the source and run `python3 tools/vendor.py`.
"""
Where a change's task list stands — the mechanical half of the "are all tasks done?" check that
the implement and close phases both make.

    python3 task_state.py <repo-root> --change <change-name>

Prints JSON: {found, total, done, unchecked: [titles], manual: [{title, command}], blocking: [titles]}.

A task that needs a human step (a generated secret, a deploy, a device) is left unchecked and
carries a `(manual: <what to run>)` marker in its line. Those are listed in `manual` and never in
`blocking`: the work is finished, a person still has something to run. Every other unchecked task
is `blocking` — the change is not done.
"""
import argparse
import re
import sys
from pathlib import Path

_here = Path(__file__).resolve()
for _cand in (_here.parent, _here.parents[3] / "lib"):
    if (_cand / "backlog_kit.py").is_file():
        sys.path.insert(0, str(_cand))
        break
import backlog_kit as bk

TASK = re.compile(r"^\s*[-*]\s*\[( |x|X)\]\s*(.+?)\s*$")
MANUAL = re.compile(r"\(manual:\s*(.+?)\)\s*$", re.I)


def task_state(root, cfg, change):
    path = Path(root) / cfg["spec"]["changes_dir"] / change / "tasks.md"
    lines = bk.read_lines(path)
    if lines is None:
        return {"found": False, "total": 0, "done": 0, "unchecked": [], "manual": [], "blocking": []}
    total = done = 0
    unchecked, manual, blocking = [], [], []
    for ln in lines:
        m = TASK.match(ln)
        if not m:
            continue
        total += 1
        if m.group(1) in "xX":
            done += 1
            continue
        title = m.group(2)
        unchecked.append(title)
        mm = MANUAL.search(title)
        if mm:
            manual.append({"title": MANUAL.sub("", title).strip(), "command": mm.group(1)})
        else:
            blocking.append(title)
    return {"found": True, "total": total, "done": done, "unchecked": unchecked, "manual": manual, "blocking": blocking}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root")
    ap.add_argument("--change", required=True)
    a = ap.parse_args()
    bk.emit(task_state(a.repo_root, bk.load_config(a.repo_root), a.change))


if __name__ == "__main__":
    main()
