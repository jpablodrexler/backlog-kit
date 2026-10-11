#!/usr/bin/env python3
"""
Copy the kit's skills into a project's .claude/skills/ (the no-plugin install).

    python3 tools/install.py <repo-root>                      # the core skills
    python3 tools/install.py <repo-root> --extras code-reviewer,docs-sync   # core + chosen extras
    python3 tools/install.py <repo-root> --all                # core + every extra
    python3 tools/install.py <repo-root> --force              # overwrite skills already there
    python3 tools/install.py <repo-root> --only bug-fix,bugs-next   # exactly these

Refuses to overwrite an existing skill directory without --force, because a
project's own skill of the same name would otherwise be replaced silently.
Each skill is self-contained (see tools/vendor.py), so nothing else is needed.
"""
import argparse
import shutil
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
SKILLS = KIT / "skills"
EXTRAS = KIT / "extras"


def available(root):
    return sorted(p.name for p in root.iterdir() if (p / "SKILL.md").is_file())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", default="", help="exactly these skills (core or extras)")
    ap.add_argument("--extras", default="", help="the core skills plus these extras")
    ap.add_argument("--all", action="store_true", help="the core skills plus every extra")
    a = ap.parse_args()
    core, extras = available(SKILLS), available(EXTRAS)
    where = {n: SKILLS for n in core} | {n: EXTRAS for n in extras}
    if a.only:
        names = [n for n in a.only.split(",") if n]
    else:
        wanted = extras if a.all else [n for n in a.extras.split(",") if n]
        names = core + wanted
    unknown = [n for n in names if n not in where]
    if unknown:
        sys.exit(f"unknown skill(s): {', '.join(unknown)}")
    dest = Path(a.repo_root) / ".claude" / "skills"
    clash = [n for n in names if (dest / n).exists()]
    if clash and not a.force:
        sys.exit("already present (use --force to overwrite): " + ", ".join(clash))
    for n in names:
        target = dest / n
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(where[n] / n, target, ignore=shutil.ignore_patterns("__pycache__"))
    print(f"installed {len(names)} skill(s) into {dest}")


if __name__ == "__main__":
    main()
