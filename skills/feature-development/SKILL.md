---
name: feature-development
description: Orchestrates the full lifecycle of one backlog feature — selects it (features-next), sets up a feature branch, plans it (and, with OpenSpec, proposes the spec), implements it with tests, runs the configured reviews and verification gates until they pass, then archives it (features-archive; plus OpenSpec archive and a spec-compliance check when spec.workflow = "openspec"). Never commits — leaves the work uncommitted on its branch for the human to review and open as a PR. TRIGGER when the user asks to develop a feature or to build the next feature from the backlog.
license: MIT
metadata:
  version: "0.1"
---

Orchestrate one feature from selection to archive, one subagent per phase. `<backlog>` is `docs/backlog` unless `.backlog-kit.toml` says otherwise. Everything project-specific — verification commands, reviews, branch prefixes, whether OpenSpec is used — comes from that file, never from this skill.

**Input**: an optional feature name or number, optionally followed by `--skip-branch-setup` and/or `--confirmed`. The name/number is passed to `features-next` to skip the recommendation and go straight to confirmation. `--skip-branch-setup` is for orchestrators (a batch runner) that already checked out one shared branch and run several features on it without committing between them. `--confirmed` (only with a name/number) means the caller already got the user's approval of this exact feature as part of a confirmed list, so the per-feature question is skipped. A batch runner passes both; omit both for normal single-feature use.

**Before starting**, read `reference/pipeline-guardrails.md` — the rules that hold across every phase (no commits, confirmations reach the user, one branch, no weakening tests, no secrets).

## Phases

| Phase | Who | What |
| ----- | --- | ---- |
| 0 — Select & confirm | orchestrator's own context | `features-next` (recommend + mandatory `AskUserQuestion`) |
| 1 — Branch | subagent | `reference/phase-branch.md`: create/resume `feature/<change-name>`, flip the row to `🔶 In Progress` |
| 2 — Plan | subagent | read the brief; with OpenSpec, `openspec-propose` if artifacts are missing; check for a newly discovered hard dependency |
| 3 — Implement & review | subagent | build it with tests; with OpenSpec, `openspec-apply-change`; then the configured reviews (`reference/phase-reviews.md`) |
| 4 — Gates | orchestrator pre-step + subagent | `reference/phase-gates.md`: the project's own verification commands, to a pass |
| 5 — Close | subagent | with OpenSpec, a spec-compliance check that closes every gap; optional docs sync; archive the change; `features-archive` |

---

## Phase 0 — Select & confirm (orchestrator's own context — never a subagent)

Selecting what gets built next is the user's decision, always — a spawned subagent can't reliably surface `AskUserQuestion`, and "auto mode" never changes that.

