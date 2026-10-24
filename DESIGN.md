# backlog-kit — design

How the kit is put together and why. The history of each release is in [CHANGELOG.md](CHANGELOG.md).

## Goal

A small set of skills that takes a feature or a bug from idea to a verified, archived result, keeps the backlog as markdown files, follows git-flow, and works on a small project without writing guides or configuration. If a project does not fit, the skills are plain markdown to fork or copy and edit.

## Shape

- **Core (`skills/`, 12 skills):** planning (`feature-plan`, `features-next`, `features-status`, `features-archive`, `bug-report`, `bugs-next`, `bugs-status`, `bugs-archive`), `decision-record`, the two pipelines (`feature-development`, `bug-fix`) and `gitflow`.
- **Extras (`extras/`, 10 skills):** the reviewers, `docs-sync`, `dependency-upgrade`, `spec-compliance-check` and the two batch runners. Installed on request (`tools/install.py --extras`).
- **Scripts (`lib/`, `skills/*/scripts`):** ranking, status counts, table checks and ids. Mechanics are code; judgment is Claude. They are read-only and standard library only. `lib/` is the single source and `tools/vendor.py` copies it into each skill so every skill works installed alone.
- **State:** markdown. `<backlog>/features-planned.md`, `features-implemented.md`, `bugs-open.md`, `bugs-fixed.md`, one brief per item under `features/` and `bugs/`. No database, no service.

## Rules the skills keep

- **Nothing is committed unless the user asks.** Only `gitflow` pushes, opens a PR or tags, with the confirmations of the original skills (first push of a branch, tag, delete). Lint tests enforce it for the others.
- **Subagents report back with a signal line** (`REPRO: DONE`, `TESTS: PASS`, …), in the final text of their response; a missing signal is treated as blocked and the orchestrator checks the working tree before anything is re-run.
- **Confirmations stay in the orchestrator's context** (bug or feature selection, credentials, decision points); they are never delegated to a subagent.
- **Optional phases are skipped with a reason**, never silently: tests, E2E and build in the pipelines, database/security reviews and the viewport check inside the fix/implement phase, the version bump and regression suite in a release.
- **Credentials:** a skill never reads a credentials file and never puts credentials in a prompt; it asks how the test account is provided.
- **Fixed vocabulary:** priorities P0–P3, efforts in story points (1/2/3/5/8/13), severities S1–S4, bug prefix `BUG`, branch names `feature/`, `fix/`, base `develop`. The only settings are the backlog folder and the viewport check devices.
- **OpenSpec is optional.** With an `openspec/` folder the pipelines use it; without one, the feature brief is the spec.

## Extras and project knowledge

The reviewers, `docs-sync`, `spec-compliance-check` and `dependency-upgrade` need to know the stack. The skill holds the frame (workflow, severities, report format); the stack-specific knowledge lives in named sections of the project's own docs (`Architecture review checks`, `Code review checks`, `Dependency upgrade checks`, …). With none, the skill works from `CLAUDE.md` and the docs and says so in its report. See [docs/extras.md](docs/extras.md).

## Origin

The skills were converted from the workflow skills of two real projects, keeping their text wherever the stack allows; the pipelines' phases, the architecture reviewer and the roaster were rewritten freely afterwards.

## Tests

`python3 -m unittest discover -s tests` checks: frontmatter and author on every skill, no stack words in skills/scripts, the no-commit promise, gitflow's confirmations, script behaviour on fixture backlogs, vendored copies in sync (`tools/vendor.py --check`).
