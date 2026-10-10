---
name: feature-plan
description: Adds a new feature to the markdown backlog — drafts the table row (Priority, Effort, Area, Summary), writes the feature's full brief to features/NNN-<name>.md, assigns the next feature number, inserts it into the Recommended implementation order, and confirms with the user before writing. Creates the backlog files on first use. TRIGGER when the user asks to plan a new feature, add a feature to the backlog, or file a feature idea or request.
license: MIT
metadata:
  version: "0.1"
---

Add a new feature to the backlog — a brief file `<backlog>/features/NNN-<change-name>.md` plus a row in `<backlog>/features-planned.md` — drafted from the user's description and confirmed before anything is written. `<backlog>` is `docs/backlog` unless `.backlog-kit.toml` says otherwise.

**Input**: A description of the feature, as detailed as the user likes. It may include an explicit change name and/or explicit Priority / Effort / Area values — use those as given and draft only the rest.

**Scripts**: run every script below from this skill's base directory (`scripts/…`), passing the repository root as its first argument. Configuration lives in the optional `<repo-root>/.backlog-kit.toml`; with no file, the defaults apply — don't ask the user about it.

---

## Steps

### 1. Make sure there's enough to draft from

If the request is too vague to say what the feature does (a one- or two-word title with no hint at the mechanism), ask **one** clarifying question first. A good row names the concrete mechanism — modules, endpoints, data, components — not a restatement of the title. If there's enough to work with, don't ask.

### 2. Create the backlog files if they don't exist

```
python3 scripts/scaffold.py <repo-root>
```

Idempotent: it creates `features-planned.md` and `features-implemented.md` (with the table headers and a Column legend generated from the config) only where missing and reports what it created. Never invent a different structure by hand.

If the output has `planned_header_mismatch`, the existing `features-planned.md` was created under a different `spec.workflow` than the one now configured (the `SDD Artifacts` column is missing or extra), and a row drafted for the configured header would land in the wrong columns. Say so in one line, run `python3 scripts/scaffold.py <repo-root> --fix-header` (lossless: it adds a `⬜ Pending` cell per existing row, or drops the column), and carry on. Mention the repair in the final report.

Then read both files. They're needed to pick a non-colliding number and name and to draft values consistent with existing rows.

### 3. Derive the change name and the next number

**Change name**: validate a user-supplied name is kebab-case (lowercase letters, digits, hyphens) and convert it if not. If none was given, derive a short descriptive slug (`task-search`, not `implement-the-task-search-feature`).

```
python3 scripts/next_id.py <repo-root> --check-name <derived-name>
```

It returns `next_number` (max+1 across both tables and the brief filenames; one global sequence, never reused, even for a cancelled feature), `name_collision`, the configured `vocab` (`priorities`, `efforts`, `areas`, `spec_workflow`) and the exact `planned_header` column order. If `name_collision` is true, tell the user and ask for a different name — never silently rename or proceed with a duplicate.

### 4. Draft Priority, Effort and Area

Use the `vocab` from step 3 (also printed in the Column legend of `features-planned.md`) as the only valid values. A value the user gave is used as-is after checking it's valid. Otherwise infer:

- **Priority** — a security, data-loss or production-safety gap takes the top tier; user-visible high-impact work the next; scalability/quality and convenience follow. Rank by the order of `vocab.priorities` (first = highest).
- **Effort** — in the order of `vocab.efforts` (first = smallest).
- **Area** — whichever `vocab.areas` value best matches what the feature touches.

`Implementation` is always `⬜ Pending` for a new row. When `spec_workflow` is `openspec`, the `SDD Artifacts` column is also `⬜ Pending`: this skill only plans — it never creates spec artifacts or implements anything.

### 5. Draft the brief and the Summary

**Brief** — one dense paragraph naming the concrete mechanism. Reuse every technical detail the user gave; fill gaps with reasonable choices consistent with the project's documented conventions (look at `CLAUDE.md`, the README and any decision records) rather than inventing an unrelated approach. This is the text a later implementation or spec step will receive as "what to build", so give it the specificity that step needs.

**Summary** — a plain-text one- or two-sentence summary of the brief: at most 250 characters (aim for ~160), no pipe characters, no Markdown links. For humans skimming the table and for `features-next`'s display only; it may drop detail the brief keeps.

### 6. Confirm before writing

First look for dependencies the brief implies but nobody has recorded. Pipe the drafted brief to the scanner (nothing is written; it only reads the repo and the backlog):

```
python3 scripts/dep_scan.py <repo-root> --new --name <change-name> --number <number> <<'BRIEF'
<the drafted brief>
BRIEF
```

