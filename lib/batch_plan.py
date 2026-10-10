#!/usr/bin/env python3
"""
Resolve a batch run's work list and put it in order — the mechanical half of the
batch skills' first step.

Two input forms, for either kind of backlog:
  --ids a,b,c   the user's own ordered list (bug ids, or feature numbers / change names)
  --all         every open bug / pending feature

Output is JSON:
  items     [{id, number?, title/summary, in_progress}] in run order
  problems  things the user must resolve first — an id that matches nothing, one already
            closed/implemented, a Won't-fix / Cannot-reproduce bug, a duplicate
  warnings  non-blocking: a feature listed before a still-pending prerequisite, a row
            missing from the recommended order, a dependency cycle
  order_basis how `--all` was ordered

Ordering for `--all`:
  features  Recommended implementation order if it has entries, else hard dependencies
            (prerequisite first, topological, stable against table order), else table order
  bugs      Recommended fix order if it has entries, else severity (configured order), then number

Usage:
    python3 batch_plan.py <repo-root> --kind bugs|features (--ids "a,b,c" | --all)
"""
import argparse
import re
import sys
from pathlib import Path

_here = Path(__file__).resolve()
for _cand in (_here.parent, _here.parents[3] / "lib"):
    if (_cand / "backlog_kit.py").is_file():
        sys.path.insert(0, str(_cand))
        break
import backlog_kit as bk


def split_ids(raw):
    return [s.strip() for s in re.split(r"[,\s]+", raw) if s.strip()]


# --- bugs --------------------------------------------------------------------

def normalize_bug_id(raw, prefix):
    s = raw.strip().upper()
    m = re.match(rf"^{re.escape(prefix)}-?0*(\d+)$", s)
    if m:
        return f"{prefix}-{int(m.group(1)):03d}"
    if s.isdigit():
        return f"{prefix}-{int(s):03d}"
    return s


def plan_bugs(root, cfg, ids, want_all):
    p = bk.Paths(root, cfg)
    b = cfg["bugs"]
    prefix = b["id_prefix"]
    _, open_rows = bk.table_rows(p.bugs_open, "## Bug List", "Bug ID")
    _, fixed_rows = bk.table_rows(p.bugs_fixed, "## Bug List", "Bug ID")
    open_lines = bk.read_lines(p.bugs_open) or []
    fix_order = bk.order_list_positions(open_lines, "## Recommended fix order", rf"^\s*-\s*({re.escape(prefix)}-\d+)")

    by_id = {r.get("Bug ID", "").strip(): r for r in open_rows}
    fixed_ids = {r.get("Bug ID", "").strip() for r in fixed_rows}

    def item(r):
        return {"id": r["Bug ID"].strip(), "summary": r.get("Summary", "").strip(),
                "severity": r.get("Severity", "").strip(), "in_progress": "In Progress" in r.get("Status", "")}

    def actionable(r):
        return "Open" in r.get("Status", "") or "In Progress" in r.get("Status", "")

    items, problems, warnings, basis = [], [], [], None
    if want_all:
        rows = [r for r in open_rows if actionable(r)]
        if fix_order:
            basis = "recommended-order"
            listed = sorted((r for r in rows if r["Bug ID"].strip() in fix_order), key=lambda r: fix_order[r["Bug ID"].strip()])
            rest = [r for r in rows if r["Bug ID"].strip() not in fix_order]
            if rest:
                warnings.append("Not in the Recommended fix order, appended by severity: " + ", ".join(r["Bug ID"].strip() for r in rest))
            rest.sort(key=lambda r: (bk.tier_score(r.get("Severity", "").strip(), b["severities"]) * -1, r["Bug ID"]))
            rows = listed + rest
        else:
            basis = "severity"
            rows.sort(key=lambda r: (-bk.tier_score(r.get("Severity", "").strip(), b["severities"]), r["Bug ID"]))
        items = [item(r) for r in rows]
    else:
        seen = set()
        for raw in ids:
            bid = normalize_bug_id(raw, prefix)
            if bid in seen:
                problems.append({"input": raw, "kind": "duplicate", "detail": f"{bid} is listed more than once"})
                continue
            seen.add(bid)
            r = by_id.get(bid)
            if r is None:
                kind = "already-closed" if bid in fixed_ids else "unresolved"
                detail = f"{bid} is in bugs-fixed.md (already closed)" if kind == "already-closed" else f"{bid} matches no bug in the backlog"
                problems.append({"input": raw, "kind": kind, "detail": detail})
            elif "Won" in r.get("Status", "") and "fix" in r.get("Status", ""):
                problems.append({"input": raw, "kind": "wont-fix", "detail": f"{bid} is marked Won't fix"})
            elif "Cannot reproduce" in r.get("Status", ""):
                problems.append({"input": raw, "kind": "cannot-repro", "detail": f"{bid} is marked Cannot reproduce"})
            elif "Fixed" in r.get("Status", ""):
                problems.append({"input": raw, "kind": "already-closed", "detail": f"{bid} still shows Fixed in bugs-open.md (an interrupted archive?)"})
            else:
                items.append(item(r))
    return {"kind": "bugs", "mode": "all" if want_all else "named", "items": items,
            "problems": problems, "warnings": warnings, "order_basis": basis}


