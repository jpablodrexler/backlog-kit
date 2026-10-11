# Kit conventions

Where the backlog-kit skills read and write. Every project that uses the kit looks the same; a project keeps only the files it needs, and says in this section of its `CLAUDE.md` where it differs.

## Kit conventions

| Path | What it holds |
| ---- | ------------- |
| `docs/backlog/` | the backlog: `features-planned.md`, `features-implemented.md`, `bugs-open.md`, `bugs-fixed.md`, plus one brief per item in `features/` and `bugs/` (the folder is the one setting: `[paths] backlog_dir` in `.backlog-kit.toml`) |
| `docs/decisions/` | architecture decision records, numbered and append-only (`decision-record`) |
| `docs/explorations/` | notes of ideas still being explored, offered by `features-next` |
| `docs/reports/` | dated reports of the reviewers and the batch runs; usually gitignored |
| `docs/architecture.md` | system and component diagrams, the data-model diagram, the project structure |
| `docs/features.md` | what a user can actually reach today (never the planned backlog) |
| `docs/product.md` | optional: what the product is for and who uses it |
| `docs/frontend.md`, `docs/backend.md` | per side the project has: technologies, structure, routing or endpoints, data flow, running, building, testing and deploying |
| `docs/database.md` | tables, access rules, migration history, the database workflow |
| `docs/authentication.md` | the authentication flow, guards or filters, the session model |
| `docs/<topic>.md` | any other reference topic gets its own file |
| `CLAUDE.md` | the lean quick-start for an agent: commands, repo layout, short fixed-pointer subsections into `docs/`, and this section |
| `README.md` | a short intro and the documentation index into `docs/` |

The decisions, explorations and reports folders sit next to the backlog folder: with `backlog_dir = "app/docs/backlog"` they are `app/docs/decisions`, `app/docs/explorations` and `app/docs/reports`.

Every reference doc under `docs/` states what it is checked against in a line under its title, `Sources of truth: <paths or globs in the code, and any rule for reading them>` (a section with different sources carries its own line under its heading). `docs-sync` uses these lines to know which docs a code change affects. `CLAUDE.md` and `README.md` have fixed sources and need none.
