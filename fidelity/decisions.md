# Fidelity decisions

Every point where the kit's skills differ from the source projects' skills because something became
configurable, was removed, or was changed on purpose is recorded here with the owner's answer.
`fidelity/ledgers/<skill>.md` links each edited paragraph to one of these ids.

| Id | Question | Answer | Date |
| --- | --- | --- | --- |
| D1 | `Schema Change` (Yes/No) column in the planned and implemented tables: fixed or optional? | **Fixed**, as in both source projects. No config key. | 2026-10-10 |
| D2 | `features-next` tier 4: the original +5 for "no schema change", or the kit's own +5 for smallest effort? | **Original.** The effort bonus is removed. | 2026-10-10 |
| D3 | How `bugs-next` knows a bug's fix needs a schema change (the projects use different regexes over the details file) | **An explicit line** `- **Schema change:** yes\|no` in the bug's details file; no regex. `bug-report` writes it (done when `bug-report` is converted). | 2026-10-10 |
| D4 | Priority (P0–P3), Effort (S/M/L) and Severity (S1–S4) vocabularies: configurable or fixed? | **Fixed**, as in both projects. The config keys `priorities`, `priority_labels`, `efforts`, `severities`, `severity_labels` go away once every planning skill that reads them is converted. | 2026-10-10 |
| D5 | Area vocabulary (differs between the projects) | **The legend of the backlog file defines it.** No config key. | 2026-10-10 |
| D6 | Environment vocabulary (`prod` vs `deployed`) and the +20 bonus | **Any Environment other than `local`** earns the bonus. No config keys. | 2026-10-10 |
| D7 | A hard dependency whose prerequisite has no row in the planned table | **As the originals:** counts as shipped; the script also checks features-implemented.md and **warns** when the number is in neither file. | 2026-10-10 |
| D8 | `--confirmed` batch mode (skips the per-item question) | **Removed.** Every item is confirmed by the user, also inside a batch, as in the source projects. | 2026-10-10 |
| D9 | Where the snapshots of the originals live | **In the kit while it is private**; revisit before publishing (the text of the projects' skills must not be published without the owner's say). | 2026-10-10 |
| D10 | Explore command named in `features-next` (`/opsx:explore` in one project, `/openspec-explore` in the other) | Both are named; the skill says "whichever your OpenSpec install generated". Wording only, no config key. | 2026-10-10 |
| D11 | OpenSpec optional (`[spec] workflow`) or mandatory? | **Mandatory**, as in both projects. The kit depends on OpenSpec (never bundles it). The `[spec] workflow` key and every "without OpenSpec" branch go away as each skill is converted. | 2026-10-10 |
| D12 | Column order of a freshly scaffolded planned table | **The order of the first project**: `... Area \| SDD Artifacts \| Implementation \| Summary \| Brief`. Scripts read columns by name, so existing backlogs of either order keep working. | 2026-10-10 |
| D13 | "Deployment (migration) dependencies" table | **A fixed part of the backlog files**, as in the originals: skeletons create it, `features-archive` moves rows, `feature-plan` never adds rows at planning time. No `[[features.tables]]`. | 2026-10-10 |
| D14 | `feature-plan` step 9 (insert the new feature into the Recommended implementation order) | **Included** (from the first project); `features-next` then gives the order bonus. | 2026-10-10 |
| D15 | Kit-only helper scripts (`dep_scan.py`, `spec_link.py`, `clean_order_notes.py`, `scaffold.py`): keep any? | **None kept** (no selection given, so the recommendation applies): the originals do these things with prose, and the skeletons are inline in `feature-plan`. Each goes away as the skill that used it is converted; `scaffold.py` and `dep_scan.py` from `feature-plan` are gone. Reversible from git history. | 2026-10-10 |
| D16 | `features-status`: the two projects' checks differ (stale-note detection: the first requires both ends of a dependency to be implemented and only reads the heading form; the second flags any referenced feature that is implemented and also reads the prose forms) | **The second project's** (newer and stricter); not a configuration choice. | 2026-10-10 |
| D17 | Annotation `features-archive` writes when a dependency's prerequisite has shipped (`(resolved)` in one project, `(prerequisite already implemented)` in the other) | **`(prerequisite already implemented)`**. No config key. | 2026-10-10 |
| D18 | Bug id prefix (`[bugs] id_prefix`) | **Fixed `BUG`**, as in both projects. The key goes away as the batch runners are converted. | 2026-10-10 |
| D19 | Auxiliary folders (`decisions_dir`, `explorations_dir`, `reports_dir`) | **One setting, `backlog_dir`**; the others sit next to it: `<docs>/decisions`, `<docs>/explorations`, `<docs>/reports`, where `<docs>` is the folder that contains the backlog folder. | 2026-10-10 |
| D20 | Pipelines (`feature-development`, `bug-fix`): how are the project-specific phases (tests, E2E, build/deploy) expressed? | **Project-owned phase files.** The kit keeps the generic phases (select, propose, implement, archive) verbatim from the originals; the project's own phases live as files in its repo and the pipeline runs them. | 2026-10-10 |
| D21 | Where those phase files live | **Folder convention, no config key:** `.backlog-kit/feature/NN-name.md` and `.backlog-kit/bug/NN-name.md`, run in filename order. | 2026-10-10 |
| D22 | Where the review/fix loops live | **Inside the project's phase files** (no `[[reviews]]` config, no `phase-reviews.md`). | 2026-10-10 |
| D23 | Branches in the pipelines (`feature/<name>`, `fix/<slug>`, base `develop`, via `gitflow`) | **Fixed, as in the originals.** `[git] base_branch/feature_prefix/fix_prefix/finish_skill` go away from these skills; `gitflow` is converted separately. | 2026-10-10 |
| D24 | Code review vs conditional reviews | **Code review (with its 3-round loop and `CHANGED_FILES`) stays in the kit's Phase 2**, verbatim; database/security/viewport reviews live in the project's phase files. | 2026-10-10 |
| D25 | Phase-file format | **`## Orchestrator` (optional, main context) + `## Subagent` (prompt, placeholders substituted) ending in `PHASE: PASS\|SKIPPED\|BLOCKED — reason` and optional `SUMMARY: …`.** Final summary prints one line per phase file. | 2026-10-10 |
| D26 | Regression-test layer (bug-fix Phase 1) and no phase files | **Generic text** (pick the layer where the bug lives, following the project's test conventions); with no phase files the pipeline warns and continues. | 2026-10-10 |
| D27 | Topic branch types (`feature/`, `fix/`, `doc/`, `skill/`, `chore/`, plus `release/`, `hotfix/`) | **Fixed, as in the originals** — no `[git.topics]`. | 2026-10-10 |
| D28 | The project-specific part of `finish release/hotfix` (version bump, e2e/regression gate) | **Project phase files** `.backlog-kit/release/NN-*.md`, same mechanism as feature/bug (D20–D25); a file may have only an `## Orchestrator` section. The kit keeps CHANGELOG, push, the two PRs and the tag. | 2026-10-10 |
| D29 | `gitflow` `commit` action and a yes before every write | **Dropped, faithful to the originals**: no `commit` action (the work skills leave changes uncommitted and the user commits); `finish` pushes and opens the PR with the originals' own confirmations (first push, tag, delete, changelog/version commits). | 2026-10-10 |
| D30 | The three reviewers (`code-reviewer`, `security-reviewer`, `database-reviewer`): what the kit carries | **The frame, from the originals, naming no stack** (workflow, severities, scoped review, dated report, fix workflow, sweep process); the stack-specific checklists, pitfalls, metrics sections and the sweep layer table live in the project as `.backlog-kit/review/<code\|security\|database>/*.md`. | 2026-10-10 |
| D31 | How a reviewer finds the project files | Each file starts with `# Title` and a `Read when: <when>` line (`every review` = always); the reviewer lists the folder, reads those lines and loads only what the change touches. No folder: review with the frame plus CLAUDE.md/docs and say there is no project checklist. No config key. | 2026-10-10 |

Not asked (not configurable, taken from the more complete original): order lists accept numbered and
link forms (J's `bugs-next`); `features-next` reads `SDD Artifacts` from the cell only (no disk check).
