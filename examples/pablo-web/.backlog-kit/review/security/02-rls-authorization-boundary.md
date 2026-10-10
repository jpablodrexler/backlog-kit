# Row Level Security: the Authorization Boundary
Read when: a change touches data access, a query or service method, or a database migration or policy

## 2. Row Level Security — the Actual Authorization Boundary

There is no server-side controller, filter chain, or middleware in this
project — **RLS policies on the Supabase tables are the entire
authorization layer**, and the frontend has no way to enforce anything RLS
doesn't already enforce (a malicious client can call the Supabase REST API
directly with the same anon key the legitimate frontend uses, bypassing
Angular entirely). This means:

🔴 Flag any new table or column exposed to `anon`/`authenticated` via
`GRANT` that has RLS enabled but **no policy** covering an operation the
frontend performs on it, or has RLS **not enabled at all** — this is not a
defense-in-depth nicety here, it is the only defense. Full detail (policy
correctness, `USING` vs. `WITH CHECK`, per-user scoping shape) lives in
`database-reviewer` §4 — invoke that skill for the actual migration/policy
review; this section exists so a security sweep doesn't skip past
`supabase/migrations/**` as "not frontend code, not in scope."

🔴 Flag any frontend code that filters or hides data purely in
TypeScript/the template (e.g. `tasks.filter(t => t.user_id === me.id)`)
under the assumption that this is what keeps other users' data safe — it
isn't; the query itself must be scoped by RLS, since the raw response from
Supabase is whatever RLS allowed through, and any client-side filtering on
top is cosmetic at best and a false sense of security at worst.

🟡 Flag a new service method whose data-scoping intent isn't obviously
backed by a corresponding RLS policy in the same change (e.g. a
"my tasks" query with no policy update in the diff, when the table's
existing policy was previously more permissive) — this is the same signal
`code-reviewer` §4 flags from the code-quality angle; flagging it here too
is deliberate, since a scoping gap is a security finding first and a
code-quality one second.

## 5. Row Level Security & Migration-Specific Checks

This section is a pointer, not a duplicate: **all detailed RLS/migration
security checks live in `database-reviewer` §4–§6** (policy coverage,
`USING` vs. `WITH CHECK` correctness, grants, `SECURITY DEFINER` functions,
migration mechanics). When this skill's scope includes
`supabase/migrations/**` (directly, or via the `supabase-migrations` layer
in a full sweep), invoke `database-reviewer` for that portion rather than
re-deriving the same checklist here — the two skills should agree, not
diverge, on what "correct RLS" looks like.

🔴 Flag a `SECURITY DEFINER` function (if one is ever introduced) with no
comment justifying why it needs to bypass RLS — this is the Supabase
equivalent of a Spring Security misconfiguration in a traditional backend:
a single place where the entire access-control model can be silently
punched through.
