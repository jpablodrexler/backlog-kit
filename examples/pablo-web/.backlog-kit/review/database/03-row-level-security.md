# Row Level Security
Read when: every review

## 4. Row Level Security — the primary access-control layer

This is the highest-value section in this skill for this project. There is
no backend server to enforce authorization — RLS policies (plus the
coarse-grained `GRANT`s alongside them) are the *only* thing standing
between `anon`/`authenticated` clients and the data.

### 4.1 A table must have policies covering every operation the frontend performs

🔴 Flag any table with `ENABLE ROW LEVEL SECURITY` that has **zero**
policies for an operation (`SELECT`/`INSERT`/`UPDATE`/`DELETE`) that a
frontend service actually calls — with RLS enabled and no matching policy,
Postgres denies the operation outright for every role except the table
owner/`service_role`. For `SELECT` specifically, this denial is **silent**
from the frontend's point of view: `.select()` resolves with `data: []` and
`error: null`, not a thrown error (see `CLAUDE.md`'s documented incident).
Cross-check every `core/*.service.ts` method against the actual `CREATE
POLICY` statements for that table — don't assume a policy exists because
the table "obviously" needs one.

Before doing this cross-check by hand, run
`npm run rls-route-coverage:report` from `frontend/` — it replays every
migration in chronological order (`frontend/scripts/rls-route-coverage-report.js`)
and writes a dated table × SELECT/INSERT/UPDATE/DELETE-policy-count matrix
(plus RLS-enabled/anon-revoked columns) to
`docs/reports/rls-route-coverage/`, flagging any table with RLS enabled but
zero SELECT policies exactly like this rule does. It's a factual snapshot,
not a judgment call — several tables intentionally have fewer than 4
policies by design (reference tables like `document_type`/`bank`/
`currency`, the `notification` `SECURITY DEFINER` exception), so still
cross-check a flagged gap against CLAUDE.md's "Database access model"
section before treating it as a real finding rather than a documented
exception. The same report's second half (a route → E2E-test-coverage
table) is the `e2e-suite` skill's tool, not this one's — see that skill
§7.

🔴 Flag a table with RLS **not** enabled (`ALTER TABLE ... ENABLE ROW LEVEL
SECURITY` missing) that is reachable by `anon`/`authenticated` roles via
`GRANT` — this exposes every row to every client with no per-row
restriction at all.

### 4.2 Policy correctness

🔴 Flag a policy whose `USING`/`WITH CHECK` expression doesn't actually
scope by the authenticated user where per-user ownership is the intent —
this project's current pattern (`task`'s four policies in
`task_user_scoping.sql`) is `auth.uid() = user_id`; a new per-user table
should follow the same shape. Watch specifically for:
- A `SELECT`/`UPDATE`/`DELETE` policy using only `USING (...)` when the
  operation also needs `WITH CHECK (...)` (`UPDATE` needs both — `USING`
  gates which existing rows are visible to update, `WITH CHECK` gates what
  the row is allowed to become).
- An `INSERT` policy using `USING (...)` instead of `WITH CHECK (...)` —
  `INSERT` has no pre-existing row to apply `USING` to; only `WITH CHECK`
  applies.
- A policy scoped `TO anon, authenticated` when the operation should be
  `authenticated`-only (this project's history shows exactly this
  transition: the original `task_select_policy.sql` granted `anon,
  authenticated` read access; `task_user_scoping.sql` later revoked `anon`
  entirely and re-scoped to `authenticated` only, once login became
  mandatory — a new policy should match the *current* intent, `TO
  authenticated`, not resurrect the old permissive shape).

🟡 Flag a policy whose `USING`/`WITH CHECK` is literally `true` (fully
permissive) on a table containing anything user-specific — this is only
correct for genuinely public, non-owned data.

### 4.3 Grants alongside policies

🟡 Flag a migration that adds a `CREATE POLICY` for a role that has no
corresponding table-level `GRANT` (or an inherited default privilege via
`ALTER DEFAULT PRIVILEGES`, as set up in this project's first migration) —
RLS policies only restrict *rows*; the role still needs the underlying
`GRANT` for the operation at all, or it's denied before the policy is even
evaluated.

🟡 Flag a `REVOKE` that isn't paired with removing the now-pointless
policies for that role, or vice versa — this project's own
`task_user_scoping.sql` does both together (`REVOKE ALL ... FROM anon` +
`DROP POLICY` for the old `anon`-inclusive policies) in the same migration;
a future change that does only one half leaves a confusing, partially-dead
authorization state.
