#!/usr/bin/env python3
"""
Shared helpers for backlog-kit's skill scripts: config loading, markdown-table
parsing, and path resolution. Pure stdlib (Python 3.11+ for tomllib).

Every script takes a <repo-root>; the project's settings live in an optional
`<repo-root>/.backlog-kit.toml`. Anything missing from it falls back to the
defaults below, so a repo with no config file works out of the box.
"""
import copy
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    tomllib = None

CONFIG_FILE = ".backlog-kit.toml"

# Scripts print status emoji (✅ 🔶). Windows consoles default stdout to a legacy
# codepage (cp1252) and would crash with UnicodeEncodeError, so force UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):  # captured / replaced streams
        pass

DEFAULTS = {
    "paths": {
        "backlog_dir": "docs/backlog",
        "decisions_dir": "docs/decisions",
        "explorations_dir": "docs/explorations",
        "reports_dir": "docs/reports",
    },
    "features": {
        # Ordered highest -> lowest; position drives scoring (see tier_score).
        "priorities": ["P0", "P1", "P2", "P3"],
        "priority_labels": {
            "P0": "production-safety / security / data-loss gap",
            "P1": "high-impact",
            "P2": "scalability / quality",
            "P3": "convenience",
        },
        # Ordered smallest -> largest; the first entry earns the small-effort bonus.
        "efforts": ["S", "M", "L"],
        "areas": ["Frontend", "Backend", "Full-stack"],
    },
    "bugs": {
        "id_prefix": "BUG",
        # Ordered most -> least severe.
        "severities": ["S1", "S2", "S3", "S4"],
        "severity_labels": {
            "S1": "blocker - app unusable, data loss or security hole",
            "S2": "major - a feature is broken with no workaround",
            "S3": "minor - impaired, but there is a workaround",
            "S4": "trivial - cosmetic or copy",
        },
        "environments": ["local", "prod", "both"],
        # Environments that earn the "hurting real users now" bonus.
        "prod_environments": ["prod", "both"],
    },
    "git": {
        # Empty = detect from origin/HEAD, then main / master / develop / trunk.
        "base_branch": "",
        "feature_prefix": "feature/",
        "fix_prefix": "fix/",
    },
    "work": {
        # Rounds of review-and-fix per review before the run stops and asks a human.
        "review_max_rounds": 3,
    },
    "guidance": {
        # Free text handed to the subagent that writes a bug's failing regression
        # test: where tests live, how to run a single one, what to prefer.
        "regression_tests": "",
    },
    "docs": {
        # Optional skill name to invoke (best-effort) in the close phase to keep
        # reference docs in step with what shipped. Empty = skip.
        "sync_skill": "",
    },
    # Verification commands, run in order after implementation. Each entry:
    #   name, run, cwd (default "."), when (path globs; default ["**"]),
    #   ask_before (a question to put to the user before running, e.g. a gate that
    #   hits a live service), timeout_minutes (default 10).
    "gates": [],
    # Reviews run on the changed files. Each entry: name, focus (what to look for),
    # skill (optional: delegate to a project review skill instead of the built-in
    # reviewer), when (path globs; default ["**"]).
    "reviews": [
        {"name": "code",
         "focus": "correctness, regressions, missing or weak tests, unintended changes, anything surprising in the diff",
         "skill": "", "when": ["**"]},
    ],
    "spec": {
        # "none" or "openspec". With "openspec", the planned-features table gains
        # an `SDD Artifacts` column and implemented rows link the archived spec.
        "workflow": "none",
        "changes_dir": "openspec/changes",
    },
}


