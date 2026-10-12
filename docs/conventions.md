# Conventions: where things live

The kit's skills read and write in fixed places, so every project that uses it looks the same. The table is [`shared/conventions.md`](../shared/conventions.md); `docs-sync` carries a copy.

## What a project must have

A `## Kit conventions` section in its `CLAUDE.md` with that table, the "Checked against" column filled in for the project. It is the one place that tells a person, any skill of the project, and `docs-sync`:

- where the backlog, the decisions, the explorations, the reports and each reference doc live;
- what each reference doc is compared with when `docs-sync` checks it against the code.

The column is a phrase, not a list of paths: the doc itself names the code it describes, and `docs-sync` also searches the docs for the path, folder and names of every changed file. A project keeps only the docs it needs, may add its own (`docs/<topic>.md`), and writes its own phrase where it differs from the kit's default. `docs-sync` checks the section on a full sweep and offers to add it when it is missing.

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
