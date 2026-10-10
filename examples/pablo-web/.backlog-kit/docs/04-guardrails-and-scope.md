# Guardrails and scope

Read when: every run

- Don't let `CLAUDE.md` regrow a full RLS/table reference, a routing table,
  or a long step-by-step runbook — that belongs in `docs/`. Moving
  misplaced detail out is itself a finding to fix, not just a staleness
  issue to patch in place.
- Every subsection under `CLAUDE.md`'s "Architecture" heading (Environment
  configuration, Frontend data flow, Pagination, Authentication, Database
  access model, UI library, Mobile-responsive layout, Deploying to Vercel)
  is a short, fixed pointer into the matching `docs/*.md` section, with no
  per-feature narrative of its own, by design — this was progressively
  restructured out of `CLAUDE.md` (see `docs/decisions/0014-...` and
  `docs/decisions/0021-...`). A feature that changes what one of these
  describes updates the linked `docs/*.md` file only; do not add narrative
  detail back into `CLAUDE.md`, and do not treat a subsection's unchanged
  wording as something needing a sync on every feature. The only reason to
  touch one of these subsections again is if the `docs/*.md` section (or
  heading) it points at is renamed or moved, or if the one or two
  load-bearing facts it states directly (e.g. the required minimum mobile
  check device, the pagination `PagedResult`/`PageRequest` shape) changes.
- This skill's scope is `CLAUDE.md`, `README.md`, and the five files
  directly under `docs/` (`architecture.md`, `authentication.md`,
  `database.md`, `frontend.md`, `features.md`). It does not touch
  `docs/backlog/features-planned.md`/`features-implemented.md` (owned by
  `feature-plan`/`features-archive`), `docs/decisions/*.md` (owned by
  `decision-record` — an append-only decision history, not current-state
  reference material this skill keeps synced against the code), or any of
  the gitignored
  `docs/reports/{code-review,security-review,database-review,spec-compliance,incident-response}/`
  report directories (owned by their respective skills) — those are
  tracked/managed elsewhere, not part of this skill's "keep the docs
  honest" job.
