# Changelog

Versions follow the plugin version in `.claude-plugin/plugin.json`. Design notes behind each change are in [DESIGN.md](DESIGN.md).

## 0.2.12
- Fidelity pilot complete for the planning family: `feature-plan`, `features-status`, `features-archive`, `bug-report`, `bugs-status`, `bugs-archive` and `decision-record` are now rebuilt from the source projects' skills and scripts (60–84% of the original paragraphs verbatim; every other difference recorded in `fidelity/ledgers/` and tied to a decision in `fidelity/decisions.md`, D1–D19).
- Simpler configuration: `[paths]` has the single `backlog_dir` (the decisions, explorations and reports folders sit next to it); the priority, effort, severity, area and environment vocabularies and the `Schema Change` column are fixed or defined by the backlog's own legend; `(prerequisite already implemented)` is the one resolved annotation; the bug id prefix is `BUG`.
- Removed the kit-only helpers the originals do not have: `scaffold.py` (skeletons are inline in `feature-plan` and `bug-report`), `dep_scan.py` from `feature-plan` and `features-status`, `spec_link.py`, `clean_order_notes.py`, and the library code behind them (header migration, spec-link depth, order-note cleanup).
- `features-status` and `bugs-status` follow the second project's checks (prose stale-note forms, every resolved bug needs a Resolution line); the environment split is counted from the data.

