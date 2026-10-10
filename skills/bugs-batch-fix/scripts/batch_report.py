#!/usr/bin/env python3
# VENDORED from lib/batch_report.py — do not edit here; edit the source and run `python3 tools/vendor.py`.
"""
The batch run's resumable progress report — written after EVERY status change,
never accumulated in memory, so a crash, a cutoff or a power loss leaves an
accurate trace of what finished and what was underway.

Subcommands (all print JSON):

  find   <root> --kind bugs|features --items a,b,c
         Look for an unfinished report from an earlier run that overlaps this list.
         match = exact | near | partial | none  (Jaccard overlap of the requested sets).
         Only a report with an item still `not-started` or `in-progress` is resumable.
  init   <root> --kind K --branch B --items a,b,c
         Create a new report (a same-day name collision gets -2, -3, ...); every item
         starts as `⬜ Not started`.
  set    <report> --id X --status S [--summary "..."]
         Change one entry in place (atomic write). Statuses:
           not-started in-progress closed completed cannot-reproduce left-open blocked skipped
  finish <report>
         Append (or refresh) the Run Summary footer with counts and an end time.
  show   <report>
         Parse a report back into JSON.

Never edits anything but the report file. Set BACKLOG_KIT_NOW=YYYY-MM-DD HH:MM to fix
the clock (tests).
"""
import argparse
import datetime
import os
import re
import sys
from pathlib import Path

_here = Path(__file__).resolve()
for _cand in (_here.parent, _here.parents[3] / "lib"):
    if (_cand / "backlog_kit.py").is_file():
        sys.path.insert(0, str(_cand))
        break
import backlog_kit as bk

KINDS = {
    "bugs": {"title": "Bug Batch Fix Report", "prefix": "BUG_BATCH_REPORT_", "dir": "bug-batch", "done": "closed"},
    "features": {"title": "Feature Batch Development Report", "prefix": "FEATURE_BATCH_REPORT_", "dir": "feature-batch", "done": "completed"},
}
LABEL = {
    "not-started": "⬜ Not started", "in-progress": "🔄 In progress",
    "closed": "✅ Closed", "completed": "✅ Completed",
    "cannot-reproduce": "❓ Cannot reproduce", "left-open": "⚠ Left open",
    "blocked": "⚠ Blocked", "skipped": "⏭ Skipped",
}
ENTRY_RE = re.compile(r"^- \[( |x)\] \*\*(.+?)\*\* — (.*)$")


def now():
    fixed = os.environ.get("BACKLOG_KIT_NOW")
    return datetime.datetime.strptime(fixed, "%Y-%m-%d %H:%M") if fixed else datetime.datetime.now()


def status_of(text):
    for key, label in LABEL.items():
        if text.startswith(label):
            return key
    return "not-started"


