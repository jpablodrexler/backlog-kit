# Full-Codebase Sweep Layers
Read when: a full-codebase sweep

**The layers:**

| Layer key         | Report suffix     | Directory scope             | Primary checklist sections |
| ------------------- | -------------------- | ------------------------------ | ----------------------------- |
| Frontend core       | `frontend-core`       | `frontend/src/app/core/**`     | §2, §4 (full), §6.1            |
| Frontend features   | `frontend-features`   | `frontend/src/app/features/**` (and, until the `features/` move happens, the top-level `login/`, `register/`, `task-list/` folders) | §4.1, §6.1, §6.2 |
| Frontend shared     | `frontend-shared`     | `frontend/src/app/shared/**`   | §6.2                            |
| Supabase migrations | `supabase-migrations` | `supabase/migrations/**`       | §5 (full) — cross-check against `database-reviewer`'s own §4, since RLS is both a correctness *and* a security concern |
| Cross-cutting       | `cross-cutting`       | Whole repo; no single directory | §1 (dependency vulnerabilities), §3.3 (key handling), §7, any finding whose root cause spans two layers at once (e.g. a component reading `environment.ts` values it shouldn't) |

If only the frontend (or only the Supabase schema) is in scope, skip the
layers that don't apply.

## Subagent reminders

Include in each subagent's prompt, where it applies to that layer:

   - A reminder that `frontend/src/environments/environment.ts` is
     committed and its `supabaseKey` is a publishable/anon key, not a
     secret (see §3.3) — reviewing it is about confirming the *code* reads
     it correctly and no `secret`/`service_role` key ever lands there, not
     about treating its contents as sensitive.
