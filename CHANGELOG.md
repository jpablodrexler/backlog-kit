# Changelog

Versions follow the plugin version in `.claude-plugin/plugin.json`. Design notes behind each change are in [DESIGN.md](DESIGN.md).

## 0.2.36
- Replaces the 0.2.35 `Sources of truth:` line in every doc with a "Checked against" column in the `Kit conventions` table that `CLAUDE.md` must carry: one phrase per doc, with defaults in `shared/conventions.md`; `docs-sync` also searches the docs for the path, folder and names of each changed file. New `docs/conventions.md` explains the section and shows pablo-web's table as an example; the README links it.

## 0.2.35
- `docs-sync` no longer needs a per-project table mapping doc sections to code: every reference doc declares what it is checked against in a `Sources of truth:` line under its title (or under a section heading), a convention described in `shared/conventions.md`. `CLAUDE.md` and `README.md` have fixed sources. A doc without the line gets one inferred and added. `.backlog-kit/docs/` is now only for optional extra notes, and a missing folder is not reported.

## 0.2.34
- `docs-sync`: the guardrails that every project repeated in its notes are now fixed text in the skill: what a fixed-pointer subsection of `CLAUDE.md` is and when to touch it, and the scope (`CLAUDE.md`, `README.md` and the reference docs of the kit conventions; never the backlog, decisions, explorations or reports). A project's notes keep only what is specific to it. The pablo-web example of that note was removed.

## 0.2.33
- The standard locations now have one source in the kit, `shared/conventions.md`, vendored only into `docs-sync` (the other skills keep their own defaults, and a new test checks that every `docs/` path any skill mentions is in the table). A project carries the table as a `## Kit conventions` section of its `CLAUDE.md`; `docs-sync`'s full sweep checks it and offers to add it. `docs-sync`'s tiers section points to the table instead of embedding it.

## 0.2.32
- Standard locations are now a convention of the kit: `docs-sync` carries a table of where each kind of reference doc lives (`docs/architecture.md`, `features.md`, `frontend.md`, `backend.md`, `database.md`, `authentication.md`, `decisions/`, `backlog/`, `reports/`), moved from the per-project tiers note, and the README gains a "Where things live" table. A project keeps only the files it needs and its notes can say where it differs.

## 0.2.31
- `docs-sync`: the three documentation tiers (lean `CLAUDE.md`, reference `docs/*.md`, `README.md` index) are now a fixed section of the skill instead of a project note, so a project no longer needs a `.backlog-kit/docs/` file to describe them. The notes keep only what is specific to the project: the section-to-source table and its scope. The example tiers files were removed.

## 0.2.30
- Viewport check, from the first real `bug-fix` run in pablo-web (BUG-101): only the smallest phone and the desktop were asserted although six phones were configured. `feature-development` and `bug-fix` now require checking each configured viewport in turn and listing each in the hand-back as verified or skipped with a reason; the Final Summary shows the status per viewport (`bug-fix` gains a Viewport check line).

## 0.2.29
- Community files and docs for publishing: `CONTRIBUTING.md` and `SECURITY.md` added; `DESIGN.md` rewritten as the current design (the per-release log lives in this changelog); `MIGRATING.md` rewritten for the core-plus-extras design with no phase files; `tools/migrate_check.py` now lists the optional project-note folders (including architecture and product), treats OpenSpec as optional and checks that `develop` contains the kit's skills.

## 0.2.28
- The snapshots of the source projects' skills (`fidelity/base/`) are no longer stored in the repository: `tools/fidelity.py --fetch NAME=REPO@REF` exports them from the projects' own repositories at the commits pinned in `fidelity/SOURCES.md`, into a gitignored folder. Without them the fidelity check says so and its tests are skipped. Decision D9 updated.

## 0.2.27
- `architecture-reviewer`, fourth real run, wording only: `Maps to:` accepts a list or free text and a note without one is assigned by the reviewer; P-numbers belong to the skill; a note's `Read when` may list several conditions; `[docs]` tag for documentation findings; documented deliberate exceptions and documented idempotent writes are strengths, undocumented ones are not; Coverage markers are `[x]`/`[~]`/`[ ]`, a rule is one bullet or one technique, and Not verified names the dimension and what was skipped.

## 0.2.26
- `architecture-reviewer`, third real run: notes declare `Maps to:` between their dimensions and the skill's; a note rule without its own dimension applies under the one it names; healthy and documented-unused channels go under Strengths; finding IDs run continuously across severities; searches are cited inline; and the report gains a `### Coverage` checklist (per dimension and per note rule: covered, partial or not covered, with files opened and searches run) so runs can be compared on what each looked at. Non-atomic writes of any kind (create, update, delete, retried by a wrapper) are one class in pablo-web's notes.

