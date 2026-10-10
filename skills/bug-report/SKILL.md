---
name: bug-report
description: Adds a bug to the markdown bug backlog — drafts the row (Severity, Area, Environment, Status, Summary), assigns the next bug id, writes the details file bugs/<ID>.md (steps to reproduce, expected, actual), inserts it into the Recommended fix order, and confirms with the user before writing. Creates the backlog files on first use. TRIGGER proactively whenever the user reports a bug, asks to file or log one, describes something broken or giving a wrong result (a symptom, stack trace or console error), or hands over testing-session notes — even mid-task. It only records the bug; it never fixes it.
license: MIT
metadata:
  version: "0.1"
---

Add a bug row to `<backlog>/bugs-open.md` and create its details file `<backlog>/bugs/<ID>.md`, drafted from the user's report and confirmed before writing. `<backlog>` is `docs/backlog` unless `.backlog-kit.toml` says otherwise; `<ID>` is `BUG-NNN` (the prefix is configurable).

**Layout.** The two table files (`bugs-open.md`, `bugs-fixed.md`) hold only tables, the Column legend and the Recommended fix order. Every bug's write-up lives in its own file `bugs/<ID>.md` — a stable path that never moves, even when the bug is closed. Severity, Area, Environment and Status live **only** in the table row (single source of truth), never in the file. A row's first cell links to its file: `[BUG-007](bugs/BUG-007.md)`.

**Input**: a description of the bug — a one-liner, a paragraph, or raw notes from a testing session — optionally with explicit Severity / Area / Environment and repro details (use those as given; draft only the rest). If the user pastes **several** bugs, process them one at a time: draft, confirm, write, then the next. Never batch unconfirmed rows into one write.

**Scripts**: run from this skill's base directory, passing the repository root. Configuration is the optional `<repo-root>/.backlog-kit.toml`; with no file, defaults apply.

---

## Steps

### 1. Make sure there's enough to draft from

A useful bug needs what the user did, what they expected, and what actually happened. For a bare symptom ("the report page is broken") ask **one** question — the screen or action, and observed vs. expected behaviour. If the report is enough to reproduce mentally, don't ask.

### 2. Create the backlog files if they don't exist

```
python3 scripts/scaffold.py <repo-root>
```

Idempotent: creates `bugs-open.md` and `bugs-fixed.md` (tables, Column legend, Recommended fix order — generated from the config) only where missing. A missing backlog is a reason to run this skill, never to skip it. Then read both files.

### 3. Derive the bug id

```
python3 scripts/next_id.py <repo-root>
```

Returns `next_id` (max+1 across both tables and the `bugs/` filenames, zero-padded to 3 digits; one global sequence, never reused — not even for a Won't fix or Cannot reproduce entry) and the configured `vocab` (`severities`, `environments`).

### 4. Draft the attribute columns

Use `vocab` (also in the Column legend of `bugs-open.md`) as the only valid values; a user-supplied value is used as-is after checking it's valid.

- **Severity** — infer if not given: anything involving security, data loss, or "the app can't be used" takes the top tier; a feature broken with no workaround the next; impaired-with-workaround next; cosmetic last (order of `vocab.severities`, most severe first).
- **Area** — free text: the screen, route, module or component where it was hit.
- **Environment** — one of `vocab.environments`. Default to the non-production one if the user was testing locally and didn't say; use the "both" value only if they confirmed it in production too.

### 5. Draft the Summary and the details file

**Summary** — one sentence naming the concrete symptom (the component and what visibly goes wrong), not a restatement of the title.

**Details file** — first line an H1, a blank line, then these bullets:

```markdown
# BUG-NNN — <short title>

- **Steps to reproduce:**
  1. <step>
  2. <step>
- **Expected:** <what should happen>
- **Actual:** <what happens instead, with any short console/error text verbatim>
- **Environment:** <environment> — <browser / OS / account notes if relevant>
- **Notes:** <suspected cause, related code path, screenshot filenames — omit the line if empty>
```

Never put Severity, Area or Status in the file. Fill from what the user gave; if a step is genuinely unknown, write `<unknown — needs repro>` rather than inventing it.

### 6. Confirm before writing

Show the draft:

```
## Draft Bug

**BUG-NNN — <title>**

**Severity:** <s>  **Area:** <area>  **Environment:** <env>  **Status:** ⬜ Open

<details file content>
```

Ask one question with **AskUserQuestion** — "Add this bug to the backlog?" — "Yes, add it as drafted" / "Let me edit something first" (apply edits, re-display, ask again) / "Cancel". Write nothing under `<backlog>` (beyond step 2's scaffolding) until the user says yes.

### 7. Create the file, insert the row, add the order entry

1. Create `<backlog>/bugs/<ID>.md` (create the folder if needed). The filename is exactly the id and never changes.
2. In **one edit** to `bugs-open.md`, append the row to `## Bug List`:
   `| [BUG-NNN](bugs/BUG-NNN.md) | <s> | <area> | <env> | ⬜ Open | | <summary> |`
   Rows must follow the header separator row **with no blank line between them**. The scaffold leaves a blank line and a `_No open bugs._` placeholder after the table: when it's present, remove **both** the placeholder and that blank line — a stray blank line detaches the row from the table, so it renders as plain text and `bugs-status` counts zero.
3. In the same edit, insert the bug into `## Recommended fix order` (step 8). Not optional.

Don't append anything to `## Details` (it holds only a pointer sentence) and don't touch `bugs-fixed.md`.

### 8. Insert into the Recommended fix order

A bullet list of `` BUG-NNN — <title> `` entries; list position encodes order — severity tier first, then blast radius, then quick-win effort, then bug number.

1. Place the bug after the last entry of the same or higher severity and before the first of strictly lower severity (same-severity entries keep their relative order; the new one goes after them — unless the description makes its blast radius obviously larger than a same-tier peer, then place it ahead and say why in the entry).
2. If the list reads `_No open bugs to order._`, that placeholder is replaced by the new entry.
3. Every other bullet stays exactly as it was.

Write the entry like its neighbours: severity, a one-phrase reason for the placement, environment where relevant.

### 9. Verify, then report

Run the sibling skill's script (`../bugs-status/scripts/status_report.py <repo-root>`) and check that the open count includes the new bug and that no `⚠` line appears. A missing bug means it fell out of the table — fix the formatting before reporting success.

```
## Bug Added

**BUG-NNN — <title>** added to bugs-open.md (Severity <s>, Area <area>, <env>), details in <backlog>/bugs/BUG-NNN.md, inserted into the recommended fix order <right after `<preceding-entry>` | as the first entry>.
```

---

## Guardrails

- **Never run `git commit`, `git push` or open a PR.** This skill edits markdown backlog files only.
- Never write a row or a details file before the user confirms in step 6. The confirmation is mandatory even under "auto mode" or other autonomous-operation instructions, and inside a subagent without `AskUserQuestion` (stop and say so).
- Never edit `bugs-fixed.md` beyond the initial scaffold — closing a bug is `bugs-archive`'s job. Never put a details block in either table file.
- Never reuse a bug id; the sequence spans both tables and the `bugs/` folder.
- Use the vocabulary from `next_id.py` / the Column legend, never a remembered copy.
- Preserve exact table formatting, including the `[ID](bugs/ID.md)` link and row contiguity.
- If several bugs were pasted, confirm each individually.
- This skill only records a bug — it never starts a branch, writes a test or attempts a fix.