## 0.2.11
- Fidelity pilot, first step. `features-next` and `bugs-next` are rebuilt from the source projects' own skills and scripts instead of being rewritten: 84% and 77% of the original paragraphs are verbatim, and every other difference is recorded in `fidelity/ledgers/` with the owner's decision (`fidelity/decisions.md`). `tools/fidelity.py --check` (also part of the test suite) fails when a difference is unrecorded; `rank_features.py` and `rank_bugs.py` are the originals plus a few edited lines and give identical results on both projects' real backlogs.
- Behaviour restored to what the projects do: `Schema Change` column and the +5 "no schema change" tier (the kit's own effort bonus is gone); fixed P0–P3 / S1–S4 scales; the +20 environment bonus for anything other than `local`; a prerequisite with no row counts as shipped, with a warning when it is in neither file; every item is confirmed by the user also in a batch (`--confirmed` removed).
- `bugs-next` reads an explicit `- **Schema change:** yes` line from the bug's details file instead of a regex.

## 0.2.10
- `dependency-upgrade` reworked: snapshots live in the git directory (never in `git status`) and also cover every file the skill edits; a group whose tool rewrites source is declared beforehand and, if it fails, is reported with the files it changed instead of being half-restored; the vulnerability check runs before and after and says "not checked" when it could not run; the command table is corrected (Maven, uv, cargo, dotnet, npm caret, yarn flavour, workspaces); a BOM or parent is bumped first; `ask_before` gates, the unused-dependency caveat and the base-branch warning are back.
- `docs-sync` reads staged work and skips backlog bookkeeping, re-derives cumulative facts from the whole glob, and requires map docs to be in-repo Markdown; `product-scope-roaster` no longer contradicts itself on cited documents; `architecture-reviewer` writes to `architecture-review/` and its data-access and state dimensions regain the transaction, caching, N+1, migration-discipline, API-consistency and client-storage checks.

## 0.2.9
- Work pipelines: a task that needs a person (a generated secret, a deploy) is marked `(manual: <command>)`, reported to the user and no longer makes `TASKS_INCOMPLETE` / `CLOSE_BLOCKED` certain; `IMPLEMENT: DONE` is checked against the task list (new `task_state.py`) by the subagent and again by the orchestrator.
- The close phase no longer re-runs gates inside a subagent (which ignored `ask_before`): it hands back `CLOSE_NEEDS_REGATE` and the orchestrator re-gates and re-reviews. The archive prompts of OpenSpec are no longer answered by the subagent (`ARCHIVE_NEEDS_DECISION`). Close hands back `COMPLIANCE:` and `DOCS:` lines for the summary.
- Spec compliance gains a guarded `Manual` class; spec markdown (`openspec/changes`, `openspec/specs`) no longer counts as changed code; a `PROD_CODE_FIXED` re-review uses the configured review skill; a blocker has a defined re-entry protocol; `bug-fix` hands back the exact command of its regression test.

## 0.2.8
- The review phase and the three reviewer skills now share one input contract: each review gets only its own matching files (the list is no longer cut at 20), plus `deleted_files`, `bulk_files`, `id` (default `adhoc`), `focus` and `self_review`. A file list alone selects the non-interactive mode, and a skill-run review is always marked self-reviewed.
- Reviewers judge the change (`git diff HEAD -- <file>`), not pre-existing lines; findings may omit `:<line>` (missing test, lockfile not updated); a deleted or edited applied migration is still reviewed and still 🔴.

## 0.2.7
- Safety and correctness fixes from the second comparison round: globs no longer strip the leading dot of a name (`.github/**` matched nothing); `--fix-header` keeps escaped pipes in cells; `gitflow commit` commits explicit paths only and reports what is already staged; `gitflow cleanup` also checks the `origin/<branch>` tip, warns on shallow clones and rejects invalid branch names; non-ASCII paths are reported as they are; the `gitread` allowlist can no longer create a ref (`git branch <name>`) or write a file (`diff --output`).
- `batch_plan --all` now ranks exactly like `features-next` / `bugs-next` (shared scoring in `lib/backlog_kit.py`), with prerequisites before dependents.
- `bug-fix`: `ARCHIVE_BLOCKED` (tooling) and `CLOSE_BLOCKED` (the work) no longer share a signal.

## 0.2.6
- Seven skills generalized from the source projects: `code-reviewer`, `security-reviewer`, `database-reviewer` (non-interactive review mode for `[[reviews]]`), `architecture-reviewer`, `product-scope-roaster`, `dependency-upgrade` and `docs-sync` (optional `[[docs.map]]`).

## 0.2.5
- CI workflow (tests on Linux, non-blocking Windows and macOS, vendor drift check, manifest and changelog consistency); README rewritten with the full loop, configuration table and an honest limitations section; this changelog.

## 0.2.4
- Hand-backs are defined and consumed: `REVIEWS:` (with an honest self-reviewed marker), `DEPS_DISMISSED`, the `PLAN: READY` / `BUG_ID` echoes, `ORIGINAL SCENARIO`, the base-ahead note.
- The orchestrator re-runs the regression test itself; `bug-fix` checks the reported scenario and falls back to the row summary when the details file is missing.
- `PROD_CODE_FIXED` has a re-review procedure; reviews get the verbatim changed-files list; subagents never end a turn on a backgrounded command; `ARCHIVE_BLOCKED` vs `CLOSE_BLOCKED` reconciled.
- `features-next` blocks on an unknown prerequisite; numbered order lists are read; `features-archive` finishes leftover rows and restores the empty hard-dependencies placeholder.
- A resume whose list differs now asks; batch plans report a missing brief; `features-status` describes all its checks.

## 0.2.3
- `gitflow start` asks before leaving a topic branch; merge requests redirect to `sync`; the `#N` rule covers copied commit messages.

## 0.2.2
- Spec-compliance rigor restored in one shared procedure (tests actually run, evidence recorded, dated report, prose-conflict check); new `spec-compliance-check` skill; `[spec] compliance_skill`.

## 0.2.1
- Fixes from comparing with the source projects: spec-artifact readiness from disk, safer `gitflow cleanup`, new files in the commit plan, `gate_max_rounds`, computed `[spec]` links, prose stale-dependency notes, `decision-record` confirms before writing, idempotent `bugs-archive`, stricter `bugs-status`, OpenSpec skills preflight.

## 0.2.0
- New `gitflow` skill: `start`, `sync`, `commit`, `finish` (push + PR) and `cleanup`, each write confirmed first. The public promise becomes "nothing is committed, pushed or opened as a PR unless you ask for it".

## 0.1.7
- `[git] finish_skill` names the project's own finish skill in hand-off messages.

## 0.1.6
- `dep_scan.py`: mechanical detection of unrecorded hard dependencies, wired into `feature-plan`, `feature-development` and `features-status`.

## 0.1.5
- The OpenSpec close phase checks requirement prose, not only scenarios.

## 0.1.4
- Table-header / `spec.workflow` mismatch repair (`--fix-header`); missing-OpenSpec and missing-spec-link checks; empty order-list placeholder restored.

## 0.1.3
- `features-archive` clears stale "blocked on #N" notes from the order list.

## 0.1.2
- `--all` ranks like `features-next` / `bugs-next`; the order list only breaks ties.

## 0.1.1
- UTF-8 output on Windows consoles; stricter phase hand-backs.

## 0.1.0
- First release: the 13 core skills, batch runners, config file, vendored helper scripts.
