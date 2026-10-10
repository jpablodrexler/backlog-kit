#!/usr/bin/env python3
"""
Feature-tracker status report: counts, priority/effort breakdown, the pending
list, and data-integrity checks (duplicate numbers, stale "prerequisite still
pending" dependency notes, row <-> features/NNN-<name>.md cross-checks, a
leftover "✅ Implemented" row from an interrupted archive).

Pure table-counting over features-planned.md / features-implemented.md. The
skill reads this output and presents it; the script owns no judgment.

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

SUMMARY_MAX = 250
BRIEF_LINK_RE = re.compile(r"\[brief\]\(([^)]+)\)")
SPEC_LINK_RE = re.compile(r"\[spec\]\(([^)]+)\)")
DEP_RE = re.compile(r"\*\*Feature (\d+)\s*(?:→|->)\s*Feature (\d+)\*\*\s*\(([^)]*)\)")


def expected_file_name(row):
    n = row.get("#", "").strip()
    name = bk.strip_backticks(row.get("Change name", ""))
    return f"{int(n):03d}-{name}.md" if n.isdigit() and name else None


def compute(root):
    cfg = bk.load_config(root)
    p = bk.Paths(root, cfg)
    f = cfg["features"]
    use_spec = cfg["spec"]["workflow"] == "openspec"

    planned_ok, planned_rows = bk.table_rows(p.features_planned, "## Feature List")
    impl_ok, impl_rows = bk.table_rows(p.features_implemented, "## Feature List")

    r = {
        "planned_available": planned_ok, "implemented_available": impl_ok,
        "use_spec": use_spec,
        "pending_strict": 0, "in_progress": 0, "implemented": len(impl_rows),
        "total": None, "percent": None,
        "priority_breakdown": {k: 0 for k in f["priorities"] + ["none"]},
        "effort_breakdown": {k: 0 for k in f["efforts"] + ["none"]},
        "spec_ready": 0, "pending_rows": [],
        "duplicate_numbers": [], "stale_dependency_notes": [],
        "leftover_implemented_in_planned": [],
        "missing_feature_files": [], "orphan_feature_files": [], "bad_feature_headings": [],
        "bad_planned_summaries": [], "missing_brief_links": [], "missing_spec_targets": [],
        "priority_labels": f["priority_labels"],
    }

    implemented_numbers = {x.get("#", "").strip() for x in impl_rows if x.get("#", "").strip()}
    all_numbers = list(implemented_numbers)
    pending_like = []
    for row in planned_rows:
        n = row.get("#", "").strip()
        if n:
            all_numbers.append(n)
        impl = row.get("Implementation", "").strip()
        if "In Progress" in impl:
            r["in_progress"] += 1
            pending_like.append(row)
        elif "Pending" in impl:
            r["pending_strict"] += 1
            pending_like.append(row)
        elif "Implemented" in impl:
            r["leftover_implemented_in_planned"].append(n)

    if planned_ok and impl_ok:
        pending = r["pending_strict"] + r["in_progress"]
        total = pending + r["implemented"]
        r["total"] = total
        r["percent"] = "0% — no features tracked yet" if total == 0 else f"{round(100 * r['implemented'] / total, 1)}%"

    for row in pending_like:
        pr = row.get("Priority", "").strip()
        r["priority_breakdown"][pr if pr in f["priorities"] else "none"] += 1
        ef = row.get("Effort", "").strip()
        r["effort_breakdown"][ef if ef in f["efforts"] else "none"] += 1
        if use_spec and "Created" in row.get("SDD Artifacts", ""):
            r["spec_ready"] += 1
        r["pending_rows"].append({
            "number": row.get("#", "").strip(),
            "name": bk.strip_backticks(row.get("Change name", "")),
            "priority": pr,
            "in_progress": "In Progress" in row.get("Implementation", ""),
        })

    counts = {}
    for n in all_numbers:
        counts[n] = counts.get(n, 0) + 1
    r["duplicate_numbers"] = sorted((n for n, c in counts.items() if c > 1),
                                    key=lambda x: int(x) if x.isdigit() else 0)

    for path, label in ((p.features_planned, "features-planned.md"), (p.features_implemented, "features-implemented.md")):
        for line in bk.read_lines(path) or []:
            m = DEP_RE.search(line)
            if m and "pending" in m.group(3).lower() \
                    and m.group(1) in implemented_numbers and m.group(2) in implemented_numbers:
                r["stale_dependency_notes"].append({
                    "heading": f"Feature {m.group(1)} → Feature {m.group(2)}",
                    "note": m.group(3).strip(), "file": label})

    check_feature_files(p, planned_rows, impl_rows, r)
    return r


def check_feature_files(p, planned_rows, impl_rows, r):
    expected = {}
    for label, rows in (("planned", planned_rows), ("implemented", impl_rows)):
        for row in rows:
            fname = expected_file_name(row)
            if fname is None:
                continue
            n = row.get("#", "").strip()
            name = bk.strip_backticks(row.get("Change name", ""))
            expected[fname] = (n, name)
            if label == "planned":
                summary = row.get("Summary", "").strip()
                if not summary:
                    r["bad_planned_summaries"].append({"number": n, "name": name, "problem": "empty"})
                elif len(summary) > SUMMARY_MAX:
                    r["bad_planned_summaries"].append(
                        {"number": n, "name": name, "problem": f"{len(summary)} chars (max {SUMMARY_MAX})"})
                if not BRIEF_LINK_RE.search(row.get("Brief", "")):
                    r["missing_brief_links"].append({"number": n, "name": name, "file": "features-planned.md"})
            else:
                details = row.get("Details", "")
                if not BRIEF_LINK_RE.search(details):
                    r["missing_brief_links"].append({"number": n, "name": name, "file": "features-implemented.md"})
                m = SPEC_LINK_RE.search(details)
                if m and not (p.backlog / m.group(1)).is_file():
                    r["missing_spec_targets"].append({"number": n, "name": name, "target": m.group(1)})
            if not (p.features_dir / fname).is_file():
                r["missing_feature_files"].append(fname)

    if p.features_dir.is_dir():
        for fpath in sorted(p.features_dir.glob("*.md")):
            if fpath.name not in expected:
                r["orphan_feature_files"].append(fpath.name)
                continue
            n, name = expected[fpath.name]
            first = fpath.read_text(encoding="utf-8").splitlines()[:1]
            want = f"# Feature {int(n)} — {name}"
            if not first or first[0].strip() != want:
                r["bad_feature_headings"].append({"file": fpath.name, "expected": want})


def render(r, cfg_rel_backlog):
    L = ["## Feature Tracker Status", ""]
    if r["total"] is None:
        missing = [f"{cfg_rel_backlog}/{n}" for ok, n in
                   ((r["planned_available"], "features-planned.md"), (r["implemented_available"], "features-implemented.md")) if not ok]
        L += [f"**Total/Progress unavailable** — missing or table-less: {', '.join(missing)}", ""]
        if r["implemented_available"]:
            L.append(f"- ✅ Implemented: {r['implemented']}")
        if r["planned_available"]:
            L += [f"- ⬜ Pending: {r['pending_strict']}", f"- 🔶 In Progress: {r['in_progress']}"]
        L.append("")
    else:
        L += ["| Metric | Count |", "| ------ | ----- |",
              f"| Total features | {r['total']} |", f"| ✅ Implemented | {r['implemented']} |",
              f"| ⬜ Pending | {r['pending_strict']} |", f"| 🔶 In Progress | {r['in_progress']} |",
              f"| **Progress** | **{r['percent']}** |", ""]

    L += ["### Pending breakdown by priority", "", "| Tier | Count |", "| ---- | ----- |"]
    for k, v in r["priority_breakdown"].items():
        label = "No explicit tier" if k == "none" else f"{k} — {r['priority_labels'].get(k, '')}".rstrip(" —")
        L.append(f"| {label} | {v} |")
    L += ["", "### Pending breakdown by effort", "", "| Effort | Count |", "| ------ | ----- |"]
    for k, v in r["effort_breakdown"].items():
        L.append(f"| {'No explicit effort' if k == 'none' else k} | {v} |")
    L.append("")

    if r["use_spec"]:
        pending_count = r["pending_strict"] + r["in_progress"]
        L += ["### Spec readiness", "",
              f"{r['spec_ready']} of {pending_count} pending features already have spec artifacts "
              "created and can be implemented without a propose step.", ""]

    L += ["### Pending features", ""]
    if r["pending_rows"]:
        for row in r["pending_rows"]:
            suffix = " — 🔶 In Progress" if row["in_progress"] else ""
            L.append(f"- #{row['number']} `{row['name']}` ({row['priority'] or 'no tier'}){suffix}")
    else:
        L.append("_None._")
    L.append("")

    bl = cfg_rel_backlog
    issues = []
    issues += [f"- ⚠ Duplicate feature number {n}." for n in r["duplicate_numbers"]]
    issues += [f"- ⚠ Stale dependency note \"{d['heading']}\": all referenced features are already implemented, "
               f"but it's still annotated \"{d['note']}\" in {d['file']}." for d in r["stale_dependency_notes"]]
    issues += [f"- ⚠ {x} has a table row but no {bl}/features/{x} file." for x in r["missing_feature_files"]]
    issues += [f"- ⚠ {bl}/features/{x} exists but its feature has no row in either table." for x in r["orphan_feature_files"]]
    issues += [f"- ⚠ {bl}/features/{b['file']} does not start with `{b['expected']}`." for b in r["bad_feature_headings"]]
    issues += [f"- ⚠ #{s['number']} `{s['name']}` has a bad Summary in features-planned.md ({s['problem']})." for s in r["bad_planned_summaries"]]
    issues += [f"- ⚠ #{b['number']} `{b['name']}` has no `[brief](features/...)` link in {b['file']}." for b in r["missing_brief_links"]]
    issues += [f"- ⚠ #{s['number']} `{s['name']}`: the [spec] link target {s['target']} does not exist (warning)." for s in r["missing_spec_targets"]]
    issues += [f"- ⚠ #{n} still shows ✅ Implemented in features-planned.md — an archive pass was interrupted; "
               "run features-archive to finish the move." for n in r["leftover_implemented_in_planned"]]
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
        cfg = bk.load_config(args.repo_root)
        render(r, cfg["paths"]["backlog_dir"].strip("/"))


if __name__ == "__main__":
    main()
