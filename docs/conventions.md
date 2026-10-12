# Conventions: where things live

The kit's skills read and write in fixed places, so every project that uses it looks the same. The table is [`shared/conventions.md`](../shared/conventions.md); `docs-sync` carries a copy.

## What a project must have

A `## Kit conventions` section in its `CLAUDE.md` with that table, the "Checked against" column filled in for the project. It is the one place that tells a person, any skill of the project, and `docs-sync`:

- where the backlog, the decisions, the explorations, the reports and each reference doc live;
- what each reference doc is compared with when `docs-sync` checks it against the code.

The column is a phrase, not a list of paths: the doc itself names the code it describes, and `docs-sync` also searches the docs for the path, folder and names of every changed file. A project keeps only the docs it needs, may add its own (`docs/<topic>.md`), and writes its own phrase where it differs from the kit's default. `docs-sync` checks the section on a full sweep and offers to add it when it is missing.

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

## Example: pablo-web

An Angular frontend that talks straight to Supabase (no backend server), so it has no `docs/backend.md` and two extra reference docs.

```markdown
## Kit conventions

Where the backlog-kit skills read and write. This project keeps the files it needs (no `docs/backend.md`: there is no backend server) and two extra reference docs, `docs/glossary.md` and `docs/hosting-cost-comparison.md`.

| Path | What it holds | Checked against |
| ---- | ------------- | --------------- |
| `docs/backlog/` | the backlog: `features-planned.md`, `features-implemented.md`, `bugs-open.md`, `bugs-fixed.md`, plus one brief per item in `features/` and `bugs/` | — |
| `docs/decisions/` | architecture decision records, numbered and append-only | — |
| `docs/explorations/` | notes of ideas still being explored | — |
| `docs/reports/` | dated reports of the reviewers and the batch runs (gitignored) | — |
| `docs/architecture.md` | system and component diagrams, the data-model diagram, the project structure, and an `Architecture review checks` section (what `architecture-reviewer` checks in this project) | `supabase/migrations/**`, `frontend/src/app/app.routes.ts`, the top-level directory tree |
| `docs/features.md` | what a user can actually reach today (never the planned backlog) | the routes and components under `frontend/src/app/` |
| `docs/frontend.md` | technologies, structure, routing, data flow, running, building, testing and deploying, and the `Code review checks`, `Spec compliance checks` and `Dependency upgrade checks` sections | `frontend/src/app/**`, `frontend/angular.json`, `frontend/package.json` |
| `docs/product.md` | what the product is for, and the `Product scope review checks` section | `docs/features.md` and the backlog tables |
| `docs/database.md` | tables, RLS policies, migration history, the Supabase CLI workflow, and the `Database review checks` section | every migration in `supabase/migrations/**` in order, and `supabase/config.toml` |
| `docs/security.md` | the Supabase Auth flow, guards, the session model, and the `Security review checks` section | `frontend/src/app/core/auth.service.ts`, `auth.guard.ts` and `app.config.ts`, the RLS policies in `supabase/migrations/**`, `frontend/package.json` |
| `CLAUDE.md` | this file: the lean quick-start for an agent | its commands against both `package.json` scripts, its layout against the real top-level directories |
| `README.md` | a short intro and the documentation index into `docs/` | which `docs/*.md` exist and what each covers |
```