def _merge(base, override):
    out = copy.deepcopy(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(root):
    """Defaults merged with <root>/.backlog-kit.toml (if present)."""
    p = Path(root) / CONFIG_FILE
    if not p.is_file():
        return copy.deepcopy(DEFAULTS)
    if tomllib is None:
        raise SystemExit(f"{CONFIG_FILE} needs Python 3.11+ (tomllib) to be read.")
    with p.open("rb") as fh:
        return _merge(DEFAULTS, tomllib.load(fh))


class Paths:
    """Resolved locations of every backlog-kit file, from a config."""

    def __init__(self, root, cfg):
        self.root = Path(root)
        self.backlog = self.root / cfg["paths"]["backlog_dir"]
        self.rel_backlog = cfg["paths"]["backlog_dir"].strip("/")
        self.features_planned = self.backlog / "features-planned.md"
        self.features_implemented = self.backlog / "features-implemented.md"
        self.features_dir = self.backlog / "features"
        self.bugs_open = self.backlog / "bugs-open.md"
        self.bugs_fixed = self.backlog / "bugs-fixed.md"
        self.bugs_dir = self.backlog / "bugs"
        self.decisions = self.root / cfg["paths"]["decisions_dir"]
        self.explorations = self.root / cfg["paths"]["explorations_dir"]
        self.reports = self.root / cfg["paths"]["reports_dir"]


def planned_header(cfg):
    cols = ["#", "Change name", "Priority", "Effort", "Area"]
    if cfg["spec"]["workflow"] == "openspec":
        cols.append("SDD Artifacts")
    cols += ["Implementation", "Summary", "Brief"]
    return cols


def planned_header_found(path):
    """The header cells of the table under `## Feature List` in features-planned.md, or None."""
    lines = read_lines(path)
    table = find_table(lines, "## Feature List") if lines is not None else None
    return table[0] if table else None


def migrate_planned_header(path, cfg):
    """Add or drop the `SDD Artifacts` column so the table matches `spec.workflow`.

    Lossless: an added cell reads `⬜ Pending` (no spec artifacts yet), a dropped one is just
    removed. Only rows whose cell count matches the old header are rewritten. Returns
    {"changed": bool, "rows": n, "skipped": [line numbers]}; writes atomically.
    """
    import os
    lines = read_lines(path)
    want = planned_header(cfg)
    start = next((i for i, ln in enumerate(lines or []) if ln.strip() == "## Feature List"), None)
    if start is None:
        return {"changed": False, "rows": 0, "skipped": []}
    h = next((i for i in range(start + 1, len(lines)) if lines[i].lstrip().startswith("|")), None)
    if h is None:
        return {"changed": False, "rows": 0, "skipped": []}
    old = split_row(lines[h])
    if old == want:
        return {"changed": False, "rows": 0, "skipped": []}
    if "SDD Artifacts" in old:
        col, adding = old.index("SDD Artifacts"), False
    elif "SDD Artifacts" in want:
        col, adding = want.index("SDD Artifacts"), True
    else:
        return {"changed": False, "rows": 0, "skipped": [], "note": "headers differ in more than the SDD column"}
    def fmt(cells):
        return "| " + " | ".join(cells) + " |"
    def convert(cells, fill="⬜ Pending"):
        return cells[:col] + [fill] + cells[col:] if adding else cells[:col] + cells[col + 1:]
    new_header = convert(old, "SDD Artifacts")
    lines[h] = fmt(new_header)
    lines[h + 1] = "| " + " | ".join("-" * max(3, len(c)) for c in new_header) + " |"
    rows, skipped = 0, []
    i = h + 2
    while i < len(lines) and lines[i].lstrip().startswith("|"):
        cells = split_row(lines[i])
        if len(cells) == len(old):
            lines[i] = fmt(convert(cells))
            rows += 1
        else:
            skipped.append(i + 1)
        i += 1
    tmp = Path(path).with_suffix(".md.tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return {"changed": True, "rows": rows, "skipped": skipped}


IMPLEMENTED_HEADER = ["#", "Change name", "Priority", "Effort", "Area", "Details"]


# --- markdown tables ---------------------------------------------------------

def split_row(line):
    """Split a table row on unescaped pipes; unescape `\\|` back to `|`."""
    parts = re.split(r"(?<!\\)\|", line)
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [p.strip().replace("\\|", "|") for p in parts]


def find_table(lines, heading):
    """Find the first table under `heading`; return (header, rows) or None.

    A single stray blank line inside the table does not end it (an easy
    hand-edit slip), but two blank lines or any other text does.
    """
    start = next((i for i, ln in enumerate(lines) if ln.strip() == heading), None)
    if start is None:
        return None
    i = start + 1
    while i < len(lines) and not lines[i].lstrip().startswith("|"):
        if lines[i].startswith("## "):
            return None
        i += 1
    if i >= len(lines):
        return None
    header = split_row(lines[i])
    i += 1
    if i < len(lines) and re.match(r"^\|?[\s:-]+\|", lines[i]):
        i += 1
    rows = []
    while i < len(lines):
        if lines[i].lstrip().startswith("|"):
            rows.append(split_row(lines[i]))
            i += 1
        elif (lines[i].strip() == "" and i + 1 < len(lines)
              and lines[i + 1].lstrip().startswith("|")):
            i += 1
        else:
            break
    return header, rows


def row_dict(header, row, id_column=None):
    """Header-keyed dict for a row; unwraps a `[text](link)` in `id_column`."""
    d = {h: (row[i] if i < len(row) else "") for i, h in enumerate(header)}
    if id_column and id_column in d:
        m = re.match(r"^\[([^\]]+)\]\([^)]*\)$", d[id_column].strip())
        if m:
            d[id_column] = m.group(1)
    return d


def read_lines(path):
    p = Path(path)
    return p.read_text(encoding="utf-8").splitlines() if p.is_file() else None


def strip_backticks(s):
    return s.strip().strip("`")


def table_rows(path, heading, id_column=None):
    """(available, [row_dict, ...]) for the table under `heading` in `path`."""
    lines = read_lines(path)
    if lines is None:
        return False, []
    table = find_table(lines, heading)
    if not table:
        return False, []
    header, rows = table
    return True, [row_dict(header, r, id_column) for r in rows]


# --- scoring -----------------------------------------------------------------

def tier_score(value, ordered, step=100, untiered=50):
    """Score by position in `ordered` (first = highest): n*step ... 1*step.

    A value not in the list scores `untiered`, so a blank or unknown cell
    sorts last instead of erroring.
    """
    if value in ordered:
        return (len(ordered) - ordered.index(value)) * step
    return untiered


def order_list_positions(lines, heading, entry_regex):
    """{captured-id: 1-based position} from a bullet list under `heading`.

    `heading` is the exact line (e.g. `### Recommended implementation order`);
    `entry_regex` must capture the id in group 1.
    """
    positions = {}
    start = next((i for i, ln in enumerate(lines) if ln.strip() == heading), None)
    if start is None:
        return positions
    level = len(heading) - len(heading.lstrip("#"))
    pos = 0
    for ln in lines[start + 1:]:
        m_head = re.match(r"^(#+) ", ln)
        if m_head and len(m_head.group(1)) <= level:
            break
        m = re.match(entry_regex, ln)
        if m:
            pos += 1
            positions[m.group(1)] = pos
    return positions


DEPENDENCY_RE = re.compile(r"\*\*Feature (\d+)\s*(?:→|->)\s*Feature (\d+)\*\*")


def hard_dependencies(lines):
    """[(dependent, prerequisite), ...] from `### Hard implementation dependencies`.

    `**Feature A → Feature B**` means A is blocked until B ships; B is the prerequisite.
    """
    start = next((i for i, ln in enumerate(lines)
                  if ln.strip() == "### Hard implementation dependencies"), None)
    if start is None:
        return []
    deps = []
    for ln in lines[start + 1:]:
        if ln.startswith("## ") or (ln.startswith("### ") and "Hard implementation" not in ln):
            break
        m = DEPENDENCY_RE.search(ln)
        if m:
            deps.append((m.group(1), m.group(2)))
    return deps


# --- free-text "blocked on #N" notes in the Recommended implementation order --------------------

_ITEM = r"(?:`[^`]+`\s*\(#\d+\)|#\d+)"
BLOCKED_NOTE_RE = re.compile(
    rf"(?P<lead>,?\s*)\bblocked (?P<prep>on|by) (?P<items>{_ITEM}(?:\s*(?:,|and|&)\s*{_ITEM})*)(?P<paren>\s*\([^)]*\))?",
    re.IGNORECASE)
ORDER_HEADING = "### Recommended implementation order"


def clean_blocked_notes(line, implemented):
    """Drop prerequisites that have shipped from a "blocked on #N" note in one order-list bullet.

    `implemented` is the set of implemented feature numbers (strings). A note whose prerequisites
    have all shipped is removed with its explanatory parenthetical; a note that still has an
    unshipped prerequisite keeps only those (its parenthetical is dropped, since it may describe a
    shipped one). Returns the new line, or `line` unchanged.
    """
    def repl(m):
        nums = re.findall(r"#(\d+)", m.group("items"))
        remaining = [n for n in nums if n not in implemented]
        if len(remaining) == len(nums):
            return m.group(0)
        if not remaining:
            return ""
        return f"{m.group('lead')}blocked {m.group('prep')} " + ", ".join(f"#{n}" for n in remaining)

    new = BLOCKED_NOTE_RE.sub(repl, line)
    if new == line:
        return line
    new = re.sub(r"(—|-)\s*,\s*", r"\1 ", new)          # "— , small" left by removing the first clause
    new = re.sub(r"\s*(?:,|—|-)\s*$", "", new)             # nothing left after a trailing separator
    return re.sub(r"[ \t]{2,}", " ", new).rstrip()


def order_section_bounds(lines):
    """(start, end) line indexes of the bullets under the order heading, or None."""
    start = next((i for i, ln in enumerate(lines) if ln.strip() == ORDER_HEADING), None)
    if start is None:
        return None
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if re.match(r"^#{1,3} ", lines[i]):
            end = i
            break
    return start + 1, end


def emit(obj):
    print(json.dumps(obj, indent=2))


def script_main_guard():
    if sys.version_info < (3, 8):  # pragma: no cover
        raise SystemExit("backlog-kit scripts need Python 3.8+ (3.11+ to read .backlog-kit.toml).")


# --- path globs --------------------------------------------------------------

def kit_globs(cfg):
    """Paths backlog-kit itself writes. They never count as "the change" or as a dirty tree.

    Filing a bug or installing the kit leaves these uncommitted; they carry over to a new
    branch untouched. Treating them as work would block every first run, and would make a
    `when = ["**"]` gate or review match 150 files of bookkeeping.
    """
    pc = cfg["paths"]
    dirs = (pc["backlog_dir"], pc["reports_dir"], pc["decisions_dir"])
    return [".backlog-kit.toml", ".claude/skills/**"] + [d.strip("/") + "/**" for d in dirs]


def glob_to_regex(pattern):
    """`**` spans directories, `*` and `?` stay within one path segment."""
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def glob_match(path, patterns):
    """True if `path` matches any pattern. An empty pattern list matches everything."""
    if not patterns:
        return True
    p = path.replace("\\", "/").lstrip("./")
    return any(glob_to_regex(g.lstrip("./")).match(p) for g in patterns)
