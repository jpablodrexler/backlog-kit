# backlog-kit — design notes (v0, scratch)

Thesis: *your backlog is plain markdown in the repo, and Claude works it to done through quality gates. Nothing is committed without you.* (See pablo-web ADR 0032.)

## What's here

```
lib/backlog_kit.py          shared: config loading, markdown-table parsing, path resolution, scoring
backlog-kit.example.toml    every config key with its default
skills/                     the 9 core skills (SKILL.md + scripts/)
  feature-plan  features-next  features-status  features-archive
  bug-report    bugs-next      bugs-status      bugs-archive
  decision-record
skills/ (work skills)       bug-fix, feature-development — orchestrators; project specifics come from config
skills/ (batch skills)      bugs-batch-fix, features-batch-development — thin per-family skills over one shared loop
shared/                     phase documents (branch, reviews, gates, guardrails) and the batch loop (batch-runner.md)
tools/vendor.py             copies lib/ and shared/ into each skill so it is self-contained (--check for CI)
examples/                   a complete worked config (angular-supabase.toml)
tests/                      script behaviour (throwaway git repos) + skill lint + the shipped example
```

Run the tests: `python3 tools/vendor.py && python3 -m unittest discover -s tests -v`

## Configuration

Optional `<repo-root>/.backlog-kit.toml`; absent file = defaults. Sections: `paths`, `features` (priorities, efforts, areas, priority_labels), `bugs` (id_prefix, severities, environments, prod_environments, severity_labels), `spec` (workflow = "none" | "openspec", changes_dir). Scoring is *derived from list order* (first priority = highest), so a team can have 3 priorities or 6 without touching a script.

Scaffolding (creating the backlog files + Column legend) moved from prose into `scaffold.py`, so the legend a skill reads and the vocabulary a script validates come from one source.

## Behaviour changes from the pablo-web originals

| Change | Why |
| --- | --- |
| Dropped the `Schema Change` column, the "Deployment (migration) dependencies" table, and the Supabase-only `Area` values | Stack-specific. |
| features-next tier 4 was "no schema change (+5)"; now "smallest configured effort (+5)" | Keeps a quick-win nudge without a stack-specific column. |
| bugs-next tier 4 ("no schema fix", detected by grepping details for `migration\|RLS`) removed | Pure stack heuristic. |
| `SDD Artifacts` column and the `[spec]` link exist only when `spec.workflow = "openspec"` | OpenSpec is a dependency, never bundled or required. |
| Bug `Area` is free text; legend no longer lists routes | Was this app's route list. |
| Table parser tolerates one stray blank line inside a table in the bug scripts too (it already did in the feature scripts) | Consistency; an easy hand-edit slip. |
| Removed the `BUG-070`/`BUG-071` historical-quirk notes, references to `feature-development`, `bug-fix`, `web-docs-sync`, `opsx:*` | Project history / skills outside the core. |
| Every skill carries the same guardrail verbatim: **Never run `git commit`, `git push` or open a PR.** (enforced by `tests/test_skills.py`) | The public promise. |

Validated against pablo-web's real backlog (95 bugs, 99 features): bugs-status and features-status counts, the integrity section, the bugs-next and features-next rankings, and next-id output are identical to the originals; only table padding and legend wording differ.

## The work skills (bug-fix, feature-development)

The originals were ~900 lines of prose welded to one stack (npm scripts, a Cypress component tier, a mocked and a live E2E tier, three reviewer skills, a viewport check, `gitflow`, `web-docs-sync`, `spec-compliance-check`, `openspec-*`). Generalizing meant replacing *what* they run with *configuration* and keeping *how* they orchestrate:

