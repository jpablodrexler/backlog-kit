# Database context and workflow specifics
Read when: every review

Review the PostgreSQL schema of the pablo-web Supabase project: migrations
under `supabase/migrations/*.sql`, and the Supabase-JS queries issued
against them from `frontend/src/app/core/*.service.ts`. There is no ORM and
no backend server — the frontend calls `supabase.client.from('<table>')...`
directly, and **Row Level Security policies are the entire server-side
access-control layer** (see `CLAUDE.md`'s RLS gotcha: a missing policy
returns an empty array to the client, not an error, which has already
caused a real bug in this project — `task_select_policy.sql` was the fix).

## Workflow (project specifics)

2. Read every migration file in scope **in filename order**
   (`{YYYYMMDDHHMMSS}_{description}.sql`, sorted by timestamp — this is the
   Supabase CLI's own naming scheme, not a hand-maintained version number)
   — schema history is cumulative, so a column added in one migration may
   be altered or have its RLS policy replaced in a later one (e.g.
   `task_user_scoping.sql` drops and replaces the policies
   `task_select_policy.sql` and the initial `remote_schema.sql` migration
   created). Reviewing a migration in isolation misses that.
3. For each table touched, find every service method under
   `frontend/src/app/core/` (`TasksService` and anything similar) that
   reads or writes it, and check whether the query's filter/sort columns
   are covered by an actual index (§3) — not just plausible-looking ones.
4. **For every table with RLS enabled, enumerate its actual policies** (§4)
   — a table can have `ENABLE ROW LEVEL SECURITY` with zero policies (which
   silently denies everything to `anon`/`authenticated`) or with policies
   that don't cover every operation the frontend actually performs.

## Severity levels (project wording)

| Level             | Meaning                                                                                     |
| ----------------- | --------------------------------------------------------------------------------------------- |
| 🔴 **CRITICAL**   | Data integrity risk, an RLS gap that exposes or hides data incorrectly, or a query that will corrupt/silently drop data. Must be fixed before merging. |
