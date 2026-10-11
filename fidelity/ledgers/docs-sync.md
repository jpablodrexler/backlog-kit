kit: extras/docs-sync
sub: JPPhotoManagerWeb/docs/backlog => <backlog>
sub: docs/backlog => <backlog>
sub: JPPhotoManagerWeb/docs/reports => <reports>
sub: docs/reports => <reports>

PARAM | name: web-docs-sync description: > Keeps `JPPhotoManagerWeb/CLAUDE.md` | description rewritten stack-free (TRIGGER structure kept); `scope` removed, `version` is the kit's (D30)
PARAM | # Web Docs Sync Skill | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | `JPPhotoManagerWeb` documents itself in two tiers, and both need activ | second project's variant of this text; the kit follows the first project
DROPPED | - **`CLAUDE.md`** — a lean quick-start for an agent working in the cod | second project's variant of this text; the kit follows the first project
DROPPED | - **`JPPhotoManagerWeb/docs/*.md`** — the actual reference material, i | second project's variant of this text; the kit follows the first project
PARAM | - **Full sweep** — audit every table/section in §1 against the current | second project's variant of this text; the kit follows the first project
PARAM | Both modes **edit the doc/config files directly** rather than writing | second project's variant of this text; the kit follows the first project
DROPPED | ## 1. Doc Sections & Their Source of Truth | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Section ¦ File(s) ¦ Source of truth to check against ¦ | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦---¦---¦---¦ | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Commands, package layout, conventions ¦ `CLAUDE.md` ¦ `pom.xml`/`pac | second project's variant of this text; the kit follows the first project
DROPPED | ¦ REST API table ¦ `docs/backend.md` (REST API section) ¦ Every `@Rest | second project's variant of this text; the kit follows the first project
DROPPED | ¦ `curl` examples ¦ `docs/curl-reference.md` ¦ Same controllers as abo | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Configuration table ¦ `docs/backend.md` (Configuration section) ¦ Ev | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Persistence narrative ¦ `docs/backend.md` (Persistence), `docs/archi | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Authentication flow ¦ `docs/authentication.md` ¦ `SecurityConfig`, ` | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Catalog pipeline & Kafka topics ¦ `docs/catalog-process.md` ¦ `infra | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Server-side caching ¦ `docs/backend.md`/`docs/architecture.md` ¦ `Ap | second project's variant of this text; the kit follows the first project
DROPPED | ¦ System/backend/database diagrams ¦ `docs/architecture.md` ¦ Overall | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Frontend structure & routes ¦ `docs/frontend.md` ¦ `frontend/src/app | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Feature list ¦ `docs/features.md` ¦ What's actually reachable in the | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Docker Compose reference ¦ `docs/docker-compose.md` ¦ `docker-compos | second project's variant of this text; the kit follows the first project
DROPPED | ¦ Kubernetes reference ¦ `docs/kubernetes.md` ¦ `k8s/*.yaml`, `kustomi | second project's variant of this text; the kit follows the first project
DROPPED | ¦ **Deploy manifest parity** ¦ `docker-compose.yml` ↔ `k8s/configmap.y | second project's variant of this text; the kit follows the first project
DROPPED | ¦ **Custom metrics ↔ dashboard** ¦ `grafana/provisioning/dashboards/ph | second project's variant of this text; the kit follows the first project
DROPPED | ## 2. Deploy Manifest Parity | second project's variant of this text; the kit follows the first project
DROPPED | `k8s/configmap.yaml`'s own header comment states the requirement direc | second project's variant of this text; the kit follows the first project
DROPPED | **Check:** every non-secret environment variable in `docker-compose.ym | second project's variant of this text; the kit follows the first project
DROPPED | **Secrets are out of scope for this check.** `JWT_SECRET`, `POSTGRES_P | second project's variant of this text; the kit follows the first project
DROPPED | 🔴 Flag a new environment variable added to `docker-compose.yml`'s `bac | second project's variant of this text; the kit follows the first project
DROPPED | **Fix:** add the missing key directly to whichever manifest is missing | second project's variant of this text; the kit follows the first project
DROPPED | ## 3. Custom Metrics ↔ Grafana Dashboard | second project's variant of this text; the kit follows the first project
DROPPED | Every custom application metric follows the pattern documented in `doc | second project's variant of this text; the kit follows the first project
DROPPED | **Check:** grep the backend for `Counter.builder("photomanager_`, `Tim | second project's variant of this text; the kit follows the first project
DROPPED | 🟡 Flag any `photomanager_*` metric registered in code with no correspo | second project's variant of this text; the kit follows the first project
DROPPED | 🟢 Flag a dashboard panel querying a `photomanager_*` metric name that | second project's variant of this text; the kit follows the first project
DROPPED | **Fix:** add a panel to `photomanager.json` following the existing pan | second project's variant of this text; the kit follows the first project
PARAM | 1. Identify what changed: `git diff origin/develop..HEAD --stat` (or t | second project's variant of this text; the kit follows the first project
PARAM | 4. Apply the fix directly with `Edit`, one section at a time, matching | second project's variant of this text; the kit follows the first project
DROPPED | 1. Read `JPPhotoManagerWeb/CLAUDE.md` and `JPPhotoManagerWeb/README.md | second project's variant of this text; the kit follows the first project
DROPPED | 2. For each row of §1 (plus §2 and §3), independently re-derive the cu | second project's variant of this text; the kit follows the first project
PARAM | 5. Summarize in chat: a short list of what was added/updated/removed, | second project's variant of this text; the kit follows the first project
DROPPED | - Never document behavior you haven't verified in the actual code — no | second project's variant of this text; the kit follows the first project
DROPPED | - Never read `JPPhotoManagerWeb/k8s/secret.yaml` or `JPPhotoManagerWeb | second project's variant of this text; the kit follows the first project
DROPPED | - Don't let `CLAUDE.md` regrow the content this skill's first run extr | second project's variant of this text; the kit follows the first project
DROPPED | - Manifest-parity and dashboard-panel fixes (§2, §3) are config edits, | second project's variant of this text; the kit follows the first project
PARAM | - This skill's scope is `CLAUDE.md`, `README.md`, and the files direct | second project's variant of this text; the kit follows the first project
PARAM | name: web-docs-sync description: > Keeps `CLAUDE.md`, the reference do | description rewritten stack-free (TRIGGER structure kept); `scope` removed, `version` is the kit's (D30)
DROPPED | pablo-web documents itself in three tiers, and all three need active u | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | - **`CLAUDE.md`** — a lean quick-start for an agent working in the cod #2 | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | - **`docs/*.md`** — the actual reference material, indexed from `READM | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | - **`README.md`** — a short intro plus the documentation index table p | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | - **Full sweep** — audit every row in §1 against the current codebase | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | ¦ Commands (Supabase CLI, frontend npm scripts) ¦ `CLAUDE.md` ("Comman | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Repository layout ¦ `CLAUDE.md` ("Repository layout") ¦ Actual top-l | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Documentation index ¦ `CLAUDE.md` ("Documentation"), `README.md` ("D | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ System architecture, database ER diagram, frontend component hierarc | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Frontend structure, routing table, data flow, running/building/testi | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Tables, RLS policies, migration history, Supabase CLI workflow ¦ `do | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Supabase Auth flow, guards, session storage/security model ¦ `docs/a | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Feature list ¦ `docs/features.md` ¦ What's actually reachable in the #2 | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Environment configuration ¦ `docs/frontend.md` ("Environment configu | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Frontend data flow / architecture narrative ¦ `docs/frontend.md` ("A | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Pagination ¦ `docs/frontend.md` ("Pagination") ¦ `frontend/src/app/c | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Authentication ¦ `docs/authentication.md` ¦ `frontend/src/app/core/a | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Database access model / RLS narrative ¦ `docs/database.md` ("Databas | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ UI library ¦ `docs/frontend.md` ("UI library") ¦ `frontend/package.j | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Mobile-responsive layout ¦ `docs/frontend.md` ("Mobile-responsive la | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
DROPPED | ¦ Vercel deploy settings ¦ `docs/frontend.md` ("Deploying to Vercel") | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | 1. Identify what changed: `git diff main..HEAD --stat` (or the equival | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 4. Apply the fix directly with `Edit`, one section at a time, matching #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 6. If a `docs/*.md` file's content changed enough that its one-line de | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 1. Read `CLAUDE.md`, `README.md`, and every file under `docs/` (exclud | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 2. For each row of §1, independently re-derive the current state from | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | 5. Summarize in chat: a short list of what was added/updated/removed, #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - Never document behavior you haven't verified in the actual code — no #2 | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
PARAM | - Don't let `CLAUDE.md` regrow a full RLS/table reference, a routing t | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
DROPPED | - Every subsection under `CLAUDE.md`'s "Architecture" heading (Environ | stack-specific text, moved unchanged to the project's review checklist files (D30, D31)
PARAM | - This skill's scope is `CLAUDE.md`, `README.md`, and the five files d | stack and tool names removed, `<reports>` path, or the project-checklists step (D30, D31); the generic wording is kept
