---
name: decision-record
description: Records a short, numbered Architecture Decision Record (ADR) in the decisions folder whenever a real technical decision is made — a pattern chosen over an alternative, a library rejected, a constraint discovered the hard way — capturing what was decided, what was rejected and why, and what it costs going forward. TRIGGER when asked to record or log a decision, write an ADR, or capture "why did we do X"; also proactively right after making or reversing a non-obvious technical choice, before the reasoning is lost.
license: MIT
metadata:
  version: "0.1"
---

Record a numbered ADR under `<decisions_dir>` (default `docs/decisions/`, configurable in `.backlog-kit.toml`) capturing a real decision, the alternatives it rejected, and its consequences — **not** a description of what the code does. Records are an append-only decision *history*; current-state reference docs are a different thing.

**Input**: a description of the decision — what was decided and ideally what was considered and why it lost. Ask a clarifying question only if there's no rejected alternative or no discoverable reason at all to work from (step 1).

---

## Steps

### 1. Confirm it's decision-worthy

Would a future engineer or agent plausibly ask "why not X instead?" If yes, record it. If it's just how something was implemented, with no real fork (no alternative seriously considered, no non-obvious constraint that forced the outcome), it belongs in a code comment or the relevant reference doc — say so and skip, rather than padding the log. If the request doesn't make clear what was rejected or why, ask **one** question before drafting. Never invent a plausible-sounding alternative.

### 2. Find the next number

```
python3 scripts/next_id.py <repo-root>
```

(from this skill's base directory). It returns `next_number` (4-digit, max+1 over the `NNNN-` filename prefixes; one global sequence, never reused even for a superseded record), `directory_exists` and `directory`.

Read every existing record and the folder's `README.md` index. If the folder or index doesn't exist, this is the first record: create `README.md` first —

```markdown
# Architecture Decision Records

Numbered, append-only records of non-obvious technical decisions — what was decided, what alternatives were rejected and why, and what it costs going forward. This is decision *history*, not current-state reference material: a record stays as written even after a later one supersedes it.

## Index

| # | Title | Status | Date |
| - | ----- | ------ | ---- |
```

### 3. Slug

A short kebab-case title with no filler (`reject-primeng-licensing`, `no-prod-environment-split`) → `<decisions_dir>/NNNN-title-slug.md`.

### 4. Draft the record

```markdown
# NNNN. <Title, a plain declarative sentence>

**Date:** <YYYY-MM-DD>
**Status:** Accepted

## Context

<The problem or question that forced a decision — 2–4 sentences. What was about to go wrong, or what genuinely had more than one reasonable answer?>

## Decision

<What was decided, stated plainly — one or two sentences, not a summary of the discussion.>

## Alternatives considered

- **<Alternative A>** — <why it was rejected>
- **<Alternative B>** — <why it was rejected>

## Consequences

- <What this makes easier, or protects against>
- <What this makes harder, or what future work must watch for>
```

Reuse every technical detail the user gave; fill gaps only with detail clearly inferable from the actual repo — don't invent an alternative that wasn't genuinely considered.

### 5. Confirm before writing

Show the draft and ask one question with **AskUserQuestion** — "Record this decision?" — "Yes, record it as drafted" / "Let me edit something first" (apply edits, re-display) / "Cancel". Write nothing until the user confirms.

### 6. Write the record and the index row

1. Write `<decisions_dir>/NNNN-title-slug.md`.
2. Append `| NNNN | <Title> | Accepted | <YYYY-MM-DD> |` to the index table, preserving its format.

### 7. If it supersedes an earlier decision

Change **only the `Status:` line** of the earlier record to `Superseded by NNNN` and update its index row to match. Never edit or delete its Context / Decision / Alternatives / Consequences — what was believed at the time stays intact; only its standing changes.

### 8. Report

```
## Decision Recorded

**#NNNN** `<decisions_dir>/NNNN-title-slug.md` — <Title>
[If superseding:] Marked **#MMMM** as superseded by this record.

If this changes what your reference docs (README, architecture docs) should currently say, update them separately — this skill only records *why*.
```

---

## Guardrails

- **Append-only.** Never rewrite or delete an existing record's body; only a `Status` line changes, and only per step 7.
- Not every choice is decision-worthy; when in doubt, ask rather than pad.
- Never edit the project's reference docs from this skill; recommend the update instead.
- Never write anything before the user confirms in step 5.
- Never assign a number that already exists; always scan fresh.
- **Never run `git commit`, `git push` or open a PR.** Recording a decision edits markdown files only.
