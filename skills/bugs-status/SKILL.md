---
name: bugs-status
description: Reports bug-backlog progress by counting rows in bugs-open.md and bugs-fixed.md — total, fixed, open, in-progress, won't-fix and cannot-reproduce counts, percent resolved, severity/area/environment breakdowns of open bugs, the open list, and data-integrity issues (duplicate ids, rows without a details file or files without a row, missing Resolution lines, stale statuses). Read-only. TRIGGER when the user asks for a bug status report, how many bugs are open or fixed, or a bug backlog summary.
license: MIT
metadata:
  version: "0.1"
---

Report bug-tracking progress by counting the rows of `<backlog>/bugs-open.md` and `<backlog>/bugs-fixed.md`. `<backlog>` is `docs/backlog` unless `.backlog-kit.toml` says otherwise.

**Input**: none.

## How

`scripts/status_report.py` (run from this skill's base directory) owns all counting and every integrity check; this skill presents its output as-is:

```
python3 scripts/status_report.py <repo-root>
```

It prints the `## Bug Tracker Status` report: summary table, severity / area / environment breakdowns of open bugs, the open list, and a **Data integrity** section only if it finds something. `--json` gives raw data.

Integrity checks: duplicate ids across both files; a table row with no `bugs/<ID>.md` file, and a file with no row; a details file whose first line isn't `# <ID>`; a row in `bugs-fixed.md` whose file has no `**Resolution:**` line; a leftover `✅ Fixed` row in `bugs-open.md` (an interrupted `bugs-archive`).

If either file is missing or has no `## Bug List` table, the script reports Total/Progress as unavailable and names the file. Don't fall back to reading the files by hand.

## Guardrails

- **Read-only.** Never modify the backlog files or anything under `bugs/`, including to fix a reported issue.
- **Never run `git commit`, `git push` or open a PR.**
- Always re-run the script against the current files; never reuse remembered counts.
