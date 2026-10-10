#!/usr/bin/env python3
"""
Score and rank pending features from features-planned.md per features-next's
steps 2-4: resolve hard-dependency blocking from each prerequisite's *live*
Implementation-column status (never a dependency note's own possibly-stale
parenthetical), then apply the fixed point-tier scoring:

    In Progress (+1000) > Priority (n*100 .. 100, from the configured order)
    > SDD artifacts ready (+20, only with spec.workflow = "openspec")
    > listed in the Recommended implementation order (+10)
    > smallest configured effort (+5)

with tie-breaks: earlier order-list position, then lower feature number.

This script only computes the ranking. It never asks the user anything and
never returns a final decision — features-next still owns the mandatory
confirmation.

Usage:
    python3 rank_features.py <repo-root> [--select <number-or-name>] [--json]
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

def brief_file_path(rel_backlog, row):
    n = row.get("#", "").strip()
    name = bk.strip_backticks(row.get("Change name", ""))
    if not n.isdigit() or not name:
        return ""
    return f"{rel_backlog}/features/{int(n):03d}-{name}.md"


def fail(msg, **extra):
    bk.emit({"error": msg, **extra})
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root")
    ap.add_argument("--select", help="a feature number or change-name to resolve directly, skipping scoring")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = Path(args.repo_root)
    cfg = bk.load_config(root)
    p = bk.Paths(root, cfg)
    f_cfg = cfg["features"]
    use_spec = cfg["spec"]["workflow"] == "openspec"

    planned_lines = bk.read_lines(p.features_planned)
    if planned_lines is None:
        fail("features-planned.md not found — run feature-plan first")
    table = bk.find_table(planned_lines, "## Feature List")
    if not table:
        fail("no ## Feature List table in features-planned.md")
    header, rows = table
    all_rows = [bk.row_dict(header, r) for r in rows]

    candidates, seen, duplicate_numbers = [], set(), set()
    for r in all_rows:
        impl = r.get("Implementation", "")
        n = r.get("#", "").strip()
        if "Pending" in impl or "In Progress" in impl:
            if n in seen:
                duplicate_numbers.add(n)
            seen.add(n)
            candidates.append({
                "number": n,
                "name": bk.strip_backticks(r.get("Change name", "")),
                "priority": r.get("Priority", "").strip(),
                "effort": r.get("Effort", "").strip(),
                "area": r.get("Area", "").strip(),
                "artifacts_ready": use_spec and ("Created" in r.get("SDD Artifacts", "") or bk.spec_artifacts_ready(
                    root, cfg, bk.strip_backticks(r.get("Change name", "")))),
                "in_progress": "In Progress" in impl,
                "brief": r.get("Summary", "").strip(),
                "brief_file": brief_file_path(p.rel_backlog, r),
            })
    if not candidates:
        fail("no pending or in-progress features in the backlog")

    pending_numbers = {c["number"] for c in candidates}
    by_number = {}
    for c in candidates:
        by_number.setdefault(c["number"], []).append(c)
    missing_briefs = [c["brief_file"] for c in candidates if not (root / c["brief_file"]).is_file()]

    _, impl_rows = bk.table_rows(p.features_implemented, "## Feature List")
    impl_numbers = {x.get("#", "").strip() for x in impl_rows}
    blocked, blocked_reason, unknown_prereqs = set(), {}, []
    for a, b in bk.hard_dependencies(planned_lines):
        # Blocked while the prerequisite still has a live Pending/In Progress row. A prerequisite
        # absent from this table counts as shipped only if features-implemented.md really lists it:
        # a typo'd or deleted number must not silently unblock its dependent.
        if a in by_number and b in pending_numbers:
            blocked.add(a)
            blocked_reason[a] = b
        elif a in by_number and b not in impl_numbers:
            blocked.add(a)
            blocked_reason[a] = f"{b} (unknown: in neither features-planned.md nor features-implemented.md)"
            unknown_prereqs.append(f"Feature {a} → Feature {b}")

    order = bk.order_list_positions(
        planned_lines, "### Recommended implementation order", r"^\s*-\s*`[^`]+`\s*\(#(\d+)\)")
    smallest_effort = f_cfg["efforts"][0] if f_cfg["efforts"] else None

    def score(c):
        s = 1000 if c["in_progress"] else 0
        s += bk.tier_score(c["priority"], f_cfg["priorities"])
        if c["artifacts_ready"]:
            s += 20
        if order.get(c["number"]) is not None:
            s += 10
        if smallest_effort and c["effort"] == smallest_effort:
            s += 5
        return s

    if args.select:
        sel = args.select.strip().lstrip("#")
        matches = by_number.get(sel) or [c for c in candidates if c["name"] == sel]
        if not matches:
            fail(f"'{args.select}' does not match a pending/in-progress feature")
        if len(matches) > 1:
            fail(f"'{args.select}' is ambiguous — {len(matches)} rows share it "
                 "(duplicate feature number; fix the backlog or select by exact name)",
                 candidates=matches)
        m = matches[0]
        result = {"selected": m, "blocked": m["number"] in blocked,
                  "blocked_on": blocked_reason.get(m["number"])}
        if m["brief_file"] in missing_briefs:
            result["warning"] = f"Brief file {m['brief_file']} is missing — run features-status for the full integrity report."
        print(json.dumps(result, indent=2) if args.json else render_selected(result))
        return

    ranked = []
    for c in candidates:
        if c["number"] in blocked:
            continue
        e = dict(c)
        e["score"] = score(c)
        e["order_position"] = order.get(c["number"])
        ranked.append(e)
    if not ranked:
        fail("every pending feature is blocked",
             blocked=[{"number": n, "blocked_on": blocked_reason[n]} for n in blocked])

    ranked.sort(key=lambda c: (
        -c["score"],
        c["order_position"] if c["order_position"] is not None else 10 ** 9,
        int(c["number"]) if c["number"].isdigit() else 10 ** 9,
    ))
    result = {
        "top": ranked[0],
        "runners_up": ranked[1:4],
        "blocked": [{"number": n, "blocked_on": blocked_reason[n],
                     "name": ", ".join(c["name"] for c in by_number.get(n, []))} for n in sorted(blocked)],
        "use_spec": use_spec,
    }
    warnings = []
    if duplicate_numbers:
        warnings.append(f"Duplicate feature number(s) in features-planned.md: {', '.join(sorted(duplicate_numbers))} — run features-status for the full integrity report.")
    if missing_briefs:
        warnings.append(f"Brief file(s) missing: {', '.join(missing_briefs)} — run features-status for the full integrity report.")
    if unknown_prereqs:
        warnings.append("Unknown prerequisite(s), treated as blocking: " + ", ".join(unknown_prereqs)
                        + " — fix the number or the dependency note.")
    if warnings:
        result["warning"] = " ".join(warnings)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        render_ranked(result, cfg)


def reason_bullets(c, cfg):
    f = cfg["features"]
    out = []
    if c["in_progress"]:
        out.append("🔶 Already in progress — resuming beats starting something new")
    label = f["priority_labels"].get(c["priority"])
    out.append(f"{c['priority']} {label}".strip() if c["priority"] in f["priorities"] else "no explicit priority tier")
    if c["artifacts_ready"]:
        out.append("spec artifacts already created — no propose step needed")
    if c.get("order_position"):
        out.append(f"position {c['order_position']} in the Recommended implementation order")
    if f["efforts"] and c["effort"] == f["efforts"][0]:
        out.append(f"smallest effort tier ({c['effort']}) — quick to deliver")
    return out


def render_selected(result):
    m = result["selected"]
    lines = [f"#{m['number']} `{m['name']}`", m["brief"], f"Full brief: {m['brief_file']}", ""]
    if result.get("warning"):
        lines.append(f"⚠ {result['warning']}")
    if result["blocked"]:
        lines.append(f"⚠ BLOCKED on feature {result['blocked_on']}, which is still pending.")
    return "\n".join(lines)


def render_ranked(result, cfg):
    top = result["top"]
    lines = ["## Recommended Next Feature", ""]
    if result.get("warning"):
        lines += [f"⚠ {result['warning']}", ""]
    lines += [f"**#{top['number']} `{top['name']}`**", top["brief"], f"Full brief: {top['brief_file']}", "",
              f"**Priority:** {top['priority']}  **Effort:** {top['effort']}  **Area:** {top['area']}", "",
              "**Why this feature:**"]
    lines += [f"- {b}" for b in reason_bullets(top, cfg)]
    lines.append("")
    if result["use_spec"]:
        lines += [f"**Spec artifacts:** {'✅ Created' if top['artifacts_ready'] else '⬜ Not yet created'}", ""]
    if result["runners_up"]:
        lines += ["### Runners-up", ""]
        for r in result["runners_up"]:
            why = reason_bullets(r, cfg)
            lines.append(f"- #{r['number']} `{r['name']}` (score {r['score']}) — {why[0] if why else ''}")
        lines.append("")
    if result["blocked"]:
        lines += ["### Blocked (excluded from ranking)", ""]
        lines += [f"- #{b['number']} `{b['name']}` — blocked on feature {b['blocked_on']}" for b in result["blocked"]]
    print("\n".join(lines))


if __name__ == "__main__":
    main()
