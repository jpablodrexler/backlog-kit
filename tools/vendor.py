#!/usr/bin/env python3
"""
Make every skill self-contained by copying the shared sources into it.

A skill must work when installed alone (copied into .claude/skills/ without the
rest of the kit), so it can't import from a sibling `lib/` or read a sibling
`shared/` folder. The single sources of truth stay in `lib/` and `shared/`; this
tool writes marked copies into each skill, and `--check` (run in CI and by the
test suite) fails if any copy has drifted or is missing. Edit the sources, never
the copies.

    python3 tools/vendor.py           # write / refresh every copy
    python3 tools/vendor.py --check   # exit 1 if any copy is stale or missing
"""
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
SKILLS = KIT / "skills"

CORE = ["feature-plan", "features-next", "features-status", "bug-report",
        "bugs-next", "bugs-status", "decision-record"]          # scripts need the config/table lib
WORK = ["bug-fix", "feature-development"]                         # also need git helpers + shared phases
BATCH = ["bugs-batch-fix", "features-batch-development"]          # loop over WORK skills; need list/report/branch helpers

LIB_FOR = {
    "backlog_kit.py": CORE + WORK + BATCH,
    "gitread.py": WORK + BATCH,
    "branch_state.py": WORK + BATCH,
    "work_scope.py": WORK + BATCH,
    "detect_gates.py": WORK,
    "batch_plan.py": BATCH,
    "batch_report.py": BATCH,
}

SHARED_FOR = {
    "phase-branch.md": WORK,
    "phase-reviews.md": WORK,
    "phase-gates.md": WORK,
    "pipeline-guardrails.md": WORK + BATCH,
    "batch-runner.md": BATCH,
}


def marked(src, text):
    note = f"VENDORED from {src} — do not edit here; edit the source and run `python3 tools/vendor.py`."
    if src.endswith(".py"):
        lines = text.split("\n", 1)
        if lines[0].startswith("#!"):
            return lines[0] + "\n# " + note + "\n" + (lines[1] if len(lines) > 1 else "")
        return "# " + note + "\n" + text
    return f"<!-- {note} -->\n" + text


def expected():
    out = {}
    for name, skills in LIB_FOR.items():
        text = (KIT / "lib" / name).read_text(encoding="utf-8")
        for s in skills:
            out[SKILLS / s / "scripts" / name] = marked(f"lib/{name}", text)
    for md in sorted((KIT / "shared").glob("*.md")):
        text = md.read_text(encoding="utf-8")
        for s in SHARED_FOR[md.name]:
            out[SKILLS / s / "reference" / md.name] = marked(f"shared/{md.name}", text)
    return out


def main():
    check = "--check" in sys.argv[1:]
    stale = []
    for path, text in expected().items():
        current = path.read_text(encoding="utf-8") if path.is_file() else None
        if current != text:
            stale.append(path)
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
    rel = [str(p.relative_to(KIT)) for p in stale]
    if check:
        if rel:
            print("stale or missing vendored copies (run `python3 tools/vendor.py`):\n  " + "\n  ".join(rel))
            sys.exit(1)
        print("vendored copies are up to date")
    else:
        print(f"updated {len(rel)} file(s)" + ("\n  " + "\n  ".join(rel) if rel else ""))


if __name__ == "__main__":
    main()
