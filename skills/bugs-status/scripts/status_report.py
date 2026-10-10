#!/usr/bin/env python3
"""
Bug-tracker status report: counts, severity/area/environment breakdown, the
open-bug list, and data-integrity checks (duplicate ids, rows without a
bugs/<ID>.md details file, files without a row, a bad file H1, fixed rows whose
file lacks a Resolution line, a leftover "✅ Fixed" row in bugs-open.md).

Pure table-counting over bugs-open.md / bugs-fixed.md. The Bug ID cell may be
plain or a link: `[BUG-001](bugs/BUG-001.md)`.

Usage:
    python3 status_report.py <repo-root> [--json]
"""
import argparse
import json
import re
import sys
from pathlib import Path

_here = Path(__file__).resolve()
for _cand in (_here.parent, _here.parents[3] / "lib"):
    if (_cand / "backlog_kit.py").is_file():
        sys.path.insert(0, str(_cand))
        break
import backlog_kit as bk


def compute(root):
    cfg = bk.load_config(root)
    p = bk.Paths(root, cfg)
    b = cfg["bugs"]
    prefix = re.escape(b["id_prefix"])

    open_ok, open_rows = bk.table_rows(p.bugs_open, "## Bug List", "Bug ID")
    fixed_ok, fixed_rows = bk.table_rows(p.bugs_fixed, "## Bug List", "Bug ID")

    r = {
        "open_available": open_ok, "fixed_available": fixed_ok,
        "open_strict": 0, "in_progress": 0, "wont_fix": 0, "cannot_repro": 0,
        "fixed_here": [], "fixed": len(fixed_rows), "total": None, "percent": None,
        "severity_breakdown": {k: 0 for k in b["severities"] + ["none"]},
        "severity_labels": b["severity_labels"],
        "area_breakdown": {}, "env_breakdown": {k: 0 for k in b["environments"]},
        "active_rows": [], "duplicate_ids": [], "rows_missing_file": [], "files_without_row": [],
        "files_bad_h1": [], "fixed_missing_resolution": [], "id_prefix": b["id_prefix"],
    }
    fixed_ids = {x.get("Bug ID", "").strip() for x in fixed_rows if x.get("Bug ID", "").strip()}

    open_ids, active, resolved_in_open = [], [], []
    for row in open_rows:
        bug_id = row.get("Bug ID", "").strip()
        open_ids.append(bug_id)
        status = row.get("Status", "")
        if "In Progress" in status:
            r["in_progress"] += 1
            active.append(row)
        elif "Won't fix" in status or "Won’t fix" in status:
            r["wont_fix"] += 1
            resolved_in_open.append(bug_id)
        elif "Cannot reproduce" in status:
            r["cannot_repro"] += 1
            resolved_in_open.append(bug_id)
        elif "Fixed" in status:
            r["fixed_here"].append(bug_id)
        elif "Open" in status:
            r["open_strict"] += 1
            active.append(row)

    if open_ok and fixed_ok:
        resolved = r["wont_fix"] + r["cannot_repro"] + r["fixed"]
        total = r["open_strict"] + r["in_progress"] + resolved
        r["total"] = total
        r["percent"] = "0% — no bugs tracked yet" if total == 0 else f"{round(100 * resolved / total, 1)}% resolved"

    for row in active:
        sev = row.get("Severity", "").strip()
        r["severity_breakdown"][sev if sev in b["severities"] else "none"] += 1
        area = row.get("Area", "").strip() or "(blank)"
        r["area_breakdown"][area] = r["area_breakdown"].get(area, 0) + 1
        env = row.get("Environment", "").strip() or "(blank)"
        r["env_breakdown"][env] = r["env_breakdown"].get(env, 0) + 1
        r["active_rows"].append({
            "id": row.get("Bug ID", "").strip(), "severity": sev,
            "environment": row.get("Environment", "").strip(),
            "summary": row.get("Summary", "").strip(),
            "in_progress": "In Progress" in row.get("Status", ""),
        })

    counts = {}
    for i in open_ids + list(fixed_ids):
        if i:
            counts[i] = counts.get(i, 0) + 1
    r["duplicate_ids"] = sorted(i for i, c in counts.items() if c > 1)

    active_open_ids = {x.get("Bug ID", "").strip() for x in open_rows
                       if "Open" in x.get("Status", "") or "In Progress" in x.get("Status", "")}
    all_row_ids = {i for i in open_ids if i} | fixed_ids
    file_ids = set()
    if p.bugs_dir.is_dir():
        for f in p.bugs_dir.glob("*.md"):
            m = re.match(rf"^({prefix}-\d+)\.md$", f.name)
            if m:
                file_ids.add(m.group(1))
    # Every row needs its details file, whatever its status (a Won't fix / Cannot reproduce bug keeps its write-up).
    r["rows_missing_file"] = sorted(i for i in (active_open_ids | fixed_ids | set(resolved_in_open)) if i and i not in file_ids)
    r["files_without_row"] = sorted(file_ids - all_row_ids)
    for bid in sorted(file_ids):
        text = (p.bugs_dir / f"{bid}.md").read_text(encoding="utf-8")
        first = text.lstrip("﻿").splitlines()[0] if text.strip() else ""
        if not re.match(rf"^# {re.escape(bid)}(\s|$)", first):
            r["files_bad_h1"].append(bid)
        if (bid in fixed_ids or bid in resolved_in_open) and not re.search(r"^\s*-\s*\*\*Resolution:\*\*", text, re.M):
            r["fixed_missing_resolution"].append(bid)
    return r