Each entry in `candidates` is a pending feature this one appears to need (`evidence` says why: it names that feature, or it uses a symbol or file that exists nowhere in the repo and is introduced by that feature's brief). They are evidence, not verdicts. Show them in the draft under **Possible dependencies** and let the user decide; with no candidates, omit that part.

Show the draft:

```
## Draft Feature

**#<number> `<change-name>`**

**Priority:** <p>  **Effort:** <e>  **Area:** <a>

**Summary:** <summary>

**Possible dependencies:** <`#<n> <name>` — <evidence>, one per line — or omit>

**Full brief** (will be saved to `<backlog>/features/<NNN>-<change-name>.md`):

<brief>
```

Ask one question with **AskUserQuestion** — "Add this feature to the backlog?" — options "Yes, add it as drafted", with candidates also "Yes, and record the dependency on #<n>" (one option per candidate, up to the 4-option limit — otherwise say "name the ones to record" in free text), "Let me edit something first" (apply the edits, re-display, ask again), "Cancel". Write nothing under `<backlog>` until the user says yes.

### 7. Write the brief file, then the row

Do these in order — file first, so an interrupted run leaves an orphan file (which `features-status` reports) rather than a row pointing at nothing:

1. Create `<backlog>/features/<NNN>-<change-name>.md` (`NNN` = number zero-padded to three digits; create the folder if needed). Content: the H1 `# Feature <number> — <change-name>` (an em dash; write "Feature 54", never "#54", because GitHub auto-links `#N`), a blank line, then the brief as one paragraph. The file never moves or gets renamed afterwards.
2. Append the row to the end of the `## Feature List` table, contiguous with the existing rows (no blank line inside the table), with cells in `planned_header` order. Default shape:
   `| <n> | \`<name>\` | <priority> | <effort> | <area> | ⬜ Pending | <summary> | [brief](features/<NNN>-<name>.md) |`
   (with `openspec`, a `⬜ Pending` cell for `SDD Artifacts` goes before `Implementation`).

Don't touch `features-implemented.md`.

### 8. Record a hard dependency (only if the user named or confirmed one)

If — and only if — the description names another feature this one depends on, or the user accepted a candidate from step 6, add an entry under `### Hard implementation dependencies`:

```
**Feature <new#> → Feature <dep#>** (prerequisite already implemented | still pending)

`<new-name>` <one-sentence reason it depends on `<dep-name>`>.
```

Check whether the prerequisite is implemented (it has a row in `features-implemented.md`) or still pending. Never record a dependency the user neither stated nor confirmed; the scanner's candidates are proposals only.

### 9. Insert into the Recommended implementation order

This step is **not** optional: a backlog with rows missing from the order is worse than one with a slightly uncertain placement. The `### Recommended implementation order` list is a bullet list of `` `change-name` (#number) `` entries; list position encodes order — priority tier first, then hard dependencies, then feature number.

1. Find the tier boundary: after the last entry whose priority is the same or higher than the new feature's, before the first entry with strictly lower priority. Same-priority entries keep their relative order; the new one lands after all of them. If the list isn't strictly tier-sorted, apply the rule literally and never reorder existing bullets.
2. If step 8 recorded a dependency, make sure the new entry sits after its prerequisite, whatever tier placement alone would say.
3. If the list reads `_None yet._`, the new entry replaces that placeholder.
4. Every other bullet stays exactly as it was.

Write the entry in the style of its neighbours (priority; unblocked or blocked on what; independent/small where relevant). When placement among peers is genuinely ambiguous, put it last within its tier — don't invent a rationale.

### 10. Report

```
## Feature Added

**#<number> `<change-name>`** added to features-planned.md, brief written to `<backlog>/features/<NNN>-<change-name>.md` (Priority <p>, Effort <e>, Area <a>), inserted into the recommended implementation order <right after `<preceding-entry>` (#N) | as the first entry>.
```

---

## Guardrails

- **Never run `git commit`, `git push` or open a PR.** This skill only edits the backlog's markdown files; committing them is the user's call.
- Never write anything under `<backlog>` before the user confirms in step 6 (the step 2 scaffolding is the one exception — it creates empty structure, not a feature). The confirmation is mandatory even under an "auto mode" or other autonomous-operation instruction, and in a subagent that lacks `AskUserQuestion`: stop and say so instead of proceeding.
- Never assign a number or name that already exists in either file or in the `features/` folder.
- Only add to `features-planned.md` and the new brief file; never edit `features-implemented.md` beyond what `scaffold.py` creates.
- The Summary is at most 250 characters with no pipes; the `Brief` cell always links the file written in step 7; never put the full brief in the table.
- Use the vocabulary from `next_id.py`'s `vocab` / the file's Column legend; never a remembered copy.
- Preserve the exact Markdown table formatting (pipes, contiguous rows, header order).
- Step 8 is opt-in on what the user actually said; step 9 is not.
