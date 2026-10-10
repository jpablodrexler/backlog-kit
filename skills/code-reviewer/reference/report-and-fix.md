# Code reviewer: report format and fix workflow

_Part of the `code-reviewer` skill. Load this file only for the fix workflow or when unsure of the report format._

## Report format

- Findings are GitHub task-list checkboxes: `- [ ] 🔴|🟡|🔵 <file>:<line> — <what is wrong and why it matters>`.
- Grouped by severity (Critical, Warning, Suggestion), then by file; empty groups omitted.
- Header: scope reviewed and the state it was reviewed against.
- Only findings from this run. Never carry forward items from an earlier report unless asked to produce a combined backlog, which is its own explicit step.
- After a fix, the line becomes `- [x] ...` followed by `**Fixed:** <what changed and why, one or two sentences>.` or `**Evaluated, no change made:** <rationale>`.

## Fix workflow

Interactive and incremental: fix a chunk, tick it off, ask what is next. It edits source and the report; **it never commits**, no `git add`, no `git commit`, no other state-changing version-control command. All changes stay uncommitted for the person to review.

### 1. Locate the report(s)

1. If the person names a report file, go to step 2 with it. Otherwise resolve a date: the date asked for, or the most recent date with any `<reports_dir>/code-review/CODE_REVIEW_FINDINGS_*.md` or `<reports_dir>/review/code-*.md` file. If none exists, say so and stop.
2. List every report for that date (each `-2`/`-3` rerun and each layer suffix is a distinct report). Drop those with no unchecked `- [ ]` boxes left.
3. One report left: use it. More than one: ask which to work on first, showing the layer or scope and a rough critical/warning/suggestion count. Work on exactly one report at a time; never mix findings from two reports in one pass.

### 2. Read the report, then ask what to fix

Read the whole report first. Do not silently pick a starting point. Ask whether to fix a whole severity category or one named finding, offering only categories and findings that still have unchecked boxes.

### 3. Fix loop

For each unchecked finding in the chosen scope, one at a time:

1. Read the affected files and the code around the finding. The report is a pointer, not a substitute for reading.
2. Apply the fix, following the project's own conventions.
3. If the fix hinges on a real design decision (a public contract change, a data-compatibility risk, several equally valid approaches), stop and ask before proceeding.
4. Verify: build or compile if the project has a build step, then the narrowest relevant test scope. After a signature or type change, prefer a clean build so an incremental build cannot report a false green.
5. Update tests for the new shape of the code (renamed things, changed signatures, moved files); leave no stale references or names.
6. Tick the report line now, not at the end, so an interrupted session leaves an accurate resume point.
7. If the fix incidentally resolved another unchecked finding, tick that too with a note that it was fixed as a byproduct.

### 4. Continue until done

When the chosen scope is finished, run the widest verification the project documents (full test suite, lint, build) once before asking what is next. If the report still has unchecked findings, go back to step 2 within it; if it is fully ticked, go back to step 1 and offer the remaining reports. Stop when the person says stop or every report for the date is fully ticked.
