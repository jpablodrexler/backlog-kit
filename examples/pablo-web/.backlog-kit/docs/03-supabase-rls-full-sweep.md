# Full sweep: Supabase migrations and RLS

Read when: full sweep, or any change touching `supabase/migrations/**`

For the Supabase/RLS rows in particular, read every migration file directly
in timestamp order — don't sample the most recent one or two and assume
earlier narrative still holds; a later migration can re-scope or drop
policies an earlier doc pass described (this already happened once: a
table moved from open read access to per-user scoping, and again when a
second table was added mirroring — but initially not exactly matching —
that precedent).

Never document behavior you haven't verified in the actual code — no
inferring an RLS policy's scope from a table name, no guessing which
routes exist from a component's folder name alone. Read
`app.routes.ts` and the actual `CREATE POLICY` statements directly.
