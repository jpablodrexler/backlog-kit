#!/usr/bin/env python3
"""
Create the feature backlog files if they don't exist yet — features-planned.md
and features-implemented.md under the configured backlog dir — with the table
headers and Column legend generated from .backlog-kit.toml (so the file's
legend and the scripts' vocabulary can never disagree). Idempotent: an
existing file is never touched.

If an existing features-planned.md has a table header that disagrees with `spec.workflow`
(an `SDD Artifacts` column present under "none", or missing under "openspec" — e.g. the
config was changed after the file was created) it is reported as `planned_header_mismatch`,
because a new row built for the configured header would land in the wrong columns. Pass
`--fix-header` to repair it losslessly (adds a `⬜ Pending` cell per row, or drops the column).

Usage:
    python3 scaffold.py <repo-root> [--fix-header]
Prints JSON: {"created": [...], "existing": [...], "planned_header_mismatch": {...}?, "header_fixed": {...}?}
"""
import sys
from pathlib import Path

_here = Path(__file__).resolve()
for _cand in (_here.parent, _here.parents[3] / "lib"):
    if (_cand / "backlog_kit.py").is_file():
        sys.path.insert(0, str(_cand))
        break
import backlog_kit as bk


def table(header):
    return ("| " + " | ".join(header) + " |\n"
            "| " + " | ".join("-" * max(3, len(h)) for h in header) + " |\n")


def planned_md(cfg):
    f = cfg["features"]
    prio = " · ".join(f"`{p}` ({f['priority_labels'].get(p, '')})".replace(" ()", "") for p in f["priorities"])
    effort = " / ".join(f"`{e}`" for e in f["efforts"])
    area = " · ".join(f"`{a}`" for a in f["areas"])
    spec = cfg["spec"]["workflow"] == "openspec"
    lines = [
        "# Planned Features", "",
        "## Feature List", "",
        table(bk.planned_header(cfg)).rstrip("\n"), "",
        "## Column legend", "",
        f"- **Priority**: {prio}",
        f"- **Effort**: {effort}",
        f"- **Area**: {area}",
    ]
    if spec:
        lines.append("- **SDD Artifacts**: `⬜ Pending` until the OpenSpec proposal/specs/tasks exist for the change; `✅ Created` once they do")
    lines += [
        "- **Implementation**: `⬜ Pending` until work starts; `🔶 In Progress` once someone (or a work skill) has started it; the row is removed by `features-archive` when it ships",
        "- **Summary**: a short hand-written one- or two-sentence summary of the brief (at most 250 characters, no pipes) — for humans and for `features-next`'s display, never spec input",
        "- **Brief**: link to the feature's full brief, `features/NNN-<change-name>.md` (`NNN` = zero-padded feature number). The file never moves; planned vs. implemented is decided only by which table holds the row",
        "",
        "## Dependencies", "",
        "### Hard implementation dependencies", "",
        "_None yet._", "",
        "### Recommended implementation order", "",
        "Priority tier first, then hard dependencies, then feature number. Not a schedule — a reasoning aid for `features-next` and for whoever picks the next feature by hand. A plain bullet list: list position (not a printed number) encodes order, so inserting an entry never touches any other line.", "",
        "_None yet._", "",
    ]
    return "\n".join(lines)


def implemented_md(cfg):
    return "\n".join([
        "# Implemented Features", "",
        "## Feature List", "",
        table(bk.IMPLEMENTED_HEADER).rstrip("\n"), "",
        "## Dependencies (Historical)", "",
        "### Implementation notes", "",
        "_None yet._", "",
    ])


def main():
    args = [a for a in sys.argv[1:] if a != "--fix-header"]
    fix_header = "--fix-header" in sys.argv[1:]
    if len(args) != 1:
        raise SystemExit(__doc__)
    root = args[0]
    cfg = bk.load_config(root)
    p = bk.Paths(root, cfg)
    created, existing = [], []
    for path, text in ((p.features_planned, planned_md(cfg)),
                       (p.features_implemented, implemented_md(cfg))):
        if path.exists():
            existing.append(str(path.relative_to(p.root)))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        created.append(str(path.relative_to(p.root)))
    out = {"created": created, "existing": existing}
    found = bk.planned_header_found(p.features_planned)
    want = bk.planned_header(cfg)
    if found is not None and found != want:
        if fix_header:
            out["header_fixed"] = bk.migrate_planned_header(p.features_planned, cfg)
        else:
            out["planned_header_mismatch"] = {"expected": want, "found": found}
    bk.emit(out)


if __name__ == "__main__":
    main()