## 0.2.25
- `architecture-reviewer`, second real run: overlapping dimensions are tagged `[D4/P5]` with the mapping in the header, the branch is read from `.git/HEAD`, healthy channels need one line of counts. pablo-web's notes lose the duplicated text and gain a note on non-atomic writes that cites its ADR.

## 0.2.24
- `architecture-reviewer`, from the first real run in pablo-web: dimensions of project notes are numbered P1… next to the skill's D1–D8 and findings are tagged and get stable IDs (F1…); documented exceptions are listed under Strengths with their documentation; the hunt-the-broadcast technique is explicitly exempt from the survey-depth limit. pablo-web's notes corrected (flat structure, whole-app `localStorage` grep, BUG-077 marked as fixed).

## 0.2.23
- `architecture-reviewer` and `product-scope-roaster` converted from the two projects' skills: the frame (steps, classification, report names, follow-up, guardrails) follows the originals; the stack-specific dimensions, named files and real cases moved to optional project notes (`.backlog-kit/review/architecture/`, `.backlog-kit/review/product/`), with both projects' notes in `examples/`. The obsolete phase-file examples were removed from `examples/`.

## 0.2.22
- The viewport check of `feature-development` and `bug-fix` reads an optional `[viewports]` table of `.backlog-kit.toml` (`phones`, `desktop`); default Galaxy S23 Ultra 384x824 and 1920x1080. The example file lists five popular phones to add. `docs/extras.md` documents how the extras use optional project notes under `.backlog-kit/` and fall back to `CLAUDE.md` and the docs when there are none. README: loop diagram restored.

## 0.2.21
- Simplification. The kit is now a small core (12 skills) plus optional extras (`extras/`, installed with `tools/install.py --extras`/`--all`). The project phase files (`.backlog-kit/feature|bug|release/`) are gone: `feature-development` and `bug-fix` carry the original phases themselves, restored as close to the source skills as possible and marked optional (Tests, E2E, Build; database/security/viewport reviews only when the change touches them). `gitflow` carries the original release steps (version bump when a manifest has one, regression suite) as optional steps. OpenSpec is optional: without an `openspec/` folder the feature brief is the spec. `shared/project-phases.md` is removed; the hand-back paragraph is inlined in both skills. The README opens with a one-page quick start.

## 0.2.20
- Every skill names its author again (`metadata.author`), as the source projects' skills do; the conversion had dropped it. The stack-leakage lint ignores that one line. The kit has no agent definitions, so there is nothing to change there.

## 0.2.19
- Hand-back contract for subagents (found in the first real run: a Phase 1 subagent sent only placeholder text and no signal, and the run stalled). The pipelines and `gitflow` now tell the orchestrator to append one paragraph, defined once in `shared/project-phases.md`, to every subagent prompt: the hand-back is the final text of the response, ending with the signal line, never a separate message and never placeholder text. The `Missing signal fallback` of `feature-development` and `bug-fix` gains one rule: before re-running a phase whose signal is missing, look at the working tree for what the subagent did and tell the user, who decides whether to accept that evidence or re-run. These lines are additions to the originals.

## 0.2.18
- Found in the first real run in pablo-web: `feature-development` and `bug-fix` cut their branch from `develop`, so a migration that only lives on its own branch disappears from disk when Phase 1 switches branch (the old skills return and `.backlog-kit/` is gone). `MIGRATING.md` now says to merge the migration into `develop` first, or to cut the work branch from the migration and pass `--skip-branch-setup`; `tools/migrate_check.py` warns when `develop` does not contain `.backlog-kit/`.

## 0.2.17
- `MIGRATING.md`: how to replace a project's workflow skills with the kit (what to delete, which project files to copy from `examples/`, the one config line jp-photo-manager needs, which references to fix, what behaves differently per project, how to verify and roll back). `tools/migrate_check.py <repo>` is the read-only companion: it lists the project skills the kit replaces, the other files that still mention them, the backlog location, and which `.backlog-kit/` folders are still empty.

