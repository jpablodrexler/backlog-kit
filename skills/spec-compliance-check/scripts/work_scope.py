#!/usr/bin/env python3
# VENDORED from lib/work_scope.py — do not edit here; edit the source and run `python3 tools/vendor.py`.
"""
What changed, and therefore which gates and reviews apply — the mechanical
half of the work skills' verification phases.

Reads the working tree via `git status` (untracked files included; see
gitread.changed_files for why not `git diff`), matches the changed paths
against each configured gate's / review's `when` globs, and prints JSON. Always
recompute it right before each verification step: fix rounds keep changing the
tree, so a cached snapshot goes stale.

Usage:
    python3 work_scope.py <repo-root> [--files a.py b/c.ts ...]

`--files` skips git and uses the given paths (for dry runs and tests). Files backlog-kit
itself writes (the backlog, reports and decisions folders, `.backlog-kit.toml`, installed
skills) are left out of `changed_files` and counted in `kit_files_ignored`.
"""
import argparse
import sys
from pathlib import Path

_here = Path(__file__).resolve()
for _cand in (_here.parent, _here.parents[3] / "lib"):
    if (_cand / "backlog_kit.py").is_file():
        sys.path.insert(0, str(_cand))
        break
import backlog_kit as bk
import gitread


def covers(gate, path):
    """True if a gate would exercise `path`: inside its cwd and matching its `when` globs."""
    cwd = (gate.get("cwd") or ".").strip("/")
    inside = cwd in ("", ".") or path == cwd or path.startswith(cwd + "/")
    return inside and bk.glob_match(path, gate.get("when") or ["**"])


def applies(entry, files):
    when = entry.get("when") or ["**"]
    hits = [f for f in files if bk.glob_match(f, when)]
    return bool(hits), hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root")
    ap.add_argument("--files", nargs="*")
    args = ap.parse_args()

    cfg = bk.load_config(args.repo_root)
    ignored = 0
    if args.files is not None:
        files = sorted(set(args.files))
    else:
        every = gitread.changed_files(args.repo_root)
        files = [f for f in every if not bk.glob_match(f, bk.kit_globs(cfg))]
        ignored = len(every) - len(files)

    gates = []
    for g in cfg["gates"]:
        ok, hits = applies(g, files)
        gates.append({
            "name": g.get("name", g.get("run", "")),
            "run": g.get("run", ""),
            "cwd": g.get("cwd", "."),
            "ask_before": g.get("ask_before", ""),
            "known_failures": g.get("known_failures", []),
            "timeout_minutes": g.get("timeout_minutes", 10),
            "applies": ok,
            "matched_files": hits[:20],
        })
    # With gates configured, a changed file that no gate covers is code nothing verified —
    # a green run must not read as "everything passed" when half the change was never tested.
    uncovered = [f for f in files if cfg["gates"] and not any(covers(g, f) for g in cfg["gates"])]
    reviews = []
    for r in cfg["reviews"]:
        ok, hits = applies(r, files)
        reviews.append({
            "name": r.get("name", ""), "focus": r.get("focus", ""), "skill": r.get("skill", ""),
            "applies": ok, "matched_files": hits[:20],
        })
    bk.emit({
        "changed_files": files,
        "kit_files_ignored": ignored,
        "gates": gates,
        "gates_configured": bool(cfg["gates"]),
        "uncovered_files": uncovered,
        "reviews": reviews,
        "review_max_rounds": cfg["work"]["review_max_rounds"],
        "gate_max_rounds": cfg["work"]["gate_max_rounds"],
        "reports_dir": cfg["paths"]["reports_dir"],
    })


if __name__ == "__main__":
    main()
