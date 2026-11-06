#!/usr/bin/env python3
"""
Generate docs/loop.svg, the diagram of the loop in the README, from the table below.

    python3 tools/diagram.py           # write docs/loop.svg
    python3 tools/diagram.py --check   # exit 1 when the file is not what the table produces

Why a script and not a Mermaid block: GitHub measures Mermaid labels with one font and draws them with another,
so the longest skill names were cut off. Here the skill names are set in a monospace font, whose width is the
same everywhere, and every box is wider than its text. tests/test_skills.py fails when a skill is missing from
the table or when the committed file is out of date.
"""
import sys
from html import escape
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
OUT = KIT / "docs" / "loop.svg"

# group title, rows; a row is a list of (title, [skill names or notes]); `chain` draws arrows between neighbours.
GROUPS = [
    ("Backlog", [
        {"chain": True, "nodes": [
            ("import", ["backlog-import"]),
            ("plan", ["feature-plan", "bug-report"]),
            ("refine", ["features-triage", "bugs-triage"]),
            ("select", ["features-next", "bugs-next"])]},
    ]),
    ("Develop + verify", [
        {"chain": True, "nodes": [
            ("branch", ["gitflow"]),
            ("implement", ["feature-development", "bug-fix"]),
            ("review gate", ["code-reviewer", "database-reviewer", "security-reviewer"]),
            ("prove + sync docs", ["spec-compliance-check", "docs-sync"]),
            ("archive", ["features-archive", "bugs-archive"])]},
        {"under": "implement", "note": "unattended, over a list", "nodes": [
            ("batch", ["features-batch-development", "bugs-batch-fix"])]},
    ]),
    ("Ship", [
        {"chain": True, "nodes": [
            ("commit", ["you, or gitflow"]),
            ("PR", ["gitflow"]),
            ("review", ["you"]),
            ("merge", ["you"]),
            ("clean up", ["gitflow"])]},
    ]),
    ("Around the loop, any time", [
        {"nodes": [
            ("observe", ["features-status", "bugs-status", "backlog-report"]),
            ("decide", ["decision-record"]),
            ("advise", ["architecture-reviewer", "product-scope-roaster", "dependency-upgrade"])]},
    ]),
]

SANS = "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
MONO_W, SANS_W = 7.8, 8.2          # generous widths per character at 12px mono / 13px bold sans
PAD_X, GAP, ROW_GAP, GROUP_PAD, GROUP_HEAD, GROUP_GAP, MARGIN = 18, 40, 18, 18, 30, 40, 14
LINE_H, NODE_PAD_Y = 17, 11


def node_size(title, lines):
    w = max(len(title) * SANS_W, *(len(l) * MONO_W for l in lines)) + 2 * PAD_X
    return round(w), NODE_PAD_Y * 2 + LINE_H * (1 + len(lines))