## 0.2.16
- `spec-compliance-check`, `docs-sync` and `dependency-upgrade` rebuilt from the projects' own skills (the first project's text; the second's variants are in the ledgers). Each keeps the generic frame and names no stack; the project's own knowledge is read from markdown files, found by their `Read when:` line, in `.backlog-kit/spec-compliance/`, `.backlog-kit/docs/` and `.backlog-kit/dependency-upgrade/` (D32). `examples/` has both projects' files, moved from their originals without changes.
- Configuration is down to `[paths] backlog_dir`. Removed `[[gates]]`, `[[reviews]]`, `[work]`, `[guidance]`, `[docs]` / `[[docs.map]]` and `[spec]` (OpenSpec lives at `openspec/changes`, fixed as in the originals), together with `work_scope.py`, `task_state.py`, `shared/spec-compliance.md`, the helper scripts of `spec-compliance-check`, `examples/angular-supabase.toml` and the tests that guarded them.
- `docs-sync` is the kit name of the projects' `web-docs-sync`; the old `[[docs.map]]` is replaced by a project file.

## 0.2.15
- `code-reviewer`, `security-reviewer` and `database-reviewer` rebuilt from the projects' own skills (the first project's text is the base; the second's variants are in the ledgers). The kit carries the frame — workflow, scoped review, severity legend, dated report, fix workflow, full-codebase sweep process — with no stack named (D30).
- The stack-specific checklists, pitfalls tables, metrics sections and the sweep layer tables are the project's: files in `.backlog-kit/review/<code|security|database>/`, each starting with `# Title` and a `Read when:` line; the reviewer loads only what the change touches, and says so in the report when there is no project checklist (D31). `examples/` holds both projects' files, moved from their originals without changes (the `Read when` lines were written for the database and security files, which had no index).
- Removed: the kit's non-interactive mode and input contract (`changed_files`, `deleted_files`, `bulk_files`, `self_review`), the `[[reviews]]` wiring and the tests that guarded them. The pipeline phases pass the changed files as the scope, which the originals already supported.

## 0.2.14
- `gitflow` rebuilt from the projects' own skill (the first project's text; the second's variants are in `fidelity/ledgers/gitflow.md`): topic branches `feature/`, `fix/`, `doc/`, `skill/`, `chore/` plus `release/` and `hotfix/` are fixed (D27); `start`, `sync`, `finish`, release/hotfix with changelog, two PRs and tag, and `cleanup` are the originals' text, with their own confirmations (first push, tag, delete) (D29).
- New: project release phases. The project-specific part of `finish release/hotfix` (version bump, regression suite) lives in `.backlog-kit/release/NN-*.md` and runs through the same mechanism as the feature and bug phases (D28); `examples/` has both projects'. A phase file may now consist of an `## Orchestrator` section only.
- Removed: the kit's `commit` action and the yes before every write (D29), `flow_plan.py`, `branch_state.py`, `tests/test_flow.py`, and the `[git]` and `[bugs]` configuration sections (branches are fixed; the bug id prefix is `BUG`). `list_merge_candidates.py` is the original script, reading git through the allowlisted `gitread`.

## 0.2.13
- Fidelity method applied to the pipelines: `feature-development`, `bug-fix`, `features-batch-development` and `bugs-batch-fix` are now the projects' own skills (the first project's text; the second project's variants are in the ledgers), not a rewrite. The generic phases (select, propose, implement with the code review, archive/close) are verbatim; everything project-specific is out of the kit.
- New: project phase files. Tests, E2E, build and conditional reviews (database, security, viewport) live in the project as `.backlog-kit/feature/NN-*.md` and `.backlog-kit/bug/NN-*.md`, run in filename order, one subagent each, with an optional `## Orchestrator` section for decisions that need the user (see `shared/project-phases.md`). `examples/pablo-web/` and `examples/jp-photo-manager/` hold the two source projects' phases converted to this format.
- Removed the kit-only machinery the originals do not have: `[[gates]]`-driven gate phase, `[[reviews]]` review phase, `detect_gates.py`, `dep_scan.py` in `feature-development`, `batch_plan.py`, `batch_report.py`, the batch runner and pipeline guardrails shared files, the `REVIEWS:`/`GATES:`/`CLOSE_NEEDS_REGATE` hand-backs and their tests. The batch skills are plain skills again. Branches are fixed as in the originals (`feature/`, `fix/`, base `develop`, through `gitflow`'s start and sync).
- `tools/fidelity.py` gains `FILE | project/skill/path | reason` ledger lines for a whole original file that moved out of the kit.
- Still to convert (their `[[gates]]`, `[[reviews]]`, `[docs] sync_skill` and `[spec] compliance_skill` settings are kept until then): `gitflow`, the three reviewers, `spec-compliance-check`, `docs-sync`, `dependency-upgrade`.

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
