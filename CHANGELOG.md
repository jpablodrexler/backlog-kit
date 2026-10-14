# Changelog

Versions follow the plugin version in `.claude-plugin/plugin.json`. Design notes behind each change are in [DESIGN.md](DESIGN.md).

## 0.1.1
- A project that lives in a subfolder of its repository (the backlog at `app/docs/backlog`) keeps its reference docs, `CLAUDE.md` and `README.md` next to that `docs` folder: the reviewers, `spec-compliance-check`, `dependency-upgrade`, `docs-sync` and the conventions say so, instead of assuming the repository root. The architecture reviewer no longer mentions a `reports_dir` setting that did not exist.

## 0.1.0
First public release.

- **Core skills (12):** the planning family (`feature-plan`, `features-next`, `features-status`, `features-archive`, `bug-report`, `bugs-next`, `bugs-status`, `bugs-archive`), `decision-record`, the work pipelines `feature-development` and `bug-fix`, and `gitflow`. The backlog is markdown under `docs/backlog/`; nothing is committed without you.
- **Extras (10, optional):** `code-reviewer`, `security-reviewer`, `database-reviewer`, `architecture-reviewer`, `product-scope-roaster`, `docs-sync`, `spec-compliance-check`, `dependency-upgrade`, `features-batch-development`, `bugs-batch-fix`. Each reads its project-specific checks from a named section of the project's own docs.
- **Conventions:** a fixed set of document locations and a `## Kit conventions` table in the project's `CLAUDE.md`; only `CLAUDE.md` is mandatory ([docs/conventions.md](docs/conventions.md)).
- **Configuration:** `.backlog-kit.toml` with `[paths] backlog_dir` and `[viewports]`, both optional.
- **Tools:** `tools/install.py` (copy install), `tools/vendor.py` (shared files into skills), `tools/migrate_check.py` (read-only check before replacing a project's own skills, see [MIGRATING.md](MIGRATING.md)).
