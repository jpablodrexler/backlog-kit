#!/usr/bin/env python3
"""
Fidelity check: how much of the original project skills' text survives in a kit skill,
and whether every difference is on record.

The kit's skills are derived from the workflow skills of two projects. Each original
is snapshotted under `fidelity/base/<project>/<skill>/` (markdown only). A ledger at
`fidelity/ledgers/<skill>.md` records every deliberate difference. For each logical unit
(paragraph, list item, heading, table row, code line) of the originals, after the
ledger's `sub:` substitutions are applied, this tool decides:

    KEPT     the unit appears verbatim in the kit skill
    VARIANT  the other project's near-identical twin of this unit is KEPT (the projects differ here
             and the kit follows one of them); listed by --variants, needs no entry
    EDITED   a close but not identical unit exists (ratio >= 0.6): needs a PARAM or COND entry
    ABSENT   nothing close exists: needs a MOVED or DROPPED entry

and fails (--check) when an EDITED or ABSENT unit has no ledger entry, when a ledger entry
no longer matches any unit, or when an entry's status contradicts what the tool finds.
Kit text with no origin is listed by --added, so invented text is visible too.

Ledger format (`fidelity/ledgers/<skill>.md`), one record per line, anything else is prose:

    kit: skills/features-next
    sub: JPPhotoManagerWeb/docs/backlog => <backlog>
    PARAM | <first 70 chars of the original unit> | why, and the decision id
    COND  | ...        kept, but only under a config condition
    MOVED | ...        now lives in a script, a shared phase or a project-owned document
    DROPPED | ...      removed, with the reason

Usage:
    python3 tools/fidelity.py [skill ...] [--check] [--init] [--added] [--variants]
    python3 tools/fidelity.py --snapshot --from NAME=/path/to/skills [--from ...] [skill ...]
"""
import argparse
import difflib
import re
import shutil
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
FID = KIT / "fidelity"

STATUSES = ("PARAM", "COND", "MOVED", "DROPPED")


def projects():
    """Each directory under fidelity/base is one source project; its tag is the initial of its name."""
    base = FID / "base"
    return {d.name: d.name[0].upper() for d in sorted(base.iterdir()) if d.is_dir()} if base.is_dir() else {}
MIN_LEN = 12
EDIT_RATIO = 0.6


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def units(text):
    """Logical blocks of a markdown file, whitespace-normalised."""
    out, buf, fence = [], [], False

    def flush():
        if buf:
            out.append(norm(" ".join(buf)))
            buf.clear()

    for raw in text.splitlines():
        line = raw.rstrip()
        if line.lstrip().startswith("```"):
            flush()
            fence = not fence
            continue
        if fence:
            if line.strip():
                out.append(norm(line))
            continue
        s = line.strip()
        if not s:
            flush()
        elif re.match(r"^(#{1,6}\s|\|)", s) or s in ("---", "<!--") or s.startswith("<!--"):
            flush()
            out.append(norm(s))
        elif re.match(r"^([-*+]|\d+[.)])\s", s) or s.startswith(">"):
            flush()
            buf.append(s)
        else:
            buf.append(s)
    flush()
    return [u for u in out if len(u) >= MIN_LEN and u != "---"]


def read_md(d):
    parts = []
    for f in sorted(Path(d).rglob("*.md")):
        parts.append(f.read_text(encoding="utf-8", errors="replace"))
    return "\n\n".join(parts)


class Ledger:
    def __init__(self, path):
        self.kit = None
        self.subs = []
        self.entries = []   # (status, fingerprint, note)
        for ln in Path(path).read_text(encoding="utf-8").splitlines():
            if ln.startswith("kit:"):
                self.kit = ln.split(":", 1)[1].strip()
            elif ln.startswith("sub:"):
                a, _, b = ln[4:].partition("=>")
                self.subs.append((a.strip(), b.strip()))
            else:
                m = re.match(r"^(PARAM|COND|MOVED|DROPPED)\s*\|\s*(.*?)\s*\|\s*(.*)$", ln)
                if m:
                    self.entries.append((m.group(1), norm(m.group(2)), m.group(3)))

    def apply(self, unit):
        for a, b in self.subs:
            unit = unit.replace(a, b)
        return unit


def sim(a, b):
    """Similarity of two units over words, so a long paragraph with a few edits stays recognisable."""
    return difflib.SequenceMatcher(None, a.split(), b.split(), autojunk=False).ratio()


def fingerprint(unit, seen):
    fp = unit[:70].rstrip().replace("|", "¦")   # '|' separates the ledger fields
    n = seen.get(fp, 0) + 1
    seen[fp] = n
    return fp if n == 1 else f"{fp} #{n}"