# --- features ------------------------------------------------------------------

def topo_order(rows, deps):
    """Stable topological order by feature number: a prerequisite precedes its dependents."""
    nums = [r["number"] for r in rows]
    before = {n: set() for n in nums}
    for a, bq in deps:
        if a in before and bq in before:
            before[a].add(bq)
    out, remaining, cycle = [], list(nums), False
    while remaining:
        ready = next((n for n in remaining if not (before[n] & set(remaining))), None)
        if ready is None:
            cycle = True
            ready = remaining[0]
        out.append(ready)
        remaining.remove(ready)
    by = {r["number"]: r for r in rows}
    return [by[n] for n in out], cycle


def plan_features(root, cfg, ids, want_all):
    p = bk.Paths(root, cfg)
    planned_lines = bk.read_lines(p.features_planned) or []
    _, planned_rows = bk.table_rows(p.features_planned, "## Feature List")
    _, impl_rows = bk.table_rows(p.features_implemented, "## Feature List")
    deps = bk.hard_dependencies(planned_lines)
    order = bk.order_list_positions(planned_lines, "### Recommended implementation order", r"^\s*-\s*`[^`]+`\s*\(#(\d+)\)")

    def row(r):
        return {"number": r.get("#", "").strip(), "id": bk.strip_backticks(r.get("Change name", "")),
                "summary": r.get("Summary", "").strip(), "priority": r.get("Priority", "").strip(),
                "in_progress": "In Progress" in r.get("Implementation", "")}

    pending = [row(r) for r in planned_rows
               if "Pending" in r.get("Implementation", "") or "In Progress" in r.get("Implementation", "")]
    by_number = {r["number"]: r for r in pending}
    by_name = {r["id"]: r for r in pending}
    impl_numbers = {r.get("#", "").strip() for r in impl_rows}
    impl_names = {bk.strip_backticks(r.get("Change name", "")) for r in impl_rows}

    items, problems, warnings, basis, cycle = [], [], [], None, False
    if want_all:
        if order:
            basis = "recommended-order"
            listed = sorted((r for r in pending if r["number"] in order), key=lambda r: order[r["number"]])
            rest = [r for r in pending if r["number"] not in order]
            if rest:
                warnings.append("Not in the Recommended implementation order, appended in table order: "
                                + ", ".join(f"#{r['number']} {r['id']}" for r in rest))
            items = listed + rest
        elif deps:
            basis = "dependencies"
            items, cycle = topo_order(pending, deps)
        else:
            basis = "table"
            items = pending
    else:
        seen = set()
        for raw in ids:
            key = raw.strip().lstrip("#")
            r = by_number.get(key) or by_name.get(key)
            if r is None:
                if key in impl_numbers or key in impl_names:
                    problems.append({"input": raw, "kind": "already-implemented", "detail": f"'{raw}' is already in features-implemented.md"})
                else:
                    problems.append({"input": raw, "kind": "unresolved", "detail": f"'{raw}' matches no planned feature"})
                continue
            if r["number"] in seen:
                problems.append({"input": raw, "kind": "duplicate", "detail": f"#{r['number']} {r['id']} is listed more than once"})
                continue
            seen.add(r["number"])
            items.append(r)

    # A feature listed before a still-pending prerequisite would be refused by features-next.
    position = {r["number"]: i for i, r in enumerate(items)}
    for a, bq in deps:
        if a in position:
            if bq in position and position[bq] > position[a]:
                warnings.append(f"Feature {a} is ordered before its prerequisite Feature {bq}; the run would be blocked on it.")
            elif bq not in position and bq in by_number:
                warnings.append(f"Feature {a} depends on Feature {bq}, which is still pending and not in this run; it will be blocked.")
    if cycle:
        warnings.append("Hard dependencies contain a cycle; those features are kept in table order.")
    return {"kind": "features", "mode": "all" if want_all else "named", "items": items,
            "problems": problems, "warnings": warnings, "order_basis": basis}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root")
    ap.add_argument("--kind", required=True, choices=["bugs", "features"])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--ids")
    g.add_argument("--all", action="store_true")
    args = ap.parse_args()

    cfg = bk.load_config(args.repo_root)
    ids = split_ids(args.ids) if args.ids else []
    plan = plan_bugs if args.kind == "bugs" else plan_features
    out = plan(args.repo_root, cfg, ids, args.all)
    out["empty"] = not out["items"] and not out["problems"]
    bk.emit(out)


if __name__ == "__main__":
    main()
