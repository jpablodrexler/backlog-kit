# Changelog

Versions follow the plugin version in `.claude-plugin/plugin.json`. Design notes behind each change are in [DESIGN.md](DESIGN.md).

## 0.2.0
- **`gitflow` commit action:** one local commit on a topic branch, on request only, with the file list and message confirmed first. It never pushes, amends or skips hooks. The kit's promise stands: nothing is committed unless you ask.
- **`bug-fix --commit`** (and the same flag on `bugs-batch-fix`): a new Phase 7 asks `gitflow` for one commit per closed bug, holding the fix, its regression test and the backlog move.
- **`bug-fix` phase discipline:** every phase runs or is skipped under its stated condition with a recorded reason; Phase 1 must quote the failing output of the regression test (`RED:` line) or the run is treated as blocked; the Final Summary carries a status table for every phase.
- **`feature-development --commit`** (and the same flag on `features-batch-development`): Phase 7 asks `gitflow` for one commit per completed feature. The same phase discipline applies: every phase runs or is skipped with a recorded reason, the Final Summary carries a status table, and the batch skill must run `feature-development` for every feature and write its report even when working inline.
- **`bugs-batch-fix`:** must run `bug-fix` for every bug, with all its phases, and must write its report even when the work is done inline; a conflict with the user's wishes is settled with `--commit` or a question, never by dropping the skill.

## 0.1.1
- A project that lives in a subfolder of its repository (the backlog at `app/docs/backlog`) keeps its reference docs, `CLAUDE.md` and `README.md` next to that `docs` folder: the reviewers, `spec-compliance-check`, `dependency-upgrade`, `docs-sync` and the conventions say so, instead of assuming the repository root. The architecture reviewer no longer mentions a `reports_dir` setting that did not exist.

## 0.1.0
First public release.

- **Core skills (12):** the planning family (`feature-plan`, `features-next`, `features-status`, `features-archive`, `bug-report`, `bugs-next`, `bugs-status`, `bugs-archive`), `decision-record`, the work pipelines `feature-development` and `bug-fix`, and `gitflow`. The backlog is markdown under `docs/backlog/`; nothing is committed without you.
- **Extras (10, optional):** `code-reviewer`, `security-reviewer`, `database-reviewer`, `architecture-reviewer`, `product-scope-roaster`, `docs-sync`, `spec-compliance-check`, `dependency-upgrade`, `features-batch-development`, `bugs-batch-fix`. Each reads its project-specific checks from a named section of the project's own docs.
- **Conventions:** a fixed set of document locations and a `## Kit conventions` table in the project's `CLAUDE.md`; only `CLAUDE.md` is mandatory ([docs/conventions.md](docs/conventions.md)).
- **Configuration:** `.backlog-kit.toml` with `[paths] backlog_dir` and `[viewports]`, both optional.
- **Tools:** `tools/install.py` (copy install), `tools/vendor.py` (shared files into skills), `tools/migrate_check.py` (read-only check before replacing a project's own skills, see [MIGRATING.md](MIGRATING.md)).
