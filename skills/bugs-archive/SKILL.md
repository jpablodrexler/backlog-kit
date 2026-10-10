---
name: bugs-archive
description: Closes bugs — moves a fixed bug's row from bugs-open.md to bugs-fixed.md, or marks it Won't fix / Cannot reproduce in place, and appends a Resolution line to its details file bugs/<ID>.md (which never moves). Writes the destination before touching the source so an interruption never loses a row. TRIGGER when a bug has been fixed (by hand or by a fix workflow) and needs closing, or when the user decides not to fix one.
license: MIT
metadata:
  version: "0.1"
---

Close one or more bugs. `<backlog>` is `docs/backlog` unless `.backlog-kit.toml` says otherwise.

- **fixed** (default): move the row from `bugs-open.md` to `bugs-fixed.md`.
- **wont-fix** / **cannot-repro**: the row **stays** in `bugs-open.md`; only its Status changes (so a Cannot-reproduce bug that resurfaces is easy to reopen; `bugs-next` ignores these states).

In every case, append a `- **Resolution:** …` line to `<backlog>/bugs/<ID>.md`. The details file never moves, and the row's first-cell link (`[BUG-007](bugs/BUG-007.md)`) is kept as-is.

**Input**: one or more bug ids (`BUG-004 BUG-007`), optionally a disposition and a one-line resolution note or fix reference (PR link or commit). With no ids, auto-detect (step 1).

---

## Steps

### 1. Resolve which bugs to close

Given ids → use them. Otherwise read `bugs-open.md` and list every row showing `🔶 In Progress` (a fix that got as far as being started) plus any showing `✅ Fixed` (an interrupted archive). For ≤4 use **AskUserQuestion** with `multiSelect: true`; for more, print the numbered list and ask "Close all listed" / "Close specific ones (I'll list the ids)" / "Cancel".

### 2. Read both files

If either is missing there's nothing to archive — say so and stop.

**Ordering is a data-safety rule:** extract read-only first, then write the details file's Resolution line and the **destination** row, and only after those saves succeed edit the **source**, once. An interruption leaves a duplicated row or an existing Resolution line, never a lost row.

### 3. Validate each id

Find the row in `## Bug List` by its id (the link text of the first cell). Not there (already archived, or never existed) → warn and skip it. Check `bugs/<ID>.md` exists; if not, warn that there's no file to append the Resolution to and continue with the row move.

### 4. Won't fix / Cannot reproduce

In one edit to `bugs-open.md`: set the row's Status to `🚫 Won't fix` or `❓ Cannot reproduce`, and remove it from `## Recommended fix order` if listed. Append `- **Resolution:** <note>` to the details file (step 5.3's rules). Skip steps 5.1–5.2 and 6.

### 5. Fixed — write the Resolution line and `bugs-fixed.md` first

1. Copy the row, keeping the first-cell link. **In the copy**, drop `Status`, set `Fixed` to today's date (`YYYY-MM-DD`) and `Fix` to the supplied PR/commit (blank if none). The destination columns are `Bug ID | Severity | Area | Environment | Fixed | Fix | Summary`.
2. Append the reshaped row to the end of `bugs-fixed.md`'s `## Bug List`.
3. Append `- **Resolution:** <what the fix changed, and the PR/commit reference>` to the end of `bugs/<ID>.md`. Append only; never rewrite the file. If the file holds several `# <ID> — …` sections, append to the last.

Save both and **confirm the saves succeeded** before step 6.

### 6. Edit `bugs-open.md` — one edit, one save

1. Delete each fixed bug's row.
2. Remove it from `## Recommended fix order` if listed (a plain bullet list — no renumbering).
3. If the table is now empty, restore the `_No open bugs._` placeholder **after a blank line** following the header separator (a placeholder directly under the separator reads as a table row); if the order list is empty, restore `_No open bugs to order._`.

Don't touch `## Details`.

### 7. Report

```
## Bugs Closed

- BUG-NNN `<title>` — <fixed → moved to bugs-fixed.md | 🚫 Won't fix | ❓ Cannot reproduce>

Resolution lines appended: <count>
```

---

## Guardrails

- **Destination before source, always.** `bugs-open.md` is not edited until the `bugs-fixed.md` write is saved. (Won't fix / Cannot reproduce touch only `bugs-open.md` and the details file.)
- The details file never moves, is never renamed or deleted, and its H1 and existing bullets are never edited. Never record Status, Severity or Area in it.
- Reshape the row to the destination's columns (it has a `Fixed` date and no `Status`); preserve exact table formatting in both files.
- An id that isn't in `bugs-open.md` is reported and skipped; continue with the rest.
- Auto-detection is a convenience — the user decides which bugs to close and with what disposition.
- **Never run `git commit`, `git push` or open a PR.** This skill never writes code or runs tests; it records an outcome a fix (or a decision) already produced.
