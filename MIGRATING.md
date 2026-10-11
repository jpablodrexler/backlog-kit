# Replacing a project's workflow skills with backlog-kit

> **Note (0.2.21):** the project phase files described below no longer exist; `feature-development`, `bug-fix` and `gitflow` carry their optional phases themselves. Treat the `.backlog-kit/feature|bug|release/` steps here as historical.

This is for a repository that already has its own copies of the workflow skills (the two projects backlog-kit was extracted from, or one like them) and wants to delete them and use the kit instead. Nothing in the kit edits your repository for you; `tools/migrate_check.py` only reads.

## What is replaced, what stays yours

The kit replaces these project skills (same names; `web-docs-sync` is called `docs-sync` in the kit):

`feature-plan`, `features-next`, `features-status`, `features-archive`, `bug-report`, `bugs-next`, `bugs-status`, `bugs-archive`, `decision-record`, `feature-development`, `bug-fix`, `features-batch-development`, `bugs-batch-fix`, `gitflow`, `code-reviewer`, `security-reviewer`, `database-reviewer`, `spec-compliance-check`, `web-docs-sync`, `dependency-upgrade`.

Everything else in `.claude/skills/` stays: the stack skills (`angular-developer`, `java-developer`, the test-developer skills, `e2e-testing`, `e2e-suite`, …), the `openspec-*` skills, `incident-response`, `feature-gantt`, `feature-screenshot`, `quality-metrics`, `architecture-reviewer`, `architecture-sync`, `product-scope-roaster`, `skills-docs-sync`. The kit's own `architecture-reviewer` and `product-scope-roaster` are older rewrites that have not been rebuilt from your originals: **do not install them**, keep yours (the commands below install only the converted skills).

