---
name: bug-fix
description: Runs the full lifecycle of fixing one bug from the backlog — picks the bug, sets up a fix branch, reproduces it with a FAILING regression test first, implements the fix, runs the configured reviews and verification gates (tests, build, anything in .backlog-kit.toml) until they pass, then closes the bug through bugs-archive. Never commits — leaves the fix uncommitted on its branch for the human to review and open as a PR. TRIGGER when asked to fix a bug, work through the bug backlog one at a time, or address a specific BUG-NNN — including a bug only just described (file it with bug-report first, then run this skill).
license: MIT
metadata:
  version: "0.1"
---

Orchestrate one bug fix from selection to close, one subagent per phase. Its distinguishing rule: **a failing regression test is written before the fix**, and it is the durable artifact the fix leaves behind — a fix with no failing test to justify it is not this workflow.

`<backlog>` is `docs/backlog` unless `.backlog-kit.toml` says otherwise. Everything project-specific — which commands verify a change, which reviews apply, branch prefixes — comes from that file, never from this skill; with none configured, the first run proposes gates and asks (see the gates phase).

**Input**: an optional bug id (`BUG-004`), optionally followed by `--skip-branch-setup` and/or `--confirmed`. The id is passed to `bugs-next` to skip the recommendation and go straight to confirmation. `--skip-branch-setup` is for orchestrators (a batch runner) that already checked out one shared branch and run several fixes on it without committing between them. `--confirmed` (only with an id) means the caller already got the user's approval of this exact bug as part of a confirmed list, so the per-bug question is skipped. A batch runner passes both; omit both for normal single-bug use.

**Before starting**, read `reference/pipeline-guardrails.md` — the rules that hold across every phase (no commits, confirmations reach the user, one branch, no weakening tests, no secrets).

## Phases

