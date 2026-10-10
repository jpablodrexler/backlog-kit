# Migration mechanics
Read when: a migration file is added, changed or renamed

## 6. Migration Mechanics (Supabase CLI)

🔴 Flag any modification to an **existing, already-applied** migration file
under `supabase/migrations/`. Once pushed (`npx supabase db push`), a
migration's content is fixed — the Supabase CLI tracks applied migrations
by filename/checksum remotely, and editing a historical file desyncs local
state from what's actually on the remote database. Any change goes in a
new migration file instead.

🟡 Flag a new migration filename that doesn't follow the Supabase CLI's own
`{YYYYMMDDHHMMSS}_{description}.sql` pattern (timestamp then a
`snake_case` description) — note that migrations pulled via `npx supabase
db pull` are auto-named `remote_schema.sql` by the CLI itself (see this
project's first two migrations) and that's expected for a pulled diff, not
a naming violation; the naming convention applies to migrations a
developer authors by hand going forward (e.g. `task_user_scoping.sql`).

🟡 Flag a migration that adds a `NOT NULL` column to an existing populated
table without either a `DEFAULT` or a backfill step in the same migration
— this project's own `task_user_scoping.sql` shows the right shape: add
the column nullable with a `DEFAULT`, delete/backfill the rows that would
otherwise violate the constraint, *then* `ALTER COLUMN ... SET NOT NULL` in
the same migration, all before any policy starts relying on the column
being non-null.

🟡 Flag a migration that both alters schema **and** performs a large data
backfill via `UPDATE`/`DELETE` on a large table without considering lock
duration or whether the delete is actually safe (the existing `DELETE FROM
public.task WHERE user_id IS NULL` in `task_user_scoping.sql` is fine at
this project's current scale — a handful of demo rows — but the same
pattern against a large populated table would need a batching/backfill
strategy discussion, not a blanket `DELETE`).

🟢 Flag a migration missing a header comment explaining *why* a
non-obvious step is being taken (this project's own migrations do this
well — see the numbered comments in `task_user_scoping.sql` explaining why
the column starts nullable and why old rows are deleted rather than kept).
