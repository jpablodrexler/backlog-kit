#!/usr/bin/env python3
"""Mechanics for the personal brain: a folder of markdown notes.

Standard library only. Claude writes the notes (judgment); this script does the
counting, searching and bookkeeping (mechanics). It never runs git.

    python3 brain.py where
    python3 brain.py init
    python3 brain.py search <terms...> [--area A] [--tag T] [--limit N] [--json]
    python3 brain.py recent [--limit N]
    python3 brain.py index
    python3 brain.py check

The brain folder is --dir, else $BRAIN_DIR, else on Windows a "brain" folder inside
the OneDrive folder (when there is one), else ~/brain.
"""
import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

AREAS = ("projects", "topics", "decisions", "people", "journal", "inbox")
INDEX = "INDEX.md"
FRONT = re.compile(r"\A---\n(.*?)\n---\n?", re.S)
LINK = re.compile(r"\[[^\]]*\]\(([^)#\s]+\.md)(?:#[^)]*)?\)")

README = """# Brain

Personal notes that Claude reads and writes through the `brain` skill.
One note per subject, in markdown, with a short front matter.

| Folder | What goes in it |
|---|---|
| `projects/<project>/` | State, decisions, gotchas and next steps of one project |
| `topics/` | Things learned about a subject, reusable across projects |
| `decisions/` | A choice, the alternatives rejected and why |
| `people/` | Who someone is, what they own, how to work with them |
| `journal/` | `YYYY-MM-DD.md`, one dated entry per work session |
| `inbox/` | Raw captures not filed yet |

`INDEX.md` is generated (`brain.py index`); do not edit it by hand.
Never store credentials, tokens or personal data of third parties here.
"""


def norm(s):
    """Lowercase and strip accents, so 'decisión' matches 'decision'."""
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def onedrive_dir(env, home):
    """The synced OneDrive folder on Windows, or None. Personal account first, then work."""
    for var in ("OneDrive", "OneDriveConsumer", "OneDriveCommercial"):
        d = env.get(var)
        if d and Path(d).is_dir():
            return Path(d)
    d = home / "OneDrive"
    return d if d.is_dir() else None


def brain_dir(arg=None, env=None, platform=None, home=None):
    env = os.environ if env is None else env
    platform = sys.platform if platform is None else platform
    home = home or Path.home()
    if arg or env.get("BRAIN_DIR"):
        return Path(arg or env["BRAIN_DIR"]).expanduser()
    if platform.startswith(("win", "cygwin", "msys")):
        od = onedrive_dir(env, home)
        if od:
            return od / "brain"
    return home / "brain"


def parse(text):
    """-> (meta dict, body). Understands `key: value` and `tags: [a, b]` / `tags: a, b`."""
    m = FRONT.match(text)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        k = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if k:
            meta[k.group(1).lower()] = k.group(2).strip().strip("\"'")
    return meta, text[m.end():]


def tags_of(meta):
    raw = meta.get("tags", "").strip("[]")
    return [t.strip().strip("\"'") for t in raw.split(",") if t.strip()]


def load(root):
    notes = []
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root)
        if rel.name in (INDEX, "README.md") and len(rel.parts) == 1:
            continue
        if any(part.startswith(".") for part in rel.parts):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        meta, body = parse(text)
        title = meta.get("title") or next((l.lstrip("# ").strip() for l in body.splitlines() if l.startswith("#")), rel.stem)
        notes.append({"path": rel.as_posix(), "title": title, "summary": meta.get("summary", ""),
                      "tags": tags_of(meta), "updated": meta.get("updated") or meta.get("created", ""),
                      "mtime": p.stat().st_mtime, "meta": meta, "body": body, "text": text})
    return notes


def score(note, terms):
    """Weighted substring match over title, tags, summary, path and body. 0 = no match."""
    fields = (("title", 5), ("tags", 4), ("summary", 3), ("path", 2))
    hay = {"title": norm(note["title"]), "tags": norm(" ".join(note["tags"])),
           "summary": norm(note["summary"]), "path": norm(note["path"])}
    body = norm(note["body"])
    total = hit_terms = 0
    for t in terms:
        s = sum(w for f, w in fields if t in hay[f]) + min(3, body.count(t))
        total += s
        hit_terms += 1 if s else 0
    return total + (3 * hit_terms if hit_terms == len(terms) else 0) if hit_terms else 0


def snippets(note, terms, n=2):
    out = []
    for line in note["body"].splitlines():
        if line.strip() and any(t in norm(line) for t in terms):
            out.append(line.strip()[:160])
            if len(out) == n:
                break
    return out


def cmd_where(a):
    root = brain_dir(a.dir)
    print(root)
    print("exists" if root.is_dir() else "missing: run `brain.py init`")


