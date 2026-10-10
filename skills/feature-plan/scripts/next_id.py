#!/usr/bin/env python3
"""
Next free feature number + change-name collision check, plus the configured
vocabulary — feature-plan step 3/4's mechanical work. Scans both backlog
files' `#` columns and the `features/NNN-<name>.md` filenames (one global
sequence, never reused) and takes max+1.

Usage:
    python3 next_id.py <repo-root> [--check-name <kebab-case-name>]
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


def table_numbers_and_names(path):
    _, rows = bk.table_rows(path, "## Feature List")
    nums, names = [], []
    for r in rows:
        n = r.get("#", "").strip()
        if n.isdigit():
            nums.append(int(n))
            names.append(bk.strip_backticks(r.get("Change name", "")))
    return nums, names


def file_numbers_and_names(features_dir):
    nums, names = [], []
    if features_dir.is_dir():
        for f in features_dir.glob("*.md"):
            m = re.match(r"^(\d+)-(.+)\.md$", f.name)
            if m:
                nums.append(int(m.group(1)))
                names.append(m.group(2))
    return nums, names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root")
    ap.add_argument("--check-name")
    args = ap.parse_args()

    cfg = bk.load_config(args.repo_root)
    p = bk.Paths(args.repo_root, cfg)
    np_, nm_p = table_numbers_and_names(p.features_planned)
    ni, nm_i = table_numbers_and_names(p.features_implemented)
    nf, nm_f = file_numbers_and_names(p.features_dir)

    allnums = np_ + ni + nf
    result = {
        "next_number": (max(allnums) + 1) if allnums else 1,
        "vocab": {
            "priorities": cfg["features"]["priorities"],
            "efforts": cfg["features"]["efforts"],
            "areas": cfg["features"]["areas"],
            "spec_workflow": cfg["spec"]["workflow"],
        },
        "planned_header": bk.planned_header(cfg),
    }
    if args.check_name:
        result["name_collision"] = args.check_name in set(nm_p) | set(nm_i) | set(nm_f)
    bk.emit(result)


if __name__ == "__main__":
    main()
