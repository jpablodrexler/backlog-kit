#!/usr/bin/env python3
"""
Tags and releases the version in .claude-plugin/plugin.json: the annotated tag
(`backlog-kit <version>`), its push, and the GitHub release (title equal to the tag, body the
matching CHANGELOG.md section).

    python3 tools/release.py [--dry-run] [--yes]

Run it from a PC with git and the GitHub CLI (`gh auth login` done). It needs a clean `main`,
fast-forwards it from origin, and stops if the tag already exists, locally or on origin.
Without `gh` it creates and pushes the tag and prints the title and notes to paste on GitHub.
--dry-run prints the steps and changes nothing. --yes skips the confirmation question.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_version(root):
    return json.loads((Path(root) / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]


def changelog_section(text, version):
    """The body of the `## <version>` section, up to the next `## `, or None when there is none."""
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if re.fullmatch(rf"##\s+{re.escape(version)}\s*", l)), None)
    if start is None:
        return None
    body = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body).strip() or None


def git(root, *args, check=True):
    p = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8")
    if check and p.returncode:
        sys.exit(f"git {' '.join(args)} failed: {(p.stderr or p.stdout).strip()}")
    return p.stdout.strip()


def step(dry, text, root, *cmd):
    print(f"> {text}")
    if dry:
        return
    p = subprocess.run(cmd, cwd=root)
    if p.returncode:
        sys.exit(f"Failed: {text}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", action="store_true", help="do not ask for confirmation")
    ap.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    args = ap.parse_args()
    root = Path(args.root)

    if not shutil.which("git"):
        sys.exit("git is not on PATH.")
    if git(root, "status", "--porcelain"):
        sys.exit("There are uncommitted changes. Commit or discard them first.")

    git(root, "fetch", "origin", "main", "--tags", "--force")
    git(root, "checkout", "main")
    git(root, "merge", "--ff-only", "origin/main")

    version = read_version(root)
    tag = f"v{version}"
    print(f"Version: {version} (tag {tag}, commit {git(root, 'rev-parse', '--short', 'HEAD')})")
    if git(root, "tag", "--list", tag):
        sys.exit(f"The tag {tag} already exists locally.")
    if git(root, "ls-remote", "--tags", "origin", f"refs/tags/{tag}"):
        sys.exit(f"The tag {tag} already exists on origin.")

    notes = changelog_section((root / "CHANGELOG.md").read_text(encoding="utf-8"), version)
    if not notes:
        sys.exit(f"CHANGELOG.md has no non-empty '## {version}' section.")
    print(f"\nRelease notes:\n{'-' * 40}\n{notes}\n{'-' * 40}\n")

    if not (args.dry_run or args.yes) and input(f"Create tag {tag} and the release? (y/N) ").strip().lower() not in ("y", "yes", "s", "si"):
        sys.exit("Cancelled.")

    step(args.dry_run, f"git tag -a {tag} -m 'backlog-kit {version}'", root, "git", "tag", "-a", tag, "-m", f"backlog-kit {version}")
    step(args.dry_run, f"git push origin {tag}", root, "git", "push", "origin", tag)
    if shutil.which("gh"):
        with tempfile.TemporaryDirectory() as d:
            notes_file = Path(d) / "notes.md"
            notes_file.write_text(notes + "\n", encoding="utf-8")
            step(args.dry_run, f"gh release create {tag} --title {tag} --notes-file <notes>", root,
                 "gh", "release", "create", tag, "--title", tag, "--notes-file", str(notes_file), "--verify-tag")
    else:
        print(f"\n`gh` is not installed: create the release on GitHub with tag {tag}, title {tag} and the notes above.")
    print("\n(dry run: nothing was created)" if args.dry_run else f"\nDone: {tag}")


if __name__ == "__main__":
    main()
