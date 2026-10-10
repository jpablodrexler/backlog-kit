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
  features  work already in progress first, then priority tier, with a hard prerequisite always
            before its dependents; ties follow the Recommended implementation order, then table order
  bugs      work already in progress first, then severity tier; ties follow the Recommended fix
            order, then bug number
            (the same ranking features-next / bugs-next apply, so `--all` agrees with them; the
            order lists only break ties and a stale one never reorders a higher tier. A named
            `--ids` list is always run exactly as given.)

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
        basis = "severity"

        def key(r):
            bid = r["Bug ID"].strip()
            return (0 if "In Progress" in r.get("Status", "") else 1,
                    -bk.tier_score(r.get("Severity", "").strip(), b["severities"]),
                    fix_order.get(bid, UNLISTED), bid)

        rows.sort(key=key)
        warnings += order_list_warning("Recommended fix order", fix_order, [r["Bug ID"].strip() for r in rows])
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

UNLISTED = 10 ** 6


def order_list_warning(name, positions, run_order, label=lambda x: x):
    """Tell the user when the hand-kept order list disagrees with the order the run will use."""
    listed_in_run = [i for i in run_order if i in positions]
    by_list = sorted(listed_in_run, key=lambda i: positions[i])
    out = []
    if listed_in_run != by_list:
        out.append(f"The {name} disagrees with the run order (in-progress, then priority, then dependencies); "
                   f"running: {', '.join(label(i) for i in run_order)}.")
    unlisted = [i for i in run_order if positions and i not in positions]
    if unlisted:
        out.append(f"Not in the {name}, placed by priority: {', '.join(label(i) for i in unlisted)}.")
    return out


def rank_features(rows, deps, order, priorities):
    """In-progress first, then priority tier, then list position, then table order — except that a
    pending prerequisite always precedes its dependents. Returns (ordered rows, cycle_found)."""
    index = {r["number"]: n for n, r in enumerate(rows)}
    before = {r["number"]: set() for r in rows}
    for a, bq in deps:
        if a in before and bq in before:
            before[a].add(bq)

    def key(r):
        return (0 if r["in_progress"] else 1, -bk.tier_score(r["priority"], priorities),
                order.get(r["number"], UNLISTED), index[r["number"]])

    out, remaining, cycle = [], list(rows), False
    while remaining:
        left = {r["number"] for r in remaining}
        ready = [r for r in remaining if not (before[r["number"]] & left)]
        if not ready:
            cycle = True
            ready = remaining
        pick = min(ready, key=key)
        out.append(pick)
        remaining.remove(pick)
    return out, cycle


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
        basis = "priority"
        items, cycle = rank_features(pending, deps, order, cfg["features"]["priorities"])
        warnings += order_list_warning("Recommended implementation order", order, [r["number"] for r in items],
                                       label=lambda n: f"#{n}")
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

    # The brief is what feature-development reads; a missing one would only surface mid-run.
    for r in items:
        brief = p.backlog / "features" / f"{int(r['number']):03d}-{r['id']}.md" if r["number"].isdigit() else None
        if brief is not None and not brief.is_file():
            problems.append({"input": r["id"], "kind": "missing-brief",
                             "detail": f"#{r['number']} {r['id']} has no brief file ({brief.name}); it would stop at PLAN_BLOCKED"})

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
