#!/usr/bin/env python3
"""
Read-only check for replacing a project's own workflow skills with backlog-kit's.

    python3 tools/migrate_check.py <repo-root>

It changes nothing. It reports, for the repository at <repo-root>:
  1. which of its `.claude/skills/` directories backlog-kit replaces (candidates to delete);
  2. which other tracked files still mention a skill that would be deleted (to review before deleting);
  3. where the backlog lives and the `.backlog-kit.toml` that points to it, if one is needed;
  4. which `.backlog-kit/` folders exist and how many files each holds;
  5. whether OpenSpec's folder is there (feature-development needs it);
  6. whether `develop` already contains `.backlog-kit/` (the pipelines cut their branches from it).
MIGRATING.md explains how to act on each section.
"""
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "lib"))
import gitread  # noqa: E402

# Project skill name -> the kit skill that replaces it.
REPLACES = {n: n for n in (
    "feature-plan", "features-next", "features-status", "features-archive",
    "bug-report", "bugs-next", "bugs-status", "bugs-archive", "decision-record",
    "feature-development", "bug-fix", "features-batch-development", "bugs-batch-fix",
    "gitflow", "code-reviewer", "security-reviewer", "database-reviewer",
    "spec-compliance-check", "dependency-upgrade")}
REPLACES["web-docs-sync"] = "docs-sync"

# kit folder under .backlog-kit/ -> (what reads it, whether most projects need it)
FOLDERS = {
    "feature": ("feature-development: phases after implementing", True),
    "bug": ("bug-fix: phases after the fix", True),
    "release": ("gitflow: before a release or hotfix is pushed", False),
    "review/code": ("code-reviewer checklists", True),
    "review/security": ("security-reviewer checklists", True),
    "review/database": ("database-reviewer checklists", False),
    "spec-compliance": ("spec-compliance-check notes", False),
    "docs": ("docs-sync map of doc sections to their source", True),
    "dependency-upgrade": ("dependency-upgrade notes", False),
}
SKIP = re.compile(r"(^|/)(node_modules|\.git)/|package-lock\.json$|(^|/)openspec/changes/archive/|"
                  r"(^|/)docs/(reports|decisions|backlog|explorations)/|\.backlog-kit/")


def tracked(root):
    out = gitread.git(root, "ls-files", "-z", check=False)
    return [p for p in out.split("\0") if p]


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1]).resolve()
    skills_dir = root / ".claude" / "skills"
    present = sorted(n for n in REPLACES if (skills_dir / n).is_dir())

    print(f"# backlog-kit migration check: {root}\n")
    print("## 1. Project skills the kit replaces (candidates to delete)")
    if present:
        for n in present:
            alias = "" if REPLACES[n] == n else f"  (the kit calls it `{REPLACES[n]}`)"
            print(f"- {n}{alias}")
    else:
        print("- none found under .claude/skills/")

    print("\n## 2. Other files that mention a skill you would delete (review before deleting)")
    names = sorted(set(present) | {"web-docs-sync"} & set(present))
    hits = []
    if names:
        pat = re.compile(r"(?<![\w-])(" + "|".join(re.escape(n) for n in names) + r")(?![\w-])")
        gone = tuple(f".claude/skills/{n}/" for n in names)
        for rel in tracked(root):
            if rel.startswith(gone) or SKIP.search(rel) or not rel.endswith((".md", ".json", ".yml", ".yaml", ".sh", ".py", ".xml", ".toml")):
                continue
            try:
                text = (root / rel).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            found = pat.findall(text)
            if found:
                hits.append((len(found), rel, sorted(set(found))))
    for n, rel, found in sorted(hits, reverse=True)[:40]:
        print(f"- {rel}: {n} mention(s) of {', '.join(found)}")
    if not hits:
        print("- none")

    print("\n## 3. Backlog location")
    found_dirs = sorted({str(Path(p).parent) for p in tracked(root)
                         if p.endswith(("/features-planned.md", "/bugs-open.md")) or p in ("features-planned.md", "bugs-open.md")})
    if not found_dirs:
        print("- no features-planned.md / bugs-open.md tracked yet: the defaults apply (docs/backlog)")
    for d in found_dirs:
        if d == "docs/backlog":
            print(f"- {d}: the default, no .backlog-kit.toml needed")
        else:
            print(f"- {d}: create .backlog-kit.toml with\n    [paths]\n    backlog_dir = \"{d}\"")
    if (root / ".backlog-kit.toml").is_file():
        print("- .backlog-kit.toml exists (only [paths] backlog_dir is read; other sections are ignored)")

    print("\n## 4. Project files under .backlog-kit/")
    base = root / ".backlog-kit"
    for folder, (what, common) in FOLDERS.items():
        n = len(list((base / folder).glob("*.md"))) if (base / folder).is_dir() else 0
        flag = "ok" if n else ("MISSING — most projects need it" if common else "none (optional)")
        print(f"- {folder}/: {n} file(s) — {what} [{flag}]")

    print("\n## 5. OpenSpec")
    print("- openspec/ present" if (root / "openspec").is_dir() else "- openspec/ not found: feature-development needs the OpenSpec CLI and openspec/changes")

    print("\n## 6. Base branch")
    if gitread.ok(root, "rev-parse", "--verify", "--quiet", "develop"):
        if gitread.ok(root, "rev-parse", "--verify", "--quiet", "develop:.backlog-kit"):
            print("- develop contains .backlog-kit/: feature and fix branches cut from it will have your phase files")
        else:
            print("- WARNING develop does not contain .backlog-kit/ yet. feature-development and bug-fix cut their branch from develop,\n"
                  "  so on that branch the kit's skills and your phase files are gone (the old skills come back). Merge the migration\n"
                  "  into develop first, or start from a branch cut from the migration and pass --skip-branch-setup.")
    else:
        print("- no local develop branch: gitflow will create it from main on first use")


if __name__ == "__main__":
    main()
