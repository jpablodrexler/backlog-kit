# Doc sections and their source of truth

Read when: every run

## 1. Doc Sections & Their Source of Truth

| Section | File(s) | Source of truth to check against |
|---|---|---|
| Commands (Supabase CLI, frontend npm scripts) | `CLAUDE.md` ("Commands") | Root `package.json` scripts, `frontend/package.json` scripts |
| Repository layout | `CLAUDE.md` ("Repository layout") | Actual top-level directories (`supabase/`, `frontend/`, `openspec/`, `docs/`) |
| Documentation index | `CLAUDE.md` ("Documentation"), `README.md` ("Documentation" table) | Which `docs/*.md` files actually exist and what each currently covers — a new doc file or a section moved between files must be reflected in both indexes |
| System architecture, database ER diagram, frontend component hierarchy, project structure | `docs/architecture.md` | `supabase/migrations/**` (for the ERD — every current table/column, not just the original migration), `frontend/src/app/app.routes.ts` (for the component-hierarchy diagram), actual top-level directory tree |
| Frontend structure, routing table, data flow, running/building/testing, Vercel deploy | `docs/frontend.md` | `frontend/src/app/**` (esp. `core/*.service.ts`, `app.routes.ts`), `angular.json` (build budgets, `outputPath`, `styles`), `frontend/package.json` scripts |
| Tables, RLS policies, migration history, Supabase CLI workflow | `docs/database.md` | `supabase/migrations/**` — read every migration in timestamp order, not just the most recent — and `supabase/config.toml` |
| Supabase Auth flow, guards, session storage/security model | `docs/authentication.md` | `frontend/src/app/core/auth.service.ts`, `auth.guard.ts`, `app.config.ts` (the `provideAppInitializer`/`ready` wiring) |
| Feature list | `docs/features.md` | What's actually reachable in the UI — cross-check against `app.routes.ts`/components, not `docs/backlog/features-planned.md`'s aspirational entries |
| Environment configuration | `docs/frontend.md` ("Environment configuration") | `frontend/src/environments/environment.ts` (committed), `angular.json`'s build config (no `fileReplacements`). `CLAUDE.md`'s "Environment configuration" subsection is a short, fixed pointer here and carries no detail of its own |
| Frontend data flow / architecture narrative | `docs/frontend.md` ("Application structure", "Data flow") | `frontend/src/app/core/*.service.ts`, actual component tree under `app/`. `CLAUDE.md`'s "Frontend data flow" section is a short, fixed pointer to these two `docs/frontend.md` sections and carries no per-feature detail of its own — a new/changed `core/` service or component never touches `CLAUDE.md`, only `docs/frontend.md` |
| Pagination | `docs/frontend.md` ("Pagination") | `frontend/src/app/core/*.service.ts` (`PageRequest`/`PagedResult` usage, `.range()` calls), `frontend/angular.json` (budget history). `CLAUDE.md`'s "Pagination" subsection is a short, fixed pointer here |
| Authentication | `docs/authentication.md` | `frontend/src/app/core/auth.service.ts`, `auth.guard.ts`, `app.config.ts` (the `provideAppInitializer`/`ready` wiring). `CLAUDE.md`'s "Authentication" subsection is a short, fixed pointer here |
| Database access model / RLS narrative | `docs/database.md` ("Database access model", "Tables") | `supabase/migrations/**` — read every migration in timestamp order, not just the most recent. `CLAUDE.md`'s "Database access model" subsection is a short, fixed pointer here |
| UI library | `docs/frontend.md` ("UI library") | `frontend/package.json`'s `@openng/optimus-ui` version, `frontend/src/optimus-theme.css`, `frontend/src/app/core/optimus-preset.ts`, `angular.json`'s `styles` array. `CLAUDE.md`'s "UI library" subsection is a short, fixed pointer here |
| Mobile-responsive layout | `docs/frontend.md` ("Mobile-responsive layout") | `frontend/src/app/app.ts` (`BreakpointObserver`), `nav-rail/`, `bottom-nav/`, `core/nav-entry.model.ts`. `CLAUDE.md`'s "Mobile-responsive layout" subsection is a short, fixed pointer here |
| Vercel deploy settings | `docs/frontend.md` ("Deploying to Vercel") | `frontend/package.json`'s `build` script, `angular.json`'s `outputPath`. `CLAUDE.md`'s "Deploying to Vercel" subsection is a short, fixed pointer here |