def analyse(skill):
    ledger_path = FID / "ledgers" / f"{skill}.md"
    ledger = Ledger(ledger_path) if ledger_path.is_file() else Ledger.__new__(Ledger)
    if not ledger_path.is_file():
        ledger.kit, ledger.subs, ledger.entries = f"skills/{skill}", [], []
    kit_text = read_md(KIT / ledger.kit)
    kit_units = units(kit_text)
    blob = " ".join(kit_units)
    base = {}
    for project, tag in projects().items():
        d = FID / "base" / project / skill
        if d.is_dir():
            for u in units(read_md(d)):
                u = ledger.apply(u)
                base.setdefault(u, set()).add(tag)
    results, seen = [], {}
    for u, tags in base.items():
        fp = fingerprint(u, seen)
        if u in blob:
            status, ratio = "KEPT", 1.0
        else:
            best = max((sim(u, k) for k in kit_units), default=0.0)
            ratio = best
            status = "EDITED" if best >= EDIT_RATIO else "ABSENT"
        results.append((fp, u, "".join(sorted(tags)), status, ratio))
    # A unit that differs from its twin in the other project is covered when the kit keeps that twin.
    kept = [(u, t) for fp, u, t, st, _ in results if st == "KEPT"]
    fixed = []
    for fp, u, t, st, ratio in results:
        if st in ("EDITED", "ABSENT"):
            for v, vt in kept:
                if set(vt).isdisjoint(t) and sim(u, v) >= 0.8:
                    st = "VARIANT"
                    break
        fixed.append((fp, u, t, st, ratio))
    results = fixed
    base_units = list(base)
    added = []
    for k in kit_units:
        grown = [b for b in base_units if len(b) >= 40 and b in k and len(k) - len(b) >= 12]
        if grown:
            # Text added inside or around an otherwise verbatim unit would be invisible; show it.
            added.append("(extends an original unit) " + k.replace(max(grown, key=len), "", 1).strip())
            continue
        if any(k in b or b in k for b in base_units):
            continue
        best = max((sim(k, b) for b in base_units), default=0.0)
        if best < EDIT_RATIO:
            added.append(k)
    return ledger, results, added


def check(skill, ledger, results):
    problems = []
    recorded = {fp: (st, note) for st, fp, note in ledger.entries}
    fps = {fp for fp, *_ in results}
    for fp, u, tags, status, ratio in results:
        if status in ("KEPT", "VARIANT"):
            if fp in recorded and status == "KEPT":
                problems.append(f"{skill}: ledger lists a unit that is kept verbatim: {fp!r}")
        elif fp not in recorded:
            problems.append(f"{skill}: {status} with no ledger entry ({tags}): {fp!r}")
        else:
            st = recorded[fp][0]
            if status == "EDITED" and st not in ("PARAM", "COND"):
                problems.append(f"{skill}: edited unit recorded as {st}, expected PARAM or COND: {fp!r}")
            if status == "ABSENT" and st not in ("MOVED", "DROPPED"):
                problems.append(f"{skill}: absent unit recorded as {st}, expected MOVED or DROPPED: {fp!r}")
    for st, fp, note in ledger.entries:
        if fp not in fps:
            problems.append(f"{skill}: stale ledger entry (no such original unit): {fp!r}")
        if not note.strip():
            problems.append(f"{skill}: ledger entry without a reason: {fp!r}")
    return problems


def snapshot(skill, sources):
    """Copy a skill's markdown and scripts from each `name=path` source into fidelity/base/<name>/<skill>."""
    for name, src in sources.items():
        d = Path(src) / skill
        if not d.is_dir():
            continue
        dest = FID / "base" / name / skill
        if dest.exists():
            shutil.rmtree(dest)
        for f in d.rglob("*"):
            if f.is_file() and f.suffix in (".md", ".py"):
                t = dest / f.relative_to(d)
                t.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(f, t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skills", nargs="*")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--init", action="store_true", help="print ledger lines for every unrecorded difference")
    ap.add_argument("--added", action="store_true", help="list kit text with no origin")
    ap.add_argument("--variants", action="store_true", help="list units where the projects differ and the kit follows one")
    ap.add_argument("--snapshot", action="store_true", help="copy the originals into fidelity/base (needs --from)")
    ap.add_argument("--from", dest="sources", action="append", default=[], metavar="NAME=SKILLS_DIR",
                    help="a source project's skills folder, repeatable")
    a = ap.parse_args()
    skills = a.skills or sorted(p.stem for p in (FID / "ledgers").glob("*.md"))
    if a.snapshot:
        sources = dict(x.split("=", 1) for x in a.sources)
        for s in skills:
            snapshot(s, sources)
        return
    failed = []
    print(f"{'skill':24} {'units':>6} {'kept':>6} {'variant':>8} {'edited':>7} {'absent':>7} {'added':>6}")
    for s in skills:
        ledger, results, added = analyse(s)
        n = len(results)
        kept = sum(1 for r in results if r[3] == "KEPT")
        ed = sum(1 for r in results if r[3] == "EDITED")
        ab = sum(1 for r in results if r[3] == "ABSENT")
        var = sum(1 for r in results if r[3] == "VARIANT")
        print(f"{s:24} {n:>6} {(kept / n if n else 0):>5.0%} {var:>8} {ed:>7} {ab:>7} {len(added):>6}")
        if a.variants:
            for fp, u, tags, st, ratio in results:
                if st == "VARIANT":
                    print(f"  VARIANT ({tags}): {u[:150]}")
        if a.init:
            rec = {fp for _, fp, _ in ledger.entries}
            for fp, u, tags, status, ratio in results:
                if status in ("EDITED", "ABSENT") and fp not in rec:
                    print(f"{'PARAM' if status == 'EDITED' else 'DROPPED'} | {fp} | TODO ({tags}, {status} {ratio:.2f})")
        if a.added:
            for k in added:
                print(f"  ADDED: {k[:140]}")
        failed += check(s, ledger, results)
    if a.check:
        for p in failed:
            print("FAIL", p)
        sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