What the replaced skills knew about your stack does not disappear: it moves into markdown files in your repo under `.backlog-kit/` (the two source projects' files are in `examples/`, moved from their skills without changes of text).

## Steps

Run these from a clean working tree, on a branch.

1. **Look first.**
   ```
   python3 /path/to/backlog-kit/tools/migrate_check.py <repo>
   ```
   Section 1 lists the project skills to delete, section 2 the other files that mention them, section 3 the `.backlog-kit.toml` you need (if any), section 4 which `.backlog-kit/` folders are still empty.

2. **Copy your project files.** From `examples/<project>/.backlog-kit/` into the repository root (for another project, start from the nearest example and edit):
   ```
   cp -r /path/to/backlog-kit/examples/pablo-web/.backlog-kit <repo>/
   ```
   Folders: `feature/` and `bug/` (the phases after implementing: reviews that depend on what changed, tests, E2E, build), `release/` (before a release is pushed), `review/{code,security,database}/` (the reviewers' checklists), `spec-compliance/`, `docs/`, `dependency-upgrade/`. Each file starts with `# Title`; files read by the skills also have a `Read when:` line. Read the `Read when:` lines of the database and security files: the originals had no index and they were written during the conversion.

3. **Point the kit at your backlog, if it is not `docs/backlog`.** The only setting is the backlog folder; the decisions, explorations and reports folders sit next to its parent.
   ```toml
   # <repo>/.backlog-kit.toml — jp-photo-manager
   [paths]
   backlog_dir = "JPPhotoManagerWeb/docs/backlog"
   ```
   pablo-web needs no file.

4. **Delete the project skills** (the list from step 1), then **install the kit's**:
   ```
   git rm -r .claude/skills/{feature-plan,features-next,features-status,features-archive,bug-report,bugs-next,bugs-status,bugs-archive,decision-record,feature-development,bug-fix,features-batch-development,bugs-batch-fix,gitflow,code-reviewer,security-reviewer,database-reviewer,spec-compliance-check,web-docs-sync,dependency-upgrade}
   python3 /path/to/backlog-kit/tools/install.py <repo> --only feature-plan,features-next,features-status,features-archive,bug-report,bugs-next,bugs-status,bugs-archive,decision-record,feature-development,bug-fix,features-batch-development,bugs-batch-fix,gitflow,code-reviewer,security-reviewer,database-reviewer,spec-compliance-check,docs-sync,dependency-upgrade
   ```
   Copying the skills (this step) keeps the skill names exactly as the skills call each other (`feature-development` invokes `features-next`, `gitflow`, `docs-sync` by plain name). The plugin install namespaces them (`backlog-kit:bug-fix`); that path has not been tried for a full run, so for a migration prefer the copy.

5. **Fix the references** the check listed in section 2. The usual cases:
   - `code-reviewer §N`, `database-reviewer §N`, `security-reviewer §N` cited from other skills or docs: the sections still carry their numbers, now inside `.backlog-kit/review/<kind>/*.md`. Citing them there is enough.
   - `web-docs-sync` → `docs-sync`; a path such as `.claude/skills/decision-record/SKILL.md` → the skill's new location, or just the skill name.
   - A manifest or index of skills (pablo-web's `skills-docs-sync/manifest.json`) lists the removed skills: update it.
   - README/CHANGELOG mentions are history; leave them or reword.

6. **Get the migration into `develop` before the first real run.** `feature-development` and `bug-fix` cut their branch from `develop` (through `gitflow`). If the migration only exists on its own branch, the new branch will not have it: the kit's skills and your `.backlog-kit/` files disappear from disk and the old skills come back, so the run no longer tests the kit. Either merge the migration into `develop` first, or, to try it before merging, cut the work branch yourself from the migration branch and pass `--skip-branch-setup` (`bug-fix BUG-097 --skip-branch-setup`). `migrate_check.py` section 6 warns about this.
7. **Verify** (see below), commit, and merge as you would any change.

## What behaves differently

Where the two source projects disagreed, the kit follows one; none of it is a setting. The reasons are in `fidelity/decisions.md`.

- **Everyone.** There is no `commit` action in `gitflow` (you commit your own work; `finish` pushes and opens the PR with the confirmations the originals had). Reviews, tests, builds and E2E are your phase files, run in filename order; with none present the pipeline says so and continues. `Schema Change`, the P0–P3 / S/M/L / S1–S4 scales, branch names (`feature/`, `fix/`, base `develop`) and OpenSpec's `openspec/changes` are fixed. A batch run asks you about each item.
- **Bugs.** `bugs-next` reads whether a fix needs a schema change from an explicit `- **Schema change:** yes` line in the bug's details file; without it the bug counts as not needing one. Add the line to open bugs that need schema work. Any Environment other than `local` earns the ranking bonus.
- **pablo-web.** `features-status` is stricter (stale dependency notes also in prose, any referenced feature that is implemented); `features-archive` writes `(prerequisite already implemented)`; `bugs-next` as above.
- **jp-photo-manager.** New planned tables use the column order `… Area | SDD Artifacts | Implementation | Summary | Brief`, and an archived row drops its `SDD Artifacts` cell (scripts read columns by name, so existing tables keep working); `features-archive` writes `(prerequisite already implemented)` instead of `(resolved)`.
- **Reports.** The reviewers write to `<reports>/…` next to the backlog's parent, which is where both projects already had them.

## Verify

From the repository root, with the kit's skills installed:
```
python3 .claude/skills/features-status/scripts/status_report.py .
python3 .claude/skills/bugs-status/scripts/status_report.py .
python3 .claude/skills/features-next/scripts/rank_features.py .
python3 .claude/skills/bugs-next/scripts/rank_bugs.py .
```
These should print your real counts and recommendations; the kit's versions were compared with the source projects' own scripts on both real backlogs. Then in Claude Code:

1. "What feature should I work on next?" — `features-next` recommends and asks.
2. Run `feature-development` on a small feature through to the end: the Final Summary prints one line per file in `.backlog-kit/feature/`, so you see that each phase was picked up and what it reported.
3. Ask for a review of a small change: the reviewer works through the checklist files whose `Read when:` matches, and its report says so when it found no project checklist.

## Rolling back

`git revert` the migration commit. The deleted skills come back with it; `.backlog-kit/` and `.backlog-kit.toml` go away.

## Not verified live

The converted skills and the phase files have been tested for structure and against both backlogs, not yet run end to end in a real feature or bug run of either project. Run the first one on a small, low-risk item and read each phase's hand-back.
