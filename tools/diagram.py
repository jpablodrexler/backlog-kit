#!/usr/bin/env python3
"""
Generate docs/loop.svg (light) and docs/loop-dark.svg (dark), the diagram of the loop in the README, from the
table below. The README shows the one that matches the reader's GitHub theme (a <picture> element).

    python3 tools/diagram.py           # write both files
    python3 tools/diagram.py --check   # exit 1 when a file is not what the table produces

Why a script and not a Mermaid block: GitHub measures Mermaid labels with one font and draws them with another,
so the longest skill names were cut off. Here the skill names are set in a monospace font, whose width is the
same everywhere, and every box is wider than its text. tests/test_skills.py fails when a skill is missing from
the table or when the committed file is out of date.
"""
import sys
from html import escape
from types import SimpleNamespace
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
OUT = {"light": KIT / "docs" / "loop.svg", "dark": KIT / "docs" / "loop-dark.svg"}

# Backgrounds are transparent so the image blends with any GitHub theme of that kind (dark, dimmed, high contrast).
# The dark one follows docs/social-preview.svg: GitHub-dark surfaces with one coral accent, which marks the flow
# (stage titles, arrows, the way back to the start). The light one uses a deeper coral so it stays readable on white.
PALETTES = {
    "light": {"group": "#f6f8fa", "group_line": "#d0d7de", "node": "#ffffff", "node_line": "#d0d7de",
              "title": "#1f2328", "names": "#57606a", "group_title": "#b4492a", "muted_title": "#57606a",
              "arrow": "#c4573a"},
    "dark": {"group": "#0d1117", "group_line": "#30363d", "node": "#161b22", "node_line": "#30363d",
             "title": "#ffffff", "names": "#8b949e", "group_title": "#d97757", "muted_title": "#8b949e",
             "arrow": "#d97757"},
}

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
            ("observe", ["features-status", "bugs-status", "backlog-report", "backlog-forecast", "backlog-cycle"]),
            ("decide", ["decision-record"]),
            ("advise", ["architecture-reviewer", "product-scope-roaster", "dependency-upgrade"])]},
    ]),
]

SANS = "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
MONO_W, SANS_W = 8.4, 9.0          # generous widths per character at 13px mono / 14px bold sans
PAD_X, GAP, ROW_GAP, GROUP_PAD, GROUP_HEAD, GROUP_GAP, MARGIN = 20, 44, 20, 20, 36, 44, 16
LINE_H, NODE_PAD_Y = 19, 13
LOOP_BACK = 34                      # how far right of the stages the way back to the start runs
FLOW_GROUPS = 3                     # the first three groups are the flow; the last one stands apart


def node_size(title, lines):
    w = max(len(title) * SANS_W, *(len(l) * MONO_W for l in lines)) + 2 * PAD_X
    return round(w), NODE_PAD_Y * 2 + LINE_H * (1 + len(lines))


