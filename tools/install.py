#!/usr/bin/env python3
"""
Copy the kit's skills into a project's .claude/skills/ (the no-plugin install).

    python3 tools/install.py <repo-root>            # copy every skill
    python3 tools/install.py <repo-root> --force    # overwrite skills already there
    python3 tools/install.py <repo-root> --only bug-fix,bugs-batch-fix

Refuses to overwrite an existing skill directory without --force, because a
project's own skill of the same name would otherwise be replaced silently.
Each skill is self-contained (see tools/vendor.py), so nothing else is needed.
"""
import argparse
import shutil
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / "skills"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    names = sorted(p.name for p in SKILLS.iterdir() if (p / "SKILL.md").is_file())
    if a.only:
        want = [n for n in a.only.split(",") if n]
        unknown = [n for n in want if n not in names]
        if unknown:
            sys.exit(f"unknown skill(s): {', '.join(unknown)}")
        names = want
    dest = Path(a.repo_root) / ".claude" / "skills"
    clash = [n for n in names if (dest / n).exists()]
    if clash and not a.force:
        sys.exit("already present (use --force to overwrite): " + ", ".join(clash))
    for n in names:
        target = dest / n
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(SKILLS / n, target, ignore=shutil.ignore_patterns("__pycache__"))
    print(f"installed {len(names)} skill(s) into {dest}")


if __name__ == "__main__":
    main()
