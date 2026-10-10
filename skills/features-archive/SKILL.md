---
name: features-archive
description: Marks features as implemented — moves their rows from features-planned.md to features-implemented.md, rewriting each to the implemented-table shape with a Details cell linking the feature's brief (and the archived spec, with OpenSpec), and carrying over resolved dependency notes. Writes the destination before touching the source so an interruption never loses data. TRIGGER when one or more features have shipped and need archiving.
license: MIT
metadata:
  version: "0.1"
---

Archive implemented features from `<backlog>/features-planned.md` into `<backlog>/features-implemented.md`. `<backlog>` is `docs/backlog` unless `.backlog-kit.toml` says otherwise.

**Input**: one or more feature numbers (`3 7`) or names (`task-due-dates`). If omitted, detect candidates (step 1) and ask.

---

## Steps

### 1. Resolve which features to archive

Given numbers or names → use them, go to step 2.

Otherwise detect candidates:

- **With `spec.workflow = "openspec"`**: list the directories under `<changes_dir>/archive/` (default `openspec/changes/archive/`), strip the `YYYY-MM-DD-` prefix to get change names, and match each against the `Change name` column of planned rows still showing `⬜ Pending` or `🔶 In Progress`. An archived spec change is the signal that a feature has shipped.
- **Otherwise**: candidates are the planned rows showing `🔶 In Progress` — someone started them; ask which have shipped.
- **Fallback** when nothing matches: list every `⬜ Pending` row.

`AskUserQuestion` takes 2–4 options. For ≤4 candidates use `multiSelect: true`, one per candidate. For more, print the full numbered list as plain text and ask "Archive all listed" / "Archive specific ones (I'll list the numbers)" / "Cancel", resolving "specific ones" from the free-text reply. The user always has the final say.

### 2. Read both files

If either file is missing there's nothing to archive — say so and stop (`feature-plan` creates both on first use).

### 3. Validate each selected feature

Find the planned row by `#` (numeric input) or `Change name` (the backtick-wrapped value). If no planned row matches but the feature is already in `features-implemented.md`, warn that it's already archived and skip it. Check the brief file `<backlog>/features/NNN-<name>.md` exists; if not, warn (it's never created or edited here) and still archive the row.

**Ordering is a data-safety rule.** Steps 4–5 are read-only extraction; step 6 writes the **destination**; only after that save succeeds does step 7 edit the **source**, once. An interruption then leaves content duplicated, never lost. Never edit `features-planned.md` before `features-implemented.md` is saved.

### 4. Extract and rewrite each row (in memory)

Copy the planned row, then **in the copy** reshape it from the planned shape to the implemented shape (`# | Change name | Priority | Effort | Area | Details`), reading planned cells by header name:

- keep `#`, `Change name`, `Priority`, `Effort`, `Area` exactly as they are;
- **drop** `SDD Artifacts` (if present), `Implementation`, `Summary`, `Brief` — "implemented" is decided only by which table holds the row;
- add `Details`: `[brief](features/NNN-<name>.md)`, and with `openspec` append ` · [spec](../../<changes_dir>/archive/<archive-dir>/proposal.md)` (path relative to the backlog dir). `<archive-dir>` is the folder named `YYYY-MM-DD-<change-name>` under `<changes_dir>/archive/`; with several matches take the most recent. If none exists yet, warn and build the link from today's date — `features-status` will flag the missing target until it exists.

The row left behind in the planned file keeps showing `⬜ Pending`/`🔶 In Progress` until step 7 deletes it; it is never flipped in place. Don't edit the actual planned file yet.

### 5. Extract dependency / implementation notes (in memory)

Scan the `## Dependencies` sections of the planned file for blocks that mention a selected feature number. A block starts at a heading or bold label such as `**Feature 3 — …**` or `**Feature 3 → Feature 2**` and runs to the **next `**Feature N …**`-style heading** — not the next blank line (blocks span paragraphs). A heading may name several features (`**Features 4, 5, 6 — no schema changes**`); record all of them. For a hard dependency `**Feature A → Feature B**`, B (after the arrow) is the prerequisite.

**`IMPLEMENTED_SET`** = every `#` already in `features-implemented.md`'s Feature List, plus this run's selection — the full set that will be implemented after this run, not just this batch. Prerequisites are often satisfied across separate archive runs, so judging against only this batch would leave "still pending" notes stale forever.

### 6. Write `features-implemented.md` first

1. Append each rewritten row to the end of `## Feature List` (right after its last row; rows are grouped by archive batch, not sorted), keeping the table contiguous.
2. Under `## Dependencies (Historical)` → `### Implementation notes`, add the step 5 blocks (a multi-feature block that also stays in the planned file is added here too; duplication is fine):
   - If no block with that heading exists here yet: append it. For `A → B`, judge only the **prerequisite B**: if B is in `IMPLEMENTED_SET`, write the annotation as `(resolved)` instead of copying "still pending" — A became unblocked the moment B shipped, whether or not A has.
   - If one already exists: don't append a second copy; if B is now in `IMPLEMENTED_SET` and it still reads "still pending", update it to `(resolved)` in place. A block can legitimately read "resolved" while A's row is still pending in the planned file — "resolved" means "no longer blocking", not "both done".

Save, and **confirm the save succeeded** before step 7.

### 7. Edit `features-planned.md` — one edit, one save

1. Delete each selected feature's row from `## Feature List` (it's removed, not flipped; its brief file stays put).
2. Delete the step 5 blocks whose heading numbers are **all** in `IMPLEMENTED_SET`. A block that still references an unimplemented feature stays.
3. For an `A → B` block left behind (A still pending) whose prerequisite B is now in `IMPLEMENTED_SET`, update its annotation to `(resolved)` in place.
4. Remove the archived features from `### Recommended implementation order`.
5. Remove them from any "no hard dependencies" list.

Keep the `## Dependencies` header even if it empties.

### 7b. Clear stale "blocked on" notes from the order list

Order-list entries carry free text such as ``- `playlist-unmatched-entries-log` (#2) — P3, blocked on #1 (logs its names), small``. Once #1 is archived that note is wrong. After step 7 is saved, run:

```
python3 scripts/clean_order_notes.py <repo-root>
```

It removes the `blocked on/by #N` clause (with its parenthetical) for every prerequisite now in `features-implemented.md`, keeps any prerequisite that is still pending, touches nothing else, and prints what it changed. Mention each change in the report. It is idempotent; `--dry-run` previews. Don't hand-edit the list instead — the script is the single place that decides what counts as a stale note.

### 8. Report

```
## Archive Complete

Archived N feature(s):
- #<n> `<name>` — moved to features-implemented.md (Details: brief[ + spec] link)

Dependency/implementation note blocks moved: <count>
Order-list notes cleared: <count> (<entry>: removed "blocked on #N …")
```

---

## Guardrails

- **Destination before source, always**, and the source gets exactly one edit and one save.
- The rewrite to the implemented shape happens in step 4's in-memory copy. Rewriting later against the planned row would only mutate a row step 7 deletes, leaving a wrong-width row under the implemented header.
- Only the row moves. The brief file is never copied, moved or edited.
- A dependency block's "still pending" status is judged against `IMPLEMENTED_SET`, never this run's selection alone — and for `A → B`, by B only.
- If a selected number doesn't exist in the planned file, report it and continue with the rest.
- Preserve exact table formatting in both files; keep section headers intact — only add or remove rows and note blocks, plus step 7b's removal of shipped "blocked on" clauses from order-list bullets.
- **Never run `git commit`, `git push` or open a PR.** This skill never writes code or runs tests; it only moves rows between markdown files.