def parse(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    info = {"path": str(path), "branch": "", "requested": [], "items": [], "ended": None}
    for ln in lines:
        if ln.startswith("**Branch:**"):
            info["branch"] = ln.split("**Branch:**", 1)[1].strip()
        elif ln.startswith("**Requested:**"):
            info["requested"] = [s.strip() for s in ln.split("**Requested:**", 1)[1].split(",") if s.strip()]
        elif ln.startswith("**Ended:**"):
            info["ended"] = ln.split("**Ended:**", 1)[1].strip()
        m = ENTRY_RE.match(ln)
        if m:
            info["items"].append({"id": m.group(2), "status": status_of(m.group(3)), "text": m.group(3)})
    return info


def write_atomic(path, text):
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def reports_dir(root, kind):
    cfg = bk.load_config(root)
    return bk.Paths(root, cfg).reports / KINDS[kind]["dir"]


# A blocked item is retried on resume, so it keeps a finished run resumable.
RETRYABLE = ("not-started", "in-progress", "blocked")


def cmd_find(a):
    k = KINDS[a.kind]
    want = set(a.items.split(","))
    best = None
    d = reports_dir(a.repo_root, a.kind)
    for f in sorted(d.glob(f"{k['prefix']}*.md")) if d.is_dir() else []:
        info = parse(f)
        have = set(info["requested"])
        if not have or not any(i["status"] in RETRYABLE for i in info["items"]):
            continue
        jac = len(have & want) / len(have | want)
        if jac == 0:
            continue
        cls = "exact" if have == want else "near" if jac >= 0.8 else "partial"
        cand = {"match": cls, "overlap": round(jac, 2), "path": str(f), "branch": info["branch"],
                "done": [i["id"] for i in info["items"] if i["status"] in (k["done"], "cannot-reproduce")],
                "remaining": [i["id"] for i in info["items"] if i["status"] in RETRYABLE]}
        if best is None or cand["overlap"] >= best["overlap"]:
            best = cand
    bk.emit(best or {"match": "none"})


def cmd_init(a):
    k = KINDS[a.kind]
    d = reports_dir(a.repo_root, a.kind)
    d.mkdir(parents=True, exist_ok=True)
    t = now()
    path = d / f"{k['prefix']}{t:%Y-%m-%d}.md"
    n = 2
    while path.exists():
        path = d / f"{k['prefix']}{t:%Y-%m-%d}-{n}.md"
        n += 1
    ids = [s for s in a.items.split(",") if s]
    lines = [f"# {k['title']} — {t:%Y-%m-%d}", "",
             f"**Branch:** {a.branch}", f"**Requested:** {', '.join(ids)}", f"**Started:** {t:%Y-%m-%d %H:%M}", "",
             "## Progress", ""]
    lines += [f"- [ ] **{i}** — {LABEL['not-started']}" for i in ids]
    lines.append("")
    write_atomic(path, "\n".join(lines))
    bk.emit({"path": str(path)})


def cmd_set(a):
    k = next(v for v in KINDS.values() if Path(a.report).name.startswith(v["prefix"]))
    lines = Path(a.report).read_text(encoding="utf-8").splitlines()
    hit = False
    for i, ln in enumerate(lines):
        m = ENTRY_RE.match(ln)
        if m and m.group(2) == a.id:
            hit = True
            label = LABEL[a.status]
            when = f" {now():%H:%M}" if a.status in ("closed", "completed") else ""
            tail = f" — {a.summary}" if a.summary else ""
            mark = "x" if a.status in ("closed", "completed") else " "
            lines[i] = f"- [{mark}] **{a.id}** — {label}{when}{tail}"
    if not hit:
        bk.emit({"error": f"{a.id} is not an entry in {a.report}"})
        sys.exit(1)
    write_atomic(a.report, "\n".join(lines) + "\n")
    bk.emit({"ok": True, "id": a.id, "status": a.status})


def cmd_finish(a):
    info = parse(a.report)
    k = next(v for v in KINDS.values() if Path(a.report).name.startswith(v["prefix"]))
    c = {s: 0 for s in LABEL}
    for it in info["items"]:
        c[it["status"]] += 1
    done = c[k["done"]]
    blocked = c["blocked"] + c["skipped"] + c["left-open"]
    not_reached = c["not-started"] + c["in-progress"]
    noun = "Closed" if k["done"] == "closed" else "Completed"
    text = Path(a.report).read_text(encoding="utf-8")
    text = re.split(r"\n## Run Summary", text)[0].rstrip("\n")
    footer = ["", "", "## Run Summary", "", f"**Ended:** {now():%Y-%m-%d %H:%M}",
              f"**{noun}:** {done}/{len(info['items'])}  **Cannot reproduce:** {c['cannot-reproduce']}  "
              f"**Blocked/Skipped:** {blocked}  **Not reached:** {not_reached}", ""]
    write_atomic(a.report, text + "\n".join(footer))
    bk.emit({"requested": len(info["items"]), "done": done, "cannot_reproduce": c["cannot-reproduce"],
             "blocked_or_skipped": blocked, "not_reached": not_reached})


def cmd_show(a):
    bk.emit(parse(a.report))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("find", "init"):
        s = sub.add_parser(name)
        s.add_argument("repo_root")
        s.add_argument("--kind", required=True, choices=list(KINDS))
        s.add_argument("--items", required=True)
        if name == "init":
            s.add_argument("--branch", required=True)
    s = sub.add_parser("set")
    s.add_argument("report")
    s.add_argument("--id", required=True)
    s.add_argument("--status", required=True, choices=list(LABEL))
    s.add_argument("--summary", default="")
    for name in ("finish", "show"):
        s = sub.add_parser(name)
        s.add_argument("report")
    a = ap.parse_args()
    {"find": cmd_find, "init": cmd_init, "set": cmd_set, "finish": cmd_finish, "show": cmd_show}[a.cmd](a)


if __name__ == "__main__":
    main()
