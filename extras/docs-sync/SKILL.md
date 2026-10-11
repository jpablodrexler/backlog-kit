---
name: docs-sync
description: >
  Keeps `CLAUDE.md`, the reference docs under `docs/`, and `README.md`'s
  documentation index in sync with the actual code. TRIGGER after
  implementing a feature or OpenSpec change that adds or changes anything
  the documentation describes (the project notes list which code areas map
  to which doc sections). Also TRIGGERS when explicitly asked to check,
  audit, or sync the project's documentation against the code, or as a
  standalone full sweep. Do not wait to be asked after a feature lands with
  any such change — none of this is re-derived automatically, so it drifts
  silently otherwise.
license: MIT
metadata:
  author: Juan Pablo Drexler
  version: "0.1"
---

# Docs Sync Skill

**Never run `git commit`, `git push` or open a PR.**

Paths: `<backlog>` is `docs/backlog` and `<reports>` is `docs/reports`,
unless `.backlog-kit.toml` sets `[paths] backlog_dir` (then each is the
folder of that name next to the backlog's parent).

## The documentation tiers

Every project this skill serves keeps its documentation in three tiers, and
each needs active upkeep. Nothing else in the repo maintains them
automatically; that's this skill's job.

- **`CLAUDE.md`** — a lean quick-start for an agent working in the code:
  commands, repo layout and a few short, fixed-pointer subsections that each
  name the essential rule and link to the `docs/*.md` section holding the
  full detail. It should **never** carry a full table or API reference, a
  routing table, a long step-by-step runbook, or a per-feature narrative
  inline — those belong in `docs/`. If you find one growing back in
  `CLAUDE.md`, move it out: detail left inline drifts silently for a long
  time before anyone re-derives it from the code.
- **`docs/*.md`** — the actual reference material, indexed from `README.md`:
  architecture and diagrams, the data model, routing, running, building and
  testing, the list of what is really reachable. This is comprehensive; the
  project notes (§1) say which file covers what.
- **`README.md`** — a short intro plus the documentation index table
  pointing into `docs/`. It should stay an index, not regrow the runbook
  content that lives in `docs/`.

This skill has two modes:

- **Scoped sync** (default) — after implementing one feature/change, check
  only the doc sections that change could plausibly affect, and fix them.
- **Full sweep** — audit every row in the project notes' doc-section table
  against the current codebase from scratch. Use when asked to "audit,"
  "check for drift," or when it's been a while since the last scoped sync
  ran.

Both modes **edit the doc files directly** rather than writing a separate
findings report — for `CLAUDE.md`/`docs/*.md`/`README.md` this is
documentation, not application code, so the fix *is* the review output. Show
the user a short diff-style summary of what changed in chat.

---

## 1. Project notes

Doc Sections & Their Source of Truth: list `.backlog-kit/docs/` (relative to
the repository root); each file's second line is `Read when: …`; read every
file marked `every run` and every file whose `Read when` matches the task;
follow them. If the folder does not exist or is empty, work from the frame
above plus what the project's CLAUDE.md and docs say, and tell the user that
no project notes were found.

The notes hold the project's doc-section table (doc section → files →
source of truth), any fixed-pointer subsections of `CLAUDE.md`, and which files and directories
are in or out of this skill's scope. The workflows below refer to that
table as "§1".

---

## 2. Scoped Sync Workflow

1. Identify what changed: `git diff <base>..HEAD --stat`, where `<base>` is
   the branch's base (the branch the current feature branch was cut from),
   if run at the end of a feature; otherwise, whatever files the user points
   to.
2. Map each changed file to the row(s) in §1 whose source of truth it
   touches. Skip rows whose source of truth wasn't touched — don't
   re-verify everything on a scoped sync.
3. For each mapped row, read the current doc text and the current code side
   by side and determine what's missing, stale, or wrong.
4. Apply the fix directly with `Edit`, one section at a time, matching
   that file's existing style (heading level, list vs. table, diagram
   conventions if touching a diagram).
5. **If you find detail that belongs in `docs/` sitting inline in
   `CLAUDE.md` instead**, move it — don't just update it in place. Replace
   the inline content with a short pointer, matching `CLAUDE.md`'s existing
   "Documentation" section pattern.
6. If a `docs/*.md` file's content changed enough that its one-line
   description in `README.md`'s documentation index (or `CLAUDE.md`'s
   "Documentation" paragraph) no longer describes it accurately, update that
   index entry too — don't leave the pointer stale even if the target file
   is now correct.
7. Summarize in chat: which sections were checked, which were updated, and
   the one-line reason for each update.

---

## 3. Full Sweep Workflow

1. Read `CLAUDE.md`, `README.md`, and every file under `docs/` (excluding
   the paths the project notes mark out of scope — see Guardrails) in full.
2. For each row of §1, independently re-derive the current state from code
   rather than trusting the doc's existing content, and compare. For rows
   whose source of truth is an ordered history of files (such as
   migrations), read every file directly in order — don't sample the most
   recent one or two and assume earlier narrative still holds; a later
   change can re-scope or drop what an earlier doc pass described.
3. Collect every discrepancy found before editing anything, so overlapping
   edits to the same file can be merged into one pass.
4. Apply all fixes with `Edit`, grouped by file.
5. Summarize in chat: a short list of what was added/updated/removed,
   grouped by file, so the user can spot-check anything surprising (e.g. a
   removed row means something that no longer exists in code).

---

## Guardrails

- Never document behavior you haven't verified in the actual code — no
  inferring behavior from a name, and no guessing what exists from a
  folder name alone. Read the actual definitions (routes, policies,
  configuration) directly.
- Don't let `CLAUDE.md` regrow a full reference table, a routing table, or a
  long step-by-step runbook — that belongs in `docs/`. Moving misplaced
  detail out is itself a finding to fix, not just a staleness issue to
  patch in place.
- Don't create a dated report file the way `code-reviewer`/
  `security-reviewer`/`database-reviewer` do — the corrected `CLAUDE.md`/
  `docs/*.md`/`README.md` files *are* the artifact. The chat summary is
  enough of a record for this session.
- The project notes name the fixed-pointer subsections of `CLAUDE.md` (if
  any) and the exact files this skill may edit. Respect them: a feature
  that changes what a pointer subsection describes updates the linked
  `docs/*.md` file only; do not add narrative detail back into `CLAUDE.md`.
- Stay within the scope the project notes define. Regardless, this skill
  does not touch `<backlog>/` files (owned by `feature-plan`/
  `features-archive`), `docs/decisions/*.md` (owned by `decision-record` —
  an append-only decision history, not current-state reference material this
  skill keeps synced against the code), or the report directories under
  `<reports>/` (owned by their respective skills) — those are
  tracked/managed elsewhere, not part of this skill's "keep the docs
  honest" job.
