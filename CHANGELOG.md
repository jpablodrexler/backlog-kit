# Changelog

Versions follow the plugin version in `.claude-plugin/plugin.json`. Design notes behind each change are in [DESIGN.md](DESIGN.md).

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
