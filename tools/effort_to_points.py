#!/usr/bin/env python3
"""
Convert the Effort column of a backlog from t-shirt sizes to story points (backlog-kit 0.5.0).

    python3 tools/effort_to_points.py <repo-root>             # rewrite the backlog files
    python3 tools/effort_to_points.py <repo-root> --dry-run   # only report what would change

Mapping: S=1, M=3, L=5, XL=8. The Effort column of the Feature List table of
`features-planned.md` and `features-implemented.md` is found by its header name, a numeric value
is left alone, and the `- **Effort**:` line of the Column legend is replaced. Anything else is
untouched, and a second run changes nothing. The backlog folder is `docs/backlog` unless
`.backlog-kit.toml` sets `[paths] backlog_dir`.
"""
import argparse
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "lib"))
import backlog_kit as bk  # noqa: E402

MAPPING = {"S": "1", "M": "3", "L": "5", "XL": "8"}
LEGEND_TEXT = ("story points on the Fibonacci scale `1` / `2` / `3` / `5` / `8` / `13`; "
               "`8` or more is too large for one story: a candidate for splitting into several features")
LEGEND_RE = re.compile(r"^- \*\*Effort\*\*(\s*[:—])")      # "- **Effort**: ..." or "- **Effort** — ..."


def convert_file(path):
    """Return (new_text, converted_cells, unknown_values, legend_replaced) for one features file."""
    with open(path, encoding="utf-8", newline="") as fh:         # keep the file's own line endings
        raw = fh.read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(nl)
    converted, unknown, legend = 0, [], False
    i = 0
    while i < len(lines):
        if lines[i].startswith("|") and "Effort" in lines[i]:
            header = bk.split_row(lines[i])
            if "Effort" in header:
                col = header.index("Effort")
                j = i + 2                                   # skip the separator row
                while j < len(lines) and lines[j].startswith("|"):
                    cells = re.split(r"(?<!\\)\|", lines[j])    # cells[0] and cells[-1] are the outer empties
                    k = col + 1
                    value = cells[k].strip()
                    if value in MAPPING:
                        trailing = len(cells[k]) - len(cells[k].rstrip())
                        # a column padded for alignment keeps its width; a tight cell stays " v "
                        cells[k] = (" " + MAPPING[value]).ljust(len(cells[k])) if trailing > 1 else f" {MAPPING[value]} "
                        lines[j] = "|".join(cells)
                        converted += 1
                    elif value and not value.isdigit():
                        unknown.append(value)
                    j += 1
                i = j
                continue
        m = LEGEND_RE.match(lines[i])
        if m:
            new = f"- **Effort**{m.group(1)} {LEGEND_TEXT}"
            if lines[i] != new:
                lines[i] = new
                legend = True
        i += 1
    return nl.join(lines), converted, unknown, legend


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    paths = bk.Paths(a.repo_root, bk.load_config(a.repo_root))
    total = 0
    for p in (paths.features_planned, paths.features_implemented):
        if not p.is_file():
            print(f"{p}: not found, skipped")
            continue
        text, converted, unknown, legend = convert_file(p)
        total += converted
        note = f"{converted} Effort cell(s) converted" + (", legend updated" if legend else "")
        if unknown:
            note += f"; left as is (not a known size): {sorted(set(unknown))}"
        print(f"{p.name}: {note}")
        if not a.dry_run and (converted or legend):
            p.write_text(text, encoding="utf-8", newline="")
    print(("would convert " if a.dry_run else "converted ") + f"{total} cell(s)")


if __name__ == "__main__":
    main()
