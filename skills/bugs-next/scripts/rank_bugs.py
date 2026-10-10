#!/usr/bin/env python3
"""
Score and rank actionable bugs from bugs-open.md per bugs-next's steps 2-3:

    In Progress (+1000) > Severity (n*100 .. 100, from the configured order)
    > production-facing environment (+20) > listed in the Recommended fix
    order (+10)

with tie-breaks: earlier fix-order position, then lower bug number.

Only computes the ranking — never asks the user anything and never returns a
final decision; bugs-next still owns the mandatory confirmation.

Usage:
    python3 rank_bugs.py <repo-root> [--select <ID>] [--json]
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


def fail(msg):
    bk.emit({"error": msg})
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root")
    ap.add_argument("--select", help="a Bug ID to resolve directly, skipping scoring")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cfg = bk.load_config(args.repo_root)
    p = bk.Paths(args.repo_root, cfg)
    b_cfg = cfg["bugs"]
    prefix = b_cfg["id_prefix"]

    lines = bk.read_lines(p.bugs_open)
    if lines is None:
        fail("bugs-open.md not found — run bug-report first")
    table = bk.find_table(lines, "## Bug List")
    if not table:
        fail("no ## Bug List table in bugs-open.md")
    header, rows = table
    all_rows = [bk.row_dict(header, r, "Bug ID") for r in rows]

    fix_order = bk.order_list_positions(lines, "## Recommended fix order", rf"^\s*-\s*({re.escape(prefix)}-\d+)")

    candidates, seen, duplicates, missing_files = [], set(), set(), []
    for r in all_rows:
        status = r.get("Status", "")
        if "Open" in status or "In Progress" in status:
            bug_id = r.get("Bug ID", "").strip()
            if bug_id in seen:
                duplicates.add(bug_id)
            seen.add(bug_id)
            if not (p.bugs_dir / f"{bug_id}.md").is_file():
                missing_files.append(bug_id)
            candidates.append({
                "id": bug_id,
                "severity": r.get("Severity", "").strip(),
                "area": r.get("Area", "").strip(),
                "environment": r.get("Environment", "").strip(),
                "in_progress": "In Progress" in status,
                "summary": r.get("Summary", "").strip(),
            })
    if not candidates:
        fail("no open or in-progress bugs in the backlog")

    def score(c):
        s = 1000 if c["in_progress"] else 0
        s += bk.tier_score(c["severity"], b_cfg["severities"])
        if c["environment"] in b_cfg["prod_environments"]:
            s += 20
        if fix_order.get(c["id"]) is not None:
            s += 10
        return s

    if args.select:
        sel = args.select.strip().upper()
        match = next((c for c in candidates if c["id"].upper() == sel), None)
        if not match:
            fail(f"'{args.select}' does not match an Open/In Progress bug")
        result = {"selected": match, "duplicate": sel in {d.upper() for d in duplicates}}
        print(json.dumps(result, indent=2) if args.json else render_selected(result))
        return

    ranked = []
    for c in candidates:
        e = dict(c)
        e["score"] = score(c)
        e["order_position"] = fix_order.get(c["id"])
        ranked.append(e)

    def num(c):
        tail = c["id"].rsplit("-", 1)[-1]
        return int(tail) if tail.isdigit() else 10 ** 9

    ranked.sort(key=lambda c: (-c["score"],
                               c["order_position"] if c["order_position"] is not None else 10 ** 9,
                               num(c)))
    result = {"top": ranked[0], "runners_up": ranked[1:4]}
    warnings = []
    if duplicates:
        warnings.append(f"Duplicate Bug ID(s) in bugs-open.md: {', '.join(sorted(duplicates))} — run bugs-status for the full integrity report.")
    if missing_files:
        warnings.append(f"No bugs/ details file for {', '.join(missing_files)} — run bugs-status for the full integrity report.")
    if warnings:
        result["warning"] = " ".join(warnings)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        render_ranked(result, cfg)


def reason_bullets(c, cfg):
    b = cfg["bugs"]
    out = []
    if c["in_progress"]:
        out.append("🔶 Already in progress — resuming beats starting a new one")
    label = b["severity_labels"].get(c["severity"])
    reason = f"{c['severity']} — {label}" if label else (c["severity"] or "no explicit severity")
    if c["environment"] in b["prod_environments"]:
        reason += f", reproduces on {c['environment']}"
    out.append(reason)
    if c.get("order_position"):
        out.append(f"position {c['order_position']} in the Recommended fix order")
    return out


def render_selected(result):
    m = result["selected"]
    out = [f"{m['id']} — {m['summary']}"]
    if result["duplicate"]:
        out.append(f"⚠ {m['id']} appears more than once in bugs-open.md's Bug List table.")
    return "\n".join(out)


def render_ranked(result, cfg):
    top = result["top"]
    L = ["## Recommended Next Bug", ""]
    if result.get("warning"):
        L += [f"⚠ {result['warning']}", ""]
    L += [f"**{top['id']}**", top["summary"], "",
          f"**Severity:** {top['severity']}  **Area:** {top['area']}  **Environment:** {top['environment']}", "",
          "**Why this bug:**"]
    L += [f"- {b}" for b in reason_bullets(top, cfg)]
    L.append("")
    if result["runners_up"]:
        L += ["### Runners-up", ""]
        L += [f"- {r['id']} (score {r['score']}) — {reason_bullets(r, cfg)[0]}" for r in result["runners_up"]]
    print("\n".join(L))


if __name__ == "__main__":
    main()