| Hardcoded in the original | Now |
| --- | --- |
| `npm run test` + `npm run test:e2e:mocked` + `npm run build` | `[[gates]]` — ordered commands with `cwd`, `when` globs, `timeout_minutes`. With none configured, `detect_gates.py` proposes some from the repo and the user confirms once; they are saved to `.backlog-kit.toml`. |
| the live-backend E2E tier and its credential-source question | a gate with `ask_before`: the orchestrator asks the user first; "skip" is recorded as NOT RUN, never silently dropped |
| `code-reviewer` / `database-reviewer` / `security-reviewer` / viewport check, each with a hardcoded trigger | `[[reviews]]` — `when` globs, and either a `skill` to delegate to or a `focus` for the built-in reviewer. Default: one general `code` review |
| `gitflow` start/sync/finish | `branch_state.py` (read-only) recommends one action; the subagent carries it out with plain `git switch` / `--ff-only` |
| a long branch/resume/fetch/dirty-tree prose algorithm | `branch_state.py`, tested against real repos incl. a bare origin (diverged, behind, remote-only) |
| `git status` parsing in prose | `work_scope.py` (changed files incl. untracked; which gates/reviews apply) |
| test layer for the regression test (Cypress / mocked E2E / pgTAP) | `[guidance] regression_tests` free text |
| `web-docs-sync` | `[docs] sync_skill`, optional, best-effort |
| `spec-compliance-check`, `openspec-*` | only with `spec.workflow = "openspec"`; compliance check is inlined (use the project's own skill if it has one) |

### Behaviour changes worth knowing

- **No sync merge.** The originals merged `origin/develop` into the work branch (and `origin/<branch>` from another device) and called that exempt from "no commits". A non-fast-forward merge *is* a commit, so the generic version drops it: it only fast-forwards, and when the base has moved or the branch diverged it tells the human instead. This keeps the public promise literally true.
- **Enforced in code, not just prose.** `lib/gitread.py` is the only module that may import `subprocess`; it has an allowlist (no commit/push/merge/rebase/add/reset/switch/checkout/tag/…) and refuses destructive `branch`/`fetch` flags. `tests/test_skills.py` fails if any other file shells out, if the allowlist grows a write command, or if a skill lacks the verbatim promise.
- Reviews are a loop with a cap (`review_max_rounds`) and a fresh reviewer; findings live in checkbox reports under `reports_dir/review/`.
- Dropped: the mobile/desktop viewport step (expressible as a `[[reviews]]` entry — see the example), the `.e2e-credentials.json` handling (a shared guardrail now says: never read a hand-maintained credentials file unless an approved gate needs it).
- `--skip-branch-setup` is kept (it passes `--batch` to `branch_state.py`) for a future batch runner, which is **not** yet generalized.

### Self-containment

`tools/vendor.py` copies `lib/*.py` into each skill's `scripts/` and `shared/*.md` into the work skills' `reference/` (marked as vendored; `--check` fails on drift). This closes the old open item about the shared-lib path: any skill works installed alone. Cost: ~40 generated files in the repo — edit the sources only.

## The batch skills (bugs-batch-fix, features-batch-development)

The two originals were line-for-line mirrors (240 and 328 lines) differing only in nouns. Now: **one shared loop** (`shared/batch-runner.md`) and two thin skills (~60 lines each) that supply the family-specific parts — input forms, the whole-backlog set and order, and how the work skill's outcome maps to a report status.

The fragile, mechanical parts became tested scripts rather than prose:

| Step | Script | What it guarantees |
| --- | --- | --- |
| Resolve + order the list | `batch_plan.py` | normalizes ids (`4`, `bug-4` → `BUG-004`; `#2` or a name for features); reports `unresolved`, `already-closed/implemented`, `wont-fix`, `cannot-repro`, `duplicate` as *problems* the user must settle; warns on a feature ordered before — or run without — its pending prerequisite; `--all` ranks like `features-next`/`bugs-next` (in-progress, then priority/severity tier, prerequisite before dependent, order list and table order only break ties; warns when the hand-kept order list disagrees) |
| Resume an interrupted run | `batch_report.py find` | Jaccard overlap → `exact` / `near` (≥0.8) / `partial` / `none`; only a report with an item still `not-started` or `in-progress` is resumable; a blocked or skipped item does not keep a run "open" |
| Progress report | `batch_report.py init / set / finish / show` | the report is only ever written by this script, atomically (temp file + `os.replace`), one entry per call, so a crash can never leave a half-written file; `finish` is idempotent |
| Branch | `branch_state.py` (shared with the work skills) | a fresh run on a dirty tree or a diverged branch is `blocked`; resume with a missing branch stops instead of recreating one |

Changes from the originals: `gitflow` is gone (branch step uses `branch_state.py` + plain `git switch` / `--ff-only`); "already closed / won't fix" items offer *skip or stop* only — the originals offered an "override and re-run", which the selection step (`bugs-next` / `features-next`) could never honour, since it only offers open items; the report lives under the configurable `reports_dir`; it is no longer assumed to be gitignored.

## Dogfood run 1 — jp-photo-manager (Java + .NET + Angular), 2026-10-06

Driven live in a throwaway clone: `bug-report` ×2 → `bugs-batch-fix` over both → `bug-fix` ×2 (branch, reproduce, fix + review, gates, close) → `bugs-archive`. Real subagents, real Maven (1045-test backend suite), real prompts to the user. Result: **2 of 2 bugs closed; both turned out to be genuine defects in jp-photo-manager** (Windows-style `\` playlist paths never match on Linux; non-UTF-8 playlists return nothing) — patch in `deliverables/`.

What worked first time: scaffolding, id numbering, the table-shape edge case when the first row replaces the placeholder, `bugs-status` integrity checks, the incremental report, `batch_plan` ordering, the failing-test-first discipline (both repros verified independently), destination-before-source archiving, "never commits" (0 commits throughout), the known-failures path.

Found by the run and **fixed** (all with regression tests):

| # | Finding | Fix |
| - | ------- | --- |
| 1 | `detect_gates` searched one folder deep, so it found the .NET project but missed `JPPhotoManagerWeb/backend` (Maven) and `/frontend` (npm) | depth-3 search; a module under a folder that already provides the same tool is skipped |
| 2 | A fresh batch run was **blocked as "dirty tree"** by the kit's own files (backlog written by `bug-report`, installed skills) — every first run would have hit this | `kit_globs()`: backlog, reports and decisions folders, `.backlog-kit.toml`, installed skills never count; real uncommitted work still blocks and is named |
| 3 | `git switch -c <branch> origin/develop` made the new branch **track the integration branch** | `create` uses `--no-track` (lint-enforced) |
| 4 | `work_scope` reported 148 changed files (146 were kit bookkeeping); the reviewer had to narrow by hand, and a `**` gate/review matches everything | kit files excluded from `changed_files`, counted in `kit_files_ignored` |
| 5 | A gates subagent **installed `dotnet-sdk-8.0` with apt** — the prose said "try the obvious remedy (install…)" | remedies are project-local only; never system packages, `sudo`, global config |
| 6 | One unrunnable gate (`dotnet test` on Linux) **stopped all verification**, so the Maven gate that actually covers the fix never ran | `NOT RUN (environment)` / `FAILED (environment)` are recorded and the run continues; `GATES: PARTIAL` goes to the user, never waved through |
| 7 | The pristine baseline was already red (a root-user-only test) — no concept of a known pre-existing failure | per-gate `known_failures`; reported as `KNOWN FAILURE`, not fixed, and the user can save one with a single answer |
| 8 | `npm install` rewrote `package-lock.json` (-149 lines) and the hand-back said "no changes" | remedies must not modify tracked files (`npm ci`); plus a guardrail: **a hand-back is a claim, not evidence** — spot-check it |
| 9 | Subagents don't inherit the working directory | every prompt starts "Work in `<repo-root>`…" |

## Open after the dogfood

1. **Name shadowing.** Skills are resolved by name, and a repo (or user) that already has `bug-report`, `bug-fix`… gets *its* copy, not the kit's — the harness loaded pablo-web's `bug-report` instead of the kit's, and I had to drive the kit's from the file. Installation docs must say: remove or rename same-named skills first, or install as a plugin so names are namespaced. (Not testable from here: how a plugin install resolves a clash — check the plugin docs.)
2. ~~**Per-bug confirmation in a batch**~~ — **done.** The batch runners pass `--confirmed` (alongside `--skip-branch-setup`); `bugs-next` / `features-next` then re-validate the id with `--select` and skip only the selection question. A stale, closed or *blocked* item still stops; `--confirmed` without an id is ignored; the list confirmation says it covers every item; gate setup, partial gates, cannot-reproduce, dependency and blocker prompts are untouched.
3. **"Fresh reviewer" is the same agent.** Subagents can't spawn subagents, so the review phase is a self-review — it found nothing the author didn't. Real independence needs the orchestrator to spawn the reviewer; worth a design pass.
4. **Phase 1 as a subagent is overkill in batch mode** (a script call and a one-line row flip). Run it inline.
5. **Not exercised:** `feature-development`, `features-batch-development`, the OpenSpec path, resume of an interrupted batch, `Retry now` / `Skip` / `Stop` on a blocked item, `GATES_BLOCKED` (a real defect the subagent can't fix), `--skip-branch-setup` with a clean tree. The machinery under them is unit-tested.

## Open items

1. **Prose only partly tested live (see Dogfood run 1).** Every script is tested (throwaway git repos, a bare origin, the shipped example config, batch resolution/ordering/resume), but the SKILL.md orchestration — subagent prompts, decision points, hand-back signals — has not been driven end to end. Dogfood the work skills and one batch run in a non-Angular repo (jp-photo-manager: Java + .NET) before announcing.
2. **`--all` follows the Recommended implementation order exactly, even when it isn't priority-sorted** (as the original did). On pablo-web's real backlog the two P1 features sit last in that list, so `features-batch-development --all` builds them last while `features-next` would pick them first. Decide whether the batch runner should instead sort by priority (then dependencies) and treat the order list as a tie-break, matching `features-next`.
3. **The built-in reviewer is deliberately minimal** (a focus string and a checkbox report). Specialized reviewers stay as the project's own skills, reachable through `[[reviews]] skill = …`. Decide whether backlog-kit ships any stack-neutral review skills of its own.
4. **`gitflow` is not in the core** (Gitflow-specific). The work skills no longer need it; ship it, if at all, as a separate optional plugin.
5. **Python 3.11+** is required only to *read* `.backlog-kit.toml` (tomllib); with no config file the scripts need 3.8+. Consider a JSON fallback.
6. **Name availability** for `backlog-kit` (GitHub / npm / marketplace) is still unchecked.
7. `bug-report` step 9 calls the sibling `../bugs-status/scripts/…`, which only resolves when the skills sit side by side (true for a plugin install). Same fix as the work skills if it matters: vendor the report script.
8. OpenSpec CLI behaviour (`openspec status`, the propose/apply/archive skills) is referenced, not re-implemented; confirm the exact commands against the current OpenSpec docs when testing with `spec.workflow = "openspec"`.

## Dogfood run 2 (features batch, jp-photo-manager clone)

Result: 3/3 features built across a refused-at-selection and a live resume; zero commits; backend gate 1071 tests (only the known root-user failure).

Found and fixed in the kit:
- A feature ordered before its prerequisite is refused at selection; this needed an outcome row (`blocked`, retry on resume).
- Frontend/doc changes were covered by no gate; `work_scope` now reports `uncovered_files` and the gate phase asks the user.
- `batch_report.py find` ignored finished runs that still held a `blocked` item, so the documented "resume retries it" path never triggered. Blocked items now keep a report resumable (test added).

Still open: confirm-before-write must show the draft in the same turn (I skipped it once); worker restarts re-prompt confirmations; tests don't assert log output in the built feature; OpenSpec path and GATES_BLOCKED still untested live.

## Packaging (0.1.0)

Repo root is both a Claude Code plugin (`.claude-plugin/plugin.json`) and a one-plugin marketplace; `claude plugin validate` passes and a clean-HOME install yields all 13 skills. Plugin install namespaces skills (`backlog-kit:bug-fix`), which resolves the same-name shadowing seen in the dogfood runs. Fallback: `tools/install.py` copies skills into `.claude/skills/` and refuses to overwrite without `--force`. Name check: `backlog-kit` is unclaimed on npm and PyPI; GitHub could not be checked from the sandbox.

## `--all` ordering (0.1.2)

`--all` used to follow the Recommended order list verbatim, so a stale or hand-reordered list could run a P3 before a P1. It now uses the same ranking as the `*-next` skills; the list only breaks ties and a disagreement is reported as a warning. A named `--ids` list is still run exactly as given. `order_basis` is now `severity` (bugs) or `priority` (features).

## Stale "blocked on #N" order notes (0.1.3)

Found in dogfood run 2: after feature #1 was archived, the order-list bullet for #2 still read "blocked on #1". `features-archive` fixed the dependency blocks but never the free text in the Recommended implementation order. Now `scripts/clean_order_notes.py` (archive step 7b) removes the shipped prerequisites from "blocked on/by" clauses, keeps unshipped ones, and is idempotent; `features-status` reports any such note as a data-integrity warning (so notes left by hand edits or older versions surface too). The clause grammar is deliberately narrow (`blocked on|by` followed by `#N` / `` `name` (#N) `` items) so it never rewrites other prose.

## Findings from a real install test (0.1.4)

Reviewing `backlog-kit-test` (a repo where the plugin was installed and two features and one bug were run end to end) showed:

- **Config and tables out of step.** `spec.workflow = "openspec"` was set, but `features-planned.md` had been created without the `SDD Artifacts` column. A row drafted for the configured header landed in the wrong columns (Brief = "⬜ Pending"), and nothing named the cause. `scaffold.py` now reports `planned_header_mismatch` and repairs it with `--fix-header` (lossless, both directions); `features-status` reports the mismatch.
- **Features archived with no spec.** Both features were archived as implemented under `openspec` with no spec change, no `[spec]` link and no initialized `openspec/` project at the time. `feature-development` now stops with `PLAN_BLOCKED` if the OpenSpec project folder is missing, and `features-status` lists implemented features without a `[spec]` link (informational, since it is expected for features finished before adoption).
- **Empty order list lost its placeholder.** Archiving the last planned feature left the Recommended implementation order with no `_None yet._`, unlike the bug side. `clean_order_notes.py` restores it.

What worked: the bug-fix cycle (report, regression test, fix, review report, archive, Resolution line) left a consistent backlog, and the review reports were written under `docs/reports/review/`.

## First OpenSpec run on a real install (0.1.5)

`backlog-kit-test` feature #3 (`arg-parser`) went through the full OpenSpec path: change proposed, applied, reviewed (two rounds), gates PARTIAL accepted by the user, spec-compliance Verified, change archived with its `[spec]` link, dependency notes marked resolved, and the stale "blocked on #3" order-list notes removed by `clean_order_notes.py`. The orchestrator spot-checked the archive itself and flagged what it could not settle.

Found: the spec-compliance step classified scenarios only. The brief said both "no behaviour change" and "ignore unknown flags", which changes `--whatever Juan`; the review reported it as a suggestion, the proposal was corrected, but the requirement "Greeting output is unchanged" was archived and synced into `openspec/specs/` next to a scenario that contradicts it. The close phase now also checks requirement prose: a declared intentional change gets the requirement reworded, an undeclared one blocks the close, and a change is never archived with a known prose conflict.

Also learned: `FAILED (environment)` gates can be remembered as known failures, but a gate that cannot run (`NOT RUN`) cannot, so run 2 of the guide is expected to re-ask per feature (to be measured).

## Dependency detection (0.1.6)

Spotting a hard dependency used to depend on a model noticing it while reading a brief (a vague brief once hid one in dogfood run 2). `lib/dep_scan.py` now does the mechanical half and hands back evidenced candidates:

- **mention**: the brief names another pending feature (its change name, `feature N`, `#N`) with no recorded `Feature X → Feature Y`.
- **symbol**: the brief uses a backticked identifier or file that exists nowhere in the repository, and exactly one other pending brief introduces it (named within a few words after a defining verb, in a sentence that is not about tests).

It is wired in three places: `feature-plan` shows candidates in the draft and records one only if the user confirms; `feature-development` Phase 2 must confirm or dismiss every candidate (`DEPS_DISMISSED: #n — reason`, never silently); `features-status` lists them as information. Candidates are proposals, never blockers: only recorded dependencies make `features-next` refuse a feature. Known limits: it cannot see a dependency on something described only in prose with no backticked name, and a symbol defined in two briefs is ignored as ambiguous.

## Archiving and "finish" (0.1.7)

Question raised: by the time the user says "finish a feature", `feature-development` has already archived the OpenSpec change and moved the row to implemented, so archiving feels like it belongs to finishing. Decision (the user's): keep the behaviour of the two source projects, pablo-web and jp-photo-manager. `feature-development` / `bug-fix` end with the work verified, spec-compliance checked, the change archived and the row implemented, all uncommitted on the branch; committing and opening the PR is a separate, project-specific step (in those repos the `gitflow` skill's finish action, which refuses to run on a dirty tree and only opens the PR). backlog-kit does not ship that step, because it would have to commit and push, which the kit promises never to do.

What changed: an optional `[git] finish_skill` in `.backlog-kit.toml`. When set, the hand-off message names that skill ("hand the branch to `gitflow`'s finish action") instead of the generic "commit and open the PR yourself". The kit only names it; it never invokes it.

Open trade-off, deliberately accepted: a spec change archived before human review is already synced into `openspec/specs/` if the review then rejects the work. The archive can be reverted with plain git before anything is committed.

## `gitflow` joins the plugin (0.2.0)

Why: the loop the kit exists for is plan → select → branch → develop and verify → commit → PR → review → merge → clean up → select the next item. With no skill for the two ends, the workflow was cut exactly where work gets published (and the "finish" confusion in 0.1.7 was a symptom). pablo-web and jp-photo-manager both have a `gitflow` skill for this; the kit now ships a generalized one.

What it is: `skills/gitflow` with five actions — `start feature|fix`, `sync`, `commit`, `finish` (push + open the PR), `cleanup` — driven by `[git] base_branch / feature_prefix / fix_prefix`. Read-only facts come from `lib/flow_plan.py` (the commit's files with secrets flagged, what a PR would contain including the backlog items it finishes and the review reports, which branches look merged); every write is done by the skill and preceded by a yes. Left out on purpose: `release` / `hotfix` (version bump, changelog, E2E gate are project-specific; a project can still point `[git] finish_skill` at its own skill), and merging (always the human's).

The public promise changed accordingly, as decided by the owner: "Nothing is committed, pushed or opened as a PR unless you ask for it." The work skills and batch runners are unchanged (they still never write beyond branch switching and fast-forwards, and the lint tests still require the canonical sentence in each of them). `gitflow` is the only skill exempt from it, carries its own stricter sentence, and a test fails if any other skill is described as able to invoke it. The default `[git] finish_skill` is now `gitflow`, so the work skills' hand-off message names it.

Follow-up for the owner: ADR 0032 in pablo-web records the old promise ("never commits"); it deserves a short superseding ADR.

## Comparison with the source projects (0.2.1 – 0.2.4)

A read-only comparison of every plugin skill against pablo-web and jp-photo-manager (report: `plugin-vs-originals-comparison.md`) found defects and weakened safeguards. They are fixed in four patch releases; each fix has a regression test (`tests/test_fixes.py` and friends).

0.2.1 — correctness: spec-artifact readiness read from disk (and the `SDD Artifacts` cell set when artifacts exist); `gitflow cleanup` no longer reports a just-started branch as merged, never force-deletes and never offers protected branches; the commit plan counts new files; gates stop after `gate_max_rounds`; the archived-spec link is computed from the real layout; stale dependency notes written in prose are detected; `decision-record` writes nothing before the user confirms; `bugs-archive` replaces instead of duplicating a Resolution line; `bugs-status` checks every closed bug; the OpenSpec skills are preflighted.

0.2.2 — spec-compliance rigor restored. Folding the project skill into the close phase had dropped its evidence rules. They now live in one shared procedure (`shared/spec-compliance.md`, vendored into `feature-development` and the new `spec-compliance-check` skill): the task list must be complete, each matching test's body is read and **run**, the command and result are recorded, nothing is Verified from reading the code, requirement prose is checked against its scenarios, and a dated report is written under `<reports_dir>/spec-compliance/`. Without OpenSpec the same procedure runs against the acceptance statements in the brief, so `spec.workflow = "none"` is no longer unchecked. `[spec] compliance_skill` lets a project substitute its own skill (its findings obey the same close rules). Decision: ship the standalone skill (generic, small) rather than leave the procedure only inside the close phase, so it can be run on demand and the report has one owner.
