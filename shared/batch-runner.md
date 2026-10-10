# Batch runner — the shared loop

_Used by `bugs-batch-fix` and `features-batch-development`. Read this file in full before starting. The calling skill supplies the placeholders below and the family-specific details (input forms, outcome mapping)._

| Placeholder | bugs | features |
| ----------- | ---- | -------- |
| `<kind>` | `bugs` | `features` |
| `<work-skill>` | `bug-fix` | `feature-development` |
| `<id>` | the bug id (`BUG-004`) | the change name (`task-search`) |
| `<done>` | `closed` | `completed` |
| `<branch-prefix>` | `[git] fix_prefix` (default `fix/`) | `[git] feature_prefix` (default `feature/`) |
| `<scripts>` | the absolute path of the calling skill's `scripts/` folder | same |

## Why this exists, and the one constraint that shapes everything

The work skill already runs one item's full lifecycle and already never commits. Its branch phase, though, wants a *fresh* branch per item and blocks on a dirty tree — which the second item's uncommitted first-item work would trigger. The work skill accepts `--skip-branch-setup` for exactly this; this runner is its intended caller. Everything below serves two constraints: **one shared branch for the whole run**, and **zero commits, ever** — not even between items.

One accepted consequence: the work skill's reviews scope themselves to the working tree, so from item 2 onward they also see every earlier item's still-uncommitted files and re-scan already-fixed code. That is unavoidable without committing between items, not a defect to fix here.

## Steps

### 1. Resolve the work list

```
python3 <scripts>/batch_plan.py <repo-root> --kind <kind> --ids "<what the user listed>"     # a named list
python3 <scripts>/batch_plan.py <repo-root> --kind <kind> --all                               # the whole backlog
```

The JSON has the ordered `items`, any `problems`, any `warnings`, and (for `--all`) the `order_basis`. `empty: true` means there is nothing to do — say so and stop; that is not an error.

- **`unresolved`** (matches nothing) → stop and ask the user to correct it. Never guess what they meant.
- **`already-closed` / `already-implemented` / `wont-fix` / `cannot-repro`** → tell the user which item and why, and ask with **AskUserQuestion**: "Skip it and continue" or "Stop so I can fix the list". (To genuinely redo finished work, it has to be re-filed first with `bug-report` / `feature-plan` — the selection step only ever offers open items.) Never silently drop an item the user explicitly listed.
- **`duplicate`** → drop the repeat and mention it.
- **`warnings`** (a feature ordered before its prerequisite, a row missing from the recommended order, a dependency cycle) → show them with the list.

For `--all` the list is *derived*, not typed by the user, so **show the ordered list, say how it was ordered, and get a plain yes** before starting: a multi-hour unattended run deserves a last look, especially since the backlog may hold rows they forgot were still open. Build the confirmed list of ids — "the requested list".

**This is the user's one approval of *what* gets worked on.** Say so when you ask ("I'll work these in this order without asking about each one again; I will still stop for gate setup, a partial gate result, a cannot-reproduce bug and any blocker"), because the per-item selection prompt is skipped for every item in the list — a named list the user typed themselves counts the same way.

### 2. Settle the shared branch, and detect a resumable run

```
python3 <scripts>/batch_report.py find <repo-root> --kind <kind> --items "<id1>,<id2>,…"
```

