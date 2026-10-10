# Views and functions
Read when: a migration creates or changes a view or function

## 5. Views & Functions

No `CREATE VIEW` or `CREATE FUNCTION` exists in this schema yet. If a
migration introduces the first one:

🔴 Flag any function created `SECURITY DEFINER` without an explicit,
commented justification — it executes with the privileges of the
function's owner (often `postgres`, bypassing RLS entirely), not the
caller. This is an easy way to accidentally punch a hole through the RLS
model described in §4.

🟡 Flag a `CREATE VIEW` that is not `CREATE OR REPLACE VIEW` — plain
`CREATE VIEW` fails on a rerun and can't be version-bumped in place.

🟡 Flag a view built on a table with RLS enabled where the view itself
doesn't inherit/re-declare equivalent row-level restrictions (a view
queried with `security_invoker` runs as the caller and inherits the base
table's RLS; a view without it can silently bypass RLS depending on how
it's created and by whom) — verify which behavior applies before assuming
a view is safe.