def render(r, rel_backlog):
    L = ["## Bug Tracker Status", ""]
    if r["total"] is None:
        missing = [f"{rel_backlog}/{n}" for ok, n in
                   ((r["open_available"], "bugs-open.md"), (r["fixed_available"], "bugs-fixed.md")) if not ok]
        L += [f"**Total/Progress unavailable** — missing or table-less: {', '.join(missing)}", ""]
    else:
        L += ["| Metric | Count |", "| ------ | ----- |",
              f"| Total bugs | {r['total']} |", f"| ✅ Fixed | {r['fixed']} |",
              f"| 🚫 Won't fix | {r['wont_fix']} |", f"| ❓ Cannot reproduce | {r['cannot_repro']} |",
              f"| ⬜ Open | {r['open_strict']} |", f"| 🔶 In Progress | {r['in_progress']} |",
              f"| **Progress** | **{r['percent']}** |", ""]

    L += ["### Open bugs by severity", "", "| Severity | Count |", "| -------- | ----- |"]
    for k, v in r["severity_breakdown"].items():
        label = "No explicit severity" if k == "none" else f"{k} — {r['severity_labels'].get(k, '')}".rstrip(" —")
        L.append(f"| {label} | {v} |")
    L += ["", "### Open bugs by area", "", "| Area | Count |", "| ---- | ----- |"]
    if r["area_breakdown"]:
        L += [f"| {a} | {c} |" for a, c in sorted(r["area_breakdown"].items(), key=lambda kv: (-kv[1], kv[0]))]
    else:
        L.append("| _None_ | 0 |")
    L += ["", "### Open bugs by environment", "", "| Environment | Count |", "| ----------- | ----- |"]
    L += [f"| {e} | {c} |" for e, c in r["env_breakdown"].items()]
    L += ["", "### Open bugs", ""]
    if r["active_rows"]:
        for row in r["active_rows"]:
            suffix = " — 🔶 In Progress" if row["in_progress"] else ""
            L.append(f"- {row['id']} `{row['severity'] or '?'}` ({row['environment'] or '?'}) — {row['summary']}{suffix}")
    else:
        L.append("_None._")
    L.append("")

    bd = f"{rel_backlog}/bugs"
    issues = []
    issues += [f"- ⚠ Duplicate Bug ID {i}." for i in r["duplicate_ids"]]
    issues += [f"- ⚠ {i} has a table row but no {bd}/{i}.md file." for i in r["rows_missing_file"]]
    issues += [f"- ⚠ {bd}/{i}.md exists but {i} has no table row in either file." for i in r["files_without_row"]]
    issues += [f"- ⚠ {bd}/{i}.md does not start with a `# {i}` heading." for i in r["files_bad_h1"]]
    issues += [f"- ⚠ {i} is closed (bugs-fixed.md, Won't fix or Cannot reproduce) but {bd}/{i}.md has no **Resolution:** line." for i in r["fixed_missing_resolution"]]
    issues += [f"- ⚠ {i} still shows ✅ Fixed in bugs-open.md — run `bugs-archive {i}` to finish the move." for i in r["fixed_here"]]
    if issues:
        L += ["### Data integrity", ""] + issues
    print("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    r = compute(args.repo_root)
    if args.json:
        print(json.dumps(r, indent=2))
    else:
        render(r, bk.load_config(args.repo_root)["paths"]["backlog_dir"].strip("/"))


if __name__ == "__main__":
    main()
