# Replacing a project's own workflow skills with backlog-kit

For a repository that already has its own copies of these skills (the two projects backlog-kit was extracted from, or one like them). Nothing here edits your repository for you; `tools/migrate_check.py` only reads.

If you are starting a new project, you do not need this page: install the kit and talk to Claude ([INSTALL.md](INSTALL.md)).

## What is replaced, what stays yours

The kit replaces the skills with the same names: the planning family (`feature-plan`, `features-next`, `features-status`, `features-archive`, `bug-report`, `bugs-next`, `bugs-status`, `bugs-archive`), `decision-record`, `feature-development`, `bug-fix`, `gitflow`, and the extras you choose to install (`code-reviewer`, `security-reviewer`, `database-reviewer`, `architecture-reviewer`, `product-scope-roaster`, `docs-sync` — called `web-docs-sync` in one source project —, `spec-compliance-check`, `dependency-upgrade`, `features-batch-development`, `bugs-batch-fix`). Your stack skills, `openspec-*` skills and anything else in `.claude/skills/` stay.

What the replaced skills knew about your stack does not disappear. Test, build and E2E commands are found by the pipelines in your `CLAUDE.md` and build manifest. The optional extras read their checklists from sections of your own docs (see [docs/extras.md](docs/extras.md)).

## Steps

Run these from a clean working tree, on a branch.

1. **Look first:** `python3 /path/to/backlog-kit/tools/migrate_check.py <repo>` lists the project skills to delete, the files that still mention them, the `.backlog-kit.toml` you need (if any), whether OpenSpec is there, and whether `develop` already has the kit's skills.
2. **Optional project checks.** Put the checklists your extras should use into sections of your docs (see [docs/extras.md](docs/extras.md)), or start with none: the extras then work from `CLAUDE.md` and your docs.
3. **Settings, if you need any.** `.backlog-kit.toml` is optional: the backlog folder (default `docs/backlog`) and the viewport check devices. See `backlog-kit.example.toml`.
4. **Delete the project skills, then install the kit's.**
   ```
   git rm -r .claude/skills/<each skill from step 1>
   python3 /path/to/backlog-kit/tools/install.py <repo>             # the core
   python3 /path/to/backlog-kit/tools/install.py <repo> --extras    # plus the optional extras
   ```
   Use `--only a,b,c` to take a subset. If you keep a project skill of the same name (for example your own `architecture-reviewer`), leave it out of the install.
5. **Fix the references** the check listed: skills or docs citing a removed skill name, an index of skills (a `manifest.json`), README mentions. Reviewer section numbers (§N) now live in your project notes, if you kept them.
6. **Get the migration into `develop` before the first real run.** `feature-development` and `bug-fix` cut their branch from `develop`, so a migration that only exists on its own branch disappears on the new branch and the old skills come back. Merge it first, or cut the work branch from the migration branch and pass `--skip-branch-setup`.
7. **Verify.** From the repository root:
   ```
   python3 .claude/skills/features-status/scripts/status_report.py .
   python3 .claude/skills/bugs-status/scripts/status_report.py .
   python3 .claude/skills/features-next/scripts/rank_features.py .
   python3 .claude/skills/bugs-next/scripts/rank_bugs.py .
   ```
   They should print your real counts. Then ask Claude for the next feature, and run a small `bug-fix` end to end.

## What behaves differently

Where the two source projects disagreed, the kit follows one; none of it is a setting.

- There is no `commit` action in `gitflow`: you commit your own work; `finish` pushes and opens the PR with the confirmations the originals had.
- Tests, E2E, build, database and security reviews and the viewport check are optional phases inside the pipelines, not project files; a phase that does not apply is skipped with a stated reason.
- `Schema Change`, the P0–P3 / S/M/L / S1–S4 scales, branch names (`feature/`, `fix/`, base `develop`) and OpenSpec's location are fixed.
- `bugs-next` reads whether a fix needs a schema change from a `- **Schema change:** yes` line in the bug's details file.

The reasons for each choice are in the ledgers under `fidelity/` (maintainers; the originals are exported with `tools/fidelity.py --fetch`, see `fidelity/SOURCES.md`).

## Rolling back

`git revert` the migration commit: the deleted skills come back; `.backlog-kit.toml` goes away.