| Phase | Who | What |
| ----- | --- | ---- |
| 0 — Select & confirm | orchestrator's own context | `bugs-next` (recommend + mandatory `AskUserQuestion`) |
| 1 — Branch | subagent | `reference/phase-branch.md`: create/resume `fix/<slug>`, flip the row to `🔶 In Progress` |
| 2 — Reproduce | subagent | write a regression test that **fails** for the reason in the report |
| 3 — Fix & review | subagent | narrowest fix until the regression test passes; then the configured reviews (`reference/phase-reviews.md`) |
| 4 — Gates | orchestrator pre-step + subagent | `reference/phase-gates.md`: the project's own verification commands, to a pass |
| 5 — Close | subagent + orchestrator check | optional docs sync, then `bugs-archive <id> fixed "<resolution>"` (orchestrator runs it itself if the subagent can't) |

---

## Phase 0 — Select & confirm (orchestrator's own context — never a subagent)

Which bug gets fixed is the user's decision; a spawned subagent can't reliably surface `AskUserQuestion`, and an "auto mode" instruction never changes that.

1. Invoke `bugs-next` with the Skill tool directly (not inside an Agent call), passing the id if one was given — and `--confirmed` if this skill was given it. Let it present its recommendation and ask for confirmation in this context; in `--confirmed` mode it validates the id and asks nothing.
2. No `BUG_ID:` line back (cancelled, or confirmation couldn't be obtained) → stop and tell the user. Never go on without a confirmed id.
3. Otherwise `<id>` is the confirmed id. Read its row in `<backlog>/bugs-open.md` and its details in `<backlog>/bugs/<id>.md` now (if the details file is missing, fall back to the row's Summary as the report, and tell the user the write-up is missing and thin), and keep the steps to reproduce / expected / actual / environment / notes as `<repro-details>` to paste verbatim into the reproduce subagent's prompt — a subagent shouldn't have to hunt for them.

**Branch**: `<slug>` = `<id lowercased>-<2–4 kebab words from the title>` (e.g. `bug-004-report-total-wrong`); `<branch>` = the `[git] fix_prefix` (default `fix/`) + `<slug>`.

Before spawning any subagent, substitute `<id>`, `<slug>`, `<branch>`, `<repro-details>`, `<scripts>` (this skill's `scripts/` folder, absolute), `<repo-root>` and `<docs-skill>` (the `[docs] sync_skill` value, possibly empty) in its prompt; from Phase 3 also `<repro-test-path>`.

**Begin every subagent prompt with:** "Work in `<repo-root>` (cd there first). Never run `git commit`, `git push`, `git add`, `git stash`, `git reset` or any other git write. Never install system packages or change anything outside the repository."

## Phase 1 — Branch

Follow `reference/phase-branch.md`, with `<backlog-row>` = "Open `<backlog>/bugs-open.md`, find the `<id>` row, and if its Status is `⬜ Open` change it to `🔶 In Progress`."

## Phase 2 — Reproduce (subagent, foreground)

> The bug `<id>` was selected and confirmed with the user; do not re-select. Its recorded report:
>
> `<repro-details>`
>
> Write the **smallest test that fails because of this bug** and will pass once it is fixed. Pick the layer the bug really lives at — a unit test for logic, a component/integration test for a behaviour across pieces, an end-to-end or API test only when the bug appears only through a full flow — and prefer extending an existing test file over creating one. `<test-guidance>`
>
> Run just that test and confirm it **fails**, and that it fails *for the reason in the report* — not an unrelated error, a typo, a missing stub or a bad import. Quote the failing assertion in your hand-back.
>
> **If you cannot make it fail** — the behaviour looks correct, or the recorded steps are too vague — do not invent a fix and do not widen the bug. End with `FIX_BLOCKED — cannot reproduce <id>: <what you tried and what you observed>` and stop. Change nothing else.
>
> End with exactly: `REPRO: DONE — test: <path to the test file>` then `BUG_ID: <id>`.

`<test-guidance>` = the `[guidance] regression_tests` text from `.backlog-kit.toml` if set, else omit.

After it returns:
- `FIX_BLOCKED — cannot reproduce` → in your own context ask with **AskUserQuestion**: "Mark `<id>` as ❓ Cannot reproduce?" — "Yes, mark it Cannot reproduce" (invoke `bugs-archive <id> cannot-repro "<the subagent's note>"` and stop), "Keep it open — I'll add repro detail" (stop; leave the row `🔶 In Progress`), "Cancel". Do not go on to Phase 3.
- Any other `*_BLOCKED` → surface and stop.
- Otherwise capture the `REPRO: DONE — test: <path>` line as `<repro-test-path>`, check that the `BUG_ID:` echo equals `<id>` (anything else: blocked), and **run `<repro-test-path>` yourself** to confirm it fails, for the reason in the report, before going on — a hand-back is a claim, not evidence.

## Phase 3 — Fix & review (subagent, foreground)

> The bug `<id>` has a failing regression test at `<repro-test-path>`. Recorded report:
>
> `<repro-details>`
>
> **Step 1 — Fix.** Fix the **root cause**, not the symptom, with the narrowest change that does it. Never edit a file that records history already applied elsewhere (an applied database migration, a released changelog entry, a published schema) — add a new one instead. Then run `<repro-test-path>` and confirm it now **passes**. A blocker needing a human decision → end with `FIX_BLOCKED — <reason>` and stop.
>
> **Step 1b — The reported scenario.** The regression test pins the logic; also exercise the scenario the report describes (run the program or command, call the endpoint, drive the flow) as far as the project allows without installing anything, and quote what you observed against the expected result. If it cannot be run here, say `ORIGINAL SCENARIO: not verified — <why>`.
>
> **Step 2 — Review.** Follow `reference/phase-reviews.md` over the current diff: recompute scope with `python3 <scripts>/work_scope.py <repo-root>` before each review, fix every 🔴/🟡 finding, re-review until clean or the round cap.
>
> Never print or write a generated secret's raw value; leave any task needing one unchecked with the manual command named.
>
> End with exactly `FIX_IMPLEMENTED: DONE`, then `REVIEWS: <name> clean[, <name> clean …]` (adding ` (self-reviewed)` after any review that did not go through a fresh reviewer subagent — every review run through a configured `skill` counts, since it runs in your own context — or `REVIEWS: none applied`), then `ORIGINAL SCENARIO: confirmed — <observed>` or `ORIGINAL SCENARIO: not verified — <why>` — or `REVIEW_BLOCKED — …` / `FIX_BLOCKED — …`.

Do not start Phase 4 until it returns `FIX_IMPLEMENTED: DONE`; on any `*_BLOCKED`, surface and wait. Then **run `<repro-test-path>` yourself** and confirm it passes. Keep the `REVIEWS:` and `ORIGINAL SCENARIO:` lines for the final summary.

## Phase 4 — Gates

Follow `reference/phase-gates.md` with `<id>` = the bug id. It runs on **every** invocation, whatever the fix touched — a fix that looks unrelated can still break another test. Gates with narrower `when` globs are filtered by the changed files; the rest always run.

## Phase 5 — Close (subagent, foreground)

> **Step 1 — Docs (best-effort).** If `[docs] sync_skill` is set (`<docs-skill>`), invoke it for the current branch's changes. A bug fix usually changes no documented behaviour, so "nothing to sync" is the normal outcome; only stop if the skill errors and leaves files broken. If no skill is configured, skip.
>
> **Step 2 — Close the bug.** Invoke the `bugs-archive` skill with the Skill tool: `bugs-archive <id> fixed "<one line: the root cause, what changed, and the regression test path>"`. Wait for it to move the row to `bugs-fixed.md` and append the Resolution line to `<backlog>/bugs/<id>.md`. **Never hand-edit the backlog files, or re-implement the skill with an ad-hoc script, to get the same effect** — `bugs-archive` writes the destination before touching the source so an interruption never loses a row, and a hand edit loses that guarantee. If the Skill tool is unavailable to you or the skill errors, do not work around it: end with `ARCHIVE_BLOCKED — bugs-archive could not be run: <reason>` and change nothing.
>
> End with exactly `CLOSE: DONE`.

Do not show the final summary until the bug is closed. After `CLOSE: DONE`, spot-check in your own context that the `<id>` row is gone from `bugs-open.md`, present in `bugs-fixed.md`, and that `<backlog>/bugs/<id>.md` ends with a Resolution line — a hand-back is a claim, not evidence. On `ARCHIVE_BLOCKED` (or a failed spot-check), do the close yourself: invoke `bugs-archive <id> fixed "<resolution>"` with the Skill tool in your own context, then spot-check again. On `CLOSE_BLOCKED` (the work itself is not acceptable) surface the reason and wait; do not retry. Never close the bug by editing the backlog files directly.

---

## Final summary

```
## Bug Fix Complete

**Bug:** <id> — <title>
**Regression test:** <path> (failed before the fix, passes now)
**Root cause / fix:** <one or two sentences>
**Reviews:** <name> ✓ clean [(self-reviewed)] …  (or "none applied")
**Original scenario:** <confirmed — what was observed | not verified — why>
[if the branch phase reported the base ahead:] **Base:** <base> has <n> commit(s) this branch lacks (information; syncing the branch with the base brings them in)
**Gates:** <name> ✓ …  [if `uncovered_files`: ⚠ NOT VERIFIED BY ANY GATE: <n> files (<areas>)]  (or ⚠ NOT RUN: <gate> — <why>; or ⚠ FAILED (environment): <gate> — <tests>; or KNOWN FAILURE: <test>; or "none configured — nothing was verified beyond the regression test")
[if UNREVIEWED_PROD_FIXES:] **⚠ Unreviewed production changes:** <the PROD_CODE_FIXED lines> — made while fixing gate failures; you chose to proceed without re-review.
**Docs:** <one line, or "nothing to sync" / "no sync skill configured">
**Bug:** ✓ closed — moved to bugs-fixed.md

Nothing was committed. The fix and its regression test are on `<branch>`, uncommitted. Review with `git status` / `git diff`, then ask for `gitflow` — the skill named by `[git] finish_skill` (default `gitflow`; empty means do it by hand): its `commit` and `finish` actions commit the work and open the PR after asking you. Say so by name; never invoke it yourself.
```

## Guardrails (this skill's own; the shared ones are in `reference/pipeline-guardrails.md`)

- **Never run `git commit`, `git push` or open a PR.** The finished work is left uncommitted on its branch for the human to review and commit. The only git writes this workflow performs are in Phase 1: `git switch` / `git switch -c` and `git merge --ff-only` (a fast-forward creates no commit) — never a non-fast-forward merge, rebase, pull, stash or reset.
- Capture the id confirmed in Phase 0 and substitute it everywhere. If `bugs-next` returns no `BUG_ID:`, stop before any subagent exists.
- **The regression test is written before the fix and must fail for the right reason before Phase 3 starts.** If Phase 2 can't reproduce the bug, that is `FIX_BLOCKED — cannot reproduce`, resolved through the decision point above — never worked around by jumping to a speculative fix.
- **Phase 4's gates always run.** They are never skipped because the fix "only touched" something small.
- Reviews are always scoped to the current diff and non-interactive; they never sweep the whole codebase.
- `--skip-branch-setup` affects only Phase 1 (it passes `--batch`). Every other phase already works on "whatever branch is checked out".
- `--confirmed` removes only Phase 0's per-bug question, and only for an id the caller vouches the user approved. Every other decision point — the cannot-reproduce choice, gate setup, a partial-gates result, a `PROD_CODE_FIXED` choice, any blocker — still goes to the user.
