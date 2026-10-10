#!/usr/bin/env python3
"""
Create bugs-open.md and bugs-fixed.md under the configured backlog dir if they
don't exist yet, with the Column legend generated from .backlog-kit.toml.
Idempotent: an existing file is never touched.

Usage:
    python3 scaffold.py <repo-root>
Prints JSON: {"created": [...], "existing": [...]}
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
            "| " + " | ".join("-" * max(3, len(h)) for h in header) + " |")


def open_md(cfg):
    b = cfg["bugs"]
    sev = " · ".join(f"`{s}` ({b['severity_labels'].get(s, '')})".replace(" ()", "") for s in b["severities"])
    env = " · ".join(f"`{e}`" for e in b["environments"])
    return "\n".join([
        "# Open Bugs", "",
        "## Bug List", "",
        table(["Bug ID", "Severity", "Area", "Environment", "Status", "Fix", "Summary"]), "",
        "_No open bugs._", "",
        "## Column legend", "",
        f"- **Severity**: {sev}",
        "- **Area**: the affected route, module or component — free text, use whatever your team already calls it",
        f"- **Environment**: {env}",
        "- **Status**: `⬜ Open` · `🔶 In Progress` (a fix has been started) · `✅ Fixed` (transient — `bugs-archive` moves the row to `bugs-fixed.md` in the same pass) · `🚫 Won't fix` · `❓ Cannot reproduce`",
        "- **Fix**: PR link or commit hash once closed; blank while open",
        "",
        "## Details", "",
        "<!-- Per-bug details live in bugs/<ID>.md (stable path), one file per bug, linked from its row. `bugs-archive` moves only the table row to bugs-fixed.md and appends the Resolution line to that file. -->", "",
        "Details for every bug live in `bugs/<ID>.md`, linked from its row.", "",
        "## Recommended fix order", "",
        "Severity tier first, then blast radius / how often it bites, then quick-win effort, then bug number. Not a schedule — a reasoning aid for `bugs-next` and for whoever picks the next fix by hand. A plain bullet list: list position (not a printed number) encodes order, so inserting an entry never touches any other line.", "",
        "_No open bugs to order._", "",
    ])


def fixed_md(cfg):
    return "\n".join([
        "# Fixed Bugs", "",
        "## Bug List", "",
        table(["Bug ID", "Severity", "Area", "Environment", "Fixed", "Fix", "Summary"]), "",
        "## Details", "",
        "<!-- Per-bug details live in bugs/<ID>.md (stable path). `bugs-archive` moves only the table row between bugs-open.md and bugs-fixed.md and appends the Resolution line to that file. -->", "",
        "Details for every bug live in `bugs/<ID>.md`, linked from its row.", "",
    ])


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    root = sys.argv[1]
    cfg = bk.load_config(root)
    p = bk.Paths(root, cfg)
    created, existing = [], []
    for path, text in ((p.bugs_open, open_md(cfg)), (p.bugs_fixed, fixed_md(cfg))):
        if path.exists():
            existing.append(str(path.relative_to(p.root)))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        created.append(str(path.relative_to(p.root)))
    bk.emit({"created": created, "existing": existing})


if __name__ == "__main__":
    main()