1. **OpenSpec only** (`spec.workflow = "openspec"`): run `openspec --version` yourself. If it fails or the CLI isn't found, tell the user `PLAN_BLOCKED — openspec CLI not found` and stop; don't select a feature with a broken toolchain. (backlog-kit depends on OpenSpec but never bundles it — it must be installed separately.)
2. Invoke `features-next` with the Skill tool directly (not in an Agent call), passing the name/number if one was given — and `--confirmed` if this skill was given it. Let it present and ask in this context; in `--confirmed` mode it validates the feature (including that no prerequisite is unbuilt) and asks nothing.
3. No `CHANGE_NAME:` line back (cancelled, or confirmation couldn't be obtained) → stop and tell the user. Never go on without a confirmed name.
4. Otherwise `<change-name>` is the confirmed name. Find its brief file `<backlog>/features/NNN-<change-name>.md` from the row's `Brief` link — `<brief-path>`.

**Branch**: `<branch>` = the `[git] feature_prefix` (default `feature/`) + `<change-name>`.

Before spawning any subagent, substitute `<change-name>`, `<branch>`, `<brief-path>`, `<scripts>` (this skill's `scripts/` folder, absolute), `<repo-root>`, `<changes-dir>` (`[spec] changes_dir`) and `<docs-skill>` (the `[docs] sync_skill` value, possibly empty) in its prompt.

**Begin every subagent prompt with:** "Work in `<repo-root>` (cd there first). Never run `git commit`, `git push`, `git add`, `git stash`, `git reset` or any other git write. Never install system packages or change anything outside the repository."

## Phase 1 — Branch

Follow `reference/phase-branch.md` with `<id>` = `<change-name>` and `<backlog-row>` = "Open `<backlog>/features-planned.md`, find the row whose Change name is `<change-name>`, and if its Implementation is `⬜ Pending` change it to `🔶 In Progress`."

## Phase 2 — Plan (subagent, foreground)

> The feature `<change-name>` was selected and confirmed; do not re-select. Prepare it for implementation.
>
> **Step 1 — Read the brief** at `<brief-path>`. It — not the one-line Summary in the backlog table — is the description of what to build. If it is missing or empty and no spec artifacts exist for the change, end with `PLAN_BLOCKED — brief file missing or empty`.
>
> **Step 2 — Spec artifacts (OpenSpec only).** If `<changes-dir>/<change-name>/` is missing artifacts the change needs before it can be applied (proposal, specs, design, tasks), invoke `openspec-propose` for `<change-name>`, giving it the brief verbatim as the description. Confirm everything required before applying is done. If it can't produce them, end with `PLAN_BLOCKED — <reason>`. Skip this step when OpenSpec isn't in use.
>
> **Step 3 — Check for a newly discovered hard dependency.** Now that you have the brief (and, with OpenSpec, the design), does the feature need something that doesn't exist yet — a data model, API, service, or another backlog feature — that is neither implemented nor already recorded as a dependency of this feature? Check `<backlog>/features-implemented.md`, `<backlog>/features-planned.md`'s `### Hard implementation dependencies`, and the repository itself.
> - None, or already recorded → continue.
> - A genuine unrecorded one → add `**Feature <this #> → Feature <dep #>** (still pending)` with a one-sentence reason under `### Hard implementation dependencies` in `features-planned.md` (if the dependency has no backlog row, say so and recommend `feature-plan` for it), then end with `PLAN_NEEDS_DEPENDENCY_DECISION — <change-name> (#<n>) needs <dependency> which is not implemented`.
> Only record dependencies without which a usable first version cannot work; don't hunt for speculative ones.
>
> End with exactly `PLAN: READY` (or one of the signals above).

After it returns:
- `PLAN_BLOCKED` → surface and stop.
- `PLAN_NEEDS_DEPENDENCY_DECISION` → this is not a failure but must not barrel into implementation. In your own context ask with **AskUserQuestion**: "`<change-name>` depends on something not built yet. How to proceed?" — "Stop — I'll build the dependency first" (stop; the note stays recorded), "Proceed anyway — it isn't a blocker for a usable first version" (continue to Phase 3; the note stays), "Cancel". Only "proceed anyway" continues.
- Otherwise continue.

## Phase 3 — Implement & review (subagent, foreground)

> Implement `<change-name>`.
>
> **Step 1 — Build it.** With OpenSpec, invoke `openspec-apply-change <change-name>` and work through every task, ticking each as it is done. Without it, read `<brief-path>`, write yourself a short numbered checklist of the concrete changes it implies, and implement each. Either way, follow the conventions already in the codebase, **add tests alongside the code** — tests that would fail without the change — and don't build beyond the brief. A blocker needing a human decision → end with `IMPLEMENT_BLOCKED — <reason>` and stop.
>
> Never print or write a generated secret's raw value; leave any task needing one unchecked with the manual command named.
>
> **Step 2 — Review.** Follow `reference/phase-reviews.md` over the current diff: recompute scope with `python3 <scripts>/work_scope.py <repo-root>` before each review, fix every 🔴/🟡 finding, re-review until clean or the round cap.
>
> End with exactly `IMPLEMENT: DONE` (or `IMPLEMENT_BLOCKED — …` / `REVIEW_BLOCKED — …`).

Do not start Phase 4 until it returns `IMPLEMENT: DONE`; on any `*_BLOCKED`, surface and wait.

## Phase 4 — Gates

Follow `reference/phase-gates.md` with `<id>` = `<change-name>`. It runs on **every** invocation; a gate with a narrower `when` glob is filtered by the changed files, the rest always run.

## Phase 5 — Close (subagent, foreground)

> Perform these steps in order.
>
> **Step 1 — Verify spec compliance and close every gap (OpenSpec only).** If the project has its own spec-compliance skill, use it; otherwise do this yourself, read-only against `<changes-dir>/`: read `<changes-dir>/<change-name>/specs/**/spec.md` and `tasks.md`, and classify every acceptance scenario as **Verified** (a passing test or concrete evidence exercises exactly what it claims), **Unverified** (it may well be right, but nothing proves it), or **Failing** (the code contradicts it).
> - **Any Failing** → stop: `CLOSE_BLOCKED — <N> failing scenario(s): <summary>`. That is a real behavioural gap and belongs back in Phase 3, not fixed here.
> - **Any Unverified** → close every one; never carry one forward as a caveat. Add the missing test coverage (extend an existing test file where you can), re-classify, repeat. If a new test fails because the scenario is actually broken, treat it as Failing — never weaken the test. After 3 rounds with a scenario still unverifiable, stop: `CLOSE_BLOCKED — repeated spec-compliance cycles, <N> scenario(s) still unverified`.
> - Once all are Verified, re-run the project's gates that cover tests (`python3 <scripts>/work_scope.py <repo-root>` lists them) to confirm the new tests pass alongside everything else.
>
> **Step 2 — Docs (best-effort).** If `<docs-skill>` is non-empty, invoke it for the current branch's changes. "Nothing to sync" is fine; only stop if it errors and leaves files broken. Skip if empty.
>
> **Step 3 — Archive the spec change (OpenSpec only).** Invoke `openspec-archive-change <change-name>` and respond to any prompts about delta-spec sync or incomplete tasks normally. Wait for it to finish.
>
> **Step 4 — Archive the feature.** Invoke `features-archive <change-name>` and wait until the row has moved from `features-planned.md` to `features-implemented.md`.
>
> End with exactly `CLOSE: DONE`.

Do not show the final summary until it returns `CLOSE: DONE`. A `CLOSE_BLOCKED` means the feature is implemented and tested but **not archived** — surface the scenarios and wait; never retry automatically. This workflow never archives a change with a known spec-compliance gap.

---

## Final summary

```
## Feature Development Complete

**Feature:** #<n> <change-name>
**Spec:** <✓ proposal, specs and tasks created | N/A — OpenSpec not in use>
**Implementation:** ✓ done, with tests
**Reviews:** <name> ✓ clean  …  (or "none applied")
**Gates:** <name> ✓ …  [if `uncovered_files`: ⚠ NOT VERIFIED BY ANY GATE: <n> files (<areas>)]  (or ⚠ NOT RUN: <gate> — <why>; or ⚠ FAILED (environment): <gate> — <tests>; or KNOWN FAILURE: <test>; or "none configured — nothing was verified")
[if UNREVIEWED_PROD_FIXES:] **⚠ Unreviewed production changes:** <the PROD_CODE_FIXED lines> — made while fixing gate failures; you chose to proceed without re-review.
**Spec compliance:** <✓ all scenarios verified | N/A>
**Docs:** <one line, or "nothing to sync" / "no sync skill configured">
**Archive:** ✓ <spec change archived;> feature marked implemented

Nothing was committed. The work is on `<branch>`, uncommitted. Review with `git status` / `git diff`, then commit and open the PR yourself.
```

## Guardrails (this skill's own; the shared ones are in `reference/pipeline-guardrails.md`)

- **Never run `git commit`, `git push` or open a PR.** The finished work is left uncommitted on its branch for the human to review and commit. The only git writes this workflow performs are in Phase 1: `git switch` / `git switch -c` and `git merge --ff-only` (a fast-forward creates no commit) — never a non-fast-forward merge, rebase, pull, stash or reset.
- Capture the name confirmed in Phase 0 and substitute it everywhere. If `features-next` returns no `CHANGE_NAME:`, stop before any subagent exists; no subagent is ever given the chance to cancel or change the selection.
- Do not start Phase 3 after `PLAN_BLOCKED`, **or after `PLAN_NEEDS_DEPENDENCY_DECISION` until the user says "proceed anyway"** — the workflow must never barrel into implementing a feature whose missing dependency was just discovered.
- **Phase 4's gates always run**, on every invocation.
- Reviews are always scoped to the current diff and non-interactive; they never sweep the whole codebase.
- **Never archive a change with a known spec-compliance gap.** Every Unverified scenario is closed with real, passing test coverage before archiving, or the archive doesn't happen — there is no "archive now, note the gap" path.
- `--skip-branch-setup` affects only Phase 1 (it passes `--batch`). Every other phase already works on "whatever branch is checked out".
- `--confirmed` removes only Phase 0's per-feature question, and only for a feature the caller vouches the user approved. Every other decision point — the dependency decision, gate setup, a partial-gates result, a `PROD_CODE_FIXED` choice, any blocker — still goes to the user.
- OpenSpec is a dependency, never bundled: when `spec.workflow` is `"none"`, no phase mentions or requires it.
