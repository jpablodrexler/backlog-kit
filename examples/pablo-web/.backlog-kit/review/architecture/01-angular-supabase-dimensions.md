# Architecture Reviewer — this project's dimensions (Angular frontend, Supabase)
Read when: every architecture review

Maps to: P1→D1, P2→D2, P3→D3, P4→D4 (browser storage), P5→D4 (state and coordination), P6→D8, P7→D5, P8→D7

## The dimensions

1. **File/folder organization & naming** — `core → features ← shared`
   structure (`docs/frontend.md`'s "Application structure"; today the code is flat — feature folders sit directly under `app/` and there is no `features/` directory yet — so judge the layering against what is actually there, not the arrow), whether feature
   folders stay self-contained, whether `shared/` holds genuinely
   multi-consumer code or single-consumer code kept there "for parity."
2. **Layering & inter-layer communication** — the Service → Component
   pattern (`CLAUDE.md`'s "Frontend data flow": data access in an
   injectable `core/` service, never a direct Supabase call from a
   component), and how components talk to each other absent that direct
   parent/child relationship (an `@Input`/`@Output`, a shared service, or
   — see P5 — an implicit shared signal).
3. **API / data-access patterns** — the no-`HttpClient`/no-REST-layer
   model (`@supabase/supabase-js` as the sole transport, RLS as the
   actual authorization boundary rather than a server-side authz layer),
   and the pagination convention (`PageRequest`/`PagedResult`, a
   `getAllX()` companion for unbounded/chart-feeding reads — see
   `CLAUDE.md`'s "Pagination").
4. **Browser-storage (`localStorage`) usage** — enumerate every
   `localStorage` read/write in the whole app, components included (`Grep -r "localStorage\."
   frontend/src/app/`); confirm each is a genuine per-browser
   preference (theme, language, active household member) rather than
   something that should be synced data, and confirm auth tokens are
   left to `@supabase/supabase-js`'s own persistence rather than
   hand-rolled.
5. **State management** — signals-based state throughout, no NgRx/Akita
   (appropriate for this app's actual complexity — don't recommend one
   unless evidence genuinely shows a need). The specific technique this
   skill applies here, always, on every run that touches this dimension:
   for every `core/` service that exposes a signal, an `effect()`
   dependency, or an event-like method (`refresh()`, `notify()`, a
   `version`/`tick`-style counter), `Grep` every call site across the
   whole `frontend/src/app` tree and check whether those call sites span
   features unrelated to the service's own name/purpose. A service whose
   consumers span two or more features that have no parent/child
   relationship to each other, and whose name doesn't describe that
   broadcast role, is the exact shape of the `ActiveHouseholdMemberService`
   finding recorded in `02-motivating-case.md` (already fixed there) — flag it the same way, with the full call-site count
   and the list of features it spans.
6. **Routing & guards** — lazy-loading coverage, functional guard usage
   (`authGuard`/`redirectIfAuthenticatedGuard`), whether route-level
   concerns (auth gating, scroll restoration) stay out of feature
   components.
7. **Error handling & logging** — `GlobalErrorHandler`/`ErrorLogService`
   coverage, whether a feature has grown its own ad hoc error handling
   instead of relying on the global pipeline.
8. **Testing architecture** — a light pointer only (existing coverage:
   component-test ratio, whether new features get co-located `.cy.ts`
   files). Don't duplicate `cypress-unit-test-developer`/`e2e-suite`/
   `quality-metrics` — they own this in depth; this skill only flags it
   if a structural pattern (e.g. a whole feature with no tests at all)
   shows up incidentally while reviewing another dimension.
