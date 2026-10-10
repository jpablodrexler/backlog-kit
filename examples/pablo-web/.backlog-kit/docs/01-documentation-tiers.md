# Documentation tiers

Read when: every run

pablo-web documents itself in three tiers, and all three need active upkeep:

- **`CLAUDE.md`** — a lean quick-start for an agent working in the code:
  commands, repo layout, and a set of short, fixed-pointer "Architecture"
  subsections that each name the essential rule and link to the `docs/*.md`
  section holding the full detail. It should **never** carry a full
  table/RLS reference, a routing table, a long step-by-step runbook, or a
  per-feature narrative inline — those belong in `docs/`. If you find one
  growing back in `CLAUDE.md`, move it out; this file was restructured more
  than once already (see its own "Documentation" section and
  `docs/decisions/0014-...`/`docs/decisions/0021-...`) specifically to stop
  detail drifting silently for a long time before anyone re-derived it from
  the code.
- **`docs/*.md`** — the actual reference material, indexed from `README.md`:
  `architecture.md` (system/database/component diagrams, project structure),
  `frontend.md` (technologies, app structure, routing, data flow, running/
  building/testing, Vercel deploy), `database.md` (tables, RLS policies,
  migration history, Supabase CLI workflow), `authentication.md` (Supabase
  Auth flow, guards, session model), and `features.md` (what's actually
  reachable in the UI). This is comprehensive — mermaid diagrams, full
  tables, provenance notes. Nothing else in the repo maintains it
  automatically; that's this skill's job.
- **`README.md`** — a short intro plus the documentation index table
  pointing into `docs/`. It should stay an index, not regrow the runbook
  content that now lives in `docs/frontend.md`/`docs/database.md`.
