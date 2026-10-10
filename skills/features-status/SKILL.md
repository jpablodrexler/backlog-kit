---
name: features-status
description: Reports feature-backlog progress by counting rows in features-planned.md and features-implemented.md — total, implemented, pending, in-progress and percent complete, plus priority and effort breakdowns of pending features, the pending list itself, and any data-integrity issues (duplicate numbers, stale dependency notes, missing or orphan brief files, bad summaries, missing links). Read-only. TRIGGER when the user asks for a feature status or progress report, how many features are done or pending, or a backlog summary.
license: MIT
metadata:
  version: "0.1"
---

Report feature-tracking progress by counting the rows of `<backlog>/features-planned.md` (pending) and `<backlog>/features-implemented.md` (implemented). `<backlog>` is `docs/backlog` unless `.backlog-kit.toml` says otherwise.

**Input**: none.

## How

`scripts/status_report.py` (run from this skill's base directory) owns all of the counting and every integrity check; this skill only presents its output. Run it and display the result as-is:

```
python3 scripts/status_report.py <repo-root>
```

It prints the finished `## Feature Tracker Status` report: summary table, priority and effort breakdowns, the pending list, a spec-readiness line when `spec.workflow = "openspec"`, and a **Data integrity** section only when it finds something. Add `--json` for the raw structured data when you need to reason about one field.

Integrity checks it performs: duplicate feature numbers across both files; a stale "prerequisite still pending" dependency note whose features are all implemented; a leftover `✅ Implemented` row in the planned file (an interrupted archive); a table row with no `features/NNN-<name>.md` file and the reverse (an orphan file); a brief file whose H1 isn't `# Feature N — <name>`; a bad Summary (empty or over 250 characters); a missing `[brief](…)` link; a `[spec](…)` link target that doesn't exist (a warning).

If either file is missing or has no `## Feature List` table, the script reports Total/Progress as unavailable and names the file. Don't fall back to reading the files by hand.

## Guardrails

- **Read-only.** Never modify the backlog files, including to fix an integrity issue the script reports — fixing a stale note or a duplicate number is a manual edit, or `features-archive`'s job at the source.
- **Never run `git commit`, `git push` or open a PR.**
- Always re-run the script against the current files; never reuse remembered counts.
