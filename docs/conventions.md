# Conventions: where things live

The kit's skills read and write in fixed places, so every project that uses it looks the same. The table is [`shared/conventions.md`](../shared/conventions.md); `docs-sync` carries a copy.

## What a project must have

A `## Kit conventions` section in its `CLAUDE.md` with that table, the "Checked against" column filled in for the project. It is the one place that tells a person, any skill of the project, and `docs-sync`:

- where the backlog, the decisions, the explorations, the reports and each reference doc live;
- what each reference doc is compared with when `docs-sync` checks it against the code.

The column is a phrase, not a list of paths: the doc itself names the code it describes, and `docs-sync` also searches the docs for the path, folder and names of every changed file. A project keeps only the docs it needs, may add its own (`docs/<topic>.md`), and writes its own phrase where it differs from the kit's default. `docs-sync` checks the section on a full sweep and offers to add it when it is missing.

## A project in a subfolder

When the backlog is not at `docs/backlog` (for example a repository that holds two applications and the backlog of one of them lives under `app/docs/backlog`), the `docs` folder is the one that holds it, and the project root is the folder above: `app/`. The `## Kit conventions` section goes in `app/CLAUDE.md`, the documentation index in `app/README.md`, and the reference docs in `app/docs/`. The repository root may keep its own `CLAUDE.md`, `README.md` and `docs/` for the other application; the skills ignore them. The one setting that tells the skills where the project is: `[paths] backlog_dir = "app/docs/backlog"` in `.backlog-kit.toml` at the repository root.

## Which documents a project needs

Only `CLAUDE.md` is mandatory. Everything else is optional: a skill that does not find its document still runs, works from the frame in its `SKILL.md` plus what `CLAUDE.md` and the docs say, and states in its report what it did not find.

**Mandatory**

| File | Needed by | Why |
| ---- | --------- | --- |
| `CLAUDE.md` | every skill that runs or checks something: `feature-development`, `bug-fix`, `gitflow`, the reviewers and the extras | the test, E2E and build commands, the repository layout, and the `## Kit conventions` section. Without the commands, the pipelines ask once or skip the phase. |

**Created by the kit on first use** (nothing to write up front)

| Path | Created by | Without it |
| ---- | ---------- | ---------- |
| `docs/backlog/` | `feature-plan`, `bug-report` | the planning skills start an empty backlog |
| `docs/decisions/` | `decision-record` | it creates the folder and its `README.md` index |
| `docs/reports/` | the reviewers and the batch runs | each creates its subfolder |
| `docs/explorations/` | you (notes of ideas) | `features-next` skips the step |

**Optional reference docs** (each one switches on a skill's project-specific checks)

| Doc | Section a skill reads | Skill | Without it |
| --- | --------------------- | ----- | ---------- |
| `docs/architecture.md` | `Architecture review checks` | `architecture-reviewer` | reviews with its eight built-in dimensions and says no project checks were found |
| `docs/database.md` | `Database review checks` | `database-reviewer` | reviews from the frame, `CLAUDE.md` and the existing schema |
| `docs/security.md` | `Security review checks`, including `Full-codebase sweep layers` | `security-reviewer` | scoped reviews work from the frame; the full-codebase sweep needs the layers and asks for a scope instead |
| `docs/frontend.md`, `docs/backend.md` | `Code review checks` (with `Full-codebase sweep layers`), `Spec compliance checks`, `Dependency upgrade checks` | `code-reviewer`, `spec-compliance-check`, `dependency-upgrade` | work from the frame, `CLAUDE.md` and the manifests; the code sweep needs the layers |
| `docs/product.md`, `docs/features.md` | `Product scope review checks`; the description of what users can reach | `product-scope-roaster` | works from the backlog alone and says no product description was found |
| any `docs/*.md` | the "Checked against" column of the `Kit conventions` table | `docs-sync` | keeps whatever docs exist in step with the code; with no table, it infers each doc's source and offers to add the table |
| `README.md` | the documentation index | `docs-sync` | nothing to keep in step |

A project keeps the docs it has a use for. Add a doc, or one of its sections, when a review keeps missing something the project cares about; the section names are exact, because the skills look them up by name. Each extra's page in [extras.md](extras.md) lists what its section holds.

## Example

A web app with a single-page frontend and a REST API on a relational database, so it keeps `docs/frontend.md` and `docs/backend.md` and adds one reference doc of its own.

```markdown
## Kit conventions

Where the backlog-kit skills read and write. This project keeps the files it needs and one extra reference doc, `docs/deployment.md`.

| Path | What it holds | Checked against |
| ---- | ------------- | --------------- |
| `docs/backlog/` | the backlog: `features-planned.md`, `features-implemented.md`, `bugs-open.md`, `bugs-fixed.md`, plus one brief per item in `features/` and `bugs/`, and the optional `definition-of-done.md` (the project-wide checklist every feature must meet) | — |
| `docs/decisions/` | architecture decision records, numbered and append-only | — |
| `docs/reports/` | dated reports of the reviewers and the batch runs (gitignored) | — |
| `docs/architecture.md` | diagrams, the project structure, and an `Architecture review checks` section | `db/migrations/**`, `web/src/routes.ts`, the top-level directory tree |
| `docs/features.md` | what a user can actually reach today | the routes and components under `web/src/` |
| `docs/frontend.md` | the frontend's structure, data flow, running, testing, and the `Code review checks`, `Spec compliance checks` and `Dependency upgrade checks` sections | `web/src/**`, `web/package.json` |
| `docs/backend.md` | the API's structure, endpoints, running, testing, and its own `Code review checks`, `Spec compliance checks` and `Dependency upgrade checks` sections | `api/src/**`, `api/pyproject.toml` |
| `docs/database.md` | tables, access rules, migration history, and the `Database review checks` section | every migration in `db/migrations/**` in order |
| `docs/security.md` | the authentication flow, the session model, and the `Security review checks` section | `api/src/auth/**`, the access-control rules, both dependency manifests |
| `docs/deployment.md` | how the app is built and released | `.github/workflows/**`, `Dockerfile` |
| `CLAUDE.md` | this file: the lean quick-start for an agent | its commands against the manifests, its layout against the real top-level directories |
| `README.md` | a short intro and the documentation index into `docs/` | which `docs/*.md` exist and what each covers |
```