def cmd_init(a):
    root = brain_dir(a.dir)
    created = []
    for area in AREAS:
        d = root / area
        if not d.exists():
            d.mkdir(parents=True)
            (d / ".gitkeep").touch()
            created.append(area + "/")
    if not (root / "README.md").exists():
        (root / "README.md").write_text(README, encoding="utf-8")
        created.append("README.md")
    cmd_index(a, quiet=True)
    print(f"brain at {root}")
    print("created: " + (", ".join(created) if created else "nothing, it already existed"))


def cmd_search(a):
    root = brain_dir(a.dir)
    terms = [norm(t) for t in a.terms if len(t) > 1]
    if not terms:
        sys.exit("give at least one search term")
    found = []
    for n in load(root):
        if a.area and not n["path"].startswith(a.area.strip("/") + "/"):
            continue
        if a.tag and norm(a.tag) not in [norm(t) for t in n["tags"]]:
            continue
        s = score(n, terms)
        if s:
            found.append((s, n))
    found.sort(key=lambda x: (-x[0], x[1]["path"]))
    found = found[:a.limit]
    if a.json:
        print(json.dumps([{"path": n["path"], "title": n["title"], "summary": n["summary"], "tags": n["tags"],
                           "updated": n["updated"], "score": s, "snippets": snippets(n, terms)} for s, n in found],
                         ensure_ascii=False, indent=2))
        return
    if not found:
        print("no notes match")
        return
    for s, n in found:
        print(f"{n['path']}  [{s}]  {n['title']}")
        if n["summary"]:
            print(f"    {n['summary']}")
        for sn in snippets(n, terms):
            print(f"    > {sn}")


def cmd_recent(a):
    notes = sorted(load(brain_dir(a.dir)), key=lambda n: (n["updated"], n["mtime"]), reverse=True)[:a.limit]
    for n in notes:
        print(f"{n['updated'] or '----------'}  {n['path']}  {n['title']}")


def cmd_index(a, quiet=False):
    root = brain_dir(a.dir)
    notes = load(root)
    groups = {}
    for n in notes:
        groups.setdefault(n["path"].split("/")[0] if "/" in n["path"] else ".", []).append(n)
    lines = ["# Index", "", "Generated by `brain.py index`; do not edit by hand.", ""]
    for g in sorted(groups, key=lambda g: (g not in AREAS, AREAS.index(g) if g in AREAS else 0, g)):
        lines.append(f"## {g if g != '.' else 'root'}")
        for n in groups[g]:
            tags = f" `{'` `'.join(n['tags'])}`" if n["tags"] else ""
            summ = f" — {n['summary']}" if n["summary"] else ""
            lines.append(f"- [{n['title']}]({n['path']}){summ}{tags}")
        lines.append("")
    root.mkdir(parents=True, exist_ok=True)
    (root / INDEX).write_text("\n".join(lines), encoding="utf-8")
    if not quiet:
        print(f"{INDEX}: {len(notes)} notes")


def cmd_check(a):
    root = brain_dir(a.dir)
    notes = load(root)
    paths = {n["path"] for n in notes}
    problems = []
    titles = {}
    for n in notes:
        if not n["meta"]:
            problems.append(f"{n['path']}: no front matter")
        else:
            for k in ("title", "summary"):
                if not n["meta"].get(k):
                    problems.append(f"{n['path']}: missing `{k}`")
        titles.setdefault(norm(n["title"]), []).append(n["path"])
        base = Path(n["path"]).parent
        for target in LINK.findall(n["text"]):
            if "://" in target:
                continue
            if os.path.normpath((base / target).as_posix()).replace("\\", "/") not in paths:
                problems.append(f"{n['path']}: broken link {target}")
    for t, ps in titles.items():
        if len(ps) > 1:
            problems.append("same title in " + ", ".join(ps))
    idx = root / INDEX
    if not idx.is_file() or any(f"]({p})" not in idx.read_text(encoding="utf-8") for p in paths):
        problems.append(f"{INDEX} is stale: run `brain.py index`")
    print("\n".join(problems) if problems else f"ok: {len(notes)} notes")
    sys.exit(1 if problems else 0)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", help="brain folder (default $BRAIN_DIR or ~/brain)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("where").set_defaults(fn=cmd_where)
    sub.add_parser("init").set_defaults(fn=cmd_init)
    s = sub.add_parser("search")
    s.add_argument("terms", nargs="+")
    s.add_argument("--area")
    s.add_argument("--tag")
    s.add_argument("--limit", type=int, default=8)
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_search)
    r = sub.add_parser("recent")
    r.add_argument("--limit", type=int, default=10)
    r.set_defaults(fn=cmd_recent)
    sub.add_parser("index").set_defaults(fn=cmd_index)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