def build():
    # lay out: x/y of every node and group
    placed, groups = {}, []
    y = MARGIN
    widths = []
    for gtitle, rows in GROUPS:
        row_w = []
        for row in rows:
            sizes = [node_size(t, l) for t, l in row["nodes"]]
            row_w.append(sum(s[0] for s in sizes) + GAP * (len(sizes) - 1))
        widths.append(max(row_w) + 2 * GROUP_PAD)
    canvas_w = max(widths) + 2 * MARGIN
    cx = canvas_w / 2
    parts = []
    for gi, (gtitle, rows) in enumerate(GROUPS):
        gw = widths[gi]
        gx = round(cx - gw / 2)
        gy = y
        ry = gy + GROUP_HEAD
        row_boxes = []
        for row in rows:
            sizes = [node_size(t, l) for t, l in row["nodes"]]
            rh = max(s[1] for s in sizes)
            total = sum(s[0] for s in sizes) + GAP * (len(sizes) - 1)
            x = round(cx - total / 2)
            if "under" in row:
                n = row["nodes"][0]
                x = round(placed[row["under"]][0] + placed[row["under"]][2] / 2 - sizes[0][0] / 2)
            boxes = []
            for (title, lines), (w, h) in zip(row["nodes"], sizes):
                top = ry + (rh - h) // 2
                boxes.append((title, lines, x, top, w, h))
                placed[title] = (x, top, w, h)
                x += w + GAP
            row_boxes.append((row, boxes, ry, rh))
            ry += rh + ROW_GAP
        gh = ry - ROW_GAP + GROUP_PAD - gy
        groups.append((gtitle, gx, gy, gw, gh, row_boxes))
        y = gy + gh + GROUP_GAP
    canvas_h = y - GROUP_GAP + MARGIN

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {round(canvas_w)} {round(canvas_h)}" width="{round(canvas_w)}" height="{round(canvas_h)}" role="img" aria-labelledby="t d">',
           '<title id="t">The loop</title>',
           f'<desc id="d">{escape(describe())}</desc>',
           '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#57606a"/></marker></defs>',
           f'<rect width="100%" height="100%" rx="10" fill="#ffffff"/>']
    for gi, (gtitle, gx, gy, gw, gh, row_boxes) in enumerate(groups):
        out.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="8" fill="#f6f8fa" stroke="#d0d7de"/>')
        out.append(f'<text x="{gx + 14}" y="{gy + 20}" font-family="{SANS}" font-size="13" font-weight="600" fill="#57606a">{escape(gtitle)}</text>')
        for row, boxes, ry, rh in row_boxes:
            for title, lines, x, top, w, h in boxes:
                out.append(f'<rect x="{x}" y="{top}" width="{w}" height="{h}" rx="6" fill="#ffffff" stroke="#8c959f"/>')
                tx = x + w / 2
                out.append(f'<text x="{tx:g}" y="{top + NODE_PAD_Y + 13}" text-anchor="middle" font-family="{SANS}" font-size="13" font-weight="600" fill="#1f2328">{escape(title)}</text>')
                for i, line in enumerate(lines):
                    out.append(f'<text x="{tx:g}" y="{top + NODE_PAD_Y + 13 + LINE_H * (i + 1)}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="#57606a">{escape(line)}</text>')
            if row.get("chain"):
                for (_, _, x1, t1, w1, h1), (_, _, x2, _, _, _) in zip(boxes, boxes[1:]):
                    ay = ry + rh // 2
                    out.append(f'<line x1="{x1 + w1}" y1="{ay}" x2="{x2 - 3}" y2="{ay}" stroke="#57606a" stroke-width="1.4" marker-end="url(#a)"/>')
            if "under" in row:
                title, lines, x, top, w, h = boxes[0]
                ux, uy, uw, uh = placed[row["under"]]
                mx = round(ux + uw / 2)
                out.append(f'<line x1="{mx}" y1="{top}" x2="{mx}" y2="{uy + uh + 3}" stroke="#57606a" stroke-width="1.4" stroke-dasharray="4 3" marker-end="url(#a)"/>')
                out.append(f'<text x="{mx + 10}" y="{(top + uy + uh) // 2 + 4}" font-family="{SANS}" font-size="12" fill="#57606a">{escape(row["note"])}</text>')
        if gi + 1 < len(groups) and gi + 1 < 3:          # the first three groups are the flow; the last one stands apart
            out.append(f'<line x1="{round(cx)}" y1="{gy + gh}" x2="{round(cx)}" y2="{gy + gh + GROUP_GAP - 3}" stroke="#57606a" stroke-width="1.4" marker-end="url(#a)"/>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def describe():
    return "; ".join(f"{g}: " + ", ".join(n for row in rows for _, names in row["nodes"] for n in names if "-" in n) for g, rows in GROUPS)


def skill_names():
    return {n for _, rows in GROUPS for row in rows for _, names in row["nodes"] for n in names}


if __name__ == "__main__":
    svg = build()
    if "--check" in sys.argv[1:]:
        current = OUT.read_text(encoding="utf-8") if OUT.is_file() else None
        if current != svg:
            print(f"{OUT.relative_to(KIT)} is out of date: run python3 tools/diagram.py")
            sys.exit(1)
        print("diagram is up to date")
    else:
        OUT.write_text(svg, encoding="utf-8", newline="\n")
        print(f"wrote {OUT.relative_to(KIT)}")
