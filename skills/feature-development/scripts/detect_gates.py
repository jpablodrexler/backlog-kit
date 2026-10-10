#!/usr/bin/env python3
# VENDORED from lib/detect_gates.py — do not edit here; edit the source and run `python3 tools/vendor.py`.
"""
Propose verification gates by sniffing the repo for a build/test setup — so a
project with no `[[gates]]` configured can say "yes" once instead of writing TOML.

Looks in the repo root and down to three levels of subfolders (`frontend/`, `backend/`,
or `Product/backend/`), skipping dependency and build folders. A module nested under a
folder that already provides the same tool is skipped — a multi-module Maven or workspace
root covers its children. Prints JSON plus a ready-to-paste `[[gates]]` block.
It only proposes; the work skills ask the user to confirm before saving anything.

Usage:
    python3 detect_gates.py <repo-root>
"""
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {"node_modules", ".git", "dist", "build", "target", "bin", "obj", "vendor", ".venv", "venv", "__pycache__"}


MAX_DEPTH = 3


def candidates(root, depth=0, rel=""):
    """Yield (directory, relative-path-string) for the root and every folder up to MAX_DEPTH deep."""
    yield root, rel or "."
    if depth >= MAX_DEPTH:
        return
    for d in sorted(root.iterdir()):
        if d.is_dir() and d.name not in SKIP_DIRS and not d.name.startswith("."):
            yield from candidates(d, depth + 1, f"{rel}/{d.name}" if rel else d.name)


def node_gates(d, cwd):
    pkg = d / "package.json"
    if not pkg.is_file():
        return []
    try:
        scripts = json.loads(pkg.read_text(encoding="utf-8")).get("scripts", {})
    except (ValueError, OSError):
        return []
    if (d / "pnpm-lock.yaml").is_file():
        run = "pnpm"
    elif (d / "yarn.lock").is_file():
        run = "yarn"
    else:
        run = "npm"
    out = []
    for key, name in (("lint", "lint"), ("typecheck", "typecheck"), ("test", "tests"), ("build", "build")):
        if key in scripts:
            cmd = f"{run} test" if key == "test" and run == "npm" else f"{run} run {key}"
            out.append({"name": name if cwd == "." else f"{name} ({cwd})", "run": cmd, "cwd": cwd, "kind": "node"})
    return out


def single(d, cwd, marker, name, run, pattern=None, kind=None):
    files = [f for f in d.glob(marker)] if any(c in marker for c in "*?") else ([d / marker] if (d / marker).is_file() else [])
    if not files:
        return []
    if pattern and not any(re.search(pattern, f.read_text(encoding="utf-8", errors="ignore")) for f in files):
        return []
    return [{"name": name if cwd == "." else f"{name} ({cwd})", "run": run, "cwd": cwd, "kind": kind or run.split()[0]}]


def detect(root):
    root = Path(root)
    gates, claimed = [], []          # claimed: (relative dir, kind) already covered by an ancestor
    for d, cwd in candidates(root):
        found = node_gates(d, cwd)
        found += single(d, cwd, "pytest.ini", "tests", "pytest", kind="python")
        found += single(d, cwd, "pyproject.toml", "tests", "pytest", r"pytest", kind="python")
        found += single(d, cwd, "tox.ini", "tests", "pytest", r"pytest", kind="python")
        found += single(d, cwd, "pom.xml", "tests", "mvn -q test", kind="maven")
        found += single(d, cwd, "build.gradle*", "tests", "./gradlew test", kind="gradle")
        found += single(d, cwd, "*.sln", "tests", "dotnet test", kind="dotnet")
        found += single(d, cwd, "go.mod", "tests", "go test ./...", kind="go")
        found += single(d, cwd, "Cargo.toml", "tests", "cargo test", kind="cargo")
        found += single(d, cwd, "Makefile", "tests", "make test", r"^test\s*:", kind="make")
        for g in found:
            covered = any(g["kind"] == k and (c == "." or cwd == c or cwd.startswith(c + "/")) for c, k in claimed)
            if not covered:
                gates.append(g)
        claimed += [(cwd, g["kind"]) for g in found]
    seen, unique = set(), []
    for g in gates:
        key = (g["run"], g["cwd"])
        if key not in seen:
            seen.add(key)
            unique.append({k: v for k, v in g.items() if k != "kind"})
    return unique


def to_toml(gates):
    blocks = []
    for g in gates:
        lines = ["[[gates]]", f'name = "{g["name"]}"', f'run  = "{g["run"]}"']
        if g["cwd"] != ".":
            lines.append(f'cwd  = "{g["cwd"]}"')
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    gates = detect(sys.argv[1])
    print(json.dumps({"gates": gates, "toml": to_toml(gates)}, indent=2))


if __name__ == "__main__":
    main()