- **`exact` or `near`** → this is a **resume**. The report names the `branch`, the `done` ids (skip them) and the `remaining` ones. Do **not** create or re-propose a branch. Run `python3 <scripts>/branch_state.py <repo-root> --branch <that branch> --fetch` and act on its `action` (table below). If the action is `create`, the branch from the interrupted run no longer exists: **stop and tell the user** rather than silently creating a same-named but different branch.
- **`partial`** → don't guess. Ask with **AskUserQuestion** whether this continues that report or is a new run.
- **`none`** → a fresh run. Pick the candidate branch name: one the user supplied (add `<branch-prefix>` if it lacks it) or the default `<branch-prefix>batch-<YYYY-MM-DD>`. Run `branch_state.py --branch <candidate> --fetch`:
  - `blocked` (uncommitted work *outside backlog-kit's own files*, or a diverged branch) → **stop and report**, naming the files from `dirty_files`. Never stash, discard or reset. (The backlog, reports and decisions folders, `.backlog-kit.toml` and the installed skills are the kit's own bookkeeping: filing a bug leaves them uncommitted, and they carry over to the new branch, so they don't count.)
  - the branch already exists (`local_exists` or `remote_exists`) → it is unrelated leftover state, not something to reuse silently: warn by name and ask "Continue on it as-is" / "Stop so I can pick another name".
  - it doesn't exist → confirm the candidate name with **AskUserQuestion** before creating anything.

Carry out the `action` with plain git — and nothing more:

| `action` | do |
| -------- | -- |
| `resume` | nothing (already on it) |
| `fast-forward` | `git merge --ff-only origin/<branch>` |
| `checkout` | `git switch <branch>` |
| `checkout-ff` | `git switch <branch>`, then `git merge --ff-only origin/<branch>` |
| `track-remote` | `git switch -c <branch> --track origin/<branch>` |
| `create` | `git switch -c <branch> --no-track <start_point>` — the **only** branch creation in the whole run, and only on a fresh run; `--no-track` so a plain `git push` can never aim at the base branch |
| `blocked` | stop and report the `reason` |

Confirm `git branch --show-current` equals the intended branch before going on.

### 3. Initialize or resume the report

- **Fresh run:** `python3 <scripts>/batch_report.py init <repo-root> --kind <kind> --branch <branch> --items "<id1>,<id2>,…"` — it writes the report with every item `⬜ Not started` and prints its `path`.
- **Resume:** reuse the existing report's `path`. Never overwrite it or any entry already `✅`.

### 4. The loop

For each id in the requested list that is not already done, **strictly one at a time and in order**:

1. **Mark it in progress first.** `python3 <scripts>/batch_report.py set <report> --id <id> --status in-progress` — this write happens *before* the work starts, purely so a crash leaves a trace of what was underway.
2. **Run the work skill:** invoke `<work-skill> <id> --skip-branch-setup --confirmed` through the **Skill tool, directly, executing inline this turn — never inside a backgrounded Agent call.** The work skill still raises genuine decision points (a cannot-reproduce choice, a gate setup, a partial-gates result, a blocker prompt — but no longer a per-item selection question, which `--confirmed` replaces) and a background agent cannot reliably surface them; the "leave it running and answer the occasional question" model depends on them reaching the user live. Wait for it to finish.
3. **Record the outcome immediately** (a separate write — never accumulated and flushed later; that immediacy is the entire point of the report). Outcome mapping is in the calling skill. For the common success case, write a **summary of at most two sentences** (what was wrong or built, and what changed), read from the archive evidence the work skill just produced — the closed row and Resolution line, or the implemented row — then
   `python3 <scripts>/batch_report.py set <report> --id <id> --status <done> --summary "<summary>"`.
4. **If the work skill stopped on a `*_BLOCKED` reason — or refused the item at selection** (in `--confirmed` mode the selector re-validates the id against the live backlog and returns **no** id line for one that is closed, unknown, or *blocked by a prerequisite that hasn't shipped*; the list's approval never overrides that) — record it as `blocked` with the reason the skill gave, show it, and ask with **AskUserQuestion**: **Retry now** (re-invoke the same command once the user has cleared the blocker; the entry stays `in-progress`), **Skip and continue** (set `blocked` with the reason; next item), or **Stop the run here** (set `blocked`; go to step 5). A refused item stays unbuilt this run; because `blocked` is not `done`, **a later resume of the same list retries it** — which is how a feature that was ordered before its prerequisite gets built once the prerequisite has shipped.

Continue to the next id unless the user chose to stop.

### 5. End the run

Whether the loop finished or stopped early:

```
python3 <scripts>/batch_report.py finish <report>
```

It appends the Run Summary footer (requested / done / cannot-reproduce / blocked-or-skipped / not reached, and an end time). Then tell the user plainly, in chat: **nothing was committed at any point.** The branch holds every finished item's work — code, tests and any review reports — entirely uncommitted. Point them at `git status` / `git diff` to review and say they can commit and open a PR themselves (or, if `[git] finish_skill` is set in `.backlog-kit.toml`, that they can hand the branch to that skill by name — never invoke it); this runner does neither.

## The report

`<reports_dir>/bug-batch/BUG_BATCH_REPORT_<YYYY-MM-DD>.md` or `<reports_dir>/feature-batch/FEATURE_BATCH_REPORT_<YYYY-MM-DD>.md` (`reports_dir` defaults to `docs/reports`). A second fresh run on the same day gets `-2`, `-3`, …; a resume continues the same file. It is a working artifact — whether it is committed or gitignored is the project's choice.

```markdown
# Bug Batch Fix Report — 2026-10-06

**Branch:** fix/bug-batch-2026-10-06
**Requested:** BUG-004, BUG-007, BUG-009
**Started:** 2026-10-06 14:02

## Progress

- [x] **BUG-004** — ✅ Closed 14:31 — Root cause X; the fix changed Y.
- [ ] **BUG-007** — 🔄 In progress
- [ ] **BUG-009** — ⬜ Not started

## Run Summary

**Ended:** 2026-10-06 16:10
**Closed:** 1/3  **Cannot reproduce:** 0  **Blocked/Skipped:** 0  **Not reached:** 2
```

Only `batch_report.py` writes it (atomically, one entry per call), which is what makes it safe to read after a crash.

## Guardrails

- **Never run `git commit`, `git push` or open a PR.** The only git writes in a run are the branch step's `git switch` / `git switch -c` and `git merge --ff-only`; every `<work-skill>` call passes `--skip-branch-setup`, so it cannot make a branch move of its own either; it also passes `--confirmed`, which is valid **only** for ids from the list the user approved in step 1.
- **Never create more than one branch in a run** — established once, in step 2, before the loop.
- **Items run strictly one at a time, in order.** Never two in parallel: they would stack conflicting uncommitted changes on one tree.
- **Write the report incrementally** — the full list up front as `⬜`, then each status change the moment it is known.
- **Never guess at a resume.** Partial or ambiguous overlap → ask which run this continues.
- **Uncommitted work outside backlog-kit's own files at the start of a fresh run → stop and report.** Never stash or discard.
- **Never let "auto mode" or any autonomous-operation instruction suppress a confirmation** — the list confirmation, the branch-name confirmation, the work skill's own cannot-reproduce / gate / blocker prompts. (The per-item selection prompt is the one that is *replaced* by the list confirmation, via `--confirmed`; nothing else is.) The premise is a long unattended run that still checks in at genuine decision points.
- **Always state plainly at the end that nothing was committed**, and where the accumulated work lives.