def build(theme="light"):
    c = SimpleNamespace(**PALETTES[theme])
    # lay out: x/y of every node and group; the stages are all as wide as the widest, and a chain of nodes is
    # spread over that width so the arrows between them have the same look everywhere
    placed, groups = {}, []
    y = MARGIN
    widths = []
    for gtitle, rows in GROUPS:
        row_w = []
        for row in rows:
            sizes = [node_size(t, l) for t, l in row["nodes"]]
            row_w.append(sum(s[0] for s in sizes) + GAP * (len(sizes) - 1))
        widths.append(max(row_w) + 2 * GROUP_PAD)
    group_w = max(widths)
    canvas_w = group_w + 2 * MARGIN + LOOP_BACK + 26
    cx = MARGIN + group_w / 2
    for gi, (gtitle, rows) in enumerate(GROUPS):
        gw = group_w
        gx = round(cx - gw / 2)
        gy = y
        ry = gy + GROUP_HEAD
        row_boxes = []
        for row in rows:
            sizes = [node_size(t, l) for t, l in row["nodes"]]
            rh = max(s[1] for s in sizes)
            gap = GAP
            if row.get("chain") and len(sizes) > 1:
                gap = (gw - 2 * GROUP_PAD - sum(s[0] for s in sizes)) / (len(sizes) - 1)
            total = sum(s[0] for s in sizes) + gap * (len(sizes) - 1)
            x = round(cx - total / 2)
            if "under" in row:
                x = round(placed[row["under"]][0] + placed[row["under"]][2] / 2 - sizes[0][0] / 2)
            boxes = []
            for (title, lines), (w, h) in zip(row["nodes"], sizes):
                boxes.append((title, lines, x, ry, w, rh))      # every node of a row is as tall as the row
                placed[title] = (x, ry, w, rh)
                x = round(x + w + gap)
            row_boxes.append((row, boxes, ry, rh))
            ry += rh + ROW_GAP
        gh = ry - ROW_GAP + GROUP_PAD - gy
        groups.append((gtitle, gx, gy, gw, gh, row_boxes))
        y = gy + gh + GROUP_GAP
    canvas_h = y - GROUP_GAP + MARGIN

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {round(canvas_w)} {round(canvas_h)}" width="{round(canvas_w)}" height="{round(canvas_h)}" role="img" aria-labelledby="t d">',
           '<title id="t">The loop</title>',
           f'<desc id="d">{escape(describe())}</desc>',
           f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{c.arrow}"/></marker></defs>',
           ]
    for gi, (gtitle, gx, gy, gw, gh, row_boxes) in enumerate(groups):
        out.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="14" fill="{c.group}" stroke="{c.group_line}" stroke-width="1.5"/>')
        flow = gi < FLOW_GROUPS
        out.append(f'<text x="{gx + 20}" y="{gy + 26}" font-family="{SANS}" font-size="13" font-weight="700" letter-spacing="1.2" fill="{c.group_title if flow else c.muted_title}">{escape(gtitle.upper())}</text>')
        for row, boxes, ry, rh in row_boxes:
            for title, lines, x, top, w, h in boxes:
                out.append(f'<rect x="{x}" y="{top}" width="{w}" height="{h}" rx="10" fill="{c.node}" stroke="{c.node_line}" stroke-width="1.5"/>')
                tx = x + w / 2
                base = top + (h - (14 + LINE_H * len(lines))) / 2 + 11      # first baseline, block centred in the node
                out.append(f'<text x="{tx:g}" y="{base:g}" text-anchor="middle" font-family="{SANS}" font-size="14" font-weight="600" fill="{c.title}">{escape(title)}</text>')
                for i, line in enumerate(lines):
                    out.append(f'<text x="{tx:g}" y="{base + LINE_H * (i + 1):g}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{c.names}">{escape(line)}</text>')
            if row.get("chain"):
                for (_, _, x1, t1, w1, h1), (_, _, x2, _, _, _) in zip(boxes, boxes[1:]):
                    ay = ry + rh // 2
                    out.append(f'<line x1="{x1 + w1}" y1="{ay}" x2="{x2 - 3}" y2="{ay}" stroke="{c.arrow}" stroke-width="2" marker-end="url(#a)"/>')
            if "under" in row:
                title, lines, x, top, w, h = boxes[0]
                ux, uy, uw, uh = placed[row["under"]]
                mx = round(ux + uw / 2)
                out.append(f'<line x1="{mx}" y1="{top}" x2="{mx}" y2="{uy + uh + 3}" stroke="{c.arrow}" stroke-width="2" stroke-dasharray="4 4" marker-end="url(#a)"/>')
                out.append(f'<text x="{mx + 10}" y="{(top + uy + uh) // 2 + 4}" font-family="{SANS}" font-size="13" fill="{c.names}">{escape(row["note"])}</text>')
        if gi + 1 < FLOW_GROUPS:          # the first three groups are the flow; the last one stands apart
            out.append(f'<line x1="{round(cx)}" y1="{gy + gh}" x2="{round(cx)}" y2="{gy + gh + GROUP_GAP - 3}" stroke="{c.arrow}" stroke-width="2" marker-end="url(#a)"/>')
    # the way back: after the clean up, the next item starts again in the Backlog
    first, last = groups[0], groups[FLOW_GROUPS - 1]
    rx_, y1, y0 = first[1] + first[3], last[2] + last[4] / 2, first[2] + first[4] / 2
    out.append(f'<path d="M{rx_} {y1:g} H{rx_ + LOOP_BACK} V{y0:g} H{rx_ + 3}" fill="none" stroke="{c.arrow}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#a)"/>')
    out.append(f'<text transform="translate({rx_ + LOOP_BACK + 20} {(y0 + y1) / 2:g}) rotate(-90)" text-anchor="middle" font-family="{SANS}" font-size="13" font-weight="600" letter-spacing="1" fill="{c.arrow}">NEXT ITEM</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def describe():
    return "; ".join(f"{g}: " + ", ".join(n for row in rows for _, names in row["nodes"] for n in names if "-" in n) for g, rows in GROUPS)


def skill_names():
    return {n for _, rows in GROUPS for row in rows for _, names in row["nodes"] for n in names}


if __name__ == "__main__":
    stale = []
    for theme, path in OUT.items():
        svg = build(theme)
        if "--check" in sys.argv[1:]:
            if (path.read_text(encoding="utf-8") if path.is_file() else None) != svg:
                stale.append(str(path.relative_to(KIT)))
        else:
            path.write_text(svg, encoding="utf-8", newline="\n")
            print(f"wrote {path.relative_to(KIT)}")
    if "--check" in sys.argv[1:]:
        if stale:
            print(f"out of date: {', '.join(stale)}: run python3 tools/diagram.py")
            sys.exit(1)
        print("diagram is up to date")
